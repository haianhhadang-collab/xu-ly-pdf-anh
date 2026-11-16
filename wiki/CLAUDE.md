# Quy ước wiki: Ứng dụng xử lý PDF ảnh

Vault Obsidian của dự án *Ứng dụng xử lý PDF ảnh* (quét, làm sạch, nắn phẳng, nhận dạng và chỉnh sửa tài liệu). Tài liệu gốc nằm ở thư mục cha `..\`; wiki không chép tài liệu gốc.

- Viết tiếng Việt, câu ngắn, ghi rõ nguồn. Không bịa số liệu, tên tác giả, trích dẫn; điều chưa chắc ghi `[cần xác minh]`.
- **Trang nguồn** `nguon/<ten-ngan-khong-dau>.md`: frontmatter `type: nguon`, `tep_goc`, `ngay_nap`, `loai` (bài báo, sách, văn bản pháp quy, bản thảo, dữ liệu, mã…). Thân: tóm tắt 5–10 dòng, ý chính, số liệu quan trọng (kèm trang/mục), liên kết `[[chu-de/…]]`, `[[doi-tuong/…]]`.
- **Trang chủ đề / đối tượng**: tổng hợp từ nhiều nguồn, mỗi ý gắn `[[nguon/…]]`. Khi nguồn mới mâu thuẫn với trang cũ thì ghi cả hai, không xóa ý cũ.
- **Cập nhật**: mỗi lần nạp nguồn mới → tạo/sửa trang nguồn → sửa các trang chủ đề/đối tượng liên quan → thêm vào `index.md` → nối một mục vào `log.md`.
- Tên tệp: chữ thường, không dấu, nối bằng gạch ngang. Liên kết dạng `[[ten-trang]]`.
- Dữ liệu cá nhân (mã sinh viên, số điện thoại, CCCD…) không chép vào wiki; chỉ ghi số lượng.
- Dự án phần mềm: nguồn là tài liệu (README, docs, đặc tả, ghi chú thiết kế), không tóm tắt từng tệp mã; trang `doi-tuong/` mô tả mô-đun, tính năng, quyết định thiết kế.
- `log.md` chỉ nối vào CUỐI: `## [YYYY-MM-DD] ingest|update|lint | <tiêu đề>`.
