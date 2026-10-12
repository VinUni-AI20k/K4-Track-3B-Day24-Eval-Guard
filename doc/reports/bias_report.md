# Đánh giá LLM Judge Phase B

Nhóm: FourPeoples

Người phụ trách: Mai Văn Trường – 2A202602983 (soạn báo cáo với hỗ trợ của Claude Code, số liệu đối chiếu trực tiếp từ JSON)

Nguồn: `artifacts/judge_results.json`; run timestamp: 2026-10-12T12:38:54+00:00.
Models generation/judge: generation `gpt-4o-mini-2024-07-18` (nguồn answer A); judge `gpt-4o-mini`
cho cả pairwise (`phase_b_judge.JUDGE_MODEL`) và binary helper, temperature 0, JSON mode.

## Năm cặp A/B và hai lượt

Nguồn cố định: A từ artifacts/answers_50q.json:answer; B từ
fixtures/human_labels_10q.json:model_answer; reference từ fixtures/test_set_50q.json:ground_truth.
Ids: 1, 5, 12, 21, 41. Không đổi nguồn sau khi xem kết quả judge.

Lượt 1 đưa (A, B); lượt 2 đưa (B, A) rồi quy winner và scores về A/B gốc. Scores ghi theo A/B gốc.

| ID | A (pipeline) | B (model_answer) | Pass 1 | Pass 2 (quy về gốc) | Final | Nhất quán | Scores pass 1 | Scores pass 2 |
|---|---|---|---|---|---|---|---|---|
| 1 | 3 ngày làm việc khi kết hôn (48 ký tự) | 3 ngày làm việc có lương (57 ký tự) | B | B | B | Có | A 0.8 / B 1.0 | A 0.5 / B 1.0 |
| 5 | Tổng Giám đốc (CEO) phê duyệt (34) | Giám đốc phòng ban phê duyệt (33) | A | A | A | Có | A 1.0 / B 0.0 | A 1.0 / B 0.0 |
| 12 | 1 tháng lương, nêu lại điều kiện từ 6 tháng (85) | 1 tháng lương (50) | A | tie | tie | Không | A 1.0 / B 0.5 | A 1.0 / B 1.0 |
| 21 | 18 ngày phép, không tìm thấy lương (135) | 18 ngày, lương 20–35 triệu (82) | B | B | B | Có | A 0.5 / B 1.0 | A 0.0 / B 1.0 |
| 41 | 15 ngày phép năm (62) | 12 ngày phép năm (37) | A | A | A | Có | A 1.0 / B 0.0 | A 1.0 / B 0.0 |

Reasoning tóm tắt theo nội dung judge trả về:

- ID 1: B thắng vì nêu rõ 3 ngày nghỉ là có lương, A thiếu ý này.
- ID 5: A đúng theo reference (trên 50 triệu cần CEO), B sai sự thật.
- ID 12: lượt 1 chọn A vì nêu rõ điều kiện từ 6 tháng; lượt 2 cho rằng hai answer chính xác như
  nhau và chọn tie.
- ID 21: B thắng vì có cả số ngày phép và khoảng lương; A bỏ sót lương.
- ID 41: A đúng chính sách v2024 hiện hành (15 ngày), B dùng chính sách v2023 đã bị thay thế.

Lưu ý khi đọc JSON: `reasoning_pass2` được giữ nguyên văn từ lượt 2, nên chữ "Answer A/B" trong đó
chỉ vị trí đã hoán đổi (A của lượt 2 là B gốc). Ví dụ ID 41 lượt 2 viết "Answer B chính xác với
v2024" — Answer B lúc đó chính là A gốc. Winner và scores của lượt 2 đã được quy đổi đúng.

Position bias count/rate: 1/5 = 0.2.
Verbosity win rate: 0.75; decisive cases: 4.

Case không nhất quán duy nhất là ID 12. Cả hai answer đều đúng mức thưởng 1 tháng lương; A chỉ
lặp lại điều kiện "từ 6 tháng trở lên" có sẵn trong câu hỏi. Lượt 1 coi đó là đầy đủ hơn, lượt 2
coi là tương đương. Đây là case sát nút mà tie là kết luận hợp lý, nên swap-and-average đã làm
đúng việc của nó là không ép ra winner. Một case trên 5 không đủ để kết luận judge có position bias.

Verbosity: trong 4 case decisive, answer dài hơn thắng 3 lần (ID 1, 5, 41). Đọc nội dung thì cả ba
winner thắng vì đúng/đủ hơn: ID 1 có thêm ý "có lương" là ý thiết yếu của reference; ID 5 chỉ dài
hơn 1 ký tự và B sai người phê duyệt; ID 41 B dùng chính sách cũ. Ngược lại ID 21 cho thấy judge
chọn answer **ngắn hơn** (82 so với 135 ký tự) vì answer dài bỏ sót lương. Vậy 0.75 là dấu hiệu
thống kê trên mẫu rất nhỏ, chưa có bằng chứng judge ưu tiên độ dài.

## Calibration đúng model_answer

Helper đánh giá đúng question/model_answer đang có trong fixtures/human_labels_10q.json;
không lấy answer mới của pipeline. Prompt chỉ nhận question, answer, reference.
Không gửi human_label, human_note hoặc phân bố nhãn human vào prompt.

| question_id | model_answer gốc | Judge | Reasoning của judge | Human | Agree |
|---|---|---|---|---|---|
| 1 | Nghỉ 3 ngày làm việc có lương khi kết hôn | 1 | Chính xác và đầy đủ theo reference | 1 | Có |
| 5 | Cần Giám đốc phòng ban phê duyệt | 0 | Sai: trên 50 triệu cần Tổng Giám đốc | 0 | Có |
| 12 | Thưởng Tết tối thiểu 1 tháng lương | 1 | Chính xác mức thưởng tối thiểu | 1 | Có |
| 21 | 18 ngày phép; lương Senior 20–35 triệu | 1 | Đúng cả số ngày phép và khoảng lương | 1 | Có |
| 23 | Hoàn trả 25 triệu vì chưa đủ 1 năm cam kết | 1 | Đúng số tiền và lý do hoàn trả | 1 | Có |
| 29 | Trưởng phòng phê duyệt; phạt 2% tháng trên 8 triệu | 0 | Thiếu phê duyệt Kế toán trưởng, sai cách tính phí phạt | 0 | Có |
| 33 | Phép 19 ngày; phụ cấp 1.500.000 VNĐ/tháng | 1 | Đúng số ngày phép và tổng phụ cấp | 1 | Có |
| 41 | Nghỉ 12 ngày phép năm | 0 | Sai: dùng chính sách cũ v2023 thay vì v2024 | 0 | Có |
| 46 | Thử việc không được nghỉ phép năm, phải xin nghỉ không lương | 1 | Đúng phủ định và điều kiện | 1 | Có |
| 50 | Được dùng VPN cá nhân nếu kết nối an toàn | 0 | Sai: chính sách cấm VPN cá nhân | 0 | Có |

Cohen’s κ: 1.0.
Observed/chance agreement và diễn giải: judge_labels = [1, 0, 1, 1, 1, 0, 1, 0, 1, 0] trùng hoàn
toàn human_labels, nên p_o = 10/10 = 1.0. Cả hai đều có 6 nhãn 1 và 4 nhãn 0, nên
p_e = 0.6 × 0.6 + 0.4 × 0.4 = 0.52. κ = (1.0 − 0.52) / (1 − 0.52) = 1.0, mức "almost perfect"
theo Landis-Koch và vượt ngưỡng 0.6. Các case nhãn 0 đều là lỗi thực chất dễ nhận ra (sai người
phê duyệt, dùng bản v2023, đảo phủ định về VPN, sai cách tính phạt).

## Giới hạn và cách dùng judge

- Mẫu rất nhỏ: 5 cặp pairwise và 10 nhãn nhị phân. κ = 1.0 trên 10 câu không có nghĩa judge luôn
  đúng; chỉ cần lệch 1 nhãn là κ giảm mạnh. Các câu sai trong bộ nhãn đều sai rõ ràng, chưa kiểm
  tra những case mơ hồ như answer đúng một phần.
- Judge và generation cùng họ model gpt-4o-mini, nên có thể có self-preference khi so answer của
  pipeline (A) với answer khác; kết quả 5 cặp chưa đủ để đo điều này.
- Judge có reference trong prompt, nên đây là đánh giá "đúng theo reference", phụ thuộc vào chất
  lượng ground_truth; không dùng được cho câu không có reference.
- Cách dùng đề xuất: giữ swap-and-average và coi case không nhất quán là tie; mở rộng bộ nhãn người
  (thêm case mơ hồ và multi_hop) rồi đo lại κ trước khi dùng judge làm CI gate; định kỳ lấy mẫu
  để người kiểm lại, không xem judge là đáp án tuyệt đối.
