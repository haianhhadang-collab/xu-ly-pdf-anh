---
type: nguon
tep_goc: "..\ung-dung-flutter\README.md; ..\ung-dung-flutter\assets\phong\GIAY-PHEP.txt"
ngay_nap: 2026-10-29
ngay_cap_nhat: 2026-11-16
loai: tài liệu phần mềm
---
# README – Bản Android (Flutter)

> Cập nhật 2026-10-29: README đã viết lại cho bản 0.2.0 (thêm nhận dạng chữ, khử nhiễu, tự xoay, Bấm chụp, Xem nhanh). Bản nạp trước ứng với 0.1.0; các điểm khác được ghi ở mục cuối.
>
> Cập nhật 2026-10-30: README cho bản 0.4.0. Thêm mục **Sửa chữ trên trang**, tệp `sua_chu.dart`, `ve_chu.dart`, phông Liberation (8 tệp, SIL OFL), bộ `sua_chu_test.dart`. `GIAY-PHEP.txt` thêm dòng cho Liberation.
>
> Cập nhật 2026-10-30 (lần 2): README cho bản 0.5.0: Sửa chữ có hai cách, mặc định là **Sửa ký tự (giữ nguyên bản gốc)**; cách 0.4.0 đổi tên *Vẽ lại bằng phông*. Thêm `sua_ky_tu.dart`, bộ `sua_ky_tu_test.dart`; APK khoảng 96 MB. Xem mục cuối.

**Tóm tắt.** README của bản Android dựng bằng Flutter. Ứng dụng quét, làm sạch, nắn phẳng, nhận dạng chữ và xuất PDF; mọi xử lý chạy trên máy, không gửi tài liệu đi đâu. Giao diện theo bản thiết kế 5 màn hình trên canvas *Giao diện Xử lý PDF ảnh – Android*. Lõi xử lý chuyển từ nguyên mẫu Python `ung-dung/loi_xu_ly/` sang Dart + OpenCV (`opencv_dart`), không phải C++ như kế hoạch ban đầu ([[flutter-loi-cpp]]). Nhận dạng chữ dùng Tesseract 5.5.1 (Tesseract4Android) với dữ liệu `vie` ([[tesseract-ocr]]).

## Làm được gì
- **Chụp** ([[tu-dong-chup]]): hai chế độ chọn ngay trên màn camera.
  - *Tự chụp*: tự chụp khi trang đứng yên, rõ nét, đủ sáng; không chụp trùng khi chưa lật trang.
  - *Bấm chụp*: người dùng bấm nút tròn; ứng dụng vẫn vẽ khung trang và nhắc *Đủ rõ, bấm nút tròn để chụp*.
  - Lời nhắc *Đưa máy lại gần*, *Giữ yên*, *Bị lóa*; có đèn. Chế độ mở mặc định chọn trong Cài đặt.
- **Nhập**: ảnh từ thư viện; ảnh và PDF từ tệp (kể cả PDF tải từ Zalo, email).
- **Làm sạch** ([[lam-sach-giu-mau]]): giữ màu dấu, chữ ký; chế độ xám, đen trắng, không làm sạch. Ba thanh chỉnh: độ trắng nền, độ đậm chữ, **khử nhiễu**.
  - Tương phản chữ cao hơn bản PC (đường cong dốc gấp đôi); lọc trung vị 3×3 khử nhiễu hạt.
  - Xóa đốm bụi đứng riêng; khoảng "gần chữ" tính theo cỡ chữ đo được nên giữ dấu thanh, dấu câu.
- **Nắn phẳng, xoay** ([[nan-phang-va-xoay]]): tìm mép giấy, sửa phối cảnh về tỉ lệ A4, sửa nghiêng, xóa viền nền bàn; chế độ *Sách* tách trang đôi; kéo 4 góc. Sau khi xử lý, Tesseract đoán chiều chữ từng trang (chạy nền, khoảng 1 giây một trang). **Xoay toàn bộ**: theo chiều chữ, hoặc ép *Tất cả khổ dọc* / *Tất cả khổ ngang*; xoay giữ khung cắt tay.
- **Xem nhanh** cho hồ sơ nhiều trang: lưới ảnh trang cỡ Lớn / Vừa / Nhỏ, lọc *Cần xem*; trang có vấn đề có viền cam và nhãn (*Ngược chiều*, *Chữ nằm nghiêng 90°*, *Khổ ngang/Khổ dọc* khác đa số, *Chưa thấy mép giấy*, *Xử lý lỗi*); xoay trái, phải, sửa chiều ngay trên ô; *Sửa chiều tất cả*. Ô trang ở màn Các trang có dấu "!" ([[ban-android-flutter]]).
- **Nhận dạng chữ** ([[nhan-dang-va-sua-chu]]): nút *Văn bản* ở màn Chỉnh trang, nút nhận dạng cả hồ sơ ở màn Các trang; xem, chọn, chép, chia sẻ chữ. Kết quả lưu đệm theo từng ảnh trang, trang xử lý lại thì nhận dạng lại. Khi xuất: *Thêm lớp chữ* (PDF tìm kiếm, chép chữ được, phông DejaVu Sans nhúng phần chữ đã dùng) và *Xuất kèm văn bản .txt*.
- **Hồ sơ**: nhiều trang, sắp xếp, xoay, xóa trang; lưu trong máy, còn sau khi tắt ứng dụng.
- **Xuất PDF**: khổ A4, A5, Letter hoặc theo ảnh; chọn lề, chất lượng 300/200/150 dpi; lưu vào máy hoặc chia sẻ sang Zalo, email.
- **Đánh số trang** (thêm ở 0.3.0, cập nhật 2026-10-29): chọn trang đầu được đánh số bằng cách chạm ảnh trang; số đầu chỉnh được; lề trên/dưới; căn giữa/trái/phải/so le; ảnh trang hiện số để xem trước ([[ban-android-flutter]]).
- **Sửa chữ trên trang** (thêm ở 0.4.0, cập nhật 2026-10-30): nút *Sửa chữ* ở màn Chỉnh trang ([[nhan-dang-va-sua-chu]], [[ban-android-flutter]]).
  - Chữ gộp thành **khối**: mỗi đoạn (các dòng liền nhau cùng đoạn) hoặc dòng đứng riêng (tiêu đề) là một khối; khung mờ quanh từng khối; ảnh phóng to, kéo được.
  - Chạm khối là sửa tại chỗ: ô nhập phủ đúng vị trí, điền sẵn chữ máy đọc, theo phông, cỡ, màu, căn lề của khối; *Xong* để áp, *Hủy* để bỏ. Bàn phím hiện thì ảnh tự phóng, cuộn cho ô nhập hiện rõ.
  - Tự đoán phông trong 8 phông Liberation Serif / Sans × thường, đậm, nghiêng, đậm nghiêng (cùng kích thước chữ với Times New Roman / Arial); đoán cả cỡ, độ đậm nét, màu mực. Đổi phông được ở thanh dưới.
  - Cả khối dàn lại trong bề ngang cũ: ngắt dòng theo từ, giữ thụt đầu dòng, căn trái / giữa / đều hai bên / phải như cũ, cùng khoảng cách dòng. Dòng ngắt cứng (hai dòng quốc hiệu, mỗi câu một dòng) giữ xuống dòng.
  - Số dòng đổi thì phần trang bên dưới dời lên, xuống đúng số dòng chênh; tràn mép dưới vẫn làm và báo.
  - Khối có mực màu (con dấu, chữ ký, bút phê) bị khóa, viền cam, kèm lời báo không cho sửa để tránh làm sai lệch giấy tờ.
  - **Hoàn tác** từng lần sửa. Trang đã sửa mà xử lý lại (xoay, đổi khung, đổi làm sạch) thì hỏi trước, vì chỗ sửa sẽ mất.
  - PDF xuất từ hồ sơ có chỗ sửa ghi thuộc tính Subject *Đã chỉnh sửa nội dung bằng Xử lý PDF ảnh: n chỗ sửa chữ*.

**Chưa có (README 0.2.0, 0.3.0):** nắn trang cong, sửa chữ khớp font, nhận tệp chia sẻ trực tiếp từ Zalo (phải lưu tệp rồi bấm *Nhập ảnh, PDF*). Chưa thử trên điện thoại thật.

**Chưa có (README 0.4.0, cập nhật 2026-10-30):** nắn trang cong; sửa chữ trên trang có nền màu, chữ viết tay, phông ngoài Times / Arial; nhận tệp chia sẻ trực tiếp từ Zalo. Chưa thử trên điện thoại thật.

## Cấu trúc mã
- `lib/main.dart`, `giao_dien/mau.dart` (bảng màu); `du_lieu/kho.dart` (hồ sơ, trang, hàng đợi xử lý trong isolate, đoán chiều chạy nền, xoay trang, nhận dạng có đệm, gọi kênh Tesseract).
- `lib/loi/`: `anh.dart`, `lam_sach.dart` (tính năng 2, khử nhiễu `xoaDom`), `nan_phang.dart` (tính năng 3), `nhan_dang.dart` (đọc hOCR thành dòng, từ, vị trí, góc chữ), `tu_chup.dart` (`BoTuChup`, YUV → BGR), `quy_trinh.dart`, `xuat_pdf.dart` (ghi PDF, lớp chữ ẩn).
- `lib/man_hinh/`: các màn hình, thêm `xem_nhanh.dart` và `van_ban.dart`.
- Thêm ở 0.4.0: `lib/loi/sua_chu.dart` (gộp khối, đoán căn lề; đo nét mực, màu, mực màu; xóa chữ cũ, dời phần dưới, phủ chữ mới, ghi PNG; thuần Dart + OpenCV, chạy trong isolate); `lib/loi/ve_chu.dart` (đoán phông, cỡ, độ đậm; dàn chữ, vẽ bằng dart:ui, isolate chính); chế độ Sửa chữ nằm trong `lib/man_hinh/sua_trang.dart`. `assets/phong/` thêm Liberation Serif, Sans (8 tệp, SIL OFL).
- `android/app/libs/tesseract4android-5.5.1.aar` (Apache 2.0); `MainActivity.kt` mở kênh `xlpdf/nhan_dang`, chạy Tesseract, trả hOCR.
- `assets/tessdata/`: `vie.traineddata` (nhận dạng), `osd.traineddata` (đoán chiều). `assets/phong/`: `DejaVuSans.ttf`, `GIAY-PHEP.txt` ([[giay-phep-thu-vien]]).
- `GIAY-PHEP.txt` (gộp vào trang nguồn này): DejaVu Sans dùng giấy phép tự do dựa trên Bitstream Vera, được dùng, sửa, phân phối lại kèm phần mềm, có đủ chữ tiếng Việt; `vie.traineddata` lấy từ kho `tesseract-ocr/tessdata`, Apache 2.0. Tệp chưa có dòng cho `osd.traineddata` (bản nạp 2026-10-29).
- `GIAY-PHEP.txt` bản 2026-10-30: đã có dòng cho `osd.traineddata` (cùng kho tessdata, Apache 2.0). Thêm dòng `LiberationSerif-*.ttf`, `LiberationSans-*.ttf` (thường, đậm, nghiêng, đậm nghiêng): phông Liberation 2.1.5, SIL Open Font License 1.1, cho phép dùng, nhúng và phân phối lại kèm phần mềm; dùng để vẽ chữ mới khi sửa chữ, vì cùng kích thước chữ với Times New Roman, Arial ([[giay-phep-thu-vien]]). Đã đối chiếu: 8 tệp trong `assets/phong/` đều ghi Version 2.1.5.

## Ghi chú kỹ thuật
- Tesseract dùng OpenMP nhiều luồng chờ quay vòng, tranh CPU với luồng vẽ: trên máy ảo một trang mất 9–10 giây. `MainActivity` đặt `OMP_THREAD_LIMIT=1` trước khi nạp, còn khoảng 2,5 giây ([[tesseract-ocr]]).
- Không dùng `vie+eng` (mất dấu tiếng Việt); `vie` đọc được cả tiếng Anh.
- Gói `flutter_tesseract_ocr` không dựng được với AGP 9 (jcenter, AGP 7), nên gọi thẳng `.aar` qua kênh riêng.
- Sửa chữ (0.4.0):
  - ảnh trang đã sửa lưu thành tệp PNG mới (`sua_<trang>_<ảnh>_<mã>.png`): chỗ không sửa giữ nguyên từng điểm ảnh, sửa nhiều lần không mờ dần; tên mới nên đệm nhận dạng cũ tự hết hiệu lực. Tệp trước khi sửa giữ trong `suaChu` của JSON hồ sơ để hoàn tác;
  - chữ của ảnh mới dựng sẵn (khối sửa thay bằng các dòng vừa vẽ, phần dưới dời theo) rồi ghi vào đệm, nên không phải nhận dạng lại; lớp chữ PDF dùng luôn bản này;
  - module `photo` của OpenCV (có `inpaint`) bị loại khi dựng; trang kết quả đã làm sạch nền nên xóa chữ chỉ tô màu nền (trung vị điểm không phải mực quanh khối);
  - đoán phông: vẽ thử chữ cũ của dòng dài nhất bằng 8 phông ở cỡ khớp bề rộng nét mực, so hình nét (giao / hợp độ phủ, làm mờ nhẹ) và chiều cao; độ đậm: viền thêm cho số điểm mực đậm bằng chữ thật;
  - khối một dòng khi dài ra dùng khoảng cách dòng chung của trang (trung vị các đoạn nhiều dòng), không có thì 1,2 × cỡ chữ.

## Dựng APK
- Đường dẫn có chữ có dấu làm Gradle lỗi, nên mã đặt ở `D:\DevTools\src\xlpdf`; `ung-dung-flutter` trong dự án là junction tới đó.
- Dựng bằng `flutter build apk --release --target-platform android-arm64,android-x64` (JDK 17, Android SDK ở `D:/DevTools/Android`). APK khoảng 88 MB (arm64 cho điện thoại, x86_64 cho máy ảo); phần lớn là OpenCV, Flutter, Tesseract và 18 MB dữ liệu nhận dạng. Lần đầu biên dịch OpenCV từ mã nguồn, mất khoảng 10–20 phút.
- README 0.4.0 vẫn ghi APK khoảng 88 MB; `NHAT-KY.md` dự án ghi `apk/xu-ly-pdf-anh-0.4.0.apk` khoảng 96 MB.
- Bản thử ký bằng khóa debug; phát hành thật cần khóa ký riêng.

## Kiểm thử trên máy ảo
- `flutter test` gỡ ứng dụng sau mỗi lần chạy, nên dùng `integration_test/chay_kiem_thu.sh <bộ>.dart`: cài bản debug, đẩy `D:\DevTools\src\xlpdf_kiemthu` vào thư mục tài liệu của ứng dụng, rồi chạy ([[du-lieu-kiem-thu]], [[kiem-thu]]).
- Bốn bộ: `loi_test.dart` (tìm mép, xử lý trọn trang, tách trang đôi, tự động chụp, xuất PDF); `nhan_dang_test.dart` (đọc hOCR, Tesseract trên máy so với PC, PDF có lớp chữ); `lam_sach_test.dart` (độ đen chữ, đốm nhiễu, nền trắng, dấu đỏ, nhận dạng trên ảnh chụp tốt và kém); `chieu_test.dart` (đoán chiều 4 góc, trang ngược, Xoay toàn bộ, giữ khung cắt tay, ép khổ dọc).
- README 0.4.0 liệt kê 6 bộ: thêm `so_trang_test.dart` (quy tắc đánh số, căn so le; đo vị trí bằng `kiem_so_trang.py`) và `sua_chu_test.dart`: gộp khối, căn lề; đoán phông (Serif thường / đậm); sửa "Kính gửi" dài ra (đọc lại đúng, phần trên giữ nguyên từng điểm ảnh, phần dưới dời nguyên vẹn); tiêu đề vẫn ở giữa; đoạn thêm dòng không chồng chữ; khối có con dấu bị khóa; lưu, hoàn tác, ghi chú PDF, xử lý lại thì bỏ sửa. Ảnh trước, sau lấy ra `build/kiem_thu_ra/sc_*` ([[kiem-thu]]).

## Khác bản README nạp trước (0.1.0)
- Trước: "chưa có nhận dạng chữ, tự xoay 90°/180° theo hướng chữ"; nay đã có cả hai.
- Trước: dựng chỉ `--target-platform android-arm64`, kiểm thử chạy `flutter test integration_test/loi_test.dart` sau khi `adb push`; nay dựng thêm `android-x64` và chạy qua `chay_kiem_thu.sh`.
- Trước: một công tắc tự động chụp; nay bộ chọn *Tự chụp* / *Bấm chụp*.

## Khác bản README 0.3.0 (cập nhật 2026-10-30)
- Trước: "Chưa có: … sửa chữ khớp font"; nay có Sửa chữ theo khối, gõ tại chỗ, phông Liberation.
- Trước: `assets/phong/` chỉ có `DejaVuSans.ttf`; nay thêm 8 tệp Liberation.

## Bản 0.5.0: Sửa ký tự giữ nguyên bản gốc (cập nhật 2026-10-30)
- Nút *Sửa chữ* ở màn Chỉnh trang có hai cách, chọn ở đầu màn: **Sửa ký tự (giữ nguyên bản gốc)** (mặc định) và **Vẽ lại bằng phông** (cách 0.4.0, mất nét gốc) ([[sua-ky-tu]], [[nhan-dang-va-sua-chu]]).
- Sửa ký tự: chỉ thêm, bớt ký tự; ký tự không sửa giữ nguyên từng điểm ảnh (chỉ dời ngang khi có chèn, xóa phía trước). Chạm dòng: viền cam, con trỏ đỏ, ảnh tự phóng cho dòng cao khoảng 56 điểm. Thanh dưới: ← →, ⌫, ⌦, ô gõ + *Chèn*, *Hủy*, *Xong*; xem trước ngay, ảnh tự cuộn theo con trỏ.
- Ký tự chèn **chép nguyên hình** từ chính trang (cùng cỡ, nét, độ nhòe, đúng đường chân); không có thì lấy ở trang khác của hồ sơ (nhận dạng dần ở nền), cả hồ sơ không có mới vẽ bằng phông. Hai trường hợp sau có viền vàng; chạm giữ một ký tự trên trang để dùng làm mẫu.
- Dãy chấm dẫn mục lục tự co giãn để số trang đứng nguyên chỗ. Dòng dài quá lề phải thì nhắc; dòng có mực màu bị khóa. *Xong* ghi ảnh kết quả mới, *Hoàn tác* được; PDF ghi Subject *n chỗ sửa ký tự*.
- Kỹ thuật (README mục Sửa ký tự): thuật toán chuẩn là bản PC `sua_ky_tu.py`. Dòng chia thành mảnh; phóng ảnh tới cạnh ngắn khoảng 2480 px (tối đa ×3) chỉ để nhận dạng; dãy chấm tìm theo hình dạng; nối dài dòng theo nét mực khi Tesseract bỏ sót số trang; gộp dòng cùng hàng; loại mẫu cao dưới 55% cỡ dòng; đệm `kt_<ảnh>.json` có số phiên bản `banDocKyTu`; xem trước chỉ dựng lại dải dòng. Hai điểm README ghi "khác bản PC": bỏ khe cạnh dấu chấm khi tính khe chữ chuẩn; gỡ khung ký tự chồng nhau. (`NHAT-KY.md` dự án ghi hai lỗi này đã được sửa luôn ở bản PC, nên chữ "khác bản PC" trong README có thể đã cũ [cần xác minh].)
- Đã biết: bước làm sạch (xóa đốm bụi) có thể xóa bớt chấm dẫn nhỏ của mục lục chụp bằng máy (`mau5-muc-luc.png` nhập qua ứng dụng), khi đó số trang không tự neo mép phải.
- Hiệu năng trên máy ảo: nhận dạng khung ký tự trang công văn 1503×2126 (phóng ×1,65) khoảng 2,2 giây; chèn một ký tự khoảng 10 ms (`NHAT-KY.md` ghi khoảng 13 ms).
- Cấu trúc mã thêm `lib/loi/sua_ky_tu.dart` (đọc hOCR có khung ký tự, gộp, nối dòng, dãy chấm, chia mảnh, chọn mẫu, dựng lại dòng; chuyển từ `sua_ky_tu.py`); `MainActivity.kt` trả hOCR kèm khung ký tự.
- Kiểm thử: bảng README có 7 bộ, thêm `sua_ky_tu_test.dart` (công văn "ngày 15" → "ngày 20"; mục lục "156" → "15", chèn "các " trước "Mục tiêu"; mẫu trang khác, mẫu tay, vẽ bằng phông; dòng mực màu bị khóa; đệm, lưu, ghi chú PDF, hoàn tác; ảnh ra `build/kiem_thu_ra/sk_*`) ([[kiem-thu]]).
- Dựng APK: README nay ghi khoảng 96 MB (trước ghi 88 MB), khớp `NHAT-KY.md`.
- **Chưa có (README 0.5.0):** nắn trang cong; sửa ký tự trên dòng có mực màu (khóa có chủ ý); sửa chữ trên trang nền màu, chữ viết tay, phông ngoài Times / Arial; nhận tệp chia sẻ trực tiếp từ Zalo. Chưa thử trên điện thoại thật.

## Bản 0.7.9 (2026-11-16)
- **Báo nhòe ngay trên màn camera**: `kiemTraAnhChup` (`quy_trinh`) chạy trong isolate sau mỗi ảnh; `ManChup` hiện thanh báo và nút *Chụp lại* thay ảnh vừa rồi. Đo nhòe trên ảnh gốc bằng `doMoMep` / `laNhoeGoc` (`chat_luong`) ([[tu-dong-chup]], [[ban-android-flutter]]).
- **Trang chụp trùng**: `dacTrung` / `diemKhop` / `trangTrung` (`chat_luong`), `Kho._doTrung`, `TrangTL.trungVoi`; màn Xem nhanh có nút xóa trang trùng. OpenCV dựng thêm `features2d`, `flann` (pubspec `hooks`).
- Kiểm thử `integration_test/chat_luong_test.dart` ([[kiem-thu]]).

## Bản 0.7.8 (2026-11-15)
- **Báo trang nên chụp lại**: `lib/loi/chat_luong.dart` (`laNhoe`, `doTay`); `xuLyAnh` trả `KetQuaXuLy.canhBao`, lưu ở `TrangTL.canhBaoAnh`; màn Xem nhanh có nút *Chụp lại* (`ManChup(thayTrang:)`, `Kho.thayAnh`) chụp một ảnh thay trang đó, trang giữ nguyên chỗ ([[tu-dong-chup]], [[ban-android-flutter]]).
- Kiểm thử `integration_test/chat_luong_test.dart` ([[kiem-thu]]).

## Bản 0.7.7 (2026-11-15)
- **Tách cặp trang theo khe gáy**: `tachTrangDoi` cắt giữa khe gáy theo đường xiên (`kheGay`, `catTheoDuong` trong `lib/loi/nan_phang.dart`) ([[nan-phang-va-xoay]]).
- **Lề trang**: `catSatChu(le:, giuKho:)`, lề "Vừa" mặc định, trang ít chữ giữ khổ ([[nan-phang-va-xoay]]).
- **Chụp xong mới xử lý**: `Kho.batDauChup` / `ketThucChup` tạm dừng hàng đợi xử lý khi đang ở màn chụp (Cài đặt › Chụp xong mới xử lý); `Kho.xuLyLaiHoSo` + nút *Xử lý lại cả hồ sơ* ở màn Các trang ([[tu-dong-chup]]).
- Kiểm thử `integration_test/tach_trang_test.dart` ([[kiem-thu]], [[ho-so-15-11-sach-214-trang]]).

## Bản 0.7.6 (2026-11-15)
- **Nắn vuông khối chữ**: `nanLe` trong `lib/loi/nan_cong.dart` làm hai lề thẳng, vuông góc dòng chữ; cặp trang sách mở được xoay thẳng từng trang (`_xoayThang`); `lamPhang(noi: noiKhung)` nới khung tự tìm 2,5% để không cắt lẹm chữ ở mép trang cong, nền trong dải nới được xóa (`_xoaNenNoi`) ([[nan-phang-va-xoay]]).
- PDF cũ: nhập lại ở màn Hồ sơ để nắn lại.
- Kiểm thử `integration_test/le_khoi_test.dart` ([[kiem-thu]]). Mục **Chưa có** không đổi; README vẫn ghi APK khoảng 96 MB.

## Bản 0.7.5 (2026-11-14)
- **Sách mở, nửa cặp trang**: chụp sát mà một trang lọt ra ngoài khung thì `timTuGiac` nối thêm trang bên kia gáy tới biên ảnh (`_canhNoi`); tự chụp thấy khung chạm mép thì nhắc lùi máy ([[nan-phang-va-xoay]], [[tu-dong-chup]]).
- Kiểm thử: `integration_test/nua_trang_test.dart` trên ảnh `xlpdf_kiemthu/sach_mo`, tạo bằng `ung-dung/kiem_thu/tao_anh_sach_mo.py` ([[kiem-thu]], [[du-lieu-kiem-thu]]).
- Mục **Chưa có** vẫn ghi "Chưa thử trên điện thoại thật"; mục *Dựng APK* vẫn ghi khoảng 96 MB [cần xác minh].

## Bản 0.7.4 (2026-11-14)
- **Tự chụp**: đo rung theo độ dời (không phụ thuộc tương phản; xét cả từng ô để bắt tay đang vuốt trang); khung tìm mép trượt dưới 0,4 giây không làm đếm lại; nhận động tác lật trang để phân biệt cặp trang sách giống nhau; không chụp khi tay đặt trên trang (lời nhắc "Bỏ tay ra khỏi trang"); giữ yên Nhanh/Vừa/Chắc = 0,3/0,5/0,9 giây ([[tu-dong-chup]]).
- **Rung báo**: rung nhẹ khi bắt được trang, rung khi chụp; tắt ở Cài đặt › Rung báo; kênh `xlpdf/rung` trong `MainActivity.kt` ([[ban-android-flutter]]).
- Kiểm thử: thêm dòng `tu_chup_test.dart` chạy trên 688 khung hình video chụp thật (sách mở trên nền đen, `xlpdf_kiemthu/video`): chụp đủ 6 cặp trang đúng lúc, không chụp khi tay trên trang ([[kiem-thu]], [[du-lieu-kiem-thu]]).

## Bản 0.7.3 (2026-11-14)
- **Tự xoay đúng chiều**: ảnh chụp cầm máy ngang (dòng chữ dọc) được xoay về ngang ngay sau nắn phối cảnh (`lib/loi/chieu_chu.dart`); sau khi xử lý, Tesseract đoán chiều và kho tự lật một lần (đủ 12 từ, chưa sửa chữ). Người dùng tự xoay trang thì tắt tự xoay của trang đó (`TuyChon.tuXoay`) ([[nan-phang-va-xoay]]).
- **Cắt sát chữ** thêm: ngón tay màu da tô trắng kể cả khi đè lên chữ, vệt bóng cong, mẩu đen sát mép, đường gáy giữa hai trang; giữ tiêu đề cách xa thân bài ([[nan-phang-va-xoay]]).
- Kiểm thử: dòng `cat_chu_test.dart` nay chạy trên 8 + 11 trang sách chụp thật (`xlpdf_kiemthu/sach`, `sach2`), có nhận dòng chữ dọc ([[kiem-thu]], [[du-lieu-kiem-thu]]).
- Mục **Chưa có** không đổi; README vẫn ghi "Chưa thử trên điện thoại thật" [cần xác minh]; APK vẫn ghi khoảng 96 MB.

## Bản 0.7.2 (2026-11-14)
- **Cắt sát chữ** (nút *Cắt sát chữ* ở màn Chỉnh trang, bật sẵn; `lib/loi/cat_chu.dart`): bước cuối sau sửa nghiêng, cắt sát vùng chữ (giữ số trang, chú thích, dấu, chữ ký), chừa lề trắng nhỏ; xóa vết ngoài vùng chữ: dải nền tối, nêm đen ở gáy sách, góc đen, ngón tay giữ sách. Trang không còn đúng tỉ lệ A4; xuất A4 thì co giãn vừa trang ([[nan-phang-va-xoay]]).
- **Nắn trang cong**: ảnh sách mở hai trang thì tách ở gáy, nắn từng trang ([[nan-phang-va-xoay]]).
- Kiểm thử: bảng README thêm `cat_chu_test.dart` (cắt sát chữ, xóa vết, tìm gáy trên 8 trang sách chụp thật trong `xlpdf_kiemthu/sach`, so với bản Python; công văn mẫu giữ đủ dấu đỏ, chữ ký) ([[kiem-thu]]).
- Mục **Chưa có** không đổi so với 0.7.1; README vẫn ghi "Chưa thử trên điện thoại thật" [cần xác minh]; APK vẫn ghi khoảng 96 MB.

## Bản 0.7.1 (2026-11-14)
- **Chụp**: camera ở độ phân giải tối đa (không mở được thì 1080p); chạm khung xem trước để lấy nét; trước khi chụp lấy nét vào giữa khung và chờ xong; chụp xong đo độ mờ (`tiLeNet`, ngưỡng 0,55), mờ thì lấy nét lại và chụp lại một lần. Tự chụp dùng bộ tìm mép bản nhanh (ảnh 400 px), chỉ báo "lùi máy" khi cạnh hoặc góc trang nằm trên mép khung ([[tu-dong-chup]]).
- **Nhận dạng chữ** thành chức năng riêng: nút *Nhận dạng chữ* ở màn Các trang; xuất PDF không tự nhận dạng; từ màn này có *Lưu .txt* và *PDF có chữ* (lớp chữ ẩn); báo trang máy đọc kém dưới 70% ([[nhan-dang-va-sua-chu]]).

## Bản 0.7.0 (2026-11-14)
- Tự tìm mép giấy kiểu CamScanner (`lib/loi/tim_mep.dart`): gom tứ giác ứng viên từ cạnh Canny, vùng Otsu, phân cụm màu k-means, ghép đường thẳng Hough; chấm điểm theo độ bám mép từng cạnh, phần diện tích, phần "giống giấy"; giấy nằm trên giấy trắng khác hay bìa sổ thì chọn tứ giác trong; tinh chỉnh cạnh ở ảnh 1280 px ([[nan-phang-va-xoay]]).
- **Nắn trang cong** theo dòng chữ (`lib/loi/nan_cong.dart`, nút *Nắn trang cong* ở màn Chỉnh trang, bật sẵn); trang phẳng để nguyên ([[nan-phang-va-xoay]]).
- Kiểm thử `integration_test/mep_cong_test.dart`: tự chụp (trang ôm sát khung vẫn chụp, trang bị cắt thì báo lùi máy), đo ảnh mờ, tìm mép trên 17 ảnh tổng hợp khó (tạo bằng `ung-dung/kiem_thu/tao_anh_mep.py`), nắn cong ([[kiem-thu]]).
- **Chưa có (README 0.7.1):** nắn trang cong khi trang không có dòng chữ (ảnh, bảng), giãn ngang chữ co gần gáy sách; sửa ký tự trên dòng có mực màu (khóa có chủ ý); sửa chữ trên nền màu, chữ viết tay, phông ngoài Times / Arial; nhận tệp chia sẻ trực tiếp từ Zalo. README vẫn ghi "chưa thử trên điện thoại thật" dù người dùng đã chạy máy thật ngày 2026-11-14 [cần xác minh]. APK vẫn ghi khoảng 96 MB.

## Bản 0.6.0 (2026-10-30)
- Đổi phông, cỡ chữ đoạn bôi chọn khi sửa ký tự: chạm giữ rồi kéo trong dòng, hoặc nút Bôi chọn + ← →; thanh định dạng A− / cỡ (pt) / A+ (`dinhDangChon(tiLe:)`: phóng, thu chính nét gốc) và menu phông (`dinhDangChon(kieu: DinhDangVe(...))`: vẽ lại đoạn chọn bằng phông Liberation, màu mực, viền đậm đoán bằng `BoVeKyTu.doan`); chữ phóng to được vẽ ra ngoài dải dòng (`SuaDong.vungVe`) ([[sua-ky-tu]]).
- Kiểm thử: thêm trường hợp (i) trong `sua_ky_tu_test.dart` ([[kiem-thu]]).
- README vẫn ghi APK khoảng 96 MB; mục **Chưa có** không đổi.

## Bản 0.5.2 (2026-10-30)
- Gõ tiếng Việt khi sửa ký tự không lẫn phông, lẫn đậm nhạt: khung ký tự máy đọc nắn theo nét mực thật (`nanKhung`); chọn mẫu theo bề dày nét các chữ quanh chỗ chèn (`damQuanh`, đo riêng từng ký tự, đệm trong `kt_*.json`), loại mẫu dáng lạ; tô theo màu mực chỗ chèn; chữ có dấu thiếu thì ghép thân + dấu (`ghepDau`, bảng tách dấu sinh từ unicodedata); dấu rời ghép thành chữ dựng sẵn (`ghepDauRoi`) ([[sua-ky-tu]]).

## Bản 0.5.1 (2026-10-30)
- Sửa ký tự trên ảnh chụp có dòng nghiêng, dòng sát nhau: đường chân chữ là đường xiên đo riêng từng dòng; khi dời, chỉ nét mực của chính dòng bị xóa chỗ cũ (vá nền) rồi dán sang chỗ mới theo độ dốc của dòng; nét dòng trên, dòng dưới lọt vào cùng dải giữ nguyên (`netCuaDong`). Khung dòng, con trỏ vẽ nghiêng theo dòng ([[sua-ky-tu]]).
- README vẫn ghi APK khoảng 96 MB.

Liên quan: [[ban-android-flutter]], [[readme]].
