---
type: nguon
tep_goc: "https://github.com/ONLYOFFICE/DesktopEditors"
ngay_nap: 2026-10-30
loai: mã (phần mềm tham khảo bên ngoài)
giay_phep: AGPL-3.0
---
# ONLYOFFICE DesktopEditors (tham khảo cách làm)

**Tóm tắt.** Bộ soạn thảo văn phòng mã nguồn mở, có trình sửa PDF. Người dùng đề nghị tham khảo chức năng chỉnh chữ và đối tượng trong PDF của phần mềm này (2026-10-30). Kho mã: https://github.com/ONLYOFFICE/DesktopEditors. Giấy phép **AGPL-3.0**, nên dự án **chỉ học ý tưởng, cách làm, không lấy mã** ([[yeu-cau-nguoi-dung]]; `NHAT-KY.md` dự án, 2026-10-30, mục "Tham khảo ONLYOFFICE"). Không có bản sao kho này trong thư mục dự án.

## Ý được học, đưa vào nguyên mẫu PC
Người dùng chọn đưa vào cả bốn hướng ([[yeu-cau-nguoi-dung]]):
1. Đối tượng chọn lại được: bấm chọn, kéo dời, kéo góc đổi cỡ, Delete xóa, bấm đúp sửa chữ; có làm lại Ctrl+Y → [[doi-tuong-tren-trang]].
2. Dời, đổi cỡ, xóa vùng có sẵn trên bản scan (đoạn chữ, ảnh, bảng); vùng có con dấu, chữ ký vẫn khóa → [[doi-tuong-tren-trang]].
3. Chú thích không phá bản gốc: ghi chú, bút phê, tô sáng, hình, dấu "Đã xem", lưu thành chú thích PDF chuẩn → [[chu-thich-pdf]].
4. Thao tác trang: kéo thả đổi thứ tự, menu chuột phải trên ảnh trang, chèn trang trắng trước/sau, chép/dán trang giữa các tệp → [[thao-tac-trang]].

## Ràng buộc giấy phép
- Docstring các mô-đun mới (`doi_tuong.py`, `chu_thich.py`, `sua_pdf_doi_tuong.py`) đều ghi "tham khảo … ONLYOFFICE; không dùng mã của họ".
- Cùng nguyên tắc với việc tránh MuPDF (AGPL) ([[giay-phep-thu-vien]]).

## Chưa rõ
- Nguồn trong dự án không ghi phiên đã xem phần nào của ONLYOFFICE (mã, tài liệu, hay dùng thử phần mềm) [cần xác minh].

Liên quan: [[cua-so-sua-pdf]], [[nguyen-mau-windows]].
