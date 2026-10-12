# Đánh giá LLM Judge Phase B

Nhóm: **FAMI**.

Người phụ trách: **Nguyễn Văn Hưởng — 2A202602743**.

Nguồn: `artifacts/judge_results.json`, format_version=2, run_kind=live.
Run timestamp UTC: `2026-10-12T12:30:37.395169+00:00`; giờ Việt Nam: **19:30:37 ngày 12/10/2026**, UTC+07:00.
Model generation theo answers: `gpt-4o-mini-2024-07-18`.
Model judge cấu hình: `gpt-4o-mini`; đây là alias cấu hình,
không phải xác nhận snapshot mà provider resolve trong từng response.

Đã chạy một batch thật gồm 5 cặp × 2 lượt và 10 binary judgments. **Cohen’s κ=1**,
nhãn judge khớp human 10/10; position inconsistency 0/5;
verbosity win rate 100%. Kết quả đã kiểm tra offline theo schema,
nguồn dữ liệu, phép tính và SHA-256; không chạy lại API để xác nhận.

## Năm cặp A/B và hai lượt

Nguồn cố định: A từ `artifacts/answers_50q.json:answer`, B từ
`fixtures/human_labels_10q.json:model_answer`, question/reference từ
`fixtures/test_set_50q.json:question/ground_truth`. Ids: 1, 5, 12, 21, 41.
Không thay candidates sau khi đọc kết quả judge và không lấy ground_truth làm answer.
File 50 answers được lấy từ `origin/main` commit `96f6b2c`; gồm 20 factual,
20 multi_hop, 10 adversarial và 50 records khai báo generation_mode=llm.
Việc đánh giá dùng đúng answers đã lưu của nhóm, không chạy lại RAG hoặc generation.

Pairwise prompt ưu tiên accuracy theo reference, completeness và conciseness;
kiểm tra phiên bản, phủ định và điều kiện. Candidates được gửi dưới dạng dữ liệu
JSON, không phải chỉ dẫn. Temperature=0, JSON response format, max_tokens=512;
reasoning yêu cầu 1–2 câu. Mỗi cặp chạy A/B rồi B/A với cùng reference.
Winner và scores lượt 2 đã được đổi về A/B gốc; hai lượt đồng thuận thì giữ
winner, khác nhau thì final=tie. Theo hợp đồng lab, không lấy trung bình
scores để ép ra một winner.


| Id | Question | Candidate A: pipeline | Candidate B: supplied model_answer |
| --- | --- | --- | --- |
| 1 | Nhân viên được nghỉ bao nhiêu ngày khi kết hôn? | Nhân viên được nghỉ 3 ngày làm việc khi kết hôn. | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn. |
| 5 | Muốn mua thiết bị trị giá 55 triệu cần ai phê duyệt? | Cần Tổng Giám đốc (CEO) phê duyệt. | Cần Giám đốc phòng ban phê duyệt. |
| 12 | Thưởng Tết tối thiểu cho nhân viên chính thức có từ 6 tháng trở lên là bao nhiêu? | Thưởng Tết tối thiểu cho nhân viên chính thức có thời gian làm việc từ 6 tháng trở lên là 1 tháng lương. | Nhân viên được thưởng Tết tối thiểu 1 tháng lương. |
| 21 | Một nhân viên Senior có 9 năm thâm niên được nghỉ bao nhiêu ngày phép năm và lương trong khoảng nào? | Không tìm thấy. | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu. |
| 41 | Nhân viên được nghỉ bao nhiêu ngày phép năm? | Nhân viên chính thức được hưởng 15 ngày phép năm trong chính sách nghỉ phép năm 2024. | Nhân viên được nghỉ 12 ngày phép năm. |



| Id | Winner lượt 1 | Winner lượt 2 đã quy đổi | Final | Consistent | Scores lượt 1 | Scores lượt 2 đã quy đổi | Ký tự A/B |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | B | B | B | true | A=0.5; B=1 | A=0.8; B=1 | 48/57 |
| 5 | A | A | A | true | A=1; B=0 | A=1; B=0 | 34/33 |
| 12 | A | A | A | true | A=1; B=0.5 | A=1; B=0.7 | 104/50 |
| 21 | B | B | B | true | A=0; B=1 | A=0; B=1 | 15/82 |
| 41 | A | A | A | true | A=1; B=0 | A=1; B=0 | 85/37 |


Reasoning dưới đây giữ nguyên câu trả lời của judge. **A/B trong reasoning lượt 2
vẫn chỉ thứ tự đã hoán đổi**: A của lượt 2 là candidate B gốc, B của lượt 2 là
candidate A gốc. Không thay nhãn trong văn bản rồi trình bày như response nguyên bản.


| Id | Reasoning lượt 1 | Reasoning lượt 2 nguyên bản |
| --- | --- | --- |
| 1 | Câu trả lời B chính xác và đầy đủ thông tin về việc nghỉ có lương, trong khi câu A thiếu thông tin quan trọng này. | Câu trả lời A chính xác và đầy đủ thông tin về việc nghỉ có lương, trong khi câu B thiếu thông tin về việc nghỉ có lương. |
| 5 | Câu trả lời A đúng với thông tin trong reference, trong khi câu B lại sai vì không đúng với yêu cầu phê duyệt cho đơn hàng trên 50 triệu VNĐ. | Câu trả lời B đúng với thông tin trong reference, trong khi câu A sai vì không đúng người phê duyệt. |
| 12 | Câu trả lời A chính xác và đầy đủ thông tin về mức thưởng Tết cho nhân viên chính thức có từ 6 tháng trở lên, trong khi câu B thiếu thông tin về điều kiện thời gian làm việc. | Câu trả lời B cung cấp thông tin chính xác và đầy đủ theo reference, trong khi câu A thiếu thông tin về điều kiện thời gian làm việc. |
| 21 | Câu trả lời B cung cấp thông tin chính xác và đầy đủ về số ngày phép và mức lương của nhân viên Senior, trong khi câu A không cung cấp thông tin nào. | Câu trả lời A cung cấp thông tin chính xác và đầy đủ về số ngày phép và mức lương của nhân viên Senior theo chính sách, trong khi câu B không cung cấp thông tin nào. |
| 41 | Câu trả lời A chính xác theo chính sách v2024, trong khi câu B lại dựa trên chính sách cũ đã bị thay thế, do đó không chính xác. | Câu trả lời B chính xác và đầy đủ theo chính sách v2024, trong khi câu A lại dựa trên chính sách cũ đã bị thay thế. |


### Phân tích nội dung và bias

Cả 5 cặp đồng thuận sau quy đổi: B thắng ids 1,21; A thắng ids 5,12,41;
không có tie. Position inconsistency rate=0/5=0%. Điều này chỉ cho thấy winner
ổn định trong mẫu này, chưa loại trừ position bias. Id 1 vẫn có score A dao động
0.5→0.8 và id 12 có score B dao động 0.5→0.7 sau quy đổi, dù winner không đổi.
Do đó mức chấm điểm không bất biến hoàn toàn khi hoán đổi.

Verbosity counts: a_wins_a_longer=3, b_wins_b_longer=2, total_decisive=5;
verbosity win rate=(3+2)/5=100%, vượt ngưỡng 0.6 cần xem xét. Độ dài dùng số ký
tự theo checker, không phải token hoặc số ý. Mẫu này không có các cặp kiểm soát
cùng nội dung nhưng khác độ dài, nên chưa thể quy nguyên nhân cho verbosity bias.

- Id 1: B bổ sung “có lương”; A chỉ nêu 3 ngày. Winner dài hơn có thêm chi tiết
  đúng theo reference, nhưng câu hỏi chính chỉ hỏi số ngày. Việc cho A 0.5 và
  0.8 ở hai lượt cho thấy judge có thể áp dụng completeness chưa đồng đều.
- Id 5: A đúng thẩm quyền CEO cho 55 triệu, B sai khi chọn Giám đốc phòng ban.
  Đây là khác biệt accuracy rõ ràng; việc winner dài hơn không giải thích được
  chất lượng. Chênh lệch số ký tự nhỏ cũng làm chỉ số độ dài nhạy với cách viết.
- Id 12: A nhắc lại điều kiện chính thức và đủ 6 tháng, B chỉ nêu 1 tháng lương.
  Pairwise ưu tiên A vì đầy đủ hơn, nhưng binary judge vẫn cho B label=1 vì
  điều kiện đã có trong question. Đây là case cần phân biệt so sánh tương đối
  với đạt yêu cầu nhị phân, đồng thời kiểm tra xu hướng thưởng việc lặp lại đề.
- Id 21: A trả “Không tìm thấy.”, B nêu đúng 18 ngày phép và lương 20–35 triệu.
  Winner B đáp ứng cả hai phần câu hỏi, không chỉ dài hơn. Phase A/người tích
  hợp nên kiểm tra contexts và quá trình retrieval/generation của id 21; kết
  quả judge một mình chưa đủ xác định lỗi nằm ở tầng nào.
- Id 41: A dùng chính sách v2024 (15 ngày), B dùng v2023 (12 ngày) đã bị thay
  thế. Winner A đúng phiên bản, có cơ sở accuracy; A chưa nêu phần cộng thâm
  niên của reference, nên điểm 1.0 không nên hiểu là chép đủ mọi chi tiết policy.

## Calibration trên đúng model_answer

Helper `src.experiment_support.judge_binary` đánh giá đúng question/model_answer
của 10 records trong human data, kèm ground_truth cùng id. Prompt không nhận
human_label, human_note hoặc tỷ lệ nhãn human. Runner chỉ lấy human labels để
đối chiếu sau khi đã hoàn tất cả 10 binary judgments. Không đổi winner A/B thành
nhãn 0/1 và không thay model_answer bằng answer pipeline mới.

Binary prompt cho label=1 khi answer đúng theo reference và đủ ý thiết yếu của
question; label=0 khi sai, thiếu ý thiết yếu, dùng chính sách cũ, đảo phủ định
hoặc thêm khẳng định không được hỗ trợ. Không trừ nhãn chỉ vì khác độ dài hay
cách diễn đạt. Temperature=0, JSON response format, max_tokens=256;
reasoning 1–2 câu. Label bắt buộc là integer 0/1.


| Id | Model_answer gốc | Judge | Human | Agree | Reasoning judge nguyên bản |
| --- | --- | --- | --- | --- | --- |
| 1 | Nhân viên được nghỉ 3 ngày làm việc có lương khi kết hôn. | 1 | 1 | Có | Câu trả lời chính xác và đầy đủ theo thông tin trong tài liệu tham khảo, không thiếu ý thiết yếu nào. |
| 5 | Cần Giám đốc phòng ban phê duyệt. | 0 | 0 | Có | Câu trả lời sai vì cần Tổng Giám đốc phê duyệt chứ không phải Giám đốc phòng ban. |
| 12 | Nhân viên được thưởng Tết tối thiểu 1 tháng lương. | 1 | 1 | Có | Câu trả lời chính xác và đầy đủ theo thông tin trong reference, không thiếu ý thiết yếu nào. |
| 21 | Được nghỉ 18 ngày phép (15 cơ bản + 3 thâm niên). Lương Senior từ 20 đến 35 triệu. | 1 | 1 | Có | Câu trả lời chính xác theo reference, nêu rõ số ngày phép và khoảng lương cho nhân viên Senior với 9 năm thâm niên. |
| 23 | Hoàn trả 25 triệu vì chưa đủ 1 năm cam kết. | 1 | 1 | Có | Câu trả lời chính xác theo reference, nêu rõ số tiền phải hoàn trả và lý do vì chưa đủ thời gian cam kết. |
| 29 | Trưởng phòng phê duyệt. Phạt 2% tháng trên 8 triệu. | 0 | 0 | Có | Câu trả lời thiếu thông tin về sự cần thiết có sự phê duyệt của Kế toán trưởng và tính toán phí phạt không chính xác, chỉ tính cho 15 ngày chứ không phải 30 ngày. |
| 33 | Phép: 19 ngày. Phụ cấp: 1.500.000 VNĐ/tháng. | 1 | 1 | Có | Câu trả lời cung cấp đúng số ngày phép và tổng phụ cấp hàng tháng theo thông tin trong tài liệu tham khảo. |
| 41 | Nhân viên được nghỉ 12 ngày phép năm. | 0 | 0 | Có | Câu trả lời sai vì nó dựa trên chính sách cũ (v2023) thay vì chính sách hiện hành (v2024) mà câu hỏi yêu cầu. |
| 46 | Nhân viên thử việc không được nghỉ phép năm và phải xin nghỉ không lương nếu cần. | 1 | 1 | Có | Câu trả lời chính xác theo reference, nêu rõ rằng nhân viên thử việc không được nghỉ phép năm và phải xin nghỉ không lương nếu cần, đồng thời không bỏ qua điều kiện phê duyệt từ trưởng phòng. |
| 50 | Được, miễn là đảm bảo kết nối an toàn. | 0 | 0 | Có | Câu trả lời sai vì cho phép sử dụng VPN cá nhân, trong khi chính sách rõ ràng cấm điều này. |


Thứ tự ids và hai vectors được giữ đồng bộ:

```text
question_ids = [1, 5, 12, 21, 23, 29, 33, 41, 46, 50]
judge_labels = [1, 0, 1, 1, 1, 0, 1, 0, 1, 0]
human_labels = [1, 0, 1, 1, 1, 0, 1, 0, 1, 0]
```

Có 6 nhãn tốt và 4 nhãn xấu ở cả hai vectors. Confusion matrix theo human
làm reference: TP=6, TN=4, FP=0, FN=0. Observed agreement p_o=10/10=1.
Chance agreement p_e=(6/10×6/10)+(4/10×4/10)=0.52.

```text
κ = (p_o - p_e) / (1 - p_e)
  = (1 - 0.52) / (1 - 0.52)
  = 1.0
```

Theo thang diễn giải trong đề bài, đây là almost perfect agreement trên mẫu
10 answers này; κ>0.6 đáp ứng điều kiện số liệu bonus Phase B trong rubric.
Kết quả không chứng minh human labels hoặc reasoning hoàn toàn đúng và không
đủ khẳng định judge đáng tin cậy trên mọi câu hỏi/chính sách.

### Kiểm chứng reasoning dù labels khớp

Không có case nhãn lệch human trong batch, nhưng reasoning vẫn có giới hạn:

- Id 46: answer gốc **không nhắc phê duyệt của trưởng phòng**, trong khi judge
  viết “đồng thời không bỏ qua điều kiện phê duyệt từ trưởng phòng”. Phần này
  không được answer hỗ trợ. Label=1 vẫn khớp human, nhưng reasoning thêm nhận
  xét không chính xác. Giữ nguyên response trong JSON và báo cáo để thấy rằng
  κ chỉ đánh giá agreement nhãn, không đo tính đúng của lời giải thích.
- Id 29: label=0 đúng vì thiếu Kế toán trưởng và chưa tính 80.000 VNĐ cho 15
  ngày quá hạn. Reasoning “chỉ tính cho 15 ngày chứ không phải 30 ngày” diễn đạt
  chưa rõ so với answer chỉ nêu tỷ lệ 2%/tháng. Cần người đọc đối chiếu phép
  tính trong reference, không dùng lời giải thích này thay cho policy gốc.
- Ids 5,41,50 kiểm tra lần lượt thẩm quyền phê duyệt, phiên bản phép năm và
  phủ định quyền dùng VPN cá nhân; judge phân biệt đúng trên các answers mẫu.
  Cần thêm dữ liệu độc lập, không chỉ lặp lại 10 answers đã hiệu chuẩn.

## Giới hạn và cách dùng judge

Mẫu chỉ có 5 cặp và 10 binary labels; không có thử nghiệm nhân quả về độ dài
hoặc vị trí. Temperature=0 không bảo đảm các lượt tuyệt đối giống nhau.
Nguồn reference, model alias, prompt và cách định nghĩa completeness ảnh hưởng
kết quả. Mẫu 100% longer-win nên thúc đẩy kiểm chứng bằng các cặp cùng thông
tin nhưng khác cách viết; không kết luận judge ưu tiên dài dòng từ tỷ lệ này.

Dùng swap để phát hiện disagreement và trả tie khi chưa rõ; lưu hai lượt,
scores và reasoning để người kiểm tra đọc lại. Với calibration, giữ answer
nguồn và chỉ dùng human labels sau judge. Khi judge và human lệch, kiểm tra
question, reference, phiên bản và điều kiện; không sửa fixtures/candidates,
chọn lọc run hoặc sửa nhãn để tăng κ. Với câu nhạy cảm hoặc kết quả đáng ngờ,
đưa cho người kiểm tra; không dùng judge làm đáp án tuyệt đối.

## Bằng chứng và kiểm chứng

- Code Tasks 5–8: `src/phase_b_judge.py`; helper binary đã cung cấp trong
  `src/experiment_support.py`, bổ sung giới hạn output để tiết kiệm.
- Live artifact: `artifacts/judge_results.json`; kết quả fail/khác kỳ vọng cũng
  được giữ nguyên, không thay reasoning hoặc scores để làm đẹp số liệu.
- Tests offline: **84 passed** (24 Phase B, 60 support/report contracts),
  dùng SDK mock, không gọi API. Không còn marker TODO ở module Phase B.
- Validator kiểm tra JSON schema, A/B/reference sources, ids, scores, labels,
  κ, counts/rates và metadata hashes; không thay bằng chứng gọi API bằng mock.
- Hỗ trợ AI: Codex đọc đề/scaffold, triển khai và kiểm chứng, chạy một batch
  thật và soạn phân tích từ artifact; khai phạm vi trong `doc/TEAM.md`.
  Người phụ trách cần tự đọc, giải thích và xác nhận nội dung khi nộp.

Lệnh đã chạy một lần khi answers được tích hợp:

```bash
.venv/bin/python scripts/run_experiments.py --phase b --live
```

Không chạy lại integration/API chỉ để đối chiếu file; kiểm chứng sau batch
thực hiện offline. Source hashes trong metadata phục vụ phát hiện báo cáo cũ
khi dữ liệu nguồn thay đổi; chúng không tự chứng minh tính đúng của pipeline.


| File đầu vào | SHA-256 |
| --- | --- |
| answers_50q.json | 2ab8e6ea982c5f74752af9891a327c6a8d9d005cd2fc68c426a7736d5c0bc1df |
| test_set_50q.json | 3ad288426e3066e561737b35b66b671e6c411697dffd0d1161cc7b801e5954cc |
| human_labels_10q.json | 37231c1f4a635801e27a98333898d2d4c9c3c71167e8b9e7259b90cec5956782 |
