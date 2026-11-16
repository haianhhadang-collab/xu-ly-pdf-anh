---
type: doi-tuong
loai: kiến trúc
---
# Kiến trúc đích: Flutter + lõi C++

- Giao diện Flutter (Dart) cho Android, iOS, Windows (macOS nếu cần); lõi xử lý ảnh C++ + OpenCV gọi qua FFI; ONNX Runtime chạy mô hình (bản nhẹ điện thoại, bản đầy đủ PC); `pdf` (Dart) ghi PDF, PDFium đọc; SQLite lưu danh sách tài liệu; tệp mã hóa; không máy chủ ([[ke-hoach-ung-dung]]).
- Luồng: chụp / nhận tệp → tìm mép, phối cảnh, tách trang đôi, nắn cong, xoay, sửa nghiêng → ước lượng nền, giữ màu, tương phản → sắp xếp, xuất PDF → (khi sửa) OCR + bố cục → hướng A hoặc B ([[ke-hoach-ung-dung]]).
- Tự động chụp trên di động: giao diện C `tu_chup_tao / tu_chup_nhan_khung / tu_chup_dat_lai / tu_chup_huy`, struct `TrangThaiTuChup` ([[dac-ta-tu-dong-chup]]).
- Thuật toán chuyển từ [[nguyen-mau-windows]]; dùng chung bộ kiểm thử với bản Python ([[dac-ta-tu-dong-chup]]).
- Trạng thái (theo `NHAT-KY.md` dự án, lúc dựng wiki): chưa dựng; máy chưa có Flutter.
- Cập nhật 2026-10-29: đã có [[ban-android-flutter]]. Lõi của bản này viết bằng Dart + `opencv_dart`, không qua C++/FFI như kế hoạch; chưa có OCR, ONNX Runtime ([[readme-ung-dung-flutter]]).
- Cập nhật 2026-10-29 (bản 0.2.0): đã có OCR, nhưng bằng Tesseract 5.5.1 (Tesseract4Android, `.aar` gọi qua kênh nền tảng trong `MainActivity.kt`), không qua ONNX Runtime; ONNX Runtime vẫn chưa dùng ([[readme-ung-dung-flutter]], [[tesseract-ocr]]).
