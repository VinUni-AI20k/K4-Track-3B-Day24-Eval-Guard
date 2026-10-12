# Phân tích lỗi Phase A

Nhóm: FourPeoples

Người soạn bản thảo ban đầu: Mai Văn Trường – 2A202602983 (soạn báo cáo với hỗ trợ của Claude Code khi chạy batch, số liệu trích xuất từ JSON)
Người review & xác minh Phase A: Nguyễn Hoàng Anh – 2A202602811 (đối chiếu 10 câu bottom với answer/contexts thực tế, kiểm tra tính nhất quán giữa code, artifacts và báo cáo)

Nguồn: `artifacts/ragas_50q.json`; run timestamp: 2026-10-12T12:38:14+00:00.
Generation mode/fallback và điều kiện chạy: cả 50 answers có `generation_mode = llm`. Lượt
`setup_answers.py --live` đầu tiên bị mất kết nối OpenAI liên tục ở id 20–33 nên 14 câu rơi vào
`extractive_fallback`; 14 câu này được sinh lại bằng `scripts/regenerate_fallbacks.py` (giữ nguyên
contexts do search/rerank lấy, cùng prompt và cùng `GENERATION_MODEL`) trước khi chạy RAGAS.
Pipeline: hierarchical chunking (m1) → enrichment 1 call/chunk (m5) → BM25 + BGE-M3 trên Qdrant
v1.9.7, RRF (m2) → `bge-reranker-v2-m3` top-3 (m3). Corpus có 107 child chunks; hai PDF scan
(`BCTC.pdf`, Nghị định 13/2023) không có text layer nên không được index.
Models generation/evaluator: generation `gpt-4o-mini-2024-07-18`; evaluator từ m4
`gpt-4o-mini` (LLM) và `text-embedding-3-small` (embedding cho answer_relevancy).

## Điểm theo distribution

| Metric | factual (20) | multi_hop (20) | adversarial (10) |
|---|---|---|---|
| faithfulness | 0.9500 | 0.5512 | 0.8000 |
| answer_relevancy | 0.5584 | 0.4421 | 0.4260 |
| context_precision | 0.9583 | 0.9667 | 0.9583 |
| context_recall | 0.9000 | 0.7958 | 0.6833 |
| avg_score | 0.8417 | 0.6889 | 0.7169 |

Retrieval tốt đều ở cả ba nhóm (context_precision ≈ 0.96). Khác biệt chủ yếu nằm ở bước
generation: faithfulness của multi_hop chỉ 0.55, và answer_relevancy thấp ở mọi nhóm.

## Bottom 10 và nguyên nhân

Diagnosis/suggested_fix dưới đây là output nguyên văn của Task 3 (`bottom_10`).

| Rank | ID | Distribution | avg_score | worst_metric | Diagnosis (Task 3) | Suggested fix (Task 3) |
|---|---|---|---|---|---|---|
| 1 | 39 | multi_hop | 0.1250 | faithfulness | LLM hallucinating (faithfulness=0.00) | Tighten system prompt, lower temperature |
| 2 | 44 | adversarial | 0.3125 | faithfulness | LLM hallucinating (faithfulness=0.00) + ghi chú bẫy phiên bản/phủ định | Tighten system prompt, lower temperature; thêm metadata version, ưu tiên bản hiện hành khi rerank |
| 3 | 33 | multi_hop | 0.3750 | faithfulness | LLM hallucinating (faithfulness=0.00) | Tighten system prompt, lower temperature |
| 4 | 50 | adversarial | 0.4167 | faithfulness | LLM hallucinating (faithfulness=0.00) + ghi chú bẫy phiên bản/phủ định | Tighten system prompt, lower temperature; thêm metadata version, ưu tiên bản hiện hành khi rerank |
| 5 | 21 | multi_hop | 0.4375 | answer_relevancy | Answer doesn't match question (answer_relevancy=0.00) | Improve prompt template |
| 6 | 5 | factual | 0.6013 | faithfulness | LLM hallucinating (faithfulness=0.00) | Tighten system prompt, lower temperature |
| 7 | 24 | multi_hop | 0.6175 | faithfulness | LLM hallucinating (faithfulness=0.00) | Tighten system prompt, lower temperature |
| 8 | 38 | multi_hop | 0.6351 | faithfulness | LLM hallucinating (faithfulness=0.00) | Tighten system prompt, lower temperature |
| 9 | 31 | multi_hop | 0.6402 | faithfulness | LLM hallucinating (faithfulness=0.33) | Tighten system prompt, lower temperature |
| 10 | 7 | factual | 0.6664 | answer_relevancy | Answer doesn't match question (answer_relevancy=0.33) | Improve prompt template |

Câu hỏi tương ứng: 39 so sánh mật khẩu v1.0/v2.0; 44 chu kỳ đổi mật khẩu; 33 phụ cấp + phép của
Manager 12 năm; 50 VPN cá nhân khi WFH; 21 phép + lương Senior 9 năm; 5 phê duyệt mua 55 triệu;
24 phạt tạm ứng quá hạn; 38 khách sạn công tác nước ngoài; 31 khách sạn công tác trong nước;
7 phê duyệt nghỉ không lương 20 ngày.

Đối chiếu answer/contexts/reference cho thấy diagnosis tự động "LLM hallucinating" **không đúng**
với phần lớn các câu này. Có ba kiểu lỗi thật:

1. **Từ chối quá mức (over-refusal), không phải hallucination** — id 39, 44, 33, 50 (rank 1–4).
   Cả bốn trả lời đúng một câu "Không tìm thấy." trong khi contexts có thông tin cần thiết:
   context đầu của id 39 là chính sách mật khẩu v1.0, của id 33 là chính sách nghỉ phép v2024,
   của id 50 là quy định sử dụng VPN. RAGAS chấm câu từ chối faithfulness = 0 và
   answer_relevancy = 0 (không có khẳng định nào để kiểm, không trả lời câu hỏi). Giả thuyết
   nguyên nhân: quy định trong system prompt "Trả lời CHỈ dựa trên context. Nếu không có → nói
   'Không tìm thấy.'" có thể quá khắt khe, khiến mô hình có xu hướng chọn từ chối an toàn khi
   câu hỏi cần ghép hai tài liệu hoặc context chỉ chứa một phần thông tin.
   Đây là 4/50 câu nhưng chiếm cả 4 vị trí cuối bảng.
2. **Suy luận/tính toán đúng nhưng bị chấm không faithful** — id 24, 38, 31, 5. Answer id 24 tính
   phí phạt 2% × 15.000.000 × 5/30 = 50.000 VNĐ, khớp reference; id 38 ra 600 USD, id 31 ra
   2.400.000 VNĐ, id 5 trả lời đúng "Tổng Giám đốc (CEO)". RAGAS faithfulness tách answer thành
   các khẳng định và đòi mỗi khẳng định được context nêu trực tiếp; kết quả phép tính
   ("bị phạt 50.000 đồng") không có nguyên văn trong context nên bị chấm 0. Quan sát này phản ánh
   đặc điểm cố hữu trong cơ chế trích xuất khẳng định của metric RAGAS đối với câu cần tính toán,
   không phải do pipeline tự bịa đặt thông tin ngoài tài liệu.
3. **Trả lời thiếu một nửa câu hỏi** — id 21: đúng 18 ngày phép nhưng nói không tìm thấy lương
   Senior (20–35 triệu); context_recall = 0 cho thấy chunk bảng lương không vào top-3. Đây là lỗi
   retrieval cho câu hỏi hai ý. Id 7 đúng (CEO phê duyệt) nhưng thiếu lưu ý tự đóng bảo hiểm.

## Matrix và nhóm yếu nhất

Mỗi câu được đếm một lần theo worst_metric của nó; tổng mỗi cột chỉ là cỡ nhóm 20/20/10.

| worst_metric | factual | multi_hop | adversarial | Tổng |
|---|---|---|---|---|
| faithfulness | 1 | 10 | 2 | 13 |
| answer_relevancy | 17 | 10 | 7 | 34 |
| context_precision | 0 | 0 | 0 | 0 |
| context_recall | 2 | 0 | 1 | 3 |

Nhóm yếu theo mean thấp nhất: multi_hop; mean: 0.6889 (adversarial 0.7169, factual 0.8417).
Worst metric xuất hiện nhiều nhất: answer_relevancy; số câu: 34.

multi_hop yếu vì hai lỗi ở mục trên cộng lại: 10/20 câu có worst_metric là faithfulness, gồm hai
câu từ chối (33, 39) và các câu tính toán bị metric chấm thấp. answer_relevancy là metric thấp nhất
ở 34/50 câu kể cả các answer đúng (mean của 46 answer không từ chối là 0.528). Metric này sinh câu
hỏi ngược từ answer rồi so embedding với câu hỏi gốc; answer tiếng Việt ngắn, không lặp lại đủ
chủ thể/điều kiện của câu hỏi nên điểm bị kéo xuống. Vì vậy không nên đọc 0.44–0.56 là "answer lạc
đề" mà cần đọc kèm nội dung.

Đề xuất sửa cụ thể và cách kiểm tra:

- Sửa prompt generation: cho phép trả lời phần có trong context và nói rõ phần nào không có, thay
  vì từ chối toàn bộ; yêu cầu nêu phiên bản chính sách áp dụng. Chạy lại `setup_answers.py --live`
  rồi Phase A; kỳ vọng số câu "Không tìm thấy." giảm từ 4 và faithfulness multi_hop tăng.
- Tăng `RERANK_TOP_K` từ 3 lên 5 cho câu hỏi hai ý (id 21, 33): kiểm tra context_recall
  multi_hop (hiện 0.7958) có tăng mà context_precision không giảm mạnh.
- Với câu tính toán, đánh giá thêm bằng answer correctness so với ground_truth thay vì chỉ dựa vào
  faithfulness.

## Bẫy adversarial và giới hạn

adversarial (0.7169) thấp hơn factual (0.8417), nhưng đọc từng câu cho thấy pipeline **xử lý đúng
bẫy ở 8/10 câu**:

- Version conflict: id 41 trả lời 15 ngày (v2024, không phải 12 ngày v2023); id 43 trả lời 12 ký tự
  (v2.0, không phải 8 ký tự v1.0); id 45 MFA bắt buộc (v2.0); id 49 hỏi đích danh v2023 và trả lời
  12 ngày kèm ghi chú v2024 đang hiệu lực.
- Negation trap: id 46 "thử việc KHÔNG được nghỉ phép năm"; id 48 "thử việc chưa được hưởng PVI";
  id 47 "không nên tự xử lý malware".
- Hai câu thất bại là id 44 (chu kỳ đổi mật khẩu, đáp án đúng 120 ngày theo v2.0) và id 50 (VPN
  cá nhân bị cấm) — cả hai đều do từ chối "Không tìm thấy.", không phải do chọn nhầm bản cũ hay
  đảo phủ định.

Như vậy điểm adversarial thấp hơn chủ yếu do 2 câu từ chối và do context_recall (0.6833) — reference
của nhóm này có thêm thông tin phiên bản cũ mà top-3 không phải lúc nào cũng lấy đủ. Điểm thấp hơn
không tự chứng minh pipeline nhận ra bẫy; bằng chứng nhận ra bẫy là nội dung các answer ở trên.

Giới hạn: chỉ 50 câu (10 adversarial) và một lượt chạy RAGAS; evaluator gpt-4o-mini có độ dao động
giữa các lượt; RAGAS 0.1.22 chấm tiếng Việt bằng prompt tiếng Anh. 14 answers được sinh lại sau sự
cố mạng (cùng contexts, cùng model), không phải cùng một lượt với 36 answers còn lại.
