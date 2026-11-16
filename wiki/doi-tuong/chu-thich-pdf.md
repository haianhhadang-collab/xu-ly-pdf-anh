---
type: doi-tuong
loai: tính năng / mã
ngay_nap: 2026-10-30
---
# Chú thích PDF chuẩn, không phá bản gốc (nguyên mẫu PC)

Công cụ *Chú thích (không sửa bản gốc)* trong [[cua-so-sua-pdf]], thêm ngày 2026-10-30 (lần 4). Mã `loi_xu_ly/chu_thich.py`; cách làm tham khảo ONLYOFFICE, không dùng mã của họ ([[onlyoffice-desktopeditors]]).

## Loại chú thích
| Trong cửa sổ | Loại PDF | Cách đặt |
|---|---|---|
| Ghi chú | /Text | bấm chỗ đặt, gõ lời |
| Bút phê | /FreeText | kéo khung, gõ lời; chữ nghiêng màu đỏ hoặc theo *Màu chữ*, cỡ theo *Cỡ (pt)* |
| Tô sáng | /Highlight | kéo vùng |
| Chữ nhật, elip | /Square, /Circle | kéo vùng |
| Đường, mũi tên | /Line | kéo |
| Dấu "ĐÃ XEM" kèm ngày | /Stamp | bấm chỗ đặt |

Nguồn: [[readme]]; `NHAT-KY.md` dự án, 2026-10-30, mục "Tham khảo ONLYOFFICE"; docstring `chu_thich.py`.

- Chú thích nằm trong danh sách thao tác của trang: chọn, dời, xóa, hoàn tác như đối tượng khác ([[doi-tuong-tren-trang]]); bấm đúp ghi chú, bút phê để sửa lời ([[readme]]).
- Lưu ra, trình đọc PDF khác (Acrobat, Foxit, trình duyệt) hiện, ẩn, sửa, xóa được ([[readme]]).

## Hình hiển thị và xem trước
- Mỗi chú thích có hình hiển thị (/AP) vẽ bằng reportlab, nhúng tập con phông Times New Roman (đủ dấu tiếng Việt), rồi chuyển thành Form XObject trong tệp đang ghi (`_form`) (`NHAT-KY.md` dự án; `chu_thich.py`).
- Xem trước trên màn hình dựng **chính hình ấy** bằng PDFium rồi vẽ chồng lên ảnh trang (`phu_len`), nên thấy sao lưu vậy (`NHAT-KY.md` dự án).
- Ảnh hiện = ảnh đã sửa + chú thích vẽ chồng. Ảnh dùng để sửa ký tự, tìm vùng scan không có chú thích ([[sua-ky-tu]], [[doi-tuong-tren-trang]]).
- Không dùng MuPDF: vẽ bằng reportlab, dựng bằng PDFium, ghi bằng pypdf ([[giay-phep-thu-vien]]).

## Đổi điểm ảnh sang điểm PDF (`_toa_do_pdf` trong `tai_lieu_pdf.py`)
Thao tác trên trang tính bằng điểm ảnh của ảnh trang đang sửa (gốc ở góc trên trái, trục dọc đi xuống). Chú thích PDF cần điểm PDF trong hệ tọa độ của trang **chưa xoay** (gốc ở góc dưới trái). Hàm trả `(f, R, s)`: `f(u, v)` → `(x, y)`; `R` là góc /Rotate; `s` là số điểm PDF ứng với một điểm ảnh (docstring `_toa_do_pdf`). Có ba trường hợp (`NHAT-KY.md` dự án, 2026-10-30):

1. **Ảnh scan đặt đúng chỗ cũ** (trang PDF chỉ gồm một ảnh, sửa trên ảnh gốc): lấy chỗ đặt ảnh (trái, dưới, rộng, cao) trên trang, đổi tỉ lệ theo bề rộng, bề cao ảnh, lật trục dọc. R = 0.
2. **Trang dựng lại thành ảnh hoặc trang trắng** (trang đã sửa nội dung, trang ảnh, trang trắng): ảnh phủ kín trang mới, giữ tỉ lệ, căn giữa (`_cho_dat`); đổi như trường hợp 1. R = 0.
3. **Trang PDF chép nguyên**: đọc /Rotate và **hộp cắt** (cropbox). Gốc hộp cắt có thể lệch khỏi (0, 0), nên cộng thêm góc dưới trái của hộp. Tỉ lệ ngang, dọc lấy theo bề rộng, bề cao hộp, đổi chỗ cho nhau khi trang xoay 90° hoặc 270°. Rồi đổi điểm theo góc xoay: 0° → (U, h − V); 90° → (V, U); 180° → (w − U, V); 270° → (w − V, h − U), với U, V là tọa độ đã nhân tỉ lệ, w, h là cỡ hộp cắt.

- **Hình hiển thị xoay ngược** góc /Rotate (ma trận /Matrix của Form XObject), để người đọc thấy chú thích đứng thẳng trên trang đang hiện xoay (`_form`).
- Ảnh gốc chỉ được lấy thẳng (không dựng lại) khi trang không có /Rotate (`NHAT-KY.md` dự án; `anh_nen` trong `tai_lieu_pdf.py`).
- **Xoay trang có chú thích**: tọa độ chú thích đổi theo ảnh trang mới (đã xoay, có thể khác độ phân giải) (`xoay`, `xoay_diem`).

## Vì sao Subject không ghi "đã chỉnh sửa"
- Chú thích không đụng vào ảnh trang: trang PDF chưa sửa nội dung vẫn **chép nguyên**, luồng nội dung trùng với tệp gốc (docstring `chu_thich.py`; kiểm thử mục 6).
- Chú thích là lớp riêng, ai cũng thấy là chú thích và tắt, xóa được bằng trình đọc khác. Vì nội dung trang không đổi, ghi "đã chỉnh sửa nội dung" sẽ sai sự thật (docstring `chu_thich.py`: "Siêu dữ liệu không ghi 'đã sửa nội dung' vì nội dung trang không đổi").
- Thay vào đó, siêu dữ liệu ghi khóa riêng `/XuLyPdfAnhChuThich` = "N chú thích (không sửa nội dung trang)". Nếu cùng tệp có trang sửa nội dung thì Subject vẫn ghi cho các chỗ sửa ấy (`luu` trong `tai_lieu_pdf.py`).
- Khác với các đối tượng chữ thêm, hình vẽ, dời vùng: các thứ ấy là sửa nội dung, có ghi dấu ([[doi-tuong-tren-trang]], [[cua-so-sua-pdf]]).
- Mỗi chú thích ghi tác giả "Xử lý PDF ảnh", mã riêng, thời điểm tạo, lời ghi, màu; cờ "in được" (`ghi_vao_trang`).

## Kiểm thử
- `kiem_thu_sua_pdf.py` mục 6 đạt: ghi đủ 5 loại /Text, /FreeText, /Highlight, /Line, /Stamp; chú thích không tính là sửa nội dung; nội dung trang chép nguyên; không có Subject; trang /Rotate 0, /Rotate 90 và trang trắng: PDFium dựng bản lưu, chú thích trùng chỗ xem trước 100%; xoay trang đi rồi về, chú thích về đúng chỗ ([[kiem-thu]]).
- Phép thử riêng trên 6 kiểu trang (có trang hộp cắt lệch gốc, trang ảnh scan của tệp hồ sơ thật của người dùng (bản sao, chỉ để thử), trang đã sửa nội dung): lưu ra trùng chỗ xem trước 100% (`NHAT-KY.md` dự án).
- Mục 6 chưa thử /Square, /Circle (chữ nhật, elip) dù mã có hai loại này.

## Chưa làm
- **Chưa đọc lại chú thích có sẵn** trong PDF mở vào: chỉ giữ nguyên, chưa sửa được (`NHAT-KY.md` dự án, 2026-10-30).
- Chưa có trên bản Android ([[ban-android-flutter]]).
- Phông của hình hiển thị lấy từ máy Windows; xem ghi chú phông ở [[giay-phep-thu-vien]].

Liên quan: [[doi-tuong-tren-trang]], [[thao-tac-trang]].
