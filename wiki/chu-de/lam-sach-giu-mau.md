---
type: chu-de
---
# Làm sáng nền, giữ màu mực (tính năng 2)

- Yêu cầu cốt lõi: nền trắng sạch, tăng tương phản, nhưng **không chuyển về đen trắng**; giữ màu chữ, con dấu đỏ, chữ ký, mực xanh, bút phê ([[prompt-ke-hoach]], [[yeu-cau-nguoi-dung]]).
- Cách làm theo kế hoạch: ước lượng nền (phép đóng hình thái học hoặc lọc trung vị lớn) → chia ảnh cho nền theo từng kênh (xóa bóng đổ, cả bóng gáy sách) → đánh dấu điểm bão hòa cao trong Lab/HSV là "cần giữ màu" → chữ xám kéo về đen đậm, chữ màu chỉ tăng độ đậm, giữ sắc độ ([[ke-hoach-ung-dung]]).
- Phần khó: dấu đỏ mờ, mực xanh nhạt, giấy ngả vàng sách cũ; cần ảnh thật để tinh chỉnh ([[ke-hoach-ung-dung]]).
- Nguyên mẫu: mô-đun `loi_xu_ly/lam_sach.py`; chế độ giữ màu, xám, đen trắng; chỉnh độ trắng nền, độ đậm chữ ([[readme]]).
- Kết quả kiểm thử trên ảnh tổng hợp: nền trắng 100% kể cả chỗ bóng đổ, sắc độ dấu đỏ lệch 3,9° (tiêu chí ≤ 10°) ([[kiem-thu]]).

## Bản Android 0.2.0: tương phản cao hơn, khử nhiễu (cập nhật 2026-10-29)
- Yêu cầu mới: bản mobile tăng thêm tương phản, khử nhiễu cho chữ ([[yeu-cau-nguoi-dung]]).
- Đã làm trong `lib/loi/lam_sach.dart` ([[readme-ung-dung-flutter]]):
  - đường cong tương phản chữ dốc gấp đôi so với bản PC;
  - lọc trung vị 3×3 khử nhiễu hạt;
  - xóa đốm đứng riêng (`xoaDom`); khoảng "gần chữ" tính theo cỡ chữ đo được để giữ dấu thanh, dấu câu;
  - thêm thanh chỉnh thứ ba *Khử nhiễu* (cạnh độ trắng nền, độ đậm chữ).
- Cách làm: thử phương án trên nguyên mẫu Python trước rồi mới chuyển sang Dart (`NHAT-KY.md` dự án).
- **Khác bản PC**: nguyên mẫu PC (`lam_sach.py`) **chưa** có khử nhiễu và đường cong tương phản mới; hai bản hiện cho kết quả làm sạch khác nhau (`NHAT-KY.md` dự án).
- Kiểm thử trên máy ảo, ảnh chụp kém tổng hợp `mau4-chup-kem.jpg`: đốm nhiễu 743 → 117; nhận dạng đúng 71% → 91,6%; chữ đen hơn (trung vị độ sáng 55 → 43). Ảnh chụp tốt vẫn đọc đúng 99,4%; dấu đỏ giữ nguyên ([[du-lieu-kiem-thu]], [[kiem-thu]]).
- Còn thiếu: ảnh chụp kém là ảnh tổng hợp; cần ảnh chụp thật để chỉnh ngưỡng khử nhiễu (`NHAT-KY.md` dự án).

Liên quan: [[nguyen-mau-windows]], [[ban-android-flutter]].
