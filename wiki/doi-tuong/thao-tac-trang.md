---
type: doi-tuong
loai: tính năng / mã
ngay_nap: 2026-10-30
---
# Thao tác trang kiểu ONLYOFFICE (nguyên mẫu PC)

Thêm vào danh sách ảnh trang bên trái của [[cua-so-sua-pdf]] ngày 2026-10-30 (lần 4), theo cách làm của ONLYOFFICE, không dùng mã của họ ([[onlyoffice-desktopeditors]]). Giao diện là lớp trộn `sua_pdf_trang.py`; phần lõi là các hàm `di_chuyen`, `chep`, `dan` của `loi_xu_ly/tai_lieu_pdf.py` ([[readme]]). Bổ sung cho các nút sửa trang đã có (xoay ⟲ ⟳, ▲ ▼, xóa, tách).

## Cách dùng
- **Kéo thả ảnh trang** để đổi thứ tự: vạch cam chỉ chỗ thả; kéo được cả nhóm trang đã chọn; kéo tới mép danh sách thì tự cuộn ([[readme]]; `NHAT-KY.md` dự án, 2026-10-30, mục "Tham khảo ONLYOFFICE").
- **Bấm chuột phải lên ảnh trang**: xoay (phải 90°, trái 90°, 180°); chèn trang trắng trước / sau (cùng khổ, cùng chiều với trang bên cạnh); chèn tệp PDF, ảnh trước / sau; nhân đôi; chép; cắt; dán trước / sau; lưu trang đã chọn ra tệp mới; xóa ([[readme]]; `sua_pdf_trang.py`).
- **Phím**: Ctrl+C / Ctrl+X / Ctrl+V chép, cắt, dán trang; Delete xóa trang ([[readme]]).
- **Chép, dán giữa hai cửa sổ Sửa PDF** (hai tệp): bộ nhớ trang dùng chung mọi cửa sổ Sửa PDF trong cùng chương trình (`sua_pdf_trang.py`). Suy từ mã: đây là biến trong bộ nhớ của một chương trình, nên hai lần chạy `sua-pdf.bat` riêng có lẽ không dán sang nhau được [cần xác minh bằng chạy thử].

## Hàm lõi (`tai_lieu_pdf.py`)
- `di_chuyen(chi_so, den)`: đưa các trang đã chọn (giữ thứ tự) tới trước trang ở vị trí `den`; trả vị trí mới.
- `chep(chi_so)`: bản sao độc lập của các trang, **kể cả thao tác sửa và chú thích**, để dán chỗ khác, tệp khác.
- `dan(cac_trang, vi_tri)`: mỗi lần dán tạo bản sao riêng, nên dán nhiều lần không dùng chung một trang.

Nguồn: docstring các hàm; `NHAT-KY.md` dự án.

## Giữ chất lượng
Trang dán, trang nhân đôi vẫn là trang PDF gốc nếu chưa sửa nội dung, nên khi lưu được chép nguyên như mọi trang chưa sửa ([[cua-so-sua-pdf]], quyết định "giữ chất lượng trang chưa sửa"). Kiểm thử mục 7 xác nhận luồng nội dung trang dán trùng với trang gốc ([[kiem-thu]]).

## Kiểm thử
- `kiem_thu_sua_pdf.py` mục 7 đạt: kéo trang 4, 5 lên trước trang 2 → thứ tự 1, 4, 5, 2, 3; kéo trang đầu xuống cuối; chép 2 trang, dán hai lần sang tài liệu khác (ra 9 trang); mỗi lần dán là trang riêng; trang dán chép nguyên chất lượng ([[kiem-thu]]).
- Bấm thử bằng script với hai cửa sổ: kéo trang 5 lên vị trí 2, chèn trang trắng, nhân đôi, chép 2 trang dán sang cửa sổ kia, lưu ra chép nguyên (`NHAT-KY.md` dự án, 2026-10-30).

## Chưa làm, chưa kiểm
- **Menu chuột phải mới kiểm bằng lệnh, chưa bấm tay** (`NHAT-KY.md` dự án, 2026-10-30).
- Chưa có trên bản Android ([[ban-android-flutter]]).

Liên quan: [[nan-phang-va-xoay]] (gộp nhiều tệp thành một PDF), [[doi-tuong-tren-trang]], [[chu-thich-pdf]].
