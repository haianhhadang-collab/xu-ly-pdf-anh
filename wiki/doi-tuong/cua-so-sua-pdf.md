---
type: doi-tuong
loai: tính năng / mã
---
# Cửa sổ Sửa PDF (nguyên mẫu PC)

Cửa sổ riêng trong [[nguyen-mau-windows]], thêm ngày 2026-10-30. Sửa trang của PDF có sẵn và sửa nội dung trang: sửa chữ khớp phông, thêm chữ, che, tô sáng, chèn ảnh ([[readme]]). Từ 2026-10-30 (lần 4) có thêm đối tượng chọn lại được, dời vùng scan, vẽ hình, chú thích PDF chuẩn, thao tác trang kiểu ONLYOFFICE (mục cuối trang). Làm theo yêu cầu người dùng: chọn cả ba hướng, sửa chữ làm trước ([[yeu-cau-nguoi-dung]]).

## Mở cửa sổ
- Nút *✏ Sửa PDF…* trên thanh công cụ giao diện chính; hỏi có đưa các trang đang mở sang không ([[readme]]).
- Chạy riêng: `ung-dung/sua-pdf.bat`; kéo PDF thả lên tệp .bat được ([[readme]]).
- Cửa sổ mở phóng to, vì màn hình máy thử 1080×1920 (dọc) hẹp hơn cửa sổ đặt sẵn (`NHAT-KY.md` dự án, 2026-10-30).

## Công cụ
| Công cụ | Cách dùng | Nguồn |
|---|---|---|
| Sửa trang | Mở, kéo thả nhiều PDF, ảnh (gộp); chèn trang trắng; xoay ⟲ ⟳; ▲ ▼; xóa; *Lưu PDF…*; *Lưu trang đang chọn ra tệp mới…* (tách) | [[readme]] |
| Sửa chữ (bản đầu 2026-10-30) | Chờ tìm chữ (khung xanh), bấm từ, Shift bấm thêm từ liền kề cùng dòng, Enter; hộp thoại cho sửa chữ máy đọc sai và gõ chữ mới | [[readme]] |
| Sửa chữ theo khối (cập nhật 2026-10-30, lần 2; thay cách trên) | Chờ tìm chữ; chữ cùng dòng, dòng cùng đoạn gộp thành khối (khung xanh nét đứt). Bấm khối: ô sửa hiện tại chỗ, đúng phông, cỡ, màu, căn lề đã đoán, điền sẵn chữ máy đọc. Enter xuống dòng cứng; Ctrl+Enter hoặc bấm ra ngoài để áp; Esc hủy. Phóng to khi đang sửa vẫn giữ chữ | [[readme]]; `NHAT-KY.md` dự án, 2026-10-30, mục sửa theo khối |
| Thêm chữ | Bấm chỗ cần thêm, gõ chữ (nhiều dòng); phông, kiểu, cỡ (pt), màu ở khung *Chữ*. Từ 2026-10-30 (lần 2): gõ ngay trên trang, Ctrl+Enter để xong | [[readme]] |
| Che, Tô sáng | Kéo chuột quanh vùng; che trắng hoặc đen, chỗ che bị xóa hẳn khi lưu | [[readme]] |
| Chèn ảnh | *Chọn ảnh để chèn…*, kéo chuột đặt ảnh (giữ tỉ lệ); ô *Bỏ nền trắng* cho chữ ký, con dấu chụp trên giấy trắng | [[readme]] |

- Mỗi việc là một thao tác trong danh sách *Thao tác trên trang này*; xóa từng thao tác hoặc Ctrl+Z ([[readme]]).

## Mô-đun
| Tệp | Vai trò |
|---|---|
| `sua_pdf.py` | Cửa sổ tkinter; chạy riêng được: `python sua_pdf.py [tệp …]` |
| `loi_xu_ly/sua_noi_dung.py` | Sửa nội dung một trang ảnh: sửa chữ (tính năng 5, hướng A), thêm chữ, che, chèn ảnh, tô sáng. Từ 2026-10-30 (lần 2): thêm `tim_khoi` (gộp khối, đoán căn lề, thụt đầu dòng) và thao tác `SuaKhoi`; giữ `SuaChu` (theo từ) cho tương thích |
| `loi_xu_ly/tai_lieu_pdf.py` | Tài liệu để sửa: trang PDF gốc, trang ảnh, trang trắng; chèn, xóa, xoay, đảo thứ tự, gộp, tách; lưu PDF |
| `sua-pdf.bat` | Mở thẳng cửa sổ Sửa PDF |

Nguồn: [[readme]], docstring đầu các tệp mã.

## Quyết định thiết kế
- **Thao tác áp lần lượt**: ảnh trang = ảnh gốc + các thao tác. Hoàn tác, xóa từng thao tác chỉ cần dựng lại (`sua_noi_dung.py`; `NHAT-KY.md` dự án, 2026-10-30).
- **Giữ chất lượng trang chưa sửa**: trang PDF chưa sửa nội dung chép nguyên bằng pypdf (giữ chữ, hình vẽ, lớp chữ); xoay chỉ đổi thuộc tính /Rotate (`tai_lieu_pdf.py`; [[readme]]).
- **Trang đã sửa nội dung**: dựng 300 dpi bằng PDFium, áp thao tác, ghi lại thành trang ảnh cùng khổ bằng reportlab; thêm lớp chữ ẩn nếu bật ô *Lớp chữ cho trang đã sửa* (`tai_lieu_pdf.py`; [[readme]]).
- **Ghi dấu đã chỉnh sửa**: siêu dữ liệu PDF (Subject) ghi "Đã chỉnh sửa nội dung…", kèm số chỗ sửa chữ, số chỗ che…; chưa sửa thì không ghi. Mục đích: tránh bị lợi dụng làm sai lệch giấy tờ ([[readme]]; `NHAT-KY.md` dự án, 2026-10-30). Khớp với biện pháp nêu trong [[ke-hoach-ung-dung]].
- **Lưu đè** lên chính tệp nguồn được (`NHAT-KY.md` dự án, 2026-10-30).
- **Không dùng MuPDF**: đọc, dựng trang bằng PDFium; ghép bằng pypdf; ghi trang ảnh bằng reportlab ([[giay-phep-thu-vien]]).
- **Sửa theo khối, gõ tại chỗ** (2026-10-30, lần 2): làm theo yêu cầu người dùng ([[yeu-cau-nguoi-dung]]). Ô gõ đặt ngay trên trang, cùng phông, cỡ, màu, căn lề, khoảng cách dòng theo tỉ lệ phóng; bỏ hộp thoại sửa chữ cũ. Chữ mới dàn lại trong bề rộng khối; số dòng đổi thì phần trang bên dưới dời theo ([[readme]]; `NHAT-KY.md` dự án, 2026-10-30, mục sửa theo khối).
- Cách sửa chữ khớp phông: xem [[nhan-dang-va-sua-chu]].

## Giới hạn, chưa làm
- Chưa thử trên ảnh chụp thật và PDF thật của người dùng; tập phông mới có Times New Roman, Arial (`NHAT-KY.md` dự án, 2026-10-30).
- Chữ sửa chỉ trên một dòng; không tự xuống dòng khi chữ mới quá dài (có cảnh báo vượt lề). Cập nhật 2026-10-30 (lần 2): đã xử lý, chữ dàn lại nhiều dòng trong khối.
- Hộp thoại sửa chữ, thêm chữ chưa được bấm bằng tay (script kiểm thử thay hộp thoại bằng kết quả giả). Cập nhật 2026-10-30 (lần 2): đã bỏ hộp thoại; ô gõ tại chỗ được bấm thử bằng script (mở ô, gõ thêm câu, phóng to, Ctrl+Enter, Esc hủy, bấm ra ngoài áp, thêm chữ tại chỗ); ảnh `kiem_thu/ket_qua/giao-dien-sua-khoi.png` ([[kiem-thu]]).
- Bản Android chưa có các chức năng này ([[ban-android-flutter]]). Cập nhật 2026-10-30 (lần 2): bản 0.4.0 đã có sửa chữ theo khối; các công cụ khác (che, chèn ảnh, sửa trang PDF) vẫn chỉ có trên PC.
- Còn chưa làm (2026-10-30, lần 2): khối có chữ đậm, nghiêng lẫn trong đoạn sẽ ra một kiểu chữ; dời phần dưới theo cả bề ngang trang, nên cột bên cạnh, con dấu cũng dời theo (`NHAT-KY.md` dự án, 2026-10-30, mục sửa theo khối).
- Kiểm thử: [[kiem-thu]].

## Cập nhật 2026-10-30 (lần 3)
- Công cụ chính đổi thành *Sửa ký tự (giữ nguyên bản gốc)* ([[sua-ky-tu]]): con trỏ đỏ trên dòng, Backspace/Delete xóa, gõ để chèn, Enter xong; ký tự chưa chắc viền vàng, chuột phải chọn mẫu; tự cuộn tới con trỏ.
- Công cụ sửa theo khối đổi tên "Viết lại cả khối chữ (vẽ lại bằng phông)"; README ghi rõ là không giữ được dáng chữ bản scan.
- Trang PDF chỉ gồm một ảnh scan được sửa trên ảnh gốc, lưu đúng kích thước, chỗ đặt cũ. Dòng README "trang đã sửa lưu dạng ảnh 300 dpi" vẫn còn; theo `NHAT-KY.md` dự án, trang không phải một ảnh nay dựng theo độ phân giải ảnh, chỉ dùng 300 dpi khi không có ảnh ([[readme]]).

## Cập nhật 2026-10-30 (lần 4): tham khảo ONLYOFFICE
Người dùng đề nghị tham khảo trình sửa PDF của ONLYOFFICE DesktopEditors và chọn đưa vào cả bốn hướng. ONLYOFFICE dùng AGPL-3.0 nên chỉ học cách làm, không lấy mã ([[onlyoffice-desktopeditors]], [[yeu-cau-nguoi-dung]]).

| Công cụ mới | Tóm tắt | Trang |
|---|---|---|
| Chọn, dời, đổi cỡ | Chữ thêm, ảnh chèn, khung che, tô sáng, hình vẽ, chú thích chọn lại được (viền tím); kéo dời, kéo ô vuông đổi cỡ, Delete, mũi tên, Ctrl+C / Ctrl+V; bấm đúp chữ thêm để sửa | [[doi-tuong-tren-trang]] |
| Vùng có sẵn trên bản scan | Mỗi dòng chữ, ảnh, bảng một vùng (viền xám); dời, đổi cỡ, xóa giữ nguyên nét mực gốc; vùng có mực màu bị khóa (viền đỏ) | [[doi-tuong-tren-trang]] |
| Vẽ hình | Chữ nhật, elip, đường, mũi tên | [[doi-tuong-tren-trang]] |
| Chú thích (không sửa bản gốc) | Ghi chú, bút phê, tô sáng, chữ nhật, elip, mũi tên, dấu "ĐÃ XEM" kèm ngày; lưu thành chú thích PDF chuẩn; trang gốc chép nguyên | [[chu-thich-pdf]] |
| Thao tác trang | Kéo thả ảnh trang, menu chuột phải, Ctrl+C / X / V trang, chép dán giữa hai cửa sổ | [[thao-tac-trang]] |
| Làm lại | Nút *Làm lại (Ctrl+Y)*, bên cạnh Ctrl+Z | [[readme]] |

Mô-đun mới (`NHAT-KY.md` dự án, 2026-10-30, mục "Tham khảo ONLYOFFICE"; [[readme]]):
| Tệp | Vai trò |
|---|---|
| `loi_xu_ly/doi_tuong.py` | Khung, dời, đổi cỡ đối tượng; `HinhVe`; `tim_vung`; `DoiVung` |
| `loi_xu_ly/chu_thich.py` | Chú thích → chú thích PDF chuẩn có hình hiển thị /AP |
| `sua_pdf_doi_tuong.py` | Lớp trộn: công cụ *Chọn, dời, đổi cỡ*, làm lại |
| `sua_pdf_trang.py` | Lớp trộn: kéo thả trang, menu chuột phải, chép / dán trang |
| `loi_xu_ly/tai_lieu_pdf.py` (sửa) | Thêm `_toa_do_pdf` (điểm ảnh → điểm PDF), `di_chuyen`, `chep`, `dan`; xoay trang thì đổi tọa độ chú thích theo |

Quyết định thiết kế mới:
- **Chú thích không tính là sửa nội dung**: trang gốc vẫn chép nguyên; Subject không ghi "đã chỉnh sửa", chỉ ghi khóa `/XuLyPdfAnhChuThich`. Quyết định "ghi dấu đã chỉnh sửa" ở trên vẫn áp dụng cho mọi thao tác khác, kể cả chữ thêm, hình vẽ, dời vùng ([[chu-thich-pdf]]).
- **Ảnh hiện = ảnh đã sửa + chú thích vẽ chồng**; sửa ký tự, tìm vùng scan dùng ảnh không có chú thích ([[chu-thich-pdf]]).
- **Vùng scan tìm trên ảnh chưa có đối tượng thêm**, để không gộp nhầm ([[doi-tuong-tren-trang]]).

Chưa làm, chưa kiểm (`NHAT-KY.md` dự án, 2026-10-30):
- Menu chuột phải mới kiểm bằng lệnh, chưa bấm tay.
- Chưa đọc lại chú thích có sẵn trong PDF mở vào (chỉ giữ nguyên, chưa sửa được).
- Đổi cỡ vùng scan là phóng ảnh nét mực nên chữ có thể nhòe.
- Chưa có trên bản Android ([[ban-android-flutter]]).
- Kiểm thử: mục 5–7 của `kiem_thu_sua_pdf.py` và các phép thử cửa sổ bằng script ([[kiem-thu]]).
