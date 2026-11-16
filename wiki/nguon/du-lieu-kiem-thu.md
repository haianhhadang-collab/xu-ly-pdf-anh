---
type: nguon
tep_goc: "..\\ung-dung\\kiem_thu\\anh_mau\\mau4.pdf; ..\\ung-dung\\kiem_thu\\ket_qua\\mau-gop-co-lop-chu.pdf; D:\\DevTools\\src\\xlpdf_kiemthu\\mau4-chup-kem.jpg; D:\\DevTools\\src\\xlpdf_kiemthu\\mau1.hocr; D:\\DevTools\\src\\xlpdf_kiemthu\\mau1.txt"
ngay_nap: 2026-10-29
ngay_cap_nhat: 2026-10-30
loai: dữ liệu kiểm thử
---
# Dữ liệu kiểm thử: ảnh mẫu, PDF mẫu và đáp án nhận dạng

**Tóm tắt.** Dữ liệu dùng để kiểm thử [[nguyen-mau-windows]] (thư mục `ung-dung/kiem_thu/`) và [[ban-android-flutter]] (thư mục `D:\DevTools\src\xlpdf_kiemthu`). Cập nhật 2026-10-29: thêm ảnh chụp kém `mau4-chup-kem.jpg` và đáp án nhận dạng `mau1.hocr`, `mau1.txt` cho bản Android.

## Nguyên mẫu PC (`ung-dung/kiem_thu/`)
- `anh_mau/mau4.pdf`: PDF 1 trang, chỉ có ảnh (không có lớp chữ), dùng làm đầu vào thử luồng đọc PDF. Ảnh mẫu khác cùng thư mục: `mau1-chup-nghieng.jpg`, `mau2-lon-nguoc.jpg`, `mau3-trang-doi.jpg`; `dap_an.json` ghi tọa độ 4 góc trang đúng của mẫu 1.
- `ket_qua/mau-gop-co-lop-chu.pdf`: PDF gộp 2 trang do nguyên mẫu xuất, có lớp chữ OCR. Trang 1 là công văn tổng hợp (quốc hiệu, "Công văn đề nghị số hóa tài liệu" gửi Thư viện Trường Đại học Hà Nội, đề nghị giữ nguyên màu con dấu). Lớp chữ đọc được tiếng Việt có dấu nhưng còn lỗi nhỏ (ví dụ "ĐÈ NGHỊ SÓ HÓA", "đóng dầu").

## Bản Android (`D:\DevTools\src\xlpdf_kiemthu`)
Script `integration_test/chay_kiem_thu.sh` đẩy cả thư mục này vào thư mục tài liệu của ứng dụng trên máy ảo trước khi chạy kiểm thử ([[readme-ung-dung-flutter]]). Thư mục gồm `mau1-chup-nghieng.jpg`, `mau3-trang-doi.jpg`, `dap_an.json`, thư mục `khung/`, và ba tệp mới:
- `mau4-chup-kem.jpg` (mới): ảnh **tổng hợp** từ mau1, giả ảnh chụp kém: chữ nhạt, nhiễu hạt, 2500 đốm bụi, nén JPEG chất lượng 65. Dùng trong `lam_sach_test.dart` để đo khử nhiễu. Không phải ảnh chụp thật (`NHAT-KY.md` dự án).
- `mau1.hocr`, `mau1.txt` (mới): kết quả `tesseract -l vie --psm 3` trên PC cho ảnh mau1 đã xử lý; dùng làm **đáp án** để so với Tesseract chạy trên máy ảo (`nhan_dang_test.dart`, `lam_sach_test.dart`). Lưu ý: đáp án là đầu ra của Tesseract PC, không phải chữ gõ tay, nên chính nó còn lỗi giống PDF kết quả ở trên ("ĐÈ NGHỊ SÓ HÓA", "con dầu"). Tỉ lệ "trùng 99,4%" vì vậy đo độ khớp với PC, không đo độ đúng tuyệt đối.

## Ba bộ kiểm thử mới dùng dữ liệu này (bản 0.2.0)
- `nhan_dang_test.dart`: đọc hOCR; Tesseract trên máy so với PC (trùng 99,4% ký tự); PDF có lớp chữ.
- `lam_sach_test.dart`: trên `mau4-chup-kem.jpg` đốm nhiễu 743 → 117, nhận dạng đúng 71% → 91,6%, trung vị độ sáng chữ 55 → 43; ảnh chụp tốt vẫn 99,4%; dấu đỏ giữ nguyên.
- `chieu_test.dart`: đoán chiều 4 góc 0°, 90°, 180°, 270° (khoảng 1,2 giây một trang); trang ngược → cảnh báo → Xoay toàn bộ.

Nguồn số liệu: `NHAT-KY.md` dự án, mục 2026-10-29 "Bản Android 0.2.0".

Liên quan: [[kiem-thu]], [[nhan-dang-va-sua-chu]], [[lam-sach-giu-mau]].

## PDF kết quả của `kiem_thu_sua_pdf.py` (nạp 2026-10-30)
Năm tệp trong `ung-dung/kiem_thu/ket_qua/`, do script kiểm thử sinh ra: `sua-nguon.pdf`, `sua-nguon-2.pdf` (PDF nguồn để gộp), `sua-ket-qua.pdf` (sau khi gộp, sửa trang), `sua-ket-qua-da-sua.pdf` (mở lại tệp đã sửa và sửa tiếp), `sua-tach.pdf` (tách trang). Là đầu ra tạm, được sinh lại mỗi lần chạy; không tóm tắt nội dung ([[kiem-thu]]).
- Cập nhật 2026-10-30 (lần 4): thêm `ct-nguon.pdf`, `ct-ra.pdf` (mục 6, chú thích PDF chuẩn) và `tt-nguon.pdf`, `tt-ra.pdf` (mục 7, thao tác trang); cũng là đầu ra tạm, sinh lại mỗi lần chạy ([[chu-thich-pdf]], [[thao-tac-trang]]).

## Bộ ảnh tìm mép, nắn cong (2026-11-14)
- `ung-dung/kiem_thu/tao_anh_mep.py` tạo `anh_mau_mep/` (17 ảnh 1500×2000 + `dap_an.json` 4 góc, độ cong): trang công văn tổng hợp chiếu qua máy ảnh lỗ kim, phẳng hoặc cong kiểu sách mở, trên nền gỗ, bàn trắng, lộn xộn (có bàn phím), vải hoa văn, tối; có ngón tay, bóng đổ, góc ra ngoài khung, giấy kín khung, giấy chồng giấy, sổ bìa tối, ảnh tối mờ. `python tao_anh_mep.py ngau_nhien N hạt` tạo `anh_mau_mep_nn/` ngẫu nhiên.
- `do_mep.py [nn] [cu]`: đo lệch góc (đạt khi < 1,2% đường chéo). `do_cong.py`: đo độ võng dòng chữ trước, sau khi nắn; ảnh trước/sau ở `ket_qua/nan-cong-*.jpg`.
- Bản chép cho Android: `D:\DevTools\src\xlpdf_kiemthu\mep\` (dùng trong `integration_test/mep_cong_test.dart`).
- Đây là ảnh tổng hợp, không thay được ảnh chụp thật ([[nan-phang-va-xoay]], [[kiem-thu]]).

## Trang sách chụp thật (2026-11-14)
- 8 ảnh trang sách mở hai trang (sách chính trị đã xuất bản, không có dữ liệu cá nhân), tách từ PDF người dùng gửi sau khi chụp bằng bản 0.7.1; chép vào `D:\DevTools\src\xlpdf_kiemthu\sach\goc0–7.png`, kèm `dap_an_python.json` (kích thước cắt, cột gáy theo bản Python). Dùng trong `integration_test/cat_chu_test.dart` ([[kiem-thu]]).

## Trang sách chụp cầm máy ngang (2026-11-14)
- 11 trang (bìa và trang trong của một sách chính trị đã xuất bản, không có dữ liệu cá nhân), ảnh kết quả bản 0.7.2 tách từ PDF người dùng gửi; chép nguyên (chữ chạy dọc) vào `D:\DevTools\src\xlpdf_kiemthu\sach2\doc0–10.jpg`, kèm `dap_an_python.json` (chữ dọc, cỡ ảnh cắt, cột gáy theo bản Python). Dùng trong `integration_test/cat_chu_test.dart` ([[kiem-thu]]).

## Video tự chụp sách trên nền đen (2026-11-14)
- Video quay màn hình lúc chụp bằng 0.7.3 (76 giây, 6 cặp trang một sách chính trị đã xuất bản, không có dữ liệu cá nhân): tách 688 khung vùng ảnh camera (452×610, còn khung màu và lời nhắc của ứng dụng vẽ đè, đã bỏ khung màn trắng lúc chụp) vào `D:\DevTools\src\xlpdf_kiemthu\video\`, kèm `thoi_gian.json` (thời điểm, khoảng chụp mong đợi của từng cặp trang, khoảng có tay trên trang). Dùng trong `integration_test/tu_chup_test.dart` ([[tu-dong-chup]], [[kiem-thu]]).

## Ảnh sách mở hai trang (2026-11-14)
- `ung-dung/kiem_thu/trang_sach/`: 14 trang sách lấy từ PDF người dùng gửi, chụp bằng bản 0.7.4 (trang 122–137). PDF này thiếu trang 123, 125 vì lỗi chỉ nhận nửa cặp trang.
- `ung-dung/kiem_thu/anh_sach_mo/` (tạo bằng `tao_anh_sach_mo.py`, có `dap_an.json`): 21 ảnh cặp trang tổng hợp. Bản sao cho Android ở `xlpdf_kiemthu/sach_mo`.
- Liên quan: [[kiem-thu]], [[nan-phang-va-xoay]].

## PDF kết quả nguyên mẫu PC xử lý `mới.pdf` (2026-11-15)
- `ket-qua/mới_nan.pdf` (thư mục `ket-qua/` ở gốc dự án, tạo lúc 11:55 ngày 15/11): 11 trang, do nguyên mẫu PC xuất (Creator "Xử lý PDF ảnh (nguyên mẫu)", ReportLab), tiêu đề `moi`. Số trang trùng với `mới.pdf` 11 trang chụp bằng bản 0.7.2 ([[nan-phang-va-xoay]]); hậu tố `_nan` gợi ý bản đã nắn phẳng [cần xác minh].
- Khổ trang: 3 trang dọc rộng 595 pt (cao 740–937 pt), 8 trang ngang rộng 842 pt (cao 559–622 pt). Không có lớp chữ OCR.
- `NHAT-KY.md` chưa ghi lượt xử lý này. Không tóm tắt nội dung ảnh trang.
