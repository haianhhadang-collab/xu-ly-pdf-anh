---
type: doi-tuong
loai: sản phẩm / mã
---
# Nguyên mẫu Windows (thư mục `ung-dung/`)

Nguyên mẫu chạy được bằng Python + OpenCV + [[tesseract-ocr]], làm trước để thử thuật toán rồi chuyển sang [[flutter-loi-cpp]] ([[readme]]).

## Mô-đun
| Tệp | Vai trò |
|---|---|
| `giao_dien.py` | Giao diện tkinter: mở, kéo thả, chụp camera, kéo 4 góc khung cắt, sắp xếp, xoay, xóa trang, xuất PDF, thư mục theo dõi |
| `tu_dong.py` | Xử lý theo lô, thư mục theo dõi |
| `loi_xu_ly/lam_sach.py` | [[lam-sach-giu-mau]] |
| `loi_xu_ly/nan_phang.py` | [[nan-phang-va-xoay]] |
| `loi_xu_ly/nhan_dang.py` | OCR ([[nhan-dang-va-sua-chu]]) |
| `loi_xu_ly/doc_ghi.py` | Đọc ảnh, PDF (PDFium); ghi PDF (reportlab, pypdf) |
| `loi_xu_ly/quy_trinh.py` | Ghép các bước |
| `loi_xu_ly/tu_chup.py` | [[tu-dong-chup]]; 2026-11-14: đo rung theo độ dời (khung và ô 4×4), chịu 0,4 giây khung lỗi lẻ, nhận lật trang, `ti_le_tay`, giữ yên 0,5 giây ([[readme]]) |
| `sua_pdf.py` | Cửa sổ Sửa PDF (thêm 2026-10-30): sửa trang, sửa chữ, thêm chữ, che, chèn ảnh ([[cua-so-sua-pdf]]) |
| `loi_xu_ly/sua_noi_dung.py` | Sửa nội dung trang: sửa chữ khớp phông, thêm chữ, che, tô sáng, chèn ảnh ([[nhan-dang-va-sua-chu]]) |
| `loi_xu_ly/tai_lieu_pdf.py` | Tài liệu để sửa: trang PDF gốc / ảnh / trắng; chèn, xóa, xoay, gộp, tách, lưu ([[cua-so-sua-pdf]]) |
| `sua_pdf_doi_tuong.py` | Lớp trộn của cửa sổ Sửa PDF (thêm 2026-10-30, lần 4): công cụ Chọn, dời, đổi cỡ đối tượng và vùng có sẵn; làm lại ([[doi-tuong-tren-trang]]) |
| `sua_pdf_trang.py` | Lớp trộn (thêm 2026-10-30, lần 4): kéo thả trang, menu chuột phải, chép / dán trang giữa các cửa sổ ([[thao-tac-trang]]) |
| `loi_xu_ly/doi_tuong.py` | Đối tượng chọn lại được, hình vẽ, tìm và dời vùng có sẵn trên bản scan (thêm 2026-10-30, lần 4) ([[doi-tuong-tren-trang]]) |
| `loi_xu_ly/chu_thich.py` | Chú thích không phá bản gốc → chú thích PDF chuẩn (thêm 2026-10-30, lần 4) ([[chu-thich-pdf]]) |
| `loi_xu_ly/chieu_chu.py` | Nhận trang có dòng chữ chạy dọc, xoay 90° sau nắn phối cảnh (thêm 2026-11-14) ([[nan-phang-va-xoay]]) |
| `loi_xu_ly/cat_chu.py` | Cắt sát chữ, xóa vết; 2026-11-14 thêm `xoa_da_tay` (ngón tay màu da), vệt bóng cong, đường gáy ([[nan-phang-va-xoay]]) |
| `kiem_thu/` | Ảnh mẫu và kiểm thử ([[kiem-thu]], [[du-lieu-kiem-thu]]) |

Nguồn: [[readme]].

## Cách chạy
- `cai-dat.bat` (một lần), rồi `chay-ung-dung.bat` ([[readme]]).
- Cập nhật 2026-10-30: nút *✏ Sửa PDF…* trên thanh công cụ mở cửa sổ Sửa PDF; `sua-pdf.bat` mở thẳng cửa sổ này, kéo PDF thả lên tệp .bat được ([[readme]], [[cua-so-sua-pdf]]).

## Quyết định thiết kế
- Dựng bằng Python vì máy không có Flutter và trình biên dịch C++, nhưng có Python 3.13, OpenCV, Tesseract (`vie`, `eng`, `osd`), pypdfium2, reportlab, pypdf, watchdog; lõi tách riêng để chuyển sang C++ (`NHAT-KY.md` dự án, 2026-10-29).
- Thư viện theo [[giay-phep-thu-vien]].

## Chưa làm
Nắn trang cong; sửa chữ khớp font; trình soạn thảo định dạng; bản Flutter; thử ảnh và camera thật (`CLAUDE.md` dự án).
- Cập nhật 2026-10-30: sửa chữ khớp font (hướng A) đã có trong [[cua-so-sua-pdf]]; còn chưa làm: nắn trang cong, trình soạn thảo định dạng, thử ảnh, PDF thật (`NHAT-KY.md` dự án, 2026-10-30). Bản Flutter đã có từ 2026-10-29 ([[ban-android-flutter]]).
- Cập nhật 2026-10-30 (lần 3): thêm mô-đun `loi_xu_ly/sua_ky_tu.py` ([[sua-ky-tu]]). Còn chưa làm: chọn vùng tùy ý làm mẫu ký tự, tự xuống dòng khi dòng dài quá lề (`NHAT-KY.md` dự án).
- Cập nhật 2026-10-30 (lần 4): tham khảo ONLYOFFICE DesktopEditors (AGPL-3.0, chỉ học cách làm) ([[onlyoffice-desktopeditors]]), thêm đối tượng chọn lại được, dời vùng có sẵn trên bản scan, vẽ hình ([[doi-tuong-tren-trang]]), chú thích PDF chuẩn ([[chu-thich-pdf]]), thao tác trang kiểu ONLYOFFICE ([[thao-tac-trang]]); `tai_lieu_pdf.py` thêm `_toa_do_pdf`, `di_chuyen`, `chep`, `dan`. Còn chưa làm, chưa kiểm: menu chuột phải chưa bấm tay; chưa đọc, sửa chú thích có sẵn trong PDF mở vào; đổi cỡ vùng scan có thể làm chữ nhòe; các tính năng này chưa có trên Android (`NHAT-KY.md` dự án, 2026-10-30).

## Nắn lại PDF có sẵn (2026-11-15)
- `nan_lai_pdf.py` / `nan-lai-pdf.bat`: chạy lại toàn bộ quy trình (xoay, nắn cong, nắn vuông khối chữ, làm sạch, cắt sát chữ) trên PDF đã có, ghi `<tên>_nan.pdf` cạnh tệp gốc; `--tach` tách cặp trang ([[nan-phang-va-xoay]]).

## Lề trang, tách gáy mới (2026-11-15)
- Cửa sổ chính có ô *Lề trang* (Sát chữ / Vừa / Giữ cả trang); `nan_lai_pdf.py --le=…`. Tách trang đôi cắt giữa khe gáy theo đường xiên ([[nan-phang-va-xoay]]).

## Báo trang nên chụp lại (2026-11-15)
- Ô thông tin trang ghi "NÊN CHỤP LẠI: chữ nhòe / tay che trang" (`chat_luong.py`) ([[kiem-thu]]).

## Báo nhòe ngay sau khi chụp, trang chụp trùng (2026-11-16)
- Cửa sổ camera: thanh báo "Ảnh vừa chụp: chữ nhòe…", nút "Chụp lại ảnh này (R)". Danh sách trang ghi "trùng?", ô thông tin ghi "CÓ THỂ CHỤP TRÙNG" ([[tu-dong-chup]], [[kiem-thu]]).
