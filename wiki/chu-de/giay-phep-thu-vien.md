---
type: chu-de
---
# Giấy phép thư viện

- **Không dùng MuPDF / PyMuPDF** (AGPL) trong mã ứng dụng ([[yeu-cau-nguoi-dung]], [[ke-hoach-ung-dung]]).
- Đọc PDF: PDFium (BSD; trong nguyên mẫu là `pypdfium2`). Ghi PDF: thư viện `pdf` của Dart (bản Flutter); reportlab và pypdf (nguyên mẫu) ([[ke-hoach-ung-dung]], [[readme]]).
- Cửa sổ Sửa PDF của nguyên mẫu (2026-10-30) vẫn không dùng MuPDF: PDFium đọc, dựng trang; pypdf ghép, chép nguyên trang chưa sửa; reportlab ghi trang ảnh đã sửa ([[cua-so-sua-pdf]], [[readme]]).
- Sửa chữ dùng phông Times New Roman, Arial lấy từ `C:/Windows/Fonts/` của máy (`sua_noi_dung.py`). Điều khoản dùng các phông này khi chuyển sang bản phân phối (Android, iOS) chưa xét (điểm ghi `[cần xác minh]` ngày 2026-10-30; đã gỡ cùng ngày, xem dòng dưới).
  - Cập nhật 2026-10-30: đã xử lý cho Android. Times New Roman, Arial không được phép đóng gói, nên bản 0.4.0 đóng gói Liberation Serif, Liberation Sans thay thế (mục dưới) (`NHAT-KY.md` dự án, 2026-10-30). Nguyên mẫu PC vẫn dùng Times New Roman, Arial có sẵn trên chính máy Windows, không đóng gói kèm. Bản iOS chưa làm, sẽ dùng phông nào chưa chốt.
- Cập nhật 2026-10-30 (lần 4): tham khảo ONLYOFFICE DesktopEditors (AGPL-3.0) cho đối tượng, chú thích, thao tác trang: **chỉ học cách làm, không lấy mã**, cùng lý do tránh MuPDF ([[onlyoffice-desktopeditors]]).
- Chú thích PDF (2026-10-30, lần 4) nhúng tập con phông Times New Roman của máy Windows vào hình hiển thị /AP trong tệp lưu ra ([[chu-thich-pdf]]). Khác với sửa chữ (vẽ lên ảnh), đây là nhúng tệp phông vào PDF. Quyền nhúng của phông này, và phông nào dùng thay khi chuyển sang Android, iOS, chưa xét [cần xác minh].
- OpenCV: Apache 2.0. Tesseract, PaddleOCR: Apache 2.0. LaMa: Apache 2.0 ([[ke-hoach-ung-dung]]).
- Cần kiểm tra lại: giấy phép và độ nặng của VietOCR, DocTr, UVDoc ([[ke-hoach-ung-dung]]).

## Thành phần mới trong bản Android 0.2.0 (cập nhật 2026-10-29)
- Tesseract4Android 5.5.1 (`tesseract4android-5.5.1.aar`): Apache 2.0 ([[readme-ung-dung-flutter]]).
- Dữ liệu nhận dạng `vie.traineddata` từ kho `tesseract-ocr/tessdata`: Apache 2.0 (`assets/phong/GIAY-PHEP.txt`).
- `osd.traineddata` (đoán chiều) cũng được đóng gói; cùng kho tessdata của Tesseract, Apache 2.0. `GIAY-PHEP.txt` đã bổ sung dòng này ngày 2026-10-29 ([[readme-ung-dung-flutter]]).
- Phông DejaVu Sans (`DejaVuSans.ttf`), dùng ghi lớp chữ ẩn trong PDF vì có đủ chữ tiếng Việt: giấy phép tự do dựa trên Bitstream Vera, cho phép dùng, sửa và phân phối lại kèm phần mềm (`GIAY-PHEP.txt`).
- Đã bỏ gói `flutter_tesseract_ocr` (lý do kỹ thuật: không dựng được với AGP 9), không phải vì giấy phép ([[readme-ung-dung-flutter]]).

## Phông sửa chữ trong bản Android 0.4.0 (cập nhật 2026-10-30)
- `LiberationSerif-*.ttf`, `LiberationSans-*.ttf`, mỗi họ 4 kiểu (thường, đậm, nghiêng, đậm nghiêng): phông Liberation 2.1.5, giấy phép SIL Open Font License 1.1; cho phép dùng, nhúng và phân phối lại kèm phần mềm (`GIAY-PHEP.txt`; [[readme-ung-dung-flutter]]). 8 tệp trong `assets/phong/` đều ghi Version 2.1.5.
- Dùng để vẽ chữ mới khi sửa chữ trên ảnh trang; cùng kích thước chữ với Times New Roman, Arial nên chữ sửa khớp văn bản in bằng hai phông này (`GIAY-PHEP.txt`).
- Tệp phông lấy từ `C:\Windows\Fonts` của máy dựng (`NHAT-KY.md` dự án, 2026-10-30); `GIAY-PHEP.txt` ghi trang dự án `liberationfonts/liberation-fonts`.
- Times New Roman, Arial: không được phép đóng gói vào ứng dụng (`NHAT-KY.md` dự án, 2026-10-30).
- DejaVu Sans vẫn dùng cho lớp chữ ẩn của PDF; Liberation chỉ dùng vẽ chữ sửa ([[readme-ung-dung-flutter]]).

## Mô-đun OpenCV thêm ở bản Android 0.7.9 (2026-11-16)
- `features2d` (ORB, BFMatcher) và `flann` (bắt buộc đi kèm) được dựng thêm vào thư viện OpenCV của `opencv_dart`/`dartcv4` để dò trang chụp trùng; cùng giấy phép Apache 2.0 của OpenCV 4.x ([[ban-android-flutter]]).
