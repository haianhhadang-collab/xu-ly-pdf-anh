---
type: doi-tuong
loai: mô-đun
---
# Bản Android (Flutter)

- Mã ở `D:\DevTools\src\xlpdf`, thư mục `ung-dung-flutter/` trong dự án là junction tới đó (tránh lỗi Gradle với đường dẫn có dấu) ([[readme-ung-dung-flutter]]).
- Lõi viết bằng Dart + `opencv_dart`, chuyển từ [[nguyen-mau-windows]]; xử lý trang chạy trong isolate ([[readme-ung-dung-flutter]]).
- Giao diện 5 màn hình theo thiết kế Claude Design, lưu ở `thiet-ke-giao-dien/` ([[readme]]); bản 0.2.0 thêm màn *Xem nhanh* và màn *Văn bản* ([[readme-ung-dung-flutter]]).

## Các phiên bản
- **0.1.0**: `apk/xu-ly-pdf-anh-0.1.0.apk` (64 MB, arm64 + x86_64), chạy Android 7 trở lên, ký bằng khóa thử nghiệm ([[readme]]; `NHAT-KY.md` dự án). Có: tự động chụp, nhập ảnh/PDF, làm sạch giữ màu, nắn phẳng phối cảnh, tách trang đôi, hồ sơ nhiều trang, xuất PDF và chia sẻ. Chưa có: OCR, tự xoay theo hướng chữ.
- **0.2.0** (2026-10-29): `apk/xu-ly-pdf-anh-0.2.0.apk`, khoảng 88 MB, arm64 + x86_64; nặng hơn vì có Tesseract và 18 MB dữ liệu nhận dạng (`NHAT-KY.md` dự án; [[readme-ung-dung-flutter]]). Thêm:
  - nhận dạng chữ, lớp chữ PDF, xuất .txt ([[nhan-dang-va-sua-chu]], [[tesseract-ocr]]);
  - khử nhiễu, tương phản cao hơn bản PC ([[lam-sach-giu-mau]]);
  - đoán chiều chữ và *Xoay toàn bộ* ([[nan-phang-va-xoay]]);
  - bộ chọn *Tự chụp* / *Bấm chụp* ([[tu-dong-chup]]);
  - màn *Xem nhanh* (dưới đây).
- **0.3.0** (2026-10-29): `apk/xu-ly-pdf-anh-0.3.0.apk`. Thêm *Đánh số trang* khi xuất PDF (dưới đây) (`NHAT-KY.md` dự án; [[readme-ung-dung-flutter]]).
- **0.4.0** (2026-10-30): `apk/xu-ly-pdf-anh-0.4.0.apk`, khoảng 96 MB (`NHAT-KY.md` dự án). Android 7 trở lên, 64-bit; cài đè được, giữ hồ sơ cũ ([[readme]]). Thêm chế độ *Sửa chữ* ở màn Chỉnh trang (dưới đây). Mã mới: `lib/loi/sua_chu.dart`, `lib/loi/ve_chu.dart` ([[readme-ung-dung-flutter]]).
- **0.5.0** (2026-10-30): `apk/xu-ly-pdf-anh-0.5.0.apk`, khoảng 96 MB. *Sửa ký tự (giữ nguyên bản gốc)* thành cách sửa chữ mặc định, chuyển từ bản PC ([[sua-ky-tu]]); cách 0.4.0 đổi tên *Vẽ lại bằng phông* ([[readme]], `NHAT-KY.md` dự án).
- **0.6.0** (2026-10-30): `apk/xu-ly-pdf-anh-0.6.0.apk`. Đổi phông, cỡ chữ đoạn bôi chọn khi sửa ký tự: thanh A− / cỡ / A+ (phóng, thu nét gốc) và menu 8 phông Liberation (vẽ lại riêng đoạn chọn) ([[sua-ky-tu]], mục Đổi phông, cỡ chữ; `NHAT-KY.md` dự án). `sua_ky_tu_test.dart` (i), 10/10.
- **0.5.2** (2026-10-30): `apk/xu-ly-pdf-anh-0.5.2.apk`. Gõ tiếng Việt khi sửa ký tự không lẫn phông, đậm nhạt: nắn khung ký tự, chọn mẫu theo độ đậm quanh chỗ chèn, tô màu mực, ghép dấu ([[sua-ky-tu]]; `NHAT-KY.md` dự án). `sua_ky_tu_test.dart` (h), 9/9.
- **0.5.1** (2026-10-30): `apk/xu-ly-pdf-anh-0.5.1.apk`. Sửa ký tự trên ảnh chụp có dòng nghiêng, dòng sát nhau: chữ sửa không lệch dòng, dòng bên cạnh giữ nguyên ([[sua-ky-tu]], mục Dòng nghiêng; `NHAT-KY.md` dự án).

## Màn Xem nhanh (0.2.0)
Đáp ứng yêu cầu xem trước hồ sơ lớn để thấy nhanh trang lệch, sai chiều ([[yeu-cau-nguoi-dung]]). Mã: `lib/man_hinh/xem_nhanh.dart` ([[readme-ung-dung-flutter]]).
- Lưới ảnh trang, cỡ ô Lớn / Vừa / Nhỏ; bộ lọc *Cần xem*.
- Trang có vấn đề có viền cam và nhãn: *Ngược chiều*, *Chữ nằm nghiêng 90°*, *Khổ ngang* / *Khổ dọc* (khác đa số trang), *Chưa thấy mép giấy*, *Xử lý lỗi*. Ô trang ở màn Các trang cũng có dấu "!".
- Xoay trái, phải, sửa chiều ngay trên ô; *Sửa chiều tất cả* một lần bấm.
- Nhãn chiều dựa vào kết quả đoán chiều chạy nền của Tesseract ([[nan-phang-va-xoay]]); trang ít chữ không đoán được chiều (`NHAT-KY.md` dự án).
- Đã bấm thử trên máy ảo: 4 ảnh (2 sai chiều) → màn Các trang báo 2 trang cần xem → Xem nhanh → *Sửa chiều tất cả* → cả 4 trang đứng thẳng ([[kiem-thu]]).

## Đánh số trang (0.3.0)
Đáp ứng yêu cầu tự chèn số trang: người dùng xác định trang đầu được đánh số, chọn vị trí và căn ([[yeu-cau-nguoi-dung]]). Mã: `DanhSo` trong `lib/loi/xuat_pdf.dart`, khối `lib/man_hinh/danh_so.dart` ở màn Xuất ([[readme-ung-dung-flutter]]).
- Chạm ảnh trang trong dải ảnh để chọn trang đầu tiên được đánh số; các trang trước để trống (vd. bỏ trang bìa). Mỗi ảnh hiện số sẽ in ở đúng chỗ (xem trước).
- Số in trên trang bắt đầu: mặc định bằng thứ tự trang (chọn trang 2 in số 2), chỉnh được, có nút *Bắt đầu từ 1*.
- Vị trí: lề trên, lề dưới. Căn: giữa, trái, phải, so le (*chẵn trái, lẻ phải* hoặc *chẵn phải, lẻ trái*, xét theo số in).
- Số phông Times cỡ 13, cách mép giấy nửa lề (ít nhất 8 mm); căn trái, phải theo mép vùng nội dung (ít nhất 20 mm). Lề nhỏ thì số in đè lên phần trắng của ảnh trang.
- Vị trí, căn, so le lưu trong Cài đặt; trang bắt đầu, số đầu lưu theo hồ sơ.
- Kiểm thử: 3 PDF 4 trang, đo bằng PDFium, 12/12 trang đúng, tâm số lệch dưới 2 pt; bấm thử trong ứng dụng đạt ([[kiem-thu]]).
- Chưa có: chọn phông, cỡ, kiểu số ("Trang 2", "- 2 -"), số La Mã cho phần đầu (`NHAT-KY.md` dự án).

## Sửa chữ (0.4.0)
Đáp ứng yêu cầu sửa chữ theo khối, gõ ngay trên trang, cho cả APK ([[yeu-cau-nguoi-dung]]). Làm bởi một tác tử con chạy song song với bản PC (`NHAT-KY.md` dự án, 2026-10-30). Cách làm chi tiết: [[nhan-dang-va-sua-chu]].
- Khung từng khối (đoạn theo `ocr_par`, dòng đơn) trên ảnh phóng to được; khối có con dấu, chữ ký, bút phê viền cam và bị khóa ([[readme-ung-dung-flutter]]).
- Chạm khối → ô gõ phủ đúng chỗ, đúng phông, cỡ, màu, căn lề, điền sẵn chữ máy đọc. Bàn phím mở thì tự phóng, cuộn cho ô hiện rõ ([[readme-ung-dung-flutter]]).
- Thanh dưới: Hủy, chọn phông (8 phông Liberation hoặc tự đoán), Xong; có Hoàn tác từng lần sửa (`NHAT-KY.md` dự án, 2026-10-30).
- Dòng gợi ý liệt kê chữ máy đọc chưa chắc, vì cả khối được viết lại nên cần soát (`NHAT-KY.md` dự án, 2026-10-30).
- Áp sửa: xóa nét bằng màu nền (không có `inpaint`), dàn chữ bằng dart:ui, dời phần dưới khi số dòng đổi; lưu ảnh PNG mới, giữ ảnh cũ để hoàn tác; ghi chữ mới vào đệm nhận dạng ([[readme-ung-dung-flutter]]).
- Xử lý lại trang đã sửa (xoay, đổi khung, đổi làm sạch) thì hỏi xác nhận. PDF xuất có Subject "Đã chỉnh sửa nội dung…" ([[readme-ung-dung-flutter]]).
- Phông đóng gói: Liberation Serif, Liberation Sans × 4 kiểu, SIL OFL; Times New Roman, Arial không được phép đóng gói ([[giay-phep-thu-vien]]).
- Kiểm thử: `sua_chu_test.dart` 7/7; 5 bộ cũ vẫn đạt. Bấm thử trên máy ảo: vào Sửa chữ, chạm khối, sửa tại chỗ, Xong, Hoàn tác; ảnh `apk/anh-chup-may-ao/0.4.0-*.png` ([[kiem-thu]]).

## Sửa ký tự (0.5.0)
- Kênh nhận dạng (`MainActivity.kt`) thêm tham số `kyTu` để Tesseract trả khung từng ký tự (`hocr_char_boxes`); lõi `lib/loi/sua_ky_tu.dart` chuyển trọn thuật toán [[sua-ky-tu]] của bản PC; đệm khung ký tự riêng từng ảnh `kt_<ảnh>.json`; dòng sửa xong được dựng lại từ các mảnh nên sửa tiếp không cần nhận dạng lại; các trang khác nhận dạng dần ở nền để lấy mẫu (`NHAT-KY.md` dự án).
- Thao tác: chạm dòng đặt con trỏ đỏ, nút ← → ⌫ ⌦, ô gõ + *Chèn*, *Xong* / *Hủy*; ký tự chưa chắc viền vàng kèm dòng nhắc, chạm giữ một ký tự trên trang để chọn mẫu; dòng có mực màu bị khóa ([[readme]]).
- Kiểm thử: `sua_ky_tu_test.dart` 7/7 (chạy lại độc lập); nhận dạng khung ký tự một trang khoảng 2,2 s, chèn một ký tự khoảng 13 ms; ảnh `apk/anh-chup-may-ao/0.5.0-*.png` ([[kiem-thu]]).
- 0.5.1: người dùng thử 0.5.0 trên điện thoại thật với ảnh chụp nghiêng thấy chữ sửa lệch dòng, dòng bên cạnh bị nát; sửa bằng đường chân xiên và chỉ dời nét của chính dòng (`netCuaDong`); `sua_ky_tu_test.dart` thêm (g), 8/8 ([[kiem-thu]]).
- Chưa kiểm: điện thoại thật, bộ gõ tiếng Việt thật. Nhập ảnh mục lục qua ứng dụng thì bước làm sạch xóa bớt chấm dẫn nhỏ (lỗi có từ trước, chưa sửa).

## Quyết định kỹ thuật, sự cố đã gỡ (0.2.0)
- Bỏ gói `flutter_tesseract_ocr` (dùng jcenter, AGP 7, không dựng được với AGP 9); gọi thẳng `.aar` Tesseract4Android qua kênh `xlpdf/nhan_dang` ([[readme-ung-dung-flutter]]).
- OpenMP của Tesseract tranh CPU với luồng vẽ: một trang 9–10 giây trong ứng dụng; đặt `OMP_THREAD_LIMIT=1` còn khoảng 2,3–3 giây ([[tesseract-ocr]]; `NHAT-KY.md` dự án).
- Flutter đặt lại `abiFilters` nên APK lẫn thư viện armeabi-v7a của Tesseract (máy 32-bit cài được nhưng mở ra chết); loại bằng `packaging.jniLibs.excludes` (`NHAT-KY.md` dự án).
- Kiểm thử chạy qua `integration_test/chay_kiem_thu.sh`, 4 bộ ([[kiem-thu]]).

## Khác nguyên mẫu PC
- Trước (0.1.0): nguyên mẫu PC có OCR và tự xoay 90°/180°, bản Android chưa có ([[readme]], [[readme-ung-dung-flutter]]).
- Nay (0.2.0): Android đã có OCR và tự xoay; ngược lại nguyên mẫu PC **chưa** có khử nhiễu và đường cong tương phản mới (`NHAT-KY.md` dự án).
- 0.4.0 (2026-10-30): cả hai bản đều sửa chữ theo khối. Khác: Android xóa chữ bằng màu nền, PC bằng `cv2.inpaint`; Android dùng phông Liberation, PC dùng Times New Roman, Arial của máy; đoạn "Căn cứ…" Android nhận căn đều, PC nhận căn trái. Che, chèn ảnh, sửa trang PDF có sẵn vẫn chỉ có ở [[cua-so-sua-pdf]] (`NHAT-KY.md` dự án, 2026-10-30).

## Chưa làm, chưa kiểm
- Nắn trang cong, sửa chữ khớp font, nhận tệp chia sẻ trực tiếp từ Zalo ([[readme-ung-dung-flutter]]). Cập nhật 2026-10-30: sửa chữ đã có ở 0.4.0; còn chưa có sửa chữ trên nền màu, chữ viết tay, phông ngoài Times / Arial ([[readme-ung-dung-flutter]]).
- Sửa chữ chưa kiểm: điện thoại thật; adb không gõ được tiếng Việt nên bấm thử chỉ gõ thêm chữ không dấu; trang sách (2 ảnh), xóa trắng cả khối, nền màu, chữ viết tay (`NHAT-KY.md` dự án, 2026-10-30).
- Chưa chạy trên điện thoại thật; tốc độ nhận dạng thật chưa đo; ngưỡng khử nhiễu mới chỉnh trên ảnh tổng hợp (`NHAT-KY.md` dự án).
- APK vẫn ký bằng khóa debug ([[readme-ung-dung-flutter]]).
- Cập nhật 2026-10-30 (lần 4): các tính năng tham khảo ONLYOFFICE của nguyên mẫu PC (đối tượng chọn lại được, dời vùng scan, chú thích PDF chuẩn, thao tác trang kéo thả) **chưa có** trên Android ([[doi-tuong-tren-trang]], [[chu-thich-pdf]], [[thao-tac-trang]]; `CLAUDE.md` dự án).

Xem thêm: [[flutter-loi-cpp]].

## Bản 0.7.0 (2026-11-14)
- Tìm mép kiểu CamScanner (`lib/loi/tim_mep.dart`), nắn trang cong (`lib/loi/nan_cong.dart`), thẻ *Cắt, nắn phẳng* có kéo giữa cạnh và kính lúp, nút *Nắn trang cong* ([[nan-phang-va-xoay]]).
- Bài học `opencv_dart`: `Mat.data`/`f32`/`i32` là cửa sổ vào bộ nhớ Mat, Mat tạm có thể bị thu hồi khi đang đọc (SIGSEGV) nên phải chép ra (`u8Chep`, `f32Chep`, `i32Chep`); `morphologyEx`, `erode`, `dilate` mặc định viền 0, khác cv2, cần `borderType: BORDER_REPLICATE`.
- APK `apk/xu-ly-pdf-anh-0.7.0.apk`; ảnh máy ảo `apk/anh-chup-may-ao/0.7.0-*.png`.

## Bản 0.7.1 (2026-11-14)
- Chụp ở độ phân giải tối đa, lấy nét trước khi chụp, chạm để lấy nét, đo ảnh mờ rồi chụp lại ([[tu-dong-chup]]).
- Tự chụp chỉ báo lùi máy khi trang bị cắt ([[tu-dong-chup]]).
- OCR tách riêng: nút *Nhận dạng chữ*, xuất PDF không tự nhận dạng ([[nhan-dang-va-sua-chu]]).
- APK `apk/xu-ly-pdf-anh-0.7.1.apk`; ảnh máy ảo `apk/anh-chup-may-ao/0.7.1-*.png`.

## Bản 0.7.2 (2026-11-14)
- Cắt sát chữ, xóa vết (`lib/loi/cat_chu.dart`, nút *Cắt sát chữ*); nắn cong sách mở tách theo gáy; lưu hồ sơ xếp hàng tránh lỗi ghi đồng thời ([[nan-phang-va-xoay]]).

## Bản 0.7.3 (2026-11-14)
- Tự xoay ảnh chụp cầm máy ngang (`lib/loi/chieu_chu.dart`), tự lật theo Tesseract; cắt sát chữ xóa ngón tay, vệt bóng, đường gáy, giữ tiêu đề ([[nan-phang-va-xoay]]).

## Bản 0.7.4 (2026-11-14)
- Tự chụp nhanh, không đứng chờ: đo rung theo độ dời, chịu khung lỗi lẻ, nhận lật trang, nhận tay trên trang; giữ yên 0,3/0,5/0,9 giây; rung báo qua kênh `xlpdf/rung` (quyền VIBRATE), tắt ở Cài đặt ([[tu-dong-chup]]).

## Bản 0.7.5 (2026-11-14)
- Chụp sách không còn mất nửa cặp trang. Khi một trang lọt ra ngoài khung, bộ tìm mép nối thêm trang bên kia gáy tới biên ảnh; tự chụp nhắc lùi máy ([[nan-phang-va-xoay]]).
- Kiểm thử `integration_test/nua_trang_test.dart` ([[kiem-thu]]). APK `apk/xu-ly-pdf-anh-0.7.5.apk`.

## Bản 0.7.6 (2026-11-15)
- Nắn vuông khối chữ, xoay thẳng từng trang của cặp trang sách mở, nới khung khi nắn phẳng để không cắt lẹm chữ ([[nan-phang-va-xoay]]).
- Kiểm thử `integration_test/le_khoi_test.dart` ([[kiem-thu]]). APK `apk/xu-ly-pdf-anh-0.7.6.apk`.

## Bản 0.7.7 (2026-11-15)
- Tách cặp trang giữa khe gáy theo đường xiên; lề "Vừa" mặc định, trang ít chữ giữ khổ ([[nan-phang-va-xoay]]).
- **Chụp xong mới xử lý** (Cài đặt, bật sẵn): đang ở màn chụp chỉ lưu ảnh gốc, hàng đợi xử lý tạm dừng; rời màn chụp mới cắt, nắn, làm sạch. Tự chụp nhanh hơn vì máy dành cho camera ([[tu-dong-chup]]).
- **Xử lý lại cả hồ sơ** (nút ở màn Các trang): chạy lại mọi trang từ ảnh gốc theo cách mới, chọn lề; trang đã sửa chữ giữ nguyên.
- Cài đặt › Lề trang. Kiểm thử `integration_test/tach_trang_test.dart` ([[kiem-thu]]). APK `apk/xu-ly-pdf-anh-0.7.7.apk`. Nguồn góp ý: [[ho-so-15-11-sach-214-trang]].

## Bản 0.7.8 (2026-11-15)
- Báo trang nên chụp lại: chữ nhòe, tay che trang; nút Chụp lại ở màn Xem nhanh thay ảnh gốc của trang đó ([[tu-dong-chup]], [[kiem-thu]]). Căn cứ: trang 145, 146 của [[ho-so-15-11-sach-214-trang]]. APK `apk/xu-ly-pdf-anh-0.7.8.apk`.

## Bản 0.7.9 (2026-11-16)
- Báo nhòe, tay che ngay trên màn camera sau mỗi ảnh, nút Chụp lại thay ảnh vừa rồi; rung báo khi máy đã chụp xong (trước đây rung lúc bắt đầu lấy nét, người dùng lật trang sớm); báo trang chụp trùng ở Xem nhanh ([[tu-dong-chup]], [[kiem-thu]], [[ho-so-15-11-sach-214-trang]]). OpenCV dựng thêm `features2d`, `flann` ([[giay-phep-thu-vien]]). APK `apk/xu-ly-pdf-anh-0.7.9.apk`.
