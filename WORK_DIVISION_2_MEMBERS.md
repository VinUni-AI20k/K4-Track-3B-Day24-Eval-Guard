# KẾ HOẠCH PHÂN CHIA CÔNG VIỆC NHÓM 2 NGƯỜI (K4 TRACK 3B)
> **Dự án:** Production Eval + Guardrail Stack  
> **Tổng điểm:** 100 điểm bắt buộc + tối đa 10 điểm bonus  
> **Hình thức nộp:** 1 repository chung của nhóm, mỗi người có cam kết commit và khai báo đóng góp thực tế trong `doc/TEAM.md`.

---

## I. TỔNG QUAN PHÂN CHIA VAI TRÒ

| Tiêu chí | Thành viên 1: Trưởng nhóm / Evaluation Lead | Thành viên 2: Guardrails & Systems Lead |
|---|---|---|
| **Trọng tâm** | Đánh giá chất lượng RAG & Đánh giá trọng tài LLM Judge | Bảo mật đầu vào/ra (Guardrails), Đo độ trễ & Thiết kế CI/CD |
| **Phần phụ trách** | **Setup Answers + Phase A + Phase B** | **Infra/Môi trường + Phase C + Task 13 (Blueprint)** |
| **Code files** | `src/phase_a_ragas.py`<br>`src/phase_b_judge.py` | `src/phase_c_guard.py`<br>`infra/`, cấu hình `guardrails/` |
| **Artifacts phụ trách** | `artifacts/answers_50q.json`<br>`artifacts/ragas_50q.json`<br>`artifacts/judge_results.json` | `artifacts/guard_results.json`<br>Kết quả đo P95 Latency |
| **Reports phụ trách** | `doc/reports/failure_clusters.md`<br>`doc/reports/bias_report.md` | `doc/reports/blueprint.md`<br>Đồng kiểm tra `doc/TEAM.md` |
| **Tỷ trọng điểm** | **65 điểm** (Phase A: 30đ, Phase B: 35đ) + tối đa 7đ bonus | **35 điểm** (Phase C: 35đ) + Blueprint + CI/CD + tối đa 3đ bonus |

---

## II. BẢNG PHÂN CÔNG CHI TIẾT THEO TỪNG GIAI ĐOẠN

### Giai đoạn 0: Chuẩn bị trước buổi học (Checkpoint 0)

#### Thành viên 1 (Evaluation Lead):
- [ ] Lấy 5 module RAG từ Day 18 (`m1_chunking.py`, `m2_search.py`, `m3_rerank.py`, `m4_eval.py`, `m5_enrichment.py`) đưa vào thư mục `src/`.
- [ ] Đảm bảo module `m4_eval.py` trả về `metadata.evaluator_models` đúng danh sách model thực tế.
- [ ] Tạo file `.env` với `OPENAI_API_KEY`.
- [ ] Chạy lệnh sinh trước 50 câu trả lời của pipeline:
  ```bash
  python scripts/setup_answers.py --live
  ```
- [ ] Kiểm tra file `artifacts/answers_50q.json` đã có đủ 50 câu (20 factual, 20 multi_hop, 10 adversarial).

#### Thành viên 2 (Guardrails & Systems Lead):
- [ ] Thiết lập môi trường Python 3.11 theo `doc/ENVIRONMENT.md`.
- [ ] Cài đặt Microsoft C++ Build Tools (cần thiết để build thư viện `annoy` cho NeMo Guardrails trên Windows).
- [ ] Khởi động Qdrant vector database:
  ```bash
  docker compose -f infra/docker-compose.yml up -d
  ```
- [ ] Tải mô hình spaCy:
  ```bash
  python -m spacy download en_core_web_lg
  ```
- [ ] Cài đặt các gói trong `requirements/requirements.txt` và chạy `pip check`.

---

### Giai đoạn 1: Thực hiện Phase A — RAGAS Evaluation (30 phút trên lớp)

#### Người thực hiện chính: **Thành viên 1** (Thành viên 2 hỗ trợ review code/test)
- [ ] **Task 1 (`src/phase_a_ragas.py`):** Viết hàm `group_by_distribution(test_set)` gom 50 câu thành 3 nhóm đúng số lượng (20 factual, 20 multi_hop, 10 adversarial).
- [ ] **Task 2 (`src/phase_a_ragas.py`):** Viết hàm `run_ragas_50q(answers)` gọi `m4_eval.evaluate_ragas`, lấy 4 chỉ số (faithfulness, answer_relevancy, context_precision, context_recall), đóng gói vào `RagasEvaluation`.
- [ ] **Task 3 (`src/phase_a_ragas.py`):** Viết hàm `bottom_10(results)` sắp xếp tăng dần theo `avg_score`, gán `diagnosis` và `suggested_fix` từ `DIAGNOSTIC_TREE`.
- [ ] **Task 4 (`src/phase_a_ragas.py`):** Viết hàm `cluster_analysis(results)` xây dựng ma trận `worst_metric x distribution`, chọn dominant distribution dựa vào **điểm trung bình thấp nhất** (không chọn theo kích thước nhóm).
- [ ] **Kiểm thử offline:**
  ```bash
  python -m pytest tests/test_phase_a.py -q
  ```
- [ ] **Chạy live và xuất artifact:**
  ```bash
  python scripts/run_experiments.py --phase a --live
  ```
  *(Sinh ra `artifacts/ragas_50q.json`)*.
- [ ] **Viết báo cáo:** Mở `doc/reports/failure_clusters.md`, điền các bảng điểm, 10 câu bottom, phân tích nguyên nhân retrieval/generation và bẫy adversarial (xóa hết placeholder).

---

### Giai đoạn 2: Thực hiện Phase B — LLM-as-a-Judge (30 phút trên lớp)

#### Người thực hiện chính: **Thành viên 1** (Thành viên 2 cùng phân tích kết quả Cohen Kappa)
- [ ] **Task 5 (`src/phase_b_judge.py`):** Viết hàm `pairwise_judge(question, answer_a, answer_b, reference)` gọi GPT-4o-mini trả về JSON gồm winner (A/B/tie), reasoning, scores.
- [ ] **Task 6 (`src/phase_b_judge.py`):** Viết hàm `swap_and_average(...)` chạy 2 lượt tráo đổi vị trí A/B và B/A, map lại kết quả. Chỉ xác định winner khi 2 lượt đồng thuận, nếu ngược chiều thì trả về `tie`.
- [ ] **Task 7 (`src/phase_b_judge.py`):** Viết hàm `cohen_kappa(judge_labels, human_labels)` tính hệ số $\kappa$ giữa 10 nhãn binary của Judge và 10 nhãn của con người.
- [ ] **Task 8 (`src/phase_b_judge.py`):** Viết hàm `bias_report(judge_results)` đo position bias rate và verbosity bias rate.
- [ ] **Kiểm thử offline:**
  ```bash
  python -m pytest tests/test_phase_b.py -q
  ```
- [ ] **Chạy live và xuất artifact:**
  ```bash
  python scripts/run_experiments.py --phase b --live
  ```
  *(Sinh ra `artifacts/judge_results.json`)*.
- [ ] **Viết báo cáo:** Mở `doc/reports/bias_report.md`, điền 5 cặp A/B, bảng 10 nhãn đối chiếu human label, diễn giải $\kappa$ và hiện tượng bias.

---

### Giai đoạn 3: Thực hiện Phase C — Guardrails Stack & Latency (30 phút trên lớp)

#### Người thực hiện chính: **Thành viên 2** (Thành viên 1 hỗ trợ review test logic)
- [ ] **Task 9a (`src/phase_c_guard.py`):** Viết hàm `pii_scan(text, analyzer, anonymizer)` sử dụng Presidio nhận diện & ẩn danh CCCD/CMND, SĐT Việt Nam, Email.
- [ ] **Task 9b (`src/phase_c_guard.py`):** Viết hàm `check_input_rail(text, rails)` (async) gọi NeMo input rail, nhận diện chặn dựa vào `result.log.activated_rails` (không bắt từ khóa text).
- [ ] **Task 10 (`src/phase_c_guard.py`):** Viết hàm `run_adversarial_suite(adversarial_set, ...)` chạy tuần tự Lớp 1 (Presidio) $\rightarrow$ Lớp 2 (NeMo input rail) cho toàn bộ 28 inputs (20 attacks + 8 clean controls). Đảm bảo chặn $\ge 15/20$ attacks (mục tiêu bonus $\ge 18/20$) và cho qua $8/8$ clean controls.
- [ ] **Task 11 (`src/phase_c_guard.py`):** Viết hàm `check_output_rail(question, answer, rails)` (async) kiểm tra output an toàn, giữ nguyên câu sạch và thay thế câu vi phạm.
- [ ] **Task 12 (`src/phase_c_guard.py`):** Viết hàm `measure_p95_latency(test_inputs, n_runs=20, ...)` thực hiện 2 warm-up thật (loại bỏ), đo tuần tự cả Presidio và NeMo input trên ít nhất 20 lần chạy, gọi `summarize_latency()` để tính P50/P95/P99.
- [ ] **Kiểm thử offline:**
  ```bash
  python -m pytest tests/test_phase_c.py -q
  ```
- [ ] **Chạy live và xuất artifact:**
  ```bash
  python scripts/run_experiments.py --phase c --live --latency-samples 20
  ```
  *(Sinh ra `artifacts/guard_results.json`)*.

---

### Giai đoạn 4: Blueprint, Kiểm tra chất lượng & Đóng gói nộp bài

#### Cả 2 thành viên cùng phối hợp:
- [ ] **Task 13 — Viết Blueprint (`doc/reports/blueprint.md`):**
  - **Thành viên 2 chủ trì:** Điền kiến trúc tuần tự, số đo Latency P50/P95/P99 thực tế (các mục RAG/Output ghi "chưa đo"), đề xuất CI gates (ngưỡng RAGAS $\ge 0.75$, attacks $\ge 18/20$, P95 $< 500$ms) và cơ chế monitoring.
  - **Thành viên 1 phối hợp:** Cung cấp số liệu RAGAS và Cohen $\kappa$ để đưa vào bảng metrics tổng thể.
- [ ] **Hoàn thiện `doc/TEAM.md`:**
  - Điền tên nhóm, repo link, commit hash dùng để chấm.
  - Mỗi thành viên tự viết mục `### HoVaTen-MSSV` của mình (phần công việc đã làm, bằng chứng commit, lệnh kiểm tra, điều đã học).
- [ ] **Kiểm tra chuẩn xác không còn sót lỗi:**
  - Đảm bảo trong `src/` đã xóa sạch chữ `# TODO` ở cả 3 module (`phase_a_ragas.py`, `phase_b_judge.py`, `phase_c_guard.py`).
  - Đảm bảo không còn bất kỳ placeholder nào (`{{...}}`, `[...]`, `?`, `HoVaTen-MSSV`) trong 4 file markdown.
- [ ] **Chạy checker tự động:**
  ```bash
  python scripts/check_lab.py --with-tests
  ```
  *(Kết quả phải đạt `0 failed checks`)*.
- [ ] **Commit, Push & Nộp link:** Trưởng nhóm push toàn bộ source code + artifacts + reports lên GitHub và nộp link repository theo hướng dẫn của lớp.

---

## III. MẪU KHAI BÁO `doc/TEAM.md` CHO TỪNG THÀNH VIÊN

Khi hoàn thành bài lab, 2 bạn chỉ cần copy mẫu dưới đây vào `doc/TEAM.md` và thay thông tin thật của mình:

```markdown
### NguyenVanA-21010001 (Thành viên 1 - Evaluation Lead)
- Phần được giao và phần thực tế đã làm: Phụ trách pipeline RAG Day 18, sinh answers_50q.json, thực hiện Tasks 1-4 (Phase A - RAGAS 4 metrics, Bottom 10, Cluster Analysis), Tasks 5-8 (Phase B - Pairwise Judge, Swap-and-average, Cohen's Kappa, Bias Analysis), viết failure_clusters.md và bias_report.md.
- Bằng chứng: Các commit cho src/phase_a_ragas.py, src/phase_b_judge.py, artifacts/answers_50q.json, artifacts/ragas_50q.json, artifacts/judge_results.json, doc/reports/failure_clusters.md, doc/reports/bias_report.md.
- Cách kiểm tra: python -m pytest tests/test_phase_a.py tests/test_phase_b.py -q; python scripts/run_experiments.py --phase a --live; python scripts/run_experiments.py --phase b --live.
- Điều đã học: Hiểu rõ 4 góc nhìn của RAGAS, nguyên lý Position Bias và cơ chế Swap-and-average để khử bias, cách đo độ đồng thuận Cohen's Kappa giữa LLM và chuyên gia con người.
- Giới hạn/cách xử lý: Tập adversarial có điểm thấp do xung đột phiên bản chính sách cũ/mới; đã phân tích nguyên nhân do retriever chưa lọc theo thời gian hiệu lực.
- Nguồn/AI hỗ trợ nếu có: Tham khảo tài liệu RAGAS và OpenAI API doc, tự kiểm chứng qua unit test và chạy live.

### TranThiB-21010002 (Thành viên 2 - Guardrails & Systems Lead)
- Phần được giao và phần thực tế đã làm: Chuẩn bị môi trường Python 3.11, C++ Build Tools, Docker Qdrant; thực hiện Tasks 9a, 9b, 10, 11, 12 (Phase C - Presidio PII scan, NeMo input/output rails, Adversarial test suite 28 câu, P95 latency benchmark); chủ trì viết Task 13 (doc/reports/blueprint.md) và chạy kiểm tra bài nộp bằng scripts/check_lab.py.
- Bằng chứng: Các commit cho src/phase_c_guard.py, artifacts/guard_results.json, doc/reports/blueprint.md, cấu hình guardrails/config.yml.
- Cách kiểm tra: python -m pytest tests/test_phase_c.py -q; python scripts/run_experiments.py --phase c --live --latency-samples 20; python scripts/check_lab.py --with-tests.
- Điều đã học: Cách phối hợp phòng thủ đa tầng (Defense in Depth: regex/Presidio nhanh ở ngoài, LLM Guardrail ở trong), cách phân biệt stop signal trong NeMo qua log activated_rails thay vì từ khóa, phương pháp benchmark P95 latency chuẩn loại trừ warm-up.
- Giới hạn/cách xử lý: Độ trễ của NeMo input rail tương đối cao do gọi LLM; đề xuất giải pháp caching và gom batch trong blueprint.
- Nguồn/AI hỗ trợ nếu có: Tham khảo tài liệu NVIDIA NeMo Guardrails và Microsoft Presidio, tự kiểm chứng toàn bộ qua test suite của đề bài.
```
