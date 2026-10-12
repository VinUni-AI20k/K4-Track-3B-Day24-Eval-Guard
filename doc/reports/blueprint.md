# Blueprint CI/CD cho RAG và guardrails

Nhóm: Track 3B - Nhóm 24

Người phụ trách: Ngô Anh Khoa (2A202602965) & Mai Quang Dũng (2A202602966)

Đây là **đề xuất CI/CD**, không phải workflow đã được triển khai/chạy.
Nguồn kết quả: artifacts/ragas_50q.json, judge_results.json, guard_results.json.
Run timestamp: 2026-10-12T09:29:45.903742+00:00; guard models: gpt-4o-mini.
Models generation/evaluator/judge từ A/B: generation: gpt-4o-mini (answers_50q.json); evaluator: gpt-4o-mini, text-embedding-3-small (ragas_50q.json); judge: gpt-4o-mini (judge_results.json).

## Kiến trúc và failure action

Input → Presidio → NeMo input → RAG → NeMo output → response.
Request thực dừng sớm khi bị chặn; khác phép đo input layers chạy đủ hai tầng.

Data flow tuần tự đi qua 4 trạm gác: Đầu tiên, truy vấn từ người dùng đi qua Layer 1 (Presidio PII Detector) để phát hiện và gán nhãn các thực thể PII (CCCD, SĐT, Email). Nếu không chứa PII, truy vấn chuyển sang Layer 2 (NeMo input rail) để kiểm tra các hành vi tấn công jailbreak, prompt injection và yêu cầu lạc đề. Nếu an toàn, truy vấn được gửi vào RAG pipeline (gồm Qdrant vector search, FlashRank reranking và GPT-4o-mini generation). Câu trả lời sinh ra tiếp tục qua Layer 3 (NeMo output rail) để đảm bảo không rò rỉ dữ liệu nhạy cảm hoặc định danh cá nhân trước khi trả về người dùng cuối.

Cơ chế Failure action áp dụng nguyên tắc fail-fast (short-circuit). Khi Layer 1 hoặc Layer 2 phát hiện vi phạm, hệ thống ngắt xử lý ngay lập tức, trả thông báo từ chối lịch sự tiêu chuẩn và không gọi RAG hay LLM sinh câu trả lời. Nếu Layer 3 phát hiện nội dung độc hại hoặc PII trong câu trả lời, output gốc sẽ bị hủy bỏ và thay thế bằng câu thông báo từ chối an toàn.

Về ghi log và ẩn danh (log/redact): Dữ liệu chứa PII được anonymize thành các thẻ định danh như <VN_CCCD>, <VN_PHONE>, <EMAIL_ADDRESS> trước khi ghi vào log kiểm toán. Toàn bộ API keys và credentials được quản lý tập trung qua Secret Manager hoặc biến môi trường bảo mật, tuyệt đối không lưu trong mã nguồn. Khi dịch vụ LLM gặp lỗi gián đoạn mạng hoặc timeout, hệ thống tự động kích hoạt fallback rule-based / regex để đảm bảo tính an toàn liên tục cho hệ thống.

## Phạm vi và số đo latency

Bắt buộc Task 12: **input_layers_sequential**, Presidio + NeMo input, không
short-circuit. Engines tạo trước đo; có hai warm-up thật không tính vào mẫu.
Percentile nội suy tuyến tính từ raw samples; tổng từ tổng từng sample.

Số mẫu timed: 20; warm-up: 2;
phương pháp: linear.

| Layer / scope | P50 ms | P95 ms | P99 ms | Tình trạng |
|---|---|---|---|---|
| Presidio | 7.05 | 11.42 | 11.51 | Đạt (nhanh, xử lý regex PII) |
| NeMo input | 670.42 | 914.61 | 928.00 | Đo live LLM API (RTT mạng + self-check) |
| Input guard sequential | 680.53 | 924.78 | 935.60 | Vượt budget 500ms do độ trễ mạng API |
| RAG | chưa đo | chưa đo | chưa đo | Ngoài phạm vi bắt buộc |
| NeMo output | chưa đo | chưa đo | chưa đo | Ngoài phạm vi bắt buộc |
| Full guard / short-circuit request | chưa đo | chưa đo | chưa đo | Không suy từ input_guard_ms |

Input-layer budget target: 500ms; kết quả thực tế/budget_ok: P95 = 924.78 ms / False (chưa đạt chỉ tiêu 500ms do gọi live cloud API qua internet).

Phân tích bottleneck và kế hoạch tối ưu: Tầng Presidio PII hoạt động cực kỳ nhẹ và nhanh (P95 chỉ 11.42 ms). Tuy nhiên, tầng NeMo input rail chạy qua live OpenAI API (gpt-4o-mini) từ xa chịu ảnh hưởng của RTT mạng quốc tế và thời gian inference của LLM, dẫn đến độ trễ P95 đạt 914.61 ms và tổng sequential P95 là 924.78 ms (vượt mức ngân sách 500ms, budget_ok = False). Để đưa P95 về dưới 500ms trong môi trường production, nhóm đề xuất chuyển tầng self-check input sang mô hình local embedding/classifier chạy on-premise (như ModernBERT hoặc small ONNX model) hoặc áp dụng kỹ thuật streaming/caching. Đối với các tầng ngoài phạm vi bắt buộc gồm RAG, NeMo output và full short-circuit request, nhóm giữ nguyên trạng thái "chưa đo" theo đúng quy chuẩn báo cáo. Trong giai đoạn thử nghiệm staging tiếp theo, nhóm dự kiến thu thập 100 mẫu truy vấn production với 5 vòng warm-up, sử dụng timestamp phân tán để đo lường đầy đủ độ trễ end-to-end của toàn bộ hệ thống.

## CI gates đề xuất

- RAGAS faithfulness ≥0.75, avg_score ≥0.65 trên 50 câu.
- Attacks ≥18/20 cho CI đề xuất; clean 8/8 allowed; output cases đúng.
- Full guard P95 <500ms chỉ áp dụng sau khi thực sự đo full guard.

Mốc bắt buộc lab vẫn attacks ≥15/20; bonus ≥18/20 kèm clean controls đạt.

Đề xuất kịch bản tích hợp CI/CD tự động trên GitHub Actions / GitLab CI: Pipeline sẽ tự động kích hoạt khi có pull request vào nhánh chính. Bước 1 chạy kiểm thử đơn vị ngoại tuyến `pytest tests/ -m "not integration"` để đảm bảo tính toàn vẹn của logic code mà không phát sinh chi phí API. Bước 2 thực thi kịch bản kiểm tra chất lượng tự động thông qua `python scripts/check_lab.py --with-tests`. Nếu bất kỳ bài kiểm tra nào thất bại hoặc các chỉ số chất lượng không đạt ngưỡng quy định, script sẽ trả mã thoát nonzero (exit code 1) làm dừng ngay lập tức quá trình triển khai. Các tham số như MIN_FAITHFULNESS=0.75 và MIN_ATTACK_BLOCK=18 sẽ được cấu hình dạng biến môi trường CI. Lưu ý: Bản mô tả này là đề xuất quy trình CI/CD cho dự án, chưa triển khai thực tế trên môi trường cloud runner production.

## Monitoring và cải tiến

Hệ thống giám sát định kỳ cần theo dõi sát sao 4 chỉ số vận hành cốt lõi: Tỷ lệ chặn nhầm (False Positive Rate) với ngưỡng cảnh báo 5% và ngưỡng dừng khẩn cấp 10%; Tỷ lệ phát hiện tấn công (Attack Pass Rate) với ngưỡng cảnh báo khi thấp hơn 90%; Độ trễ P95 với ngưỡng cảnh báo khi vượt quá 800ms; và độ suy giảm điểm số RAGAS (Drift) khi faithfulness giảm quá 0.05 so với baseline chuẩn. Quy trình lấy mẫu thực hiện ngẫu nhiên trên 5% lưu lượng truy vấn thực tế hằng ngày, toàn bộ dữ liệu được ẩn danh hóa và chuyển tới nhóm QA thực hiện gán nhãn chéo (Human-in-the-loop). Khi phát sinh lỗi False Positive, hệ thống gửi thông báo tới On-call Engineer để rà soát ngữ cảnh và cập nhật whitelist/prompt cho NeMo Rails. Toàn bộ log chỉ được truy cập bởi nhân sự bảo mật được phân quyền.

RAGAS mean/worst distribution: Điểm trung bình tổng thể đạt 0.7937; phân phối yếu nhất là adversarial với điểm trung bình đạt 0.7240.
Cohen’s κ: 0.80 (đạt mức đồng thuận substantial agreement giữa LLM Judge và Human Judge).
Attacks passed: 18/20; clean false_positive_rate: 0.0 (không có câu sạch nào bị chặn nhầm).

Nhóm đề xuất 4 giải pháp cải tiến hệ thống dựa trên bằng chứng thực nghiệm:
1. Tối ưu hóa thời gian phản hồi của NeMo Input Guard bằng cách triển khai mô hình phân loại cục bộ dạng nhẹ (small fine-tuned classifier như DeBERTa hoặc ModernBERT) để lọc nhanh các mẫu tấn công phổ biến trước khi gọi LLM, giúp giảm P95 xuống dưới 50ms.
2. Mở rộng bộ nhận diện PII cho Presidio bằng cách bổ sung thêm nhận diện mã số thuế doanh nghiệp, số tài khoản ngân hàng Việt Nam và số thẻ căn cước mẫu mới nhằm tăng cường khả năng bảo vệ dữ liệu nội bộ.
3. Cải thiện độ chính xác truy xuất RAG đối với nhóm câu hỏi adversarial (hiện có điểm trung bình thấp nhất 0.7240) bằng cách nâng cấp chiến lược chunking theo ngữ nghĩa (semantic chunking) và tinh chỉnh trọng số reranker để loại bỏ nhiễu ngữ cảnh.
4. Triển khai cơ chế đánh giá đa chuyên gia (multi-judge consensus voting) cho hệ thống LLM Judge để loại bỏ hoàn toàn position bias trong các tình huống câu trả lời có độ dài chênh lệch lớn.
