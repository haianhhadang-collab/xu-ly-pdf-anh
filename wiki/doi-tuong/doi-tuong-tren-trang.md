---
type: doi-tuong
loai: tính năng / mã
ngay_nap: 2026-10-30
---
# Đối tượng chọn lại được và vùng có sẵn trên bản scan (nguyên mẫu PC)

Thêm vào [[cua-so-sua-pdf]] ngày 2026-10-30 (lần 4), theo cách làm của trình sửa PDF ONLYOFFICE, không dùng mã của họ ([[onlyoffice-desktopeditors]]). Mã lõi `loi_xu_ly/doi_tuong.py`; giao diện là lớp trộn `sua_pdf_doi_tuong.py` dùng trong cửa sổ `sua_pdf.py` ([[readme]]).

## Đối tượng chọn lại được
- Chữ đã thêm, ảnh đã chèn, khung che, tô sáng, hình vẽ, vùng đã dời, chú thích đều chọn lại được (viền tím) bằng công cụ *Chọn, dời, đổi cỡ* ([[readme]]).
- Thao tác: bấm để chọn; kéo để dời; kéo ô vuông ở góc, cạnh để đổi cỡ; Delete xóa; phím mũi tên nhích 1 điểm ảnh (Shift: 10); Ctrl+C / Ctrl+V nhân bản ([[readme]]).
- Bấm đúp chữ đã thêm: ô sửa tại chỗ hiện ra, điền sẵn chữ cũ. Đổi phông, kiểu, cỡ, màu ở khung *Chữ* là áp ngay cho chữ đang chọn (`NHAT-KY.md` dự án, 2026-10-30, mục "Tham khảo ONLYOFFICE").
- Có **Ctrl+Y làm lại**, bên cạnh Ctrl+Z hoàn tác ([[readme]]).
- **Vẽ hình**: chữ nhật, elip, đường, mũi tên (thao tác `HinhVe`); chọn loại, độ dày ở khung *Hình, che, chèn ảnh*, màu theo nút *Màu chữ*. Đường, mũi tên giữ chiều vẽ khi dời ([[readme]]; `doi_tuong.py`).

**Vì sao chọn lại được**: ảnh trang luôn dựng lại từ ảnh gốc + danh sách thao tác ([[cua-so-sua-pdf]], quyết định "thao tác áp lần lượt"). Dời, đổi cỡ chỉ là sửa khung của một thao tác rồi dựng lại (docstring `doi_tuong.py`; các hàm `khung`, `doi`, `dat_khung`).

## Vùng có sẵn trên bản scan
- `tim_vung` tự đánh dấu vùng: nét mực gần nhau gộp theo cỡ chữ; mỗi dòng chữ, ảnh, bảng là một vùng (viền xám). Muốn lấy nhiều dòng thì kéo khung trên chỗ trống ([[readme]]; docstring `tim_vung`).
- Vùng có mực màu (con dấu, chữ ký, bút phê) bị **khóa** (viền đỏ), cùng biện pháp chống lạm dụng như sửa chữ ([[readme]]; [[ke-hoach-ung-dung]]).
- Thao tác `DoiVung`: chép nét mực gốc (có độ trong, nên nền giấy chỗ mới giữ nguyên) sang chỗ mới, vá nền chỗ cũ; hoặc chỉ xóa vùng. Ngoài chỗ cũ và chỗ mới không đổi điểm ảnh nào (`NHAT-KY.md` dự án, 2026-10-30; [[readme]]).
- Vùng scan được tìm trên ảnh đã sửa ký tự, đã dời vùng, nhưng **chưa có** chữ thêm, hình vẽ, ảnh chèn, chú thích, để các đối tượng ấy không bị gộp nhầm vào vùng của bản scan (`sua_pdf_doi_tuong.py`; `NHAT-KY.md` dự án).

## Ghi dấu khi lưu
- Đối tượng (chữ thêm, hình vẽ, dời vùng…) là sửa nội dung trang: trang được dựng lại thành ảnh và Subject ghi "Đã chỉnh sửa nội dung…" như các thao tác sửa khác ([[cua-so-sua-pdf]]). Chỉ chú thích là không tính sửa nội dung ([[chu-thich-pdf]]).
- Subject của tệp lưu ghi hình vẽ là "vẽ hình", dời vùng là "dời, xóa vùng" (`tom_tat_sua` trong `tai_lieu_pdf.py`; đã bổ sung và chạy thử ngày 2026-10-30).

## Kiểm thử
`kiem_thu_sua_pdf.py` mục 5 đạt: dời chữ đã thêm; kéo góc gấp đôi khung thì cỡ chữ 40 → khoảng 80 px; dời mũi tên giữ chiều; trang mẫu có 15 vùng, 3 vùng con dấu bị khóa; dời một vùng không đổi điểm ảnh nào ngoài chỗ cũ, chỗ mới; xóa vùng thì chỗ cũ vá nền. Bấm thử cửa sổ bằng script trên tệp hồ sơ thật của người dùng (bản sao, chỉ để thử) ([[kiem-thu]]).

## Chưa làm
- Đổi cỡ vùng scan là phóng ảnh nét mực, nên chữ có thể nhòe (`NHAT-KY.md` dự án, 2026-10-30).
- Chưa có trên bản Android ([[ban-android-flutter]]; `CLAUDE.md` dự án).

Liên quan: [[chu-thich-pdf]], [[thao-tac-trang]], [[sua-ky-tu]].
