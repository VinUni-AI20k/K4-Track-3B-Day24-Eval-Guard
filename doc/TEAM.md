# Nhóm thực hiện K4 Track 3B

Tên nhóm: FourPeoples

Repo chung: https://github.com/hoanganhIT04/K4-L3-DAY24-FourPeoples-Eval-Guard

Trưởng nhóm/người nộp: Nguyễn Hoàng Anh – 2A202602811 (chủ repo)

Ngày lab/deadline áp dụng: lab 12/10/2026; deadline 11:59 AM 13/10/2026 theo README — Asia/Ho_Chi_Minh (UTC+07:00)

Commit dùng để chấm: chưa chốt; trưởng nhóm ghi SHA commit trên `main` sau khi merge nhánh `integration` và trước khi nộp link.

Mỗi nhóm nộp một repo. Điền đủ thành viên và một mục INDIVIDUAL cho từng người.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò / công việc thật | Bằng chứng |
|---|---|---|---|---|
| 1 | Mai Văn Trường | 2A202602983 | Tích hợp pipeline và chạy batch: port m1–m5 từ Day 18, sửa `m4_eval.evaluate_ragas`, cài môi trường, sinh 50 answers, viết Task 1–12 trong `phase_a_ragas.py`, `phase_b_judge.py`, `phase_c_guard.py`, sửa prompt guard, chạy Phase A/B/C live, soạn 3 báo cáo (có Claude Code hỗ trợ) | Commit `2de53da`, `0af6999` trên nhánh `integration`; `artifacts/*.json`; `doc/reports/*.md` |
| 2 | Nguyễn Hoàng Anh | 2A202602811 | Phụ trách Phase A: review `phase_a_ragas.py` và m4, đối chiếu bottom 10 với answer/contexts, kiểm tra lại `failure_clusters.md`; trưởng nhóm, audit PR và nộp link | Bằng chứng audit trong `doc/reports/failure_clusters.md`; log `scripts/check_lab.py --with-tests` (86 passed) |
| 3 | Nguyễn Viết Đức | 2A202602732 | Phụ trách Phase B: review `phase_b_judge.py`, đọc 5 cặp A/B và 10 nhãn nhị phân, kiểm tra lại `bias_report.md` | Chưa có commit; cập nhật sau khi review |
| 4 | Lục Tiến Đạt | 2A202602969 | Phụ trách Phase C: review `phase_c_guard.py` và `guardrails/config.yml`, đối chiếu lượt chạy guard trước/sau khi sửa prompt và latency, kiểm tra lại `blueprint.md` | Chưa có commit; cập nhật sau khi review |

Người tích hợp/chạy batch/nộp link: Mai Văn Trường tích hợp pipeline, chạy setup và ba batch live,
push nhánh `integration` (commit `2de53da` code + artifacts, `0af6999` báo cáo); Nguyễn Hoàng Anh
duyệt PR vào `main` và nộp link.

## Môi trường và chuẩn bị trước lớp

OS/Python/compiler: Windows 11 Home Single Language 10.0.26200; Python 3.11.9 (`py -3.11`); Annoy
1.17.3 build thành công trong lúc cài nên compiler C++ có sẵn trên máy.
Virtualenv/dependencies/imports: `py -3.11 -m venv .venv`, `pip install -r requirements/requirements.txt -c requirements/constraints-core.txt`
thành công. Lỗi gặp phải: pip cài pyarrow 26 cần NumPy 2, trong khi constraints pin NumPy 1.26.4, nên
`import ragas` báo ImportError; xử lý bằng `pyarrow>=15,<20` (đã ghi vào requirements). Sau đó
`pip check` báo "No broken requirements found" và import được ragas 0.1.22, nemoguardrails 0.10.0,
presidio_analyzer, spacy.
Models/Qdrant/50 answers đã chuẩn bị: `en_core_web_lg`, `BAAI/bge-m3`, `BAAI/bge-reranker-v2-m3` đã
tải; Qdrant `qdrant/qdrant:v1.9.7` chạy qua Docker Compose (`localhost:6333`). `setup_answers.py --live`
index 107 chunks (2 PDF scan không có text layer bị bỏ qua) và lưu 50 answers; lượt đầu có 14 câu
(id 20–33) rơi vào extractive fallback do mất kết nối OpenAI, đã sinh lại bằng
`scripts/regenerate_fallbacks.py` giữ nguyên contexts, nên bản nộp có 50/50 câu `llm`. NeMo chạy
thật trong Phase C live (input rail, output rail và đo latency).

## INDIVIDUAL

### MaiVanTruong-2A202602983

- Phần được giao và phần thực tế đã làm: tích hợp pipeline và chạy thực nghiệm. Port m1/m2/m3/m5 và
  `pipeline.py` từ bài Day 18; viết lại `m4_eval.evaluate_ragas` để dùng evaluator rõ ràng
  (gpt-4o-mini + text-embedding-3-small), trả `metadata.evaluator_models` và báo lỗi thay vì chấm
  điểm heuristic; viết Task 1–12; viết `scripts/regenerate_fallbacks.py`; sửa prompt
  `self_check_input`; chạy setup và Phase A/B/C live; soạn ba báo cáo.
- Bằng chứng: commit `2de53da` và `0af6999` trên nhánh `integration`; `artifacts/answers_50q.json`,
  `ragas_50q.json`, `judge_results.json`, `guard_results.json`; `doc/reports/`.
- Cách kiểm tra: `python -m pytest tests/ -q` → 86 passed; `run_experiments.py --phase a/b/c --live`
  chạy thành công; `python scripts/check_lab.py --with-tests` pass toàn bộ phần code, artifacts và
  báo cáo.
- Điều đã học: các metric RAGAS đo những thứ khác nhau và phải đọc answer/contexts trước khi kết
  luận — bottom 10 bị chẩn đoán "hallucination" nhưng thực tế là LLM từ chối quá mức và metric
  faithfulness chấm thấp kết quả tính toán đúng. Guard cần clean controls: lượt 1 chặn 18/20 attacks
  nhưng chặn nhầm một câu hỏi chính sách mật khẩu.
- Giới hạn/cách xử lý: sự cố mạng làm 14 answers rơi vào fallback, đã sinh lại và ghi rõ trong báo
  cáo; prompt guard được chỉnh trên chính bộ test nên 20/20 có rủi ro overfit, đã ghi trong blueprint;
  input guard P95 843 ms vượt target 500 ms, ghi đúng số đo.
- Nguồn/AI hỗ trợ nếu có: mã m1–m5 từ bài Day 18 cá nhân; dùng Claude Code để viết code các Task,
  sửa m4, cài môi trường, chạy batch và soạn báo cáo. Tự kiểm chứng bằng unit tests, checker và đối
  chiếu số liệu báo cáo với JSON.

### NguyenHoangAnh-2A202602811

- Phần được giao và phần thực tế đã làm: phụ trách Phase A và là trưởng nhóm. Thao tác thực tế đã thực hiện:
  (1) Đọc kiểm tra mã nguồn `src/phase_a_ragas.py` (logic phân nhóm 3 distributions, công thức avg_score và
  tính ma trận cluster analysis) và `src/m4_eval.py` (khởi tạo evaluator, khai báo `metadata.evaluator_models`,
  cơ chế retry khi gặp NaN); (2) Viết và chạy script Python nội bộ để đọc chi tiết 10 câu hỏi có avg_score
  thấp nhất trong `artifacts/ragas_50q.json`, trực tiếp đối chiếu câu hỏi, câu trả lời và contexts của từng
  câu với `artifacts/answers_50q.json`; (3) Đọc đối chiếu số liệu trong báo cáo `doc/reports/failure_clusters.md`
  với JSON nguồn; (4) Chạy công cụ kiểm tra tự động `scripts/check_lab.py --with-tests` trong môi trường ảo
  `.venv`; (5) Với vai trò trưởng nhóm: kiểm tra git diff và commit log của nhánh `integration`, phát hiện
  commit `980b122` có thay đổi xóa 72 starter files để cảnh báo và ngăn chặn việc merge làm mất dữ liệu trên `main`.
- Bằng chứng:
  - Bảng quan sát thực tế từ 10 câu bottom: 4 câu có câu trả lời là "Không tìm thấy." (id 39, 44, 33, 50);
    4 câu có câu trả lời số học khớp với reference nhưng nhận điểm faithfulness 0.00 hoặc 0.33 (id 24, 38,
    31, 5); 1 câu chỉ trả lời một phần do context thiếu bảng lương (id 21); 1 câu trả lời ngắn gọn (id 7).
  - Kết quả chạy kiểm thử tự động offline bằng `scripts/check_lab.py --with-tests`: công cụ báo cáo 86 passed,
    0 failed checks.
  - Phân định rõ vai trò người soạn thảo ban đầu và người review trong `doc/reports/failure_clusters.md`.
  - Lịch sử git hiển thị commit `980b122` trên nhánh `integration` xóa 72 files so với `main`.
- Cách kiểm tra: thực thi `.\.venv\Scripts\python.exe scripts/check_lab.py --with-tests` để kiểm tra toàn bộ
  schemas và unit tests offline; dùng script Python đọc trực tiếp `artifacts/ragas_50q.json` để kiểm chứng
  độc lập các số liệu.
- Điều đã học:
  - Phân biệt giữa quan sát thực tế và nhãn tự động: Trong 10 câu bottom, nhãn tự động từ cây quyết định là
    "LLM hallucinating", nhưng đọc thực tế câu trả lời cho thấy không có hiện tượng bịa đặt thông tin; 4 câu
    là từ chối trả lời ("Không tìm thấy.") và 4 câu là kết quả tính toán đúng với reference.
  - Phân biệt quan sát và giả thuyết nguyên nhân: Quan sát thấy câu tính toán bị điểm faithfulness thấp vì
    kết quả phép tính (như 50.000 VNĐ, 600 USD) không xuất hiện nguyên văn trong context. Với các câu từ chối,
    giả thuyết đặt ra là câu lệnh prompt yêu cầu nghiêm ngặt ("Nếu không có → nói 'Không tìm thấy.'") có thể
    khiến mô hình chọn phương án từ chối an toàn khi thông tin bị phân tán; đây là giả thuyết giải thích dựa
    trên quan sát, cần thêm thực nghiệm kiểm chứng trước khi kết luận quan hệ nhân quả.
  - Về vai trò quản lý mã nguồn: Cần kiểm tra kỹ git log và diff giữa các nhánh trước khi tích hợp để tránh
    rủi ro nhánh cá nhân xóa nhầm file dùng chung của dự án.
- Giới hạn/cách xử lý: Nhận định dựa trên 1 lượt chạy dữ liệu có sẵn trong artifacts do Mai Văn Trường thực
  hiện trước đó; các giả thuyết về prompt và metric chưa được kiểm chứng bằng thực nghiệm can thiệp có đối
  chứng (ablation study) vì tuân thủ quy tắc không gọi API live tốn phí trong giai đoạn review.
- Nguồn/AI hỗ trợ nếu có: Sử dụng Antigravity Coding Assistant (Gemini 3.6 Flash) để hỗ trợ viết script
  kiểm tra số liệu JSON offline và soát lỗi cú pháp; toàn bộ thao tác đối chiếu dữ liệu và đánh giá đều được
  thực hiện trực tiếp trên file nguồn.

### NguyenVietDuc-2A202602732

- Phần được giao và phần thực tế đã làm: phụ trách Phase B. Việc cần làm: review
  `src/phase_b_judge.py`, đọc 5 cặp A/B và 10 binary judgments trong `artifacts/judge_results.json`,
  kiểm tra lại `doc/reports/bias_report.md`. Mục này là bản nháp do Mai Văn Trường soạn theo phân
  công; Nguyễn Viết Đức cần xác nhận và sửa lại theo việc đã thực sự làm.
- Bằng chứng: chưa có commit; bổ sung PR/commit review sau khi hoàn thành.
- Cách kiểm tra: tính lại κ từ `calibration` trong `judge_results.json`; chạy `python -m pytest tests/test_phase_b.py`.
- Điều đã học: bản nháp, cần tự viết lại sau khi review Phase B.
- Giới hạn/cách xử lý: bản nháp, cần tự viết lại.
- Nguồn/AI hỗ trợ nếu có: bản nháp, cần tự khai.

### LucTienDat-2A202602969

- Phần được giao và phần thực tế đã làm: phụ trách Phase C. Việc cần làm: review
  `src/phase_c_guard.py` và `guardrails/config.yml`, đọc kết quả attacks/clean/output và latency trong
  `artifacts/guard_results.json`, kiểm tra lại `doc/reports/blueprint.md`. Mục này là bản nháp do Mai
  Văn Trường soạn theo phân công; Lục Tiến Đạt cần xác nhận và sửa lại theo việc đã thực sự làm.
- Bằng chứng: chưa có commit; bổ sung PR/commit review sau khi hoàn thành.
- Cách kiểm tra: đối chiếu percentile latency với raw samples; chạy `python -m pytest tests/test_phase_c.py`.
- Điều đã học: bản nháp, cần tự viết lại sau khi review Phase C.
- Giới hạn/cách xử lý: bản nháp, cần tự viết lại.
- Nguồn/AI hỗ trợ nếu có: bản nháp, cần tự khai.

## Cập nhật sau khi nộp

Chưa nộp. Khi nộp, ghi SHA commit trên `main` ở đầu file. Nếu sửa sau deadline, ghi commit, thời điểm,
lý do và thông báo coach cho phép áp dụng bản cập nhật.
