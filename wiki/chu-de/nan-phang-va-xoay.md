---
type: chu-de
---
# Xoay, nắn phẳng, gộp PDF (tính năng 3)

- Yêu cầu: tự xoay đúng chiều, nắn phẳng theo mép giấy mà không cắt mất hoặc làm méo nội dung; gộp nhiều ảnh thành một PDF ([[prompt-ke-hoach]], [[yeu-cau-nguoi-dung]]).
- Kế hoạch: tìm mép giấy (OpenCV, mô hình phân vùng khi nền rối) → sửa phối cảnh → xoay 90°/180° (PaddleOCR hoặc Tesseract OSD) → sửa nghiêng (Hough hoặc phép chiếu) → tách trang đôi; trang sách cong dùng mô hình như DocTr, UVDoc (cần kiểm tra giấy phép, tốc độ) hoặc nắn theo dòng chữ; luôn chừa lề an toàn ([[ke-hoach-ung-dung]]).
- Nguyên mẫu (`loi_xu_ly/nan_phang.py`): tìm mép, sửa phối cảnh theo công thức tiêu cự của Zhang & He, tự xoay bằng Tesseract OSD, sửa nghiêng bằng phép chiếu, tách trang đôi, xóa viền nền bàn, kéo 4 góc khung cắt; **chưa có** nắn trang cong ([[readme]]).
- Phát hiện khi làm nguyên mẫu (theo `NHAT-KY.md` dự án, 2026-10-29): ước lượng tỉ lệ trang bằng độ dài cạnh lệch 6% khi chụp nghiêng, nên chuyển sang công thức Zhang & He; ảnh chụp kín hai trang sách từng bị cắt mất một trang, đã thêm kiểm tra "ngoài khung còn giấy có chữ thì không cắt".
- Kiểm thử: tỉ lệ A4 1,414, tự xoay 180°, nghiêng còn dưới 0,5° ([[kiem-thu]]).
- Ưu tiên của thủ thư: trang cong và tách trang đôi ([[ke-hoach-ung-dung]]).
- Gộp, sắp xếp trang PDF có sẵn trên nguyên mẫu PC: cửa sổ Sửa PDF ([[cua-so-sua-pdf]]); từ 2026-10-30 (lần 4) có thêm kéo thả ảnh trang, menu chuột phải, chép / dán trang giữa hai cửa sổ ([[thao-tac-trang]]).

## Bản Android 0.2.0: tự xoay toàn bộ (cập nhật 2026-10-29)
- Yêu cầu mới: tự xoay toàn bộ trang, có chọn ngang/dọc ([[yeu-cau-nguoi-dung]]).
- Bản Android đã có tìm mép, sửa phối cảnh về tỉ lệ A4, sửa nghiêng, xóa viền nền bàn, chế độ *Sách* tách trang đôi, kéo 4 góc (từ bản 0.1.0) ([[readme-ung-dung-flutter]]).
- Đoán chiều: sau khi xử lý, Tesseract `psm 1` với dữ liệu `osd` đoán chiều chữ từng trang, chạy nền, khoảng 1 giây một trang (README; kiểm thử đo khoảng 1,2 giây) ([[readme-ung-dung-flutter]], [[tesseract-ocr]]). Bản 0.1.0 chưa có bước này; nguyên mẫu PC đã tự xoay bằng Tesseract OSD từ trước.
- Nút **Xoay toàn bộ**: theo chiều chữ, hoặc ép *Tất cả khổ dọc* / *Tất cả khổ ngang*. Xoay giữ khung cắt tay ([[readme-ung-dung-flutter]]).
- Màn **Xem nhanh** gắn nhãn trang *Ngược chiều*, *Chữ nằm nghiêng 90°*, khổ khác đa số, *Chưa thấy mép giấy*; có *Sửa chiều tất cả* ([[ban-android-flutter]]).
- Kiểm thử trên máy ảo: đoán chiều đúng cả 4 góc 0°, 90°, 180°, 270°; luồng trang ngược → cảnh báo → Xoay toàn bộ → đúng chiều đạt ([[kiem-thu]]).
- Giới hạn: trang không đủ chữ (ảnh, bảng vẽ) không đoán được chiều, chỉ xoay được theo khổ. Bản Android vẫn **chưa có** nắn trang cong (`NHAT-KY.md` dự án; [[readme-ung-dung-flutter]]).

## Góp ý sau khi chạy máy thật (2026-11-14)
- Người dùng chạy bản Android trên máy thật: tự xoay cho khối chữ vuông góc và làm trắng đã đạt; ảnh **chưa được làm phẳng** ([[yeu-cau-nguoi-dung]]).
- Yêu cầu mới: tự căn chỉnh, làm phẳng như CamScanner: tự tìm đúng mép giấy, cắt và nắn phẳng phối cảnh, nắn trang cong; chỉnh tay 4 góc dễ dàng ([[yeu-cau-nguoi-dung]]).
- Trạng thái thực hiện: đã làm ở bản Android 0.7.0 và nguyên mẫu PC (mục dưới).

## Tìm mép kiểu CamScanner, nắn trang cong (bản Android 0.7.0, nguyên mẫu PC, 2026-11-14)
- Nguyên nhân ảnh chưa được làm phẳng: bộ tìm mép cũ chỉ lấy đường bao lớn nhất; trên bộ ảnh tổng hợp khó nó trượt khi giấy trên bàn trắng, nền lộn xộn, giấy chồng giấy, bìa sổ; không thấy mép thì trang để nguyên ([[du-lieu-kiem-thu]], `NHAT-KY.md` dự án 2026-11-14).
- Bộ tìm mép mới (`tim_mep.py`, `lib/loi/tim_mep.dart`): ứng viên tứ giác từ Canny 3 mức, Otsu, k-means, ghép đường Hough; chấm theo độ bám mép dọc từng cạnh với ngưỡng theo độ nhiễu hai bên mép, cộng diện tích và phần giống giấy; giấy nằm trên vật khác thì chọn tứ giác trong nếu vành ngoài không có chữ; tinh chỉnh cạnh ở ảnh 1280 px ([[readme]], [[readme-ung-dung-flutter]]).

## Sách mở bị cắt mất một trang (bản Android 0.7.5, nguyên mẫu PC, 2026-11-14)
- Góp ý chụp thật: khi chụp sách, có lúc ứng dụng chỉ nhận một nửa cặp trang. PDF người dùng gửi thiếu trang 123 và 125 ([[du-lieu-kiem-thu]]).
- Nguyên nhân tái hiện được: chụp sát, mép ngoài một trang lọt ra ngoài khung. Bộ tìm mép chọn trang còn nguyên, có đủ bốn mép, và tự chụp không thấy trang đó bị cắt.
- Cách sửa: nếu bên kia một cạnh của tứ giác là giấy có chữ chạy tới biên ảnh, thấy được 50–102% bề rộng trang, thì cạnh đó là gáy. Kéo cạnh ra tới biên ảnh để ảnh ra giữ cả phần trang bên kia; tự chụp nhắc lùi máy.
- Chụp từng trang thì trang bên cạnh thường lộ dưới 50%, không nối ([[kiem-thu]]).

## Nắn vuông khối chữ, không cắt lẹm (bản Android 0.7.6, nguyên mẫu PC, 2026-11-15)
- Góp ý: một số trang bị cắt lẹm vào chữ; người dùng muốn chỉnh méo, nắn vuông lại khối văn bản ([[yeu-cau-nguoi-dung]]).
- Nắn vuông khối chữ: khớp đường lề trái, lề phải qua đầu và cuối các dòng (bỏ dòng thụt đầu đoạn, dòng cuối đoạn). Sau đó kéo ngang từng hàng điểm ảnh cho hai lề thẳng, vuông góc dòng chữ.
  - Chỗ lệch thành bậc đột ngột thì không nắn, vì không phân biệt được với đoạn thụt lề.
- Cặp trang sách mở: mỗi trang được xoay thẳng riêng. Bước sửa nghiêng chung chỉ thẳng được một trang.
- Không cắt lẹm: khi nắn phẳng, khung tự tìm được nới 2,5% để giữ phần mép trang cong phình ra. Nền bàn, bìa sách trong dải nới được tô màu giấy.
- PDF có sẵn: nhập lại vào ứng dụng, hoặc chạy `nan_lai_pdf.py` trên máy tính. Chữ đã bị cắt trong PDF cũ thì không lấy lại được ([[kiem-thu]]).
- Kết quả đo: Python 17/17 ảnh cố định, 24/24 và 29/29 ảnh ngẫu nhiên (bộ cũ 10/15, 12/30, 16/29); Android máy ảo 17/17, khoảng 0,44 s/ảnh ([[kiem-thu]]).
- Nắn trang cong theo dòng chữ (`nan_cong.py`, `lib/loi/nan_cong.dart`): khớp đường cong từng dòng, mặt độ lệch dọc trơn cho cả trang, ánh xạ ngược; trang phẳng để nguyên. Võng dòng chữ 0,66% → 0,07% chiều cao trang. Giới hạn: chưa giãn ngang phần chữ co gần gáy, trang không có dòng chữ không nắn được. Kế hoạch ban đầu có nêu mô hình học sâu (DocTr, UVDoc) — chưa dùng ([[ke-hoach-ung-dung]]).
- Giao diện Android: thẻ *Cắt, nắn phẳng*, kéo góc hoặc giữa cạnh, kính lúp phóng 2,5 lần, phần ngoài khung tối đi; nút *Nắn trang cong* ([[ban-android-flutter]]).
- Chưa thử ảnh chụp thật, điện thoại thật.

## Cắt sát chữ, xóa vết, nắn cong sách mở (bản Android 0.7.2, PC, 2026-11-14)
- Góp ý sau khi chụp thử 0.7.1 (8 trang sách mở hai trang): chữ đã tốt; cần cắt sát chữ hơn, tự xóa vết, vệt đen ([[yeu-cau-nguoi-dung]]).
- Ảnh còn dải nền tối, nêm đen ở gáy, góc đen, ngón tay giữ sách; nắn cong bỏ qua 7/8 ảnh vì hai trang cong ngược nhau (`NHAT-KY.md` dự án 2026-11-14).
- Cắt sát chữ (`cat_chu.py`, `lib/loi/cat_chu.dart`): nhận vết theo độ tối, màu da, độ lấp kín, chạm mép; giữ khối chữ và khối gần (số trang, chú thích); không lẹm chữ; lề trắng 1,5 chiều cao chữ. Nắn cong tách theo gáy: võng 0,11–0,34% → 0,02–0,05% ([[kiem-thu]], [[du-lieu-kiem-thu]]).
- Đánh đổi: trang không còn tỉ lệ A4; có nút tắt *Cắt sát chữ* ([[ban-android-flutter]]).

## Tự xoay ảnh cầm máy ngang, xóa ngón tay, đường gáy (bản Android 0.7.3, PC, 2026-11-14)
- Người dùng gửi 11 trang sách mở chụp bằng 0.7.2: cả 11 trang nằm ngang. Do cầm máy ngang trong khi ứng dụng khóa dọc; ứng dụng chỉ cảnh báo sai chiều nên tìm gáy, nắn cong, cắt sát chữ đều hỏng (`NHAT-KY.md` dự án 2026-11-14).
- Nhận dòng chữ dọc (`chieu_chu.py`, `lib/loi/chieu_chu.dart`, nối chữ theo hai chiều, so độ dài dải) rồi xoay về ngang trước các bước sau. Android tự lật theo Tesseract một lần mỗi trang; người dùng tự xoay thì tắt tự xoay.
- Cắt sát chữ thêm: bán kính nét (bóng dày mà nhạt là vết), ngón tay màu da tô trắng giữ nét chữ bị đè, dải gáy giữa hai trang, tiêu đề cách xa thân bài vẫn giữ ([[kiem-thu]], [[du-lieu-kiem-thu]], [[ban-android-flutter]]).
- README hai bản ghi các ý trên: PC `xoa_da_tay` trong `cat_chu.py`, Tesseract lật 180° nếu cần; Android `TuyChon.tuXoay`, tự lật khi đủ 12 từ, chưa sửa chữ ([[readme]], [[readme-ung-dung-flutter]]).

## Tách cặp trang theo khe gáy, lề vừa (bản Android 0.7.7, PC, 2026-11-15)
- Hồ sơ 214 trang người dùng gửi: khoảng 70–80 trang bị tách gáy sai (trang trái dính chữ đầu dòng trang phải, trang phải mất chữ đầu dòng); trang ít chữ bị cắt còn mẩu ([[ho-so-15-11-sach-214-trang]]).
- Tách trang mới (`_khe_gay`, `cat_theo_duong`; Dart `kheGay`, `catTheoDuong`): tìm khe trắng giữa hai khối chữ theo 12 dải ngang, khớp đường thẳng (gáy xiên tới khoảng 6°), cắt theo đường xiên, phần thừa lấp bằng nền khe. Không theo bóng gáy nữa. Bước nắn cong cặp trang cũng cắt theo khe này.
- Lề: mặc định "Vừa" (giữ lề thật tới 6% cạnh dài), còn "Sát chữ", "Giữ cả trang"; trang ít chữ giữ khổ trang. Thay yêu cầu cắt sát chữ ngày 14/11 ([[yeu-cau-nguoi-dung]]).
- Kiểm thử: 33 cặp trang, cách cũ cắt qua chữ 3 cặp chụp thật, cách mới đạt 33/33 ([[kiem-thu]]).
