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
| 2 | Nguyễn Hoàng Anh | 2A202602811 | Phụ trách Phase A: review `phase_a_ragas.py` và m4, đối chiếu bottom 10 với answer/contexts, kiểm tra lại `failure_clusters.md`; trưởng nhóm, duyệt PR và nộp link | Chưa có commit; cập nhật sau khi review và duyệt PR |
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

- Phần được giao và phần thực tế đã làm: phụ trách Phase A và là trưởng nhóm. Việc cần làm: review
  `src/phase_a_ragas.py` và `src/m4_eval.py`, đối chiếu bottom 10 trong `artifacts/ragas_50q.json`
  với answer/contexts, kiểm tra lại `doc/reports/failure_clusters.md`, duyệt PR `integration` vào
  `main` và nộp link. Mục này là bản nháp do Mai Văn Trường soạn theo phân công; Nguyễn Hoàng Anh cần
  xác nhận và sửa lại theo việc đã thực sự làm.
- Bằng chứng: chưa có commit; bổ sung PR/commit review sau khi hoàn thành.
- Cách kiểm tra: đối chiếu số liệu báo cáo Phase A với `ragas_50q.json`; chạy `python scripts/check_lab.py`.
- Điều đã học: bản nháp, cần tự viết lại sau khi review Phase A.
- Giới hạn/cách xử lý: bản nháp, cần tự viết lại.
- Nguồn/AI hỗ trợ nếu có: bản nháp, cần tự khai.

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
