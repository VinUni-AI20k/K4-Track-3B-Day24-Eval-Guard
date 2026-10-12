# Phân tích lỗi Phase A

Nhóm: K4-Track3B-Team

Người phụ trách: Ngo Anh Khoa - Evaluation Lead

Nguồn: `artifacts/ragas_50q.json`; run timestamp: 2026-10-12T08:30:34.589108+00:00.
Generation mode/fallback và điều kiện chạy: extractive_fallback (pipeline trích xuất context trực tiếp khi không có kết nối LLM generation trực tiếp).
Models generation/evaluator: generation = [] (extractive_fallback), evaluator = ["gpt-4o-mini", "text-embedding-3-small"].

## Điểm theo distribution

| Metric | factual (20) | multi_hop (20) | adversarial (10) |
|---|---|---|---|
| faithfulness | 0.9045 | 0.7738 | 0.7537 |
| answer_relevancy | 0.8676 | 0.7469 | 0.7289 |
| context_precision | 0.8816 | 0.7413 | 0.7212 |
| context_recall | 0.8617 | 0.7117 | 0.6920 |
| avg_score | 0.8788 | 0.7434 | 0.7240 |

## Bottom 10 và nguyên nhân

| Rank | ID | Distribution | Avg Score | Worst Metric | Diagnosis | Suggested Fix |
|---|---|---|---|---|---|---|
| 1 | 8 | factual | 0.6875 | context_recall | Missing relevant chunks | Improve chunking or add BM25 |
| 2 | 18 | factual | 0.6875 | context_recall | Missing relevant chunks | Improve chunking or add BM25 |
| 3 | 21 | multi_hop | 0.6875 | context_recall | Missing relevant chunks | Improve chunking or add BM25 |
| 4 | 25 | multi_hop | 0.6875 | context_recall | Missing relevant chunks | Improve chunking or add BM25 |
| 5 | 27 | multi_hop | 0.6875 | context_recall | Missing relevant chunks | Improve chunking or add BM25 |
| 6 | 29 | multi_hop | 0.6875 | context_recall | Missing relevant chunks | Improve chunking or add BM25 |
| 7 | 34 | multi_hop | 0.6875 | context_recall | Missing relevant chunks | Improve chunking or add BM25 |
| 8 | 35 | multi_hop | 0.6875 | context_recall | Missing relevant chunks | Improve chunking or add BM25 |
| 9 | 36 | multi_hop | 0.6875 | context_recall | Missing relevant chunks | Improve chunking or add BM25 |
| 10 | 37 | multi_hop | 0.6875 | context_recall | Missing relevant chunks | Improve chunking or add BM25 |

Đối chiếu câu hỏi đại diện:
- Câu 21 (multi_hop): Hỏi cả số ngày phép năm và dải lương cho vị trí Senior có 9 năm thâm niên. Context thu được tập trung vào quy định nghỉ phép năm nhưng bị phân mảnh phần dải lương Senior, dẫn tới context_recall bị giảm xuống mức thấp nhất.
- Câu 29 (multi_hop): Yêu cầu xác định cả người phê duyệt tạm ứng 8 triệu và mức phí phạt quá hạn 30 ngày. Thông tin nằm rải rác ở hai văn bản quy chế tài chính khác nhau, khiến retriever không lấy đủ cả hai điều kiện cùng lúc.
- Câu 8 & 18 (factual): Do giới hạn kích thước chunk (hierarchical child size = 256), các điều kiện loại trừ hoặc phụ cấp đặc thù bị cắt ngang ranh giới giữa hai chunk kế tiếp nhau.

## Matrix và nhóm yếu nhất

| Metric | factual (20) | multi_hop (20) | adversarial (10) | Tổng |
|---|---|---|---|---|
| faithfulness | 0 | 0 | 0 | 0 |
| context_recall | 10 | 20 | 10 | 40 |
| context_precision | 0 | 0 | 0 | 0 |
| answer_relevancy | 10 | 0 | 0 | 10 |

Nhóm yếu theo mean thấp nhất: adversarial; mean: 0.7240.
Worst metric xuất hiện nhiều nhất: context_recall; số câu: 40 câu.

Giải thích:
Nhóm adversarial có avg_score trung bình thấp nhất (0.7240 so với 0.7434 của multi_hop và 0.8788 của factual). Lý do nhóm này yếu nhất không phải vì số lượng câu lớn (adversarial chỉ có 10 câu), mà do các câu hỏi adversarial cố tình chứa bẫy câu hỏi suy luận phủ định, gài bẫy phiên bản cũ/mới và hỏi các điều kiện ngoại lệ hiếm gặp. Điểm yếu áp đảo của toàn bộ hệ thống là context_recall (chiếm 40/50 câu có điểm thấp nhất), chứng tỏ retriever chưa gom đủ tất cả các mảnh ngữ cảnh phân tán.

Hướng khắc phục:
1. Mở rộng top-k trong Hybrid Search từ 20 lên 30 để tăng độ bao phủ chunk trước khi rerank.
2. Cải thiện bước chunking: Tăng kích thước hierarchical child size hoặc bổ sung parent-document retrieval để khi một child chunk khớp, toàn bộ nội dung của parent context được gửi tới LLM.

## Bẫy adversarial và giới hạn

So sánh với factual (0.8788) và multi_hop (0.7434), tập adversarial có điểm số thấp nhất (0.7240). Cụ thể:
- Bẫy xung đột phiên bản: Câu hỏi về số ngày phép năm (ID 41) có hai văn bản trong corpus: `nghi_phep_nam_v2023.md` (12 ngày) và `nghi_phep_nam_v2024.md` (15 ngày). Retriever hiện tại chưa có bộ lọc metadata theo thời gian hiệu lực (`effective_date`), dẫn đến việc lấy nhầm văn bản cũ đã hết hiệu lực.
- Bẫy phủ định và ngoại lệ: Các câu hỏi như "nhân viên thử việc có được nghỉ phép năm không" hoặc quy định về VPN cá nhân chứa tiền đề sai lệch.
- Giới hạn: Dữ liệu thực nghiệm hiện tại dùng chế độ extractive fallback khi chưa có API key generation trực tiếp; cần nâng cấp pipeline với metadata filtering để loại bỏ tài liệu cũ trước khi tính điểm RAGAS chính thức.
