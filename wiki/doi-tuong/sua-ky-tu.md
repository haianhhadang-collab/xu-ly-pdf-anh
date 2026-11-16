---
type: doi-tuong
ngay_nap: 2026-10-30
---
# Sửa ký tự giữ nguyên bản gốc (`loi_xu_ly/sua_ky_tu.py`, nguyên mẫu PC)

Công cụ chính để sửa chữ trong [[cua-so-sua-pdf]] từ 2026-10-30 (lần 3), thay cho cách viết lại cả khối bằng phông. Lý do đổi: người dùng nhận xét cách sửa theo khối làm mất định dạng, cỡ chữ và để chữ máy đọc sai đổi nội dung ([[yeu-cau-nguoi-dung]]).

## Cách làm
- Dòng chữ chia thành mảnh liền nhau: mỗi ký tự, mỗi khoảng trắng là một dải điểm ảnh gốc; khung ký tự lấy từ hOCR (`hocr_char_boxes`) của [[tesseract-ocr]]. OCR chỉ dùng để biết ranh giới ký tự, đọc sai không làm đổi chỗ không sửa (`NHAT-KY.md` dự án, 2026-10-30, mục "Sửa ký tự giữ nguyên bản gốc"; [[readme]]).
- Xóa = bỏ mảnh. Chèn = chép nguyên hình ký tự từ chính trang; không có thì lấy ở trang khác (đánh dấu chưa chắc, viền vàng); cả tệp không có mới vẽ bằng phông. Chuột phải lên một ký tự trên trang để chọn làm mẫu.
- Dãy chấm dẫn ở mục lục co giãn ở cuối dãy, để số trang đứng nguyên chỗ.
- Trang PDF chỉ gồm một ảnh scan được sửa trên chính ảnh gốc (PDFium `get_bitmap(render=False)`), lưu đúng kích thước, đúng chỗ đặt cũ; trang khác dựng theo độ phân giải ảnh thay vì luôn 300 dpi (`tai_lieu_pdf.py`).
- Thao tác trong cửa sổ: bấm vào dòng đặt con trỏ; ← →, Home/End; Backspace, Delete; gõ để chèn (Unikey được); Enter xong, Esc hủy; xem trước ngay.

## Bẫy gặp trên tệp thật và cách xử lý
Tệp thật người dùng gửi: PDF 7 trang ảnh xuất từ bản Android, khoảng 100–127 dpi, trang 1 là mục lục. Ở 127 dpi Tesseract đọc dãy chấm thành chữ loạn, "giữa" thành "glữ". Cách xử lý (`NHAT-KY.md` dự án, 2026-10-30, mục "Sửa ký tự giữ nguyên bản gốc"):
- phóng ảnh lên khoảng 300 dpi chỉ để nhận dạng;
- tìm dãy chấm theo hình dạng, bỏ "chữ" đọc nhầm trong đó (kể cả scan nghiêng, chấm nhòe to);
- nối dài dòng theo nét mực vì Tesseract bỏ sót số trang đứng lẻ; gộp dòng tách rời cùng hàng;
- đo cỡ chữ bằng chữ thường không dấu đọc chắc; tính đường chân chữ sau cùng;
- mẫu chép chỉ lấy nét chạm khung ký tự; loại mẫu chữ, số quá nhỏ; bỏ mảnh rộng 0.
- (bổ sung 2026-10-30, do bản Android phát hiện) mảnh chồng nhau phải so với mảnh còn giữ gần nhất, không chỉ mảnh liền trước: từ máy đọc chồng lên từ sau làm vài cột điểm ảnh bị dán hai lần thành vệt lạ. Trên tệp thật cách cũ chồng 381–399 cột ở mỗi trang mục lục, cách mới 0. Khe chuẩn giữa hai ký tự không tính khe cạnh dấu chấm, nếu không ký tự chèn trên trang mục lục bị giãn thưa (`NHAT-KY.md` dự án, mục "Sửa ký tự giữ nguyên bản gốc", phần Android).

## Dòng nghiêng (ảnh chụp), bổ sung 2026-10-30
Người dùng thử bản Android 0.5.0 trên điện thoại thật với ảnh chụp nhãn hàng có dòng nghiêng, dòng sát nhau: chữ sửa bị lệch dòng và dòng trên, dòng dưới bị nát ([[yeu-cau-nguoi-dung]]). Nguyên nhân: mỗi dòng được coi là một dải ngang thẳng; dời phần sau chỗ sửa là dời cả cột điểm ảnh trong dải, nên kéo theo nét của dòng bên cạnh lọt vào dải, còn ký tự chèn đặt theo một đường chân nằm ngang. Cách sửa, làm ở cả bản PC và bản Android (`NHAT-KY.md` dự án, mục "Sửa ký tự trên dòng nghiêng"):
- đường chân chữ là đường xiên đo riêng từng dòng: độ dốc Theil–Sen qua đáy khung các ký tự không có nét xuống (bỏ g, p, y, chữ có dấu nặng…); dải dòng là dải xiên phủ trọn dấu thanh, nét xuống;
- `net_cua_dong` phân nét mực trong dải: mỗi thành phần liên thông thuộc dòng có khung ký tự phủ nhiều điểm mực của nó nhất; nét không chạm khung nào thì theo dải xiên gần nhất; nét dính liền hai dòng tách từng điểm; đường kẻ dài, nét quá cao không thuộc dòng nào;
- dựng dòng: mảnh đứng nguyên chỗ không đụng tới; mảnh phải dời thì chỉ nét của dòng được xóa chỗ cũ (vá nền) và dán sang chỗ mới, lệch dọc theo độ dốc; ký tự chép đặt theo đường chân tại chỗ chèn; mẫu chép chỉ lấy nét của chính dòng nguồn;
- khung dòng, con trỏ trên giao diện vẽ nghiêng theo dòng; chạm chọn dòng theo dải xiên.

## Gõ tiếng Việt: phông, đậm nhạt, bổ sung 2026-10-30
Người dùng báo gõ tiếng Việt khi sửa chữ bị lỗi phông, lỗi đậm nhạt ([[yeu-cau-nguoi-dung]]). Nguyên nhân và cách sửa, làm ở cả bản PC và bản Android (`NHAT-KY.md` dự án, mục "Gõ tiếng Việt khi sửa ký tự"):
- khung ký tự LSTM của [[tesseract-ocr]] lệch ngang tới nửa chữ nên mẫu chép kèm nét, dấu của chữ bên cạnh: `nan_khung` nắn khung theo nét mực thật (ghép nét chính với chữ theo thứ tự bằng quy hoạch động; dấu theo chữ đứng dưới, trên);
- chọn mẫu theo độ đậm cả dòng, đo thô: nay đo bề dày nét riêng từng ký tự (2 × diện tích / chu vi), so vài chữ quanh chỗ chèn với vài chữ quanh mẫu, bỏ mẫu chênh trên 18% khi có mẫu vừa; loại mẫu dáng lạ;
- chữ chèn tô bằng màu mực lõi nét quanh chỗ chèn;
- chữ có dấu thiếu hoặc chỉ có ở kiểu nét khác: `ghep_dau` ghép thân chữ với cụm dấu chép từ chữ khác;
- bộ gõ dấu rời: ghép thành chữ dựng sẵn.
Kết quả: mục 1e của `kiem_thu_sua_pdf.py` và phép thử (h) bản Android đạt; bề dày nét chữ chèn trung vị 2,8 px so với chữ thường 2,6 px, dòng đậm 3,7 px.

## Đổi phông, cỡ chữ đoạn bôi chọn, bổ sung 2026-10-30
Theo yêu cầu "thêm chức năng đổi font, cỡ chữ"; người dùng chọn phạm vi là đoạn chữ bôi chọn ([[yeu-cau-nguoi-dung]]). Nguồn: `NHAT-KY.md` dự án.
- Phiên sửa dòng thêm đoạn chọn (đầu kia `moc` + con trỏ). Gõ khi đang chọn thì thay đoạn; xóa thì xóa cả đoạn.
- **Đổi cỡ, giữ nét gốc**: mỗi ký tự trong đoạn thành mảnh chép chính nét của nó (chỉ nét của dòng; nền, lõi mực đo trên cả dòng), phóng, thu theo tỉ lệ; phần sau tự dồn. Trả tỉ lệ về 1 thì mảnh gốc trở lại, dòng như chưa sửa (không ghi thao tác).
- **Đổi phông**: chỉ đoạn chọn được vẽ lại bằng phông, kiểu, cỡ đã chọn; màu mực, độ nhòe (PC) hoặc viền đậm (Android) đoán từ chính đoạn. Đây là ngoại lệ có chủ ý với quy tắc "không vẽ lại chữ bản scan": chỉ khi người dùng tự chọn phông cho đoạn đó. Chữ theo nội dung máy đọc nên cần soát.
- Mỗi mảnh nhớ bản gốc (`ban_goc`) để trả về nét gốc; chữ gõ thêm ngay sau đoạn đã đổi theo định dạng đó.
- Chữ phóng to được vẽ ra ngoài dải dòng, vẫn không đè nét dòng khác trong dải. Android tính vùng vẽ (`SuaDong.vungVe`) để xem trước phủ đúng chỗ.
- Giao diện: PC dùng khung Chữ (Phông/Kiểu "Tự đoán" = giữ nét gốc; Ctrl+] / Ctrl+[); Android có thanh A− / cỡ / A+ và menu phông ([[ban-android-flutter]]).
- Kiểm tra (dòng nghiêng): phóng 1,5 lần, cao 36 → 54 px; phần trước đoạn chọn, chữ dòng khác không đổi điểm ảnh nào; đổi sang Arial (PC) / Liberation Sans (Android) đậm, gõ "X", đọc lại "nhựaX Melamine". PC mục 1f đạt; Android (i) đạt, 10/10.

## Kết quả kiểm tra
- Tệp thật (bản sao): "giữ" → "giữa", "956" → "95" (số trang vẫn thẳng lề phải): ngoài dải dòng sửa không đổi điểm ảnh nào. "74" → "75": trang không có mẫu "5", mẫu từ trang khác lệch kiểu chữ nên bị viền vàng. Ảnh trang 1 vẫn 1057×1482; trang 2–7 chép nguyên.
- `kiem_thu_sua_pdf.py` mục 1c đạt toàn bộ ([[kiem-thu]]).
- Mục 1d (trang tổng hợp năm dòng sát nhau xoay 2,5°): đo độ nghiêng −0,0441 (thật −0,0437); chèn " nhựa ăn" thì nét dòng trên, dòng dưới không đổi điểm ảnh nào, phần trước chỗ sửa giữ nguyên, ký tự chèn lệch đường chân dưới 1 px, đọc lại đúng. Thử thêm trên ảnh chụp màn hình người dùng gửi (phần dòng chưa sửa): dòng bên cạnh không đổi điểm mực nào.

## Chưa làm
Chưa chọn được vùng tùy ý làm mẫu (chỉ chuột phải lên ký tự máy tách được); dòng dài quá lề chỉ cảnh báo, chưa tự xuống dòng; trang PDF chữ thật vẫn dựng lại thành ảnh. Bản Android có công cụ này từ 0.5.0 (`lib/loi/sua_ky_tu.dart`, kiểm thử `sua_ky_tu_test.dart` 7/7), xem [[ban-android-flutter]]; nhật ký đã ghi đủ phần Android.

Liên quan: [[nhan-dang-va-sua-chu]], [[nguyen-mau-windows]].
