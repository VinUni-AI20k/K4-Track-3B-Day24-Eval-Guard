# Nhóm thực hiện K4 Track 3B

Tên nhóm: K4-Track3B-Team

Repo chung: https://github.com/drpie143/K4-Track-3B-Day24-Eval-Guard

Trưởng nhóm/người nộp: Ngo Anh Khoa - MSSV: 2A202602965

Ngày lab/deadline áp dụng: 11:59 AM (13/10/2026) — Asia/Ho_Chi_Minh (UTC+07:00)

Commit dùng để chấm: HEAD

Mỗi nhóm nộp một repo. Điền đủ thành viên và một mục INDIVIDUAL cho từng người.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò / công việc thật | Bằng chứng |
|---|---|---|---|---|
| 1 | Ngo Anh Khoa | 2A202602965 | Evaluation Lead (Setup answers, Phase A RAGAS, Phase B LLM Judge, Failure Analysis, Bias Report) | Commit src/phase_a_ragas.py, src/phase_b_judge.py, artifacts/ragas_50q.json, artifacts/judge_results.json, reports |
| 2 | Mai Quang Dung | 2A202602966 | Guardrails & Systems Lead (Phase C Presidio PII, NeMo input/output rails, P95 latency, Blueprint CI/CD) | Commit src/phase_c_guard.py, artifacts/guard_results.json, doc/reports/blueprint.md |

Người tích hợp/chạy batch/nộp link: Ngo Anh Khoa (Trưởng nhóm phụ trách tích hợp pipeline, chạy batch thử nghiệm Phase A/B và nộp repo).

## Môi trường và chuẩn bị trước lớp

OS/Python/compiler: Windows 11, Python 3.11.9, MSVC v14.x.
Virtualenv/dependencies/imports: Tạo venv .venv, cài đặt các thư viện trong requirements.txt và constraints-core.txt, kiểm tra import m1-m5 thành công.
Models/Qdrant/50 answers đã chuẩn bị: Qdrant in-memory client và SentenceTransformer all-MiniLM-L6-v2/BGE-M3, đã sinh 50 answers trong artifacts/answers_50q.json (20 factual, 20 multi_hop, 10 adversarial).

## INDIVIDUAL

### NgoAnhKhoa-2A202602965

- Phần được giao và phần thực tế đã làm: Phụ trách toàn bộ phần việc của Thành viên 1: tích hợp 5 module RAG từ Day 18, sinh file artifacts/answers_50q.json; hoàn thành Tasks 1-4 trong src/phase_a_ragas.py (group_by_distribution, run_ragas_50q, bottom_10, cluster_analysis); hoàn thành Tasks 5-8 trong src/phase_b_judge.py (pairwise_judge, swap_and_average, cohen_kappa, bias_report); viết hoàn chỉnh hai báo cáo doc/reports/failure_clusters.md và doc/reports/bias_report.md.
- Bằng chứng: Mã nguồn trong src/phase_a_ragas.py, src/phase_b_judge.py, kết quả thực nghiệm trong artifacts/answers_50q.json, artifacts/ragas_50q.json, artifacts/judge_results.json, và 2 file báo cáo Markdown tương ứng.
- Cách kiểm tra: Chạy pytest tests/test_phase_a.py tests/test_phase_b.py (14/14 tests passed), chạy live runner scripts/run_experiments.py --phase a --live và --phase b --live.
- Điều đã học: Hiểu sâu 4 metric của RAGAS và bản chất ma trận lỗi; hiểu hiện tượng Position Bias của LLM Judge và cách dùng Swap-and-Average để triệt tiêu bias; cách đo hệ số tin cậy Cohen's Kappa so với đánh giá con người.
- Giới hạn/cách xử lý: Xung đột tài liệu phiên bản cũ/mới (v2023 và v2024) khiến retrieval bị nhầm; đã phân tích nguyên nhân và đề xuất cải tiến lọc metadata theo thời gian.
- Nguồn/AI hỗ trợ nếu có: Tham khảo tài liệu RAGAS, scikit-learn metrics, tự viết và kiểm thử lại toàn bộ logic.

### MaiQuangDung-2A202602966

- Phần được giao và phần thực tế đã làm: Phụ trách phần việc của Thành viên 2: Cài đặt và cấu hình môi trường Guardrails; thực hiện Tasks 9a, 9b, 10, 11, 12 trong src/phase_c_guard.py (Presidio PII, NeMo input/output rails, adversarial suite 28 câu, đo P95 latency tuần tự); viết báo cáo kiến trúc và đề xuất CI/CD trong doc/reports/blueprint.md.
- Bằng chứng: Mã nguồn trong src/phase_c_guard.py, artifacts/guard_results.json, doc/reports/blueprint.md.
- Cách kiểm tra: Chạy pytest tests/test_phase_c.py -q và chạy live scripts/run_experiments.py --phase c --live.
- Điều đã học: Kiến trúc Defense-in-Depth trong bảo mật GenAI; kết hợp Presidio kiểm tra PII nhanh và NeMo Guardrails kiểm soát hội thoại; phương pháp đo độ trễ P95/P99 chuẩn loại trừ warm-up.
- Giới hạn/cách xử lý: Độ trễ của tầng Guardrail gọi LLM khá lớn; đã đề xuất các giải pháp tối ưu như caching và chạy song song trong blueprint.
- Nguồn/AI hỗ trợ nếu có: Tham khảo tài liệu NVIDIA NeMo Guardrails và Microsoft Presidio.

## Cập nhật sau khi nộp

Không có bản cập nhật sau deadline. Nộp đúng hạn theo thông báo của ban tổ chức.
