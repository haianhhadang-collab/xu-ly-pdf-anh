# Nhật ký wiki

## [2026-10-29] ingest | Dựng wiki, nạp 8 tệp đầu tiên
- Dựng wiki theo mẫu chung (`.obsidian/app.json`, `CLAUDE.md`, `index.md`, `log.md`, `nguon/`, `chu-de/`, `doi-tuong/`).
- Đã nạp: `01-prompt-ke-hoach.md`, `02-ke-hoach-ung-dung.md`, `03-tu-dong-chup.md`, `README.md`, `YEU-CAU-NGUOI-DUNG.md`, `ung-dung/requirements.txt` (gộp vào [[readme]]), `ung-dung/kiem_thu/anh_mau/mau4.pdf`, `ung-dung/kiem_thu/ket_qua/mau-gop-co-lop-chu.pdf` (gộp vào [[du-lieu-kiem-thu]]). Tham khảo thêm `CLAUDE.md`, `NHAT-KY.md` của dự án.
- Đã tạo nguồn: [[readme]], [[ke-hoach-ung-dung]], [[prompt-ke-hoach]], [[dac-ta-tu-dong-chup]], [[yeu-cau-nguoi-dung]], [[du-lieu-kiem-thu]].
- Đã tạo chủ đề: [[lam-sach-giu-mau]], [[nan-phang-va-xoay]], [[tu-dong-chup]], [[nhan-dang-va-sua-chu]], [[giay-phep-thu-vien]], [[kiem-thu]].
- Đã tạo đối tượng: [[nguyen-mau-windows]], [[tesseract-ocr]], [[flutter-loi-cpp]].

## [2026-10-29] ingest | README bản Android Flutter, cập nhật README và yêu cầu
- Đã nạp: `ung-dung-flutter/README.md`, `README.md` (bản mới), `YEU-CAU-NGUOI-DUNG.md` (bản mới).
- Đã tạo: [[readme-ung-dung-flutter]], [[ban-android-flutter]].
- Đã sửa: [[readme]], [[yeu-cau-nguoi-dung]], [[flutter-loi-cpp]], `index.md`.

## [2026-10-29] update | Bản Android 0.2.0: nhận dạng chữ, khử nhiễu, tự xoay, Bấm chụp, Xem nhanh
- Đã nạp: `ung-dung-flutter/README.md` (viết lại), `ung-dung-flutter/assets/phong/GIAY-PHEP.txt` (gộp vào [[readme-ung-dung-flutter]]), `YEU-CAU-NGUOI-DUNG.md` (5 yêu cầu mới), dữ liệu `D:\DevTools\src\xlpdf_kiemthu\` (`mau4-chup-kem.jpg`, `mau1.hocr`, `mau1.txt`). Số liệu kiểm thử lấy từ `NHAT-KY.md` dự án, mục "Bản Android 0.2.0".
- Đã sửa nguồn: [[readme-ung-dung-flutter]], [[yeu-cau-nguoi-dung]], [[du-lieu-kiem-thu]].
- Đã sửa chủ đề: [[nhan-dang-va-sua-chu]], [[lam-sach-giu-mau]], [[nan-phang-va-xoay]], [[tu-dong-chup]], [[kiem-thu]], [[giay-phep-thu-vien]].
- Đã sửa đối tượng: [[ban-android-flutter]] (thêm mục màn Xem nhanh, không tạo trang riêng), [[tesseract-ocr]], [[flutter-loi-cpp]] (OCR đã có, qua Tesseract chứ không qua ONNX); `index.md` (trạng thái, mô tả trang).
- Ghi chú: "trùng 99,4%" là độ khớp với Tesseract PC, không phải độ đúng tuyệt đối; giấy phép `osd.traineddata` chưa ghi trong `GIAY-PHEP.txt` [cần xác minh].

## [2026-10-29] update | Bản Android 0.3.0: đánh số trang khi xuất PDF
- Đã nạp: yêu cầu mới trong `YEU-CAU-NGUOI-DUNG.md` (tự chèn số trang), README bản Android (mục Đánh số trang, bộ `so_trang_test.dart`), `NHAT-KY.md` dự án mục "Bản Android 0.3.0".
- Đã sửa: [[ban-android-flutter]] (phiên bản 0.3.0, mục Đánh số trang), [[readme-ung-dung-flutter]], [[yeu-cau-nguoi-dung]], [[kiem-thu]], [[giay-phep-thu-vien]] (gỡ `[cần xác minh]` về `osd.traineddata`: Apache 2.0, đã ghi vào `GIAY-PHEP.txt`); `index.md`.

## [2026-10-30] update | Nguyên mẫu PC: cửa sổ Sửa PDF
- Đã nạp: `README.md` (mục Sửa PDF, bảng tính năng dòng 5, Kiểm thử, Cấu trúc mã), `YEU-CAU-NGUOI-DUNG.md` (yêu cầu sửa PDF), `NHAT-KY.md` dự án mục "2026-10-30 · Nguyên mẫu PC: cửa sổ Sửa PDF". Tham khảo docstring `sua_noi_dung.py`, `tai_lieu_pdf.py`, `sua_pdf.py`, `kiem_thu_sua_pdf.py`.
- Đã tạo đối tượng: [[cua-so-sua-pdf]].
- Đã sửa nguồn: [[readme]], [[yeu-cau-nguoi-dung]].
- Đã sửa: [[nhan-dang-va-sua-chu]] (hướng A trên nguyên mẫu PC; giữ ghi chú trạng thái cũ), [[nguyen-mau-windows]], [[kiem-thu]], [[giay-phep-thu-vien]]; `index.md`.
- [cần xác minh]: điều khoản dùng phông Times New Roman, Arial (lấy từ `C:/Windows/Fonts/`) khi chuyển sang bản phân phối.

## [2026-10-30] update | Sửa chữ theo khối, gõ tại chỗ (nguyên mẫu PC; bản Android 0.4.0)
- Đã nạp: `NHAT-KY.md` dự án mục "2026-10-30 · Sửa chữ theo khối, gõ ngay trên trang"; `README.md` (mục Sửa PDF, bảng tính năng dòng 5, APK 0.4.0); `ung-dung-flutter/README.md` (bản 0.4.0, mục Sửa chữ, `sua_chu_test.dart`); `YEU-CAU-NGUOI-DUNG.md` (dòng 2026-10-30 về sửa theo khối); `ung-dung-flutter/assets/phong/GIAY-PHEP.txt` (thêm Liberation, SIL OFL).
- Đã sửa nguồn: [[readme]], [[readme-ung-dung-flutter]], [[yeu-cau-nguoi-dung]].
- Đã sửa chủ đề: [[nhan-dang-va-sua-chu]] (mục mới sửa theo khối cho PC và Android; giữ mục sửa theo từ), [[kiem-thu]] (mục 1b của `kiem_thu_sua_pdf.py`, bộ `sua_chu_test.dart`), [[giay-phep-thu-vien]] (phông Liberation).
- Đã sửa đối tượng: [[cua-so-sua-pdf]], [[ban-android-flutter]] (phiên bản 0.4.0, mục Sửa chữ); `index.md`.
- Gỡ `[cần xác minh]` về phông Windows khi phân phối: Android đóng gói Liberation thay Times New Roman, Arial; nguyên mẫu PC vẫn dùng phông của chính máy. Đã đối chiếu 8 tệp Liberation đều là bản 2.1.5.
- Ghi chú: README Android vẫn ghi APK khoảng 88 MB, NHAT-KY ghi 0.4.0 khoảng 96 MB; đã ghi cả hai.

## [2026-10-30] update | Sửa ký tự giữ nguyên bản gốc (nguyên mẫu PC)
- Đã nạp: `README.md` (dòng 5, mục Sửa PDF, cấu trúc mã), `YEU-CAU-NGUOI-DUNG.md` (yêu cầu thay sửa theo khối; mục Không được làm), `NHAT-KY.md` dự án mục "Sửa ký tự giữ nguyên bản gốc"; 5 PDF `ung-dung/kiem_thu/ket_qua/sua-*.pdf` (đầu ra tạm của kiểm thử, chỉ ghi vào [[du-lieu-kiem-thu]]).
- Bỏ qua (đã nạp ở lượt trước, không có nội dung mới): `ung-dung-flutter/README.md`, `ung-dung-flutter/assets/phong/GIAY-PHEP.txt`.
- Đã tạo đối tượng: [[sua-ky-tu]].
- Đã sửa: [[nhan-dang-va-sua-chu]], [[cua-so-sua-pdf]], [[nguyen-mau-windows]], [[kiem-thu]], [[readme]], [[yeu-cau-nguoi-dung]], [[du-lieu-kiem-thu]]; `index.md`.
- [cần xác minh]: tiêu đề mục nhật ký ghi "(nguyên mẫu PC; bản Android)" nhưng nội dung chỉ tả bản PC.

## [2026-10-30] ingest | Tham khảo ONLYOFFICE: đối tượng, vùng scan, chú thích, thao tác trang (nguyên mẫu PC)
- Đã nạp: `NHAT-KY.md` dự án mục "2026-10-30 · Tham khảo ONLYOFFICE…"; `README.md` (mục Sửa PDF: kéo thả trang, Vẽ hình, Chọn/dời/đổi cỡ, vùng có sẵn trên bản scan, Chú thích, Ctrl+Y; mục Cấu trúc mã); `CLAUDE.md` dự án (dòng "Xong (2026-10-30): tham khảo ONLYOFFICE…"); `YEU-CAU-NGUOI-DUNG.md` (dòng ONLYOFFICE). Tham khảo docstring, tên hàm `loi_xu_ly/doi_tuong.py`, `loi_xu_ly/chu_thich.py`, `sua_pdf_doi_tuong.py`, `sua_pdf_trang.py`, các hàm `_toa_do_pdf`, `di_chuyen`, `chep`, `dan` của `tai_lieu_pdf.py`, mục 5–7 của `kiem_thu_sua_pdf.py`. Kho ONLYOFFICE (https://github.com/ONLYOFFICE/DesktopEditors, AGPL-3.0) chỉ ghi làm nguồn tham khảo ý tưởng, không tải về.
- Đã tạo nguồn: [[onlyoffice-desktopeditors]].
- Đã tạo đối tượng: [[doi-tuong-tren-trang]], [[chu-thich-pdf]], [[thao-tac-trang]].
- Đã sửa nguồn: [[readme]], [[yeu-cau-nguoi-dung]], [[du-lieu-kiem-thu]] (thêm `ct-*.pdf`, `tt-*.pdf`).
- Đã sửa chủ đề: [[kiem-thu]] (mục 5–7, phép thử 6 kiểu trang, bấm thử cửa sổ bằng script), [[nhan-dang-va-sua-chu]], [[nan-phang-va-xoay]], [[giay-phep-thu-vien]].
- Đã sửa đối tượng: [[cua-so-sua-pdf]], [[nguyen-mau-windows]], [[ban-android-flutter]]; `index.md`.
- Tệp hồ sơ thật của người dùng chỉ nhắc là bản sao để thử, không chép tên tệp, nội dung trang.
- Ghi rõ chưa làm: chưa đọc, sửa chú thích có sẵn trong PDF mở vào; menu chuột phải mới kiểm bằng lệnh; chưa có trên Android.
- [cần xác minh]: (1) quyền nhúng tập con Times New Roman vào PDF lưu ra khi phân phối; (2) chép / dán trang giữa hai lần chạy `sua-pdf.bat` riêng (bộ nhớ trang chỉ dùng chung trong một chương trình, suy từ mã); (3) Subject có thể ghi tên lớp `HinhVe`, `DoiVung` vì bảng tên thao tác trong `tom_tat_sua` chưa có hai loại này (suy từ mã); (4) phiên đã xem phần nào của ONLYOFFICE. Ghi chú: kiểm thử mục 6 chỉ thử 5 loại chú thích, chưa thử /Square, /Circle; NHAT-KY ghi trùng chỗ 100%, ngưỡng đạt trong script là trên 90%.

## [2026-10-30] update | Bản Android 0.5.0: sửa ký tự giữ nguyên bản gốc; sửa hai lỗi ở bản PC
- Đã nạp: `NHAT-KY.md` dự án (mục "Sửa ký tự giữ nguyên bản gốc", phần Android 0.5.0), `README.md` (mục Cài bản Android), `CLAUDE.md` dự án.
- Đã sửa: [[sua-ky-tu]] (bổ sung hai lỗi sửa ở cả hai bản; gỡ điểm [cần xác minh] về phần Android), [[ban-android-flutter]] (phiên bản 0.5.0, mục Sửa ký tự), [[doi-tuong-tren-trang]] (Subject ghi "vẽ hình", "dời, xóa vùng", đã chạy thử).

## [2026-10-30] update | Lượt quét tự động: README bản Android 0.5.0
- Đã nạp: `ung-dung-flutter/README.md` (bản 0.5.0: mục Sửa ký tự giữ nguyên bản gốc, Vẽ lại bằng phông, `sua_ky_tu.dart`, bộ `sua_ky_tu_test.dart`, APK khoảng 96 MB, mục Chưa có); `README.md` (mục Cài bản Android trỏ APK 0.5.0).
- Bỏ qua (đã nạp ở lượt trước, không có nội dung mới): `YEU-CAU-NGUOI-DUNG.md`; 9 PDF `ung-dung/kiem_thu/ket_qua/sua-*.pdf`, `ct-*.pdf`, `tt-*.pdf` (đầu ra tạm của kiểm thử, chạy lại lúc 09:28, đã có trong [[du-lieu-kiem-thu]]).
- Đã sửa nguồn: [[readme-ung-dung-flutter]] (mục mới Bản 0.5.0), [[readme]]; `index.md`.
- [cần xác minh]: (1) README dự án dòng đầu vẫn ghi APK 0.4.0 là bản mới nhất; (2) README Android vẫn ghi hai điểm "khác bản PC" mà `NHAT-KY.md` nói đã sửa luôn ở bản PC; (3) thời gian chèn một ký tự: README 10 ms, NHAT-KY 13 ms.

## [2026-10-30] lint | Lượt quét tự động: README không có nội dung mới
- Bỏ qua: `README.md` (sửa lúc 09:30, đã nạp ở lượt 10:04 "README bản Android 0.5.0"; không có nội dung mới). Không sửa trang nào.

## [2026-10-30] update | Sửa ký tự trên dòng nghiêng: bản Android 0.5.1 và bản PC
- Đã nạp: `NHAT-KY.md` dự án (mục "Sửa ký tự trên dòng nghiêng"), `README.md`, `ung-dung-flutter/README.md`, `CLAUDE.md` dự án; góp ý của người dùng sau khi thử điện thoại thật (chữ sửa lệch dòng, chữ không sửa phải giữ nguyên).
- Đã sửa: [[sua-ky-tu]] (mục mới Dòng nghiêng, kết quả mục 1d), [[ban-android-flutter]] (phiên bản 0.5.1), [[yeu-cau-nguoi-dung]] (yêu cầu mới).

## [2026-10-30] update | Lượt quét tự động: README ghi bản 0.5.1; PDF kiểm thử chạy lại
- Đã nạp: `README.md` (mục Cài bản Android trỏ APK 0.5.1, dòng "Bản 0.5.1"), `ung-dung-flutter/README.md` (gạch đầu dòng 0.5.1, `netCuaDong`).
- Bỏ qua (đã nạp ở lượt "Sửa ký tự trên dòng nghiêng", không có nội dung mới): `YEU-CAU-NGUOI-DUNG.md`; 9 PDF `ung-dung/kiem_thu/ket_qua/sua-*.pdf`, `ct-*.pdf`, `tt-*.pdf` (đầu ra tạm của kiểm thử, chạy lại lúc 13:51–13:52, đã có trong [[du-lieu-kiem-thu]]).
- Đã sửa nguồn: [[readme]] (cập nhật lần 5), [[readme-ung-dung-flutter]] (mục Bản 0.5.1).

## [2026-10-30] update | Gõ tiếng Việt khi sửa ký tự: lỗi phông, đậm nhạt (Android 0.5.2, bản PC)
- Đã nạp: `NHAT-KY.md` dự án (mục "Gõ tiếng Việt khi sửa ký tự"), `README.md`, `ung-dung-flutter/README.md`, `CLAUDE.md` dự án; góp ý của người dùng (gõ tiếng Việt bị lỗi phông, lỗi đậm nhạt).
- Đã sửa: [[sua-ky-tu]] (mục mới Gõ tiếng Việt), [[ban-android-flutter]] (phiên bản 0.5.2), [[yeu-cau-nguoi-dung]] (yêu cầu mới).

## [2026-10-30] update | Lượt quét tự động: README ghi bản 0.5.2
- Đã nạp: `README.md` (mục Cài bản Android trỏ APK 0.5.2, dòng "Bản 0.5.2"), `ung-dung-flutter/README.md` (gạch đầu dòng 0.5.2: `nanKhung`, `damQuanh`, `ghepDau`, `ghepDauRoi`).
- Bỏ qua (đã nạp ở lượt "Gõ tiếng Việt khi sửa ký tự", không có nội dung mới): `YEU-CAU-NGUOI-DUNG.md`; `ung-dung/kiem_thu/ket_qua/tt-ra.pdf` (đầu ra tạm của kiểm thử, đã có trong [[du-lieu-kiem-thu]]).
- Đã sửa nguồn: [[readme]] (cập nhật lần 6), [[readme-ung-dung-flutter]] (mục Bản 0.5.2).

## [2026-10-30] update | Đổi phông, cỡ chữ đoạn bôi chọn (Android 0.6.0, PC)
- Nguồn: yêu cầu người dùng "thêm chức năng đổi font, cỡ chữ" (chọn phạm vi đoạn bôi chọn, cả PC và Android); `NHAT-KY.md`, `README.md`, `ung-dung-flutter/README.md`, `CLAUDE.md` dự án.
- Đã sửa: [[sua-ky-tu]] (mục Đổi phông, cỡ chữ đoạn bôi chọn), [[ban-android-flutter]] (bản 0.6.0), [[yeu-cau-nguoi-dung]], `index.md` (README 0.6.0).

## [2026-10-30] update | Lượt quét tự động: README ghi bản 0.6.0
- Đã nạp: `README.md` (danh sách thư mục, mục Cài bản Android trỏ APK 0.6.0; dòng "Bản 0.6.0"), `ung-dung-flutter/README.md` (gạch đầu dòng 0.6.0: `dinhDangChon`, `BoVeKyTu.doan`, `SuaDong.vungVe`, kiểm thử (i)).
- Bỏ qua (đã nạp ở lượt "Đổi phông, cỡ chữ đoạn bôi chọn", không có nội dung mới): `YEU-CAU-NGUOI-DUNG.md`; 9 PDF `ung-dung/kiem_thu/ket_qua/sua-*.pdf`, `ct-*.pdf`, `tt-*.pdf` (đầu ra tạm của kiểm thử, chạy lại lúc 17:33, đã có trong [[du-lieu-kiem-thu]]).
- Đã sửa nguồn: [[readme]] (cập nhật lần 7), [[readme-ung-dung-flutter]] (mục Bản 0.6.0). Hết [cần xác minh] về dòng danh sách thư mục ghi 0.4.0; thêm [cần xác minh] về bảng tính năng dòng 6.

## [2026-11-14] update | Lượt quét tự động: yêu cầu làm phẳng ảnh kiểu CamScanner
- Đã nạp: `YEU-CAU-NGUOI-DUNG.md` (yêu cầu mới 2026-11-14: sau khi chạy bản Android trên máy thật, ảnh chưa được làm phẳng; cần tự tìm mép, cắt, nắn phối cảnh, nắn trang cong, chỉnh 4 góc như CamScanner).
- Bỏ qua: `ung-dung/kiem_thu/ket_qua/mau-gop-co-lop-chu.pdf` (đầu ra kiểm thử sinh lại lúc 11:46, đã mô tả trong [[du-lieu-kiem-thu]]).
- Đã sửa: [[yeu-cau-nguoi-dung]], [[nan-phang-va-xoay]] (mục Góp ý sau khi chạy máy thật), `index.md`.


## [2026-11-14] ingest | Tìm mép kiểu CamScanner, nắn trang cong (Android 0.7.0, PC)
- Đã nạp: mục `NHAT-KY.md` 2026-11-14, README hai bản (mục tìm mép, nắn cong), bộ ảnh thử `ung-dung/kiem_thu/anh_mau_mep/` và các script đo.
- Đã sửa: [[nan-phang-va-xoay]], [[du-lieu-kiem-thu]], [[kiem-thu]], [[ban-android-flutter]], `index.md`.

## [2026-11-14] ingest | Góp ý chụp thật: ảnh mờ, tự chụp báo lùi máy, tách OCR (Android 0.7.1)
- Đã nạp: góp ý của người dùng kèm `Hồ sơ 14-11 13-23.pdf` (3 trang, ảnh ~1030×1430 điểm ảnh, ở Desktop người dùng, không chép vào dự án), mục `NHAT-KY.md` 2026-11-14, `YEU-CAU-NGUOI-DUNG.md`.
- Đã sửa: [[tu-dong-chup]], [[nhan-dang-va-sua-chu]], [[ban-android-flutter]], [[kiem-thu]].

## [2026-11-14] update | Lượt quét tự động: README ghi bản 0.7.0, 0.7.1
- Đã nạp: `README.md` (bảng tính năng dòng 3: tìm mép kiểu CamScanner, nắn trang cong), `ung-dung-flutter/README.md` (mục Chụp 0.7.1, tìm mép và nắn cong 0.7.0, OCR tách riêng, `mep_cong_test.dart`, mục Chưa có), `YEU-CAU-NGUOI-DUNG.md` (ba yêu cầu 2026-11-14: ảnh mờ, báo lùi máy, tách OCR).
- Bỏ qua: `ung-dung/kiem_thu/ket_qua/mau-gop-co-lop-chu.pdf` (đầu ra kiểm thử sinh lại lúc 12:31, đã có trong [[du-lieu-kiem-thu]]).
- Đã sửa: [[readme]] (cập nhật lần 8), [[readme-ung-dung-flutter]] (mục Bản 0.7.0, 0.7.1), [[yeu-cau-nguoi-dung]], `index.md`.

## [2026-11-14] ingest | Góp ý 0.7.1: cắt sát chữ, xóa vết đen (Android 0.7.2)
- Đã nạp: góp ý người dùng kèm `Hồ sơ 14-11 14-01.pdf` (8 trang sách, ở Desktop người dùng; ảnh trang chép vào bộ kiểm thử Android), mục `NHAT-KY.md` 2026-11-14, `YEU-CAU-NGUOI-DUNG.md`.
- Đã sửa: [[nan-phang-va-xoay]], [[du-lieu-kiem-thu]], [[kiem-thu]], [[ban-android-flutter]].

## [2026-11-14] update | Lượt quét tự động: README ghi bản 0.7.2
- Đã nạp: `ung-dung-flutter/README.md` (mục Cắt sát chữ 0.7.2, nắn cong sách mở tách ở gáy, dòng `cat_chu_test.dart` trong bảng kiểm thử), `YEU-CAU-NGUOI-DUNG.md` (yêu cầu 2026-11-14: cắt sát chữ, xóa vết đen).
- Bỏ qua: `ung-dung/kiem_thu/ket_qua/mau-gop-co-lop-chu.pdf` (đầu ra kiểm thử sinh lại lúc 14:14, đã có trong [[du-lieu-kiem-thu]]).
- Đã sửa: [[readme-ung-dung-flutter]] (mục Bản 0.7.2), [[yeu-cau-nguoi-dung]], `index.md`.

## [2026-11-14] update | Lượt quét tự động: không có nội dung mới
- Bỏ qua: `ung-dung-flutter/README.md` (sửa lúc 14:39; nội dung 0.7.2, `cat_chu_test.dart`, mục Chưa có đã có trong [[readme-ung-dung-flutter]]); 10 PDF `ung-dung/kiem_thu/ket_qua/` (`mau-gop-co-lop-chu.pdf`, `sua-*.pdf`, `ct-*.pdf`, `tt-*.pdf`: đầu ra tạm của kiểm thử, sinh lại lúc 17:58–18:01, đã có trong [[du-lieu-kiem-thu]]).
- Không sửa trang nào.

## [2026-11-14] ingest | Ảnh chụp thật lần hai (11 trang, chụp bằng 0.7.2): tự xoay, xóa ngón tay (Android 0.7.3)
- Đã nạp: `mới.pdf` người dùng gửi qua Zalo (ảnh trang chép vào bộ kiểm thử Android `sach2`), mục `NHAT-KY.md` 2026-11-14.
- Đã sửa: [[nan-phang-va-xoay]], [[du-lieu-kiem-thu]], [[kiem-thu]], [[ban-android-flutter]].

## [2026-11-14] update | Lượt quét tự động: README ghi bản 0.7.3
- Đã nạp: `ung-dung-flutter/README.md` (mục Tự xoay đúng chiều 0.7.3, Cắt sát chữ 0.7.3, dòng `cat_chu_test.dart` thêm 11 trang `sach2`), `README.md` (mục Tự xoay ảnh chụp cầm máy ngang, xóa ngón tay của nguyên mẫu PC).
- Đã sửa: [[readme-ung-dung-flutter]] (mục Bản 0.7.3), [[readme]] (cập nhật lần 9), [[nan-phang-va-xoay]], [[nguyen-mau-windows]] (thêm `chieu_chu.py`, `cat_chu.py`), `index.md`.

## [2026-11-14] ingest | Video và PDF tự chụp sách trên nền đen (bản 0.7.3) → tự chụp nhanh, rung báo (Android 0.7.4)
- Đã nạp: `Hồ sơ 14-11 20-26.pdf`, video quay màn hình (khung hình chép vào bộ kiểm thử `video`), mục `NHAT-KY.md` 2026-11-14, `03-tu-dong-chup.md` (ngưỡng mới, mục Nhận động tác lật trang).
- Đã sửa: [[tu-dong-chup]], [[du-lieu-kiem-thu]], [[kiem-thu]], [[ban-android-flutter]].

## [2026-11-14] update | Lượt quét tự động: README, đặc tả tự chụp ghi bản 0.7.4
- Đã nạp: `README.md` (mục Tự chụp nhanh hơn, nhận lật trang, tay trên trang của nguyên mẫu PC), `ung-dung-flutter/README.md` (mục Tự chụp 0.7.4, rung báo, dòng `tu_chup_test.dart`), `03-tu-dong-chup.md` (ngưỡng đứng yên mới, thời gian giữ, rung báo, mục Nhận động tác lật trang, mục Tay trên trang, rung theo ô), `YEU-CAU-NGUOI-DUNG.md` (yêu cầu 2026-11-14: giảm thời gian chờ, báo rung).
- Đã sửa: [[readme]] (cập nhật lần 10), [[readme-ung-dung-flutter]] (mục Bản 0.7.4), [[dac-ta-tu-dong-chup]] (mục Cập nhật bản 0.7.4), [[yeu-cau-nguoi-dung]], [[nguyen-mau-windows]], `index.md`.

## [2026-11-14] ingest | PDF chụp sách bản 0.7.4 bị mất nửa cặp trang; bản 0.7.5
- Đã nạp: PDF người dùng gửi (15 trang, thiếu trang 123 và 125). 14 trang được lưu làm ảnh nguồn cho bộ thử sách mở mới.
- Đã sửa: [[nan-phang-va-xoay]] (mục Sách mở bị cắt mất một trang), [[kiem-thu]], [[du-lieu-kiem-thu]], [[ban-android-flutter]], `index.md`.

## [2026-11-15] update | Lượt quét tự động: README ghi bản 0.7.5
- Đã nạp: `ung-dung-flutter/README.md` (mục Sách mở, nửa cặp trang 0.7.5, `nua_trang_test.dart`), `README.md` (dòng 3 bảng tính năng: sách mở một trang lọt khung, nguyên mẫu PC), `YEU-CAU-NGUOI-DUNG.md` (yêu cầu 2026-11-14 sau bản 0.7.4: lấy đủ hai trang).
- Bỏ qua: `03-tu-dong-chup.md` (sửa lúc 21:42 ngày 14/11; nội dung 0.7.4 đã có trong [[dac-ta-tu-dong-chup]]), `ung-dung/kiem_thu/ket_qua/mau-gop-co-lop-chu.pdf` (đầu ra kiểm thử sinh lại, đã có trong [[du-lieu-kiem-thu]]).
- Đã sửa: [[readme-ung-dung-flutter]] (mục Bản 0.7.5), [[readme]] (cập nhật lần 11), [[yeu-cau-nguoi-dung]], `index.md`. Các trang chủ đề đã có nội dung 0.7.5 từ mục ingest trước.

## [2026-11-15] ingest | Lượt quét tự động: PDF kết quả `ket-qua/mới_nan.pdf`
- Đã nạp: `ket-qua/mới_nan.pdf` (11 trang, nguyên mẫu PC xuất lúc 11:55, không có lớp chữ).
- Bỏ qua: `README.md`, `ung-dung-flutter/README.md` (sửa lúc 23:45 ngày 14/11; nội dung 0.7.5 đã nạp ở mục trước), `ung-dung/kiem_thu/ket_qua/mau-gop-co-lop-chu.pdf` (đầu ra kiểm thử sinh lại lúc 11:41, đã có trong [[du-lieu-kiem-thu]]).
- Đã sửa: [[du-lieu-kiem-thu]] (mục PDF kết quả nguyên mẫu PC xử lý `mới.pdf`), `index.md`.

## [2026-11-15] ingest | Gửi lại PDF 0.7.2 (mới.pdf): nắn vuông khối chữ, không cắt lẹm; bản 0.7.6
- Đã nạp: `D:\Zalo Data\mới.pdf` (11 trang, đã có trong bộ thử `sach2`), kèm câu hỏi chỉnh méo, nắn vuông khối văn bản.
- Đã sửa: [[nan-phang-va-xoay]] (mục Nắn vuông khối chữ), [[kiem-thu]], [[ban-android-flutter]], [[nguyen-mau-windows]].

## [2026-11-15] update | Lượt quét tự động: README, yêu cầu ghi bản 0.7.6
- Đã nạp: `ung-dung-flutter/README.md` (mục Nắn vuông khối chữ 0.7.6, `le_khoi_test.dart`), `README.md` (dòng 3 bảng tính năng: nắn vuông khối chữ, `nan_lai_pdf.py`, `do_le.py`), `YEU-CAU-NGUOI-DUNG.md` (yêu cầu 2026-11-15: không cắt lẹm chữ, nắn vuông khối văn bản).
- Bỏ qua: `ket-qua/mới_nan.pdf` (sửa lúc 11:55, đã nạp ở mục ingest trước).
- Đã sửa: [[readme-ung-dung-flutter]] (mục Bản 0.7.6), [[readme]] (cập nhật lần 12), [[yeu-cau-nguoi-dung]], `index.md`. Các trang chủ đề, đối tượng đã có nội dung 0.7.6 từ mục ingest trước.

## [2026-11-15] lint | Lượt quét tự động (tối muộn): đầu ra kiểm thử sinh lại
- Bỏ qua `ung-dung/kiem_thu/ket_qua/mau-gop-co-lop-chu.pdf` (sinh lại lúc 20:01 khi chạy bộ kiểm thử): đầu ra kiểm thử, đã có trong [[du-lieu-kiem-thu]].
- Không sửa trang nào.

## [2026-11-15] ingest | Hồ sơ 214 trang sách (Hồ sơ 15-11 19-33.pdf), bản 0.7.7
- Tạo: [[ho-so-15-11-sach-214-trang]].
- Sửa: [[nan-phang-va-xoay]], [[kiem-thu]], [[ban-android-flutter]], [[nguyen-mau-windows]], [[tu-dong-chup]], [[yeu-cau-nguoi-dung]], `index.md`.

## [2026-11-15] update | Báo trang nhòe, tay che trang (bản 0.7.8)
- Sửa: [[ban-android-flutter]], [[tu-dong-chup]], [[kiem-thu]], [[ho-so-15-11-sach-214-trang]], [[nguyen-mau-windows]].

## [2026-11-15] update | Lượt quét tự động: README ghi bản 0.7.7, 0.7.8
- Đã nạp: `README.md` (mục cài trỏ APK 0.7.8; mục PC *Tách cặp trang theo khe gáy, lề trang*, *Báo trang nên chụp lại*), `ung-dung-flutter/README.md` (dòng 0.7.7, 0.7.8 ở *Làm được gì*), `YEU-CAU-NGUOI-DUNG.md` (yêu cầu tối 15/11 về lề, chụp xong mới xử lý).
- Bỏ qua: `ung-dung/kiem_thu/ket_qua/mau-gop-co-lop-chu.pdf` (đầu ra kiểm thử sinh lại lúc 21:35, đã có trong [[du-lieu-kiem-thu]]).
- Đã sửa: [[readme]] (cập nhật lần 13), [[readme-ung-dung-flutter]] (mục Bản 0.7.7, 0.7.8), [[yeu-cau-nguoi-dung]], `index.md`. Các trang chủ đề, đối tượng đã có nội dung 0.7.7, 0.7.8 từ mục ingest trước.

## [2026-11-16] update | Báo nhòe trên màn camera, trang chụp trùng (bản 0.7.9)
- Sửa: [[ban-android-flutter]], [[tu-dong-chup]], [[kiem-thu]], [[ho-so-15-11-sach-214-trang]], [[nguyen-mau-windows]], [[giay-phep-thu-vien]], [[yeu-cau-nguoi-dung]].

## [2026-11-16] update | Lượt quét tự động: README ghi bản 0.7.9
- Đã nạp: `README.md` (mục cài trỏ APK 0.7.9; mục PC *Báo nhòe ngay sau khi chụp, trang chụp trùng*), `ung-dung-flutter/README.md` (dòng 0.7.9 ở *Làm được gì*).
- Bỏ qua: `YEU-CAU-NGUOI-DUNG.md` (yêu cầu 16/11 đã có trong [[yeu-cau-nguoi-dung]] từ mục update trước), `ung-dung/kiem_thu/ket_qua/mau-gop-co-lop-chu.pdf` (đầu ra kiểm thử sinh lại lúc 08:17, đã có trong [[du-lieu-kiem-thu]]).
- Đã sửa: [[readme]] (cập nhật lần 14), [[readme-ung-dung-flutter]] (mục Bản 0.7.9), `index.md`. Các trang chủ đề, đối tượng đã có nội dung 0.7.9 từ mục update trước.

## [2026-11-16] lint | Lượt quét tự động (tối): không có nội dung mới
- Bỏ qua: `ung-dung-flutter/README.md` (sửa lúc 08:21, nội dung bản 0.7.9 đã nạp vào [[readme-ung-dung-flutter]] ở mục update trước).
- Trang sửa: không có.

## [2026-11-16] lint | Lượt quét tự động (tối muộn): không có nội dung mới
- Bỏ qua: `ung-dung-flutter/README.md` (vẫn bản sửa lúc 08:21, đã nạp vào [[readme-ung-dung-flutter]]; tệp hiện lại do mốc cắt micro giây, lượt này ghi mốc .843724).
- Trang sửa: không có.

## [2026-11-16] update | Đưa dự án lên GitHub
- Hai kho công khai `xu-ly-pdf-anh` (dự án, wiki, nguyên mẫu PC) và `xu-ly-pdf-anh-flutter` (mã Flutter, APK ở Releases); ảnh của người dùng không đưa lên ([[ban-android-flutter]], [[nguyen-mau-windows]]).
