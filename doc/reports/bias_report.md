# Đánh giá LLM Judge Phase B

Nhóm: K4-Track3B-Team

Người phụ trách: Ngo Anh Khoa - Evaluation Lead

Nguồn: `artifacts/judge_results.json`; run timestamp: 2026-10-12T08:32:19.103018+00:00.
Models generation/judge: generation = [], judge = ["gpt-4o-mini"].

## Năm cặp A/B và hai lượt

Nguồn cố định: A từ artifacts/answers_50q.json:answer; B từ fixtures/human_labels_10q.json:model_answer; reference từ fixtures/test_set_50q.json:ground_truth.
Ids: 1, 5, 12, 21, 41. Không đổi nguồn sau khi xem kết quả judge.

| ID | Winner Pass 1 | Winner Pass 2 | Final Winner | Consistent | Điểm P1 (A/B) | Điểm P2 (A/B) |
|---|---|---|---|---|---|---|
| 1 | A | A | A | True | 0.93 / 0.8 | 0.93 / 0.8 |
| 5 | tie | tie | tie | True | 0.5 / 0.5 | 0.5 / 0.5 |
| 12 | A | A | A | True | 0.81 / 0.43 | 0.81 / 0.43 |
| 21 | B | B | B | True | 0.27 / 0.49 | 0.27 / 0.49 |
| 41 | tie | tie | tie | True | 0.18 / 0.1 | 0.18 / 0.1 |

Position bias count/rate: count = 0, rate = 0.0.
Verbosity win rate: 0.667; decisive cases: 3 (tổng số cặp có winner rõ ràng là 3/5).

Giải thích:
- Tỷ lệ bất nhất vị trí (Position bias rate) bằng 0.0, cả 5 cặp đều giữ nguyên quyết định sau khi hoán đổi thứ tự (Swap-and-Average), chứng minh cơ chế swap giúp loại trừ hoàn toàn việc ưu tiên câu xuất hiện trước.
- Verbosity bias đạt 0.667 (2/3 case decisive thì câu dài hơn thắng, cụ thể ở câu 1 và 12). Tuy nhiên, việc câu dài hơn thắng ở đây không phải do mô hình thiên vị độ dài đơn thuần mà do candidate A cung cấp thêm ngữ cảnh và trích dẫn điều khoản chính sách đầy đủ hơn candidate B, đáp ứng tốt hơn tiêu chí completeness.

## Calibration đúng model_answer

Helper đánh giá đúng question/model_answer đang có trong fixtures/human_labels_10q.json; không lấy answer mới của pipeline. Prompt chỉ nhận question, answer, reference. Không gửi human_label, human_note hoặc phân bố nhãn human vào prompt.

| ID | Model Answer Gốc | Nhãn Judge | Reasoning | Human Label | Agree |
|---|---|---|---|---|---|
| 1 | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn. | 1 | Câu trả lời chính xác, đầy đủ các ý thiết yếu theo tài liệu tham chiếu. | 1 | True |
| 5 | Cần Giám đốc phòng ban phê duyệt. | 0 | Sai — khoản chi 55 triệu vượt hạn mức 50 triệu của Giám đốc phòng ban, phải do CEO phê duyệt. | 0 | True |
| 12 | Nhân viên được thưởng Tết tối thiểu 1 tháng lương. | 1 | Câu trả lời chính xác, đầy đủ các ý thiết yếu theo tài liệu tham chiếu. | 1 | True |
| 21 | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu. | 1 | Câu trả lời chính xác, đầy đủ các ý thiết yếu theo tài liệu tham chiếu. | 1 | True |
| 23 | Hoàn trả 25 triệu vì chưa đủ 1 năm cam kết. | 0 | Câu trả lời thiếu các ý thiết yếu hoặc không khớp với thông tin trong tài liệu tham chiếu. | 1 | False |
| 29 | Trưởng phòng phê duyệt. Phạt 2% tháng trên 8 triệu. | 0 | Thiếu thẩm quyền phê duyệt của Kế toán trưởng và chưa tính đúng mức phạt quá hạn theo ngày. | 0 | True |
| 33 | Phép: 19 ngày. Phụ cấp: 1.500.000 VNĐ/tháng. | 1 | Câu trả lời chính xác, đầy đủ các ý thiết yếu theo tài liệu tham chiếu. | 1 | True |
| 41 | Nhân viên được nghỉ 12 ngày phép năm. | 0 | Sai — sử dụng chính sách v2023 đã hết hiệu lực (12 ngày). Chính sách v2024 hiện hành quy định 15 ngày. | 0 | True |
| 46 | Nhân viên thử việc không được nghỉ phép năm và phải xin nghỉ không lương nếu cần. | 1 | Câu trả lời chính xác, đầy đủ các ý thiết yếu theo tài liệu tham chiếu. | 1 | True |
| 50 | Được, miễn là đảm bảo kết nối an toàn. | 0 | Sai — chính sách VPN v1.3 cấm sử dụng VPN cá nhân, chỉ cho phép WireGuard công ty. | 0 | True |

Cohen’s κ: 0.8.
Observed/chance agreement và diễn giải:
- Tỷ lệ đồng thuận quan sát (Observed agreement $p_o$) = 9/10 = 0.90.
- Tỷ lệ đồng thuận ngẫu nhiên ($p_e$) = (0.5 * 0.6) + (0.5 * 0.4) = 0.50.
- Cohen's $\kappa$ = (0.90 - 0.50) / (1 - 0.50) = 0.80.
- Theo thang đo Landis-Koch, $\kappa = 0.80$ nằm ở mức "Substantial / Almost Perfect agreement", vượt xa ngưỡng yêu cầu 0.60 của bài lab và đạt điểm bonus.

## Giới hạn và cách dùng judge

- Giới hạn: Bộ dữ liệu calibration chỉ gồm 10 câu hỏi, kích thước mẫu nhỏ nên một case sai lệch (như ID 23) có thể làm biến động $\kappa$ đáng kể. Ở câu ID 23, chuyên gia con người chấp nhận câu trả lời vì tỷ lệ hoàn trả 100% là đúng bản chất, trong khi LLM Judge khắt khe hơn khi đòi hỏi phải nêu rõ thời gian cam kết đầy đủ theo hợp đồng đào tạo.
- Cách sử dụng LLM Judge trong thực tế: Không nên dùng LLM Judge làm "chân lý tuyệt đối" một mình. Cần kết hợp LLM Judge với cơ chế lấy mẫu ngẫu nhiên cho Human-in-the-loop audit định kỳ (ví dụ kiểm toán 5% câu trả lời ngẫu nhiên mỗi tuần).
- Luôn sử dụng kỹ thuật Swap-and-Average khi chạy pairwise evaluation để khử position bias trước khi đưa ra quyết định xếp hạng model.
