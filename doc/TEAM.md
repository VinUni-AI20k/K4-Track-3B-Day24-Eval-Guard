# Nhóm thực hiện K4 Track 3B

Tên nhóm: FAMI

Repo chung: {{Link repo}}

Trưởng nhóm/người nộp: {{Họ tên và MSSV}}

Ngày lab/deadline áp dụng: {{Ngày giờ theo thông báo lớp}} — Asia/Ho_Chi_Minh (UTC+07:00)

Commit dùng để chấm: {{Commit SHA}}

Mỗi nhóm nộp một repo. Điền đủ thành viên và một mục INDIVIDUAL cho từng người.
Thêm/xóa rows để khớp nhóm thật; mẫu ba rows không ép nhóm phải có ba người.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò / công việc thật | Bằng chứng |
|---|---|---|---|---|
| 1 | Nguyễn Văn Hưởng | 2A202602743 | Phụ trách Phase B: Tasks 5–8 với hỗ trợ Codex, tests offline, batch judge thật và báo cáo κ/bias | `src/phase_b_judge.py`, `tests/test_phase_b.py`, `artifacts/judge_results.json`, `doc/reports/bias_report.md` |
| 2 | {{Họ tên}} | {{MSSV}} | {{Phase/file/hàm}} | {{Commit/PR/report}} |
| 3 | {{Họ tên}} | {{MSSV}} | {{Phase/file/hàm}} | {{Commit/PR/report}} |

Người tích hợp/chạy batch/nộp link: {{Họ tên, công việc và bằng chứng}}.

## Môi trường và chuẩn bị trước lớp

OS/Python/compiler đã kiểm chứng trên máy chuẩn bị: macOS 26.5, Apple Silicon
arm64; Python 3.11.16; Apple clang 17.0.0; Annoy 1.17.3 build thành công.
Virtualenv/dependencies/imports: `.venv` cho full runtime theo requirements và
constraints; `.venv-tests` theo lockfile offline. `pip check` đạt trên cả hai.
RAGAS/NeMo/Presidio/spaCy/sentence-transformers và các dependency còn lại import
thành công. PyArrow pin 19.0.1 để tương thích NumPy 1.26.4.
Models/Qdrant: spaCy `en_core_web_lg` 3.8.0 nạp được; Presidio khởi tạo và phát
hiện email mẫu; BGE-M3 nạp từ cache và sinh embedding (1,1024); Qdrant v1.9.7
đã kiểm tra health/API và kết nối client. Cấu hình NeMo/Colang parse thành công,
chưa kiểm chứng LLM guard qua API. Đã tích hợp 50 answers từ `origin/main`
commit `96f6b2c`: schema/ids/nguồn và phân bố 20/20/10 đạt; không chạy lại
indexing hoặc generation trên máy này. Phase B đã chạy một batch thật bằng
gpt-4o-mini; 10 binary labels khớp human, κ=1.0, position inconsistency=0/5,
verbosity win rate=5/5. Bằng chứng: `artifacts/judge_results.json`.
Nếu cài full NeMo chưa thành công, ghi lỗi thực tế; không dùng unit test pass
hoặc pip resolve để khẳng định runtime đã chạy.

## INDIVIDUAL

Sao chép mẫu cho mỗi thành viên; tiêu đề họ tên không dấu-MSSV.

### NguyenVanHuong-2A202602743

- Phần được giao: Phase B — pairwise judge, hoán đổi thứ tự, Cohen’s κ và bias
  report. Phần hiện đã triển khai với hỗ trợ Codex: Tasks 5–8 trong
  `src/phase_b_judge.py`, kiểm tra JSON/scores, tests offline bổ sung, một batch
  judge thật và phân tích `doc/reports/bias_report.md`. Giới hạn output tokens
  của pairwise/binary judge để dùng API tiết kiệm; không chạy lại batch chỉ
  để kiểm chứng file kết quả.
- Bằng chứng: các file trên; helper binary trong `src/experiment_support.py`
  chỉ bổ sung giới hạn output và reasoning ngắn, không đổi nguồn calibration.
  Live evidence: `artifacts/judge_results.json`, created_at UTC
  `2026-10-12T12:30:37.395169+00:00`. Chưa xác nhận commit nộp bài.
- Cách kiểm tra: `.venv-tests/bin/python -m pytest tests/test_phase_b.py
  tests/test_support.py tests/test_report_contracts.py -q`; kết quả 84 passed
  (24 Phase B và 60 support/report contracts), dùng SDK mock, không gọi API.
  Batch live dùng runner `--phase b --live`; JSON và metadata được validate
  offline theo schema/sources/hash/κ/bias sau khi lưu, không gọi API lại.
- Điều đã học: Pairwise A/B/tie so sánh hai câu trả lời, còn nhãn 0/1 đánh giá
  một câu trả lời theo reference; không thể lấy winner A/B làm nhãn tốt/xấu.
  Khi hoán đổi candidates, phải đổi cả winner và scores lượt 2 về A/B gốc;
  nếu hai lượt không đồng thuận thì giữ tie. Calibration phải đánh giá đúng
  model_answer gốc và không đưa human_label/human_note vào prompt để tránh
  rò rỉ nhãn. Cohen’s κ điều chỉnh mức đồng thuận ngẫu nhiên: trong batch này,
  p_o=1, p_e=0.52 nên κ=1.0, nhưng 10 nhãn khớp không bảo đảm judge đúng trên
  mọi dữ liệu hoặc reasoning luôn chính xác. Id 46 là ví dụ label đúng nhưng
  reasoning thêm điều kiện không có trong answer. Position inconsistency=0/5
  và winner dài hơn=5/5 chỉ mô tả mẫu đã chạy; cần đối chiếu nội dung và các
  cặp kiểm soát để kết luận nguyên nhân bias. Tests mock kiểm tra logic và hợp
  đồng dữ liệu; kết quả live cùng schema/source/hash mới là bằng chứng thực
  nghiệm. Giữ nguyên số liệu và kiểm chứng offline giúp tránh gọi API lặp lại.
- Giới hạn/cách xử lý: mẫu chỉ có 5 cặp và 10 nhãn; κ=1.0 không chứng minh
  judge đúng trên mọi dữ liệu. Winner dài hơn 5/5 có thể do chất lượng/độ đủ
  thông tin; reasoning id 46 thêm nhận xét không được answer hỗ trợ dù label
  khớp human. Đã giữ nguyên kết quả và phân tích các giới hạn trong report.
- Nguồn/AI hỗ trợ: Codex đọc đề và scaffold của repo, hỗ trợ triển khai, viết
  tests, kiểm chứng offline, chạy một batch thật và soạn báo cáo từ kết quả.
  Người phụ trách cần tự
  đọc, kiểm tra và xác nhận hiểu phần đóng góp trước khi nộp; unit tests không
  thay thế kết quả live hoặc tự đánh giá cá nhân.

## Cập nhật sau khi nộp

{{Ghi phiên bản nộp; nếu sửa sau deadline, ghi commit/thời điểm/lý do và thông báo
coach cho phép áp dụng bản cập nhật. Nếu không có cập nhật, ghi rõ không có.}}
