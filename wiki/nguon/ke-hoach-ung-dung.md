---
type: nguon
tep_goc: "..\\02-ke-hoach-ung-dung.md"
ngay_nap: 2026-10-29
loai: kế hoạch / đặc tả
---
# Kế hoạch phát triển ứng dụng quét và chỉnh sửa tài liệu

**Tóm tắt.** Bản kế hoạch cho ứng dụng Android, iOS, PC dùng chung mã Flutter, lõi C++ + OpenCV ([[flutter-loi-cpp]]). Phân tích từng tính năng trong 6 tính năng, đánh giá khả thi, kiến trúc, chia 5 giai đoạn (tổng khoảng 8–9 tháng cho nhóm 3 người, mang tính tham khảo), rủi ro và tiêu chí kiểm thử. Lập theo [[prompt-ke-hoach]].

## Ý chính
- Người dùng: cán bộ hành chính (giữ màu dấu, chữ ký; sửa chữ khớp font) và thủ thư (nắn trang cong; tách trang đôi).
- Giả định chưa xác nhận: nguồn tệp nhận (Zalo, email, trình quản lý tệp, thư viện ảnh); nhân lực 3 người.
- Tính năng 2: ước lượng nền → chia cho nền → tách điểm có màu (Lab/HSV) → tăng tương phản có chọn lọc ([[lam-sach-giu-mau]]).
- Tính năng 3: tìm mép, phối cảnh, xoay (PaddleOCR hoặc Tesseract OSD), sửa nghiêng, trang cong (DocTr, UVDoc – cần kiểm tra giấy phép), tách trang đôi ([[nan-phang-va-xoay]]).
- Tính năng 5: OCR (Tesseract, PaddleOCR, VietOCR, ML Kit/Apple Vision); sửa chữ hướng A (vá nền + đoán font) và hướng B (tái dựng tài liệu) ([[nhan-dang-va-sua-chu]]).
- Không dùng trình quét sẵn của hệ điều hành làm luồng chính vì áp bộ lọc riêng, khó giữ màu dấu, không có trên PC.

## Khả thi (mục 2)
| Tính năng | Khả thi |
|---|---|
| 1 Chụp, xuất PDF | Cao |
| 2 Làm sáng nền, giữ màu | Cao |
| 3 Xoay, nắn, gộp | Cao (phẳng) / Trung bình (trang cong) |
| 4 Tự xử lý tệp nhận | Cao |
| 5 Sửa chữ khớp font | Trung bình (chữ in), thấp (chữ tay) |
| 6 Chỉnh định dạng | Trung bình |

## Giai đoạn (mục 4)
0 Chuẩn bị, thu 300–500 trang thật (2–3 tuần) · 1 MVP tính năng 1–4 (10–12 tuần) · 2 OCR, sửa chữ hướng A (6–8 tuần) · 3 Bố cục, hướng B, tính năng 6, trang cong (8–10 tuần) · 4 Hoàn thiện (4 tuần).

## Rủi ro đáng chú ý (mục 5)
- Sửa chữ trên văn bản có dấu, chữ ký có thể bị lợi dụng làm sai lệch giấy tờ → ghi dấu "đã chỉnh sửa" vào siêu dữ liệu PDF, lưu lịch sử, không cho sửa vùng chồng con dấu, chữ ký.
- Tiêu chí kiểm thử: xem [[kiem-thu]].
- Cần kiểm tra lại: hỗ trợ tiếng Việt của PaddleOCR, ML Kit, Apple Vision; giấy phép VietOCR, DocTr, UVDoc; tốc độ LaMa trên điện thoại; camera Flutter trên Windows ([[giay-phep-thu-vien]]).
