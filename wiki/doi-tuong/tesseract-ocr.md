---
type: doi-tuong
loai: công cụ
---
# Tesseract OCR

- Giấy phép Apache 2.0; chạy mọi nền tảng; ổn với bản in sạch, kém hơn với ảnh chụp ([[ke-hoach-ung-dung]]).
- Nguyên mẫu dùng Tesseract 5.4 với gói `vie`, `eng`, `osd`; OSD dùng để tự xoay 90°/180° ([[readme]]; `NHAT-KY.md` dự án).
- **Dùng `vie`, không dùng `vie+eng`**: `vie+eng` mất dấu tiếng Việt nặng; `vie` riêng đọc gần đúng hết, kể cả dòng tiếng Anh ([[nhan-dang-va-sua-chu]]).
- Bản di động có thể thay bằng mô hình qua ONNX Runtime ([[ke-hoach-ung-dung]]).

## Trên Android (bản 0.2.0, cập nhật 2026-10-29)
- Kế hoạch để ngỏ việc thay Tesseract trên di động; bản Android 0.2.0 vẫn chọn Tesseract: **Tesseract 5.5.1** qua thư viện Tesseract4Android (`.aar`, Apache 2.0), gọi qua kênh `xlpdf/nhan_dang` trong `MainActivity.kt`, trả hOCR ([[readme-ung-dung-flutter]]). Phiên bản khác nguyên mẫu PC (Tesseract 5.4).
- Dữ liệu đóng gói trong `assets/tessdata/`: `vie.traineddata` (nhận dạng) và `osd.traineddata` (đoán chiều); tổng khoảng 18 MB ([[readme-ung-dung-flutter]]).
- **Dùng `vie`, không dùng `vie+eng`**, giữ quy tắc đã kiểm chứng trên PC ([[readme-ung-dung-flutter]]).
- **Đoán chiều**: `psm 1` với dữ liệu `osd`, chạy nền sau khi xử lý trang; khoảng 1 giây một trang theo README, 1,2 giây theo kiểm thử; đúng cả 4 góc 0°/90°/180°/270° trên máy ảo ([[nan-phang-va-xoay]], [[kiem-thu]]).
- **`OMP_THREAD_LIMIT=1`**: OpenMP của Tesseract chạy nhiều luồng chờ quay vòng, tranh CPU với luồng vẽ giao diện; trong ứng dụng một trang mất 9–10 giây (kiểm thử riêng chỉ khoảng 1 giây). `MainActivity` đặt biến này trước khi nạp Tesseract, còn khoảng 2,5 giây (README) / 2,3–3 giây (`NHAT-KY.md`) trên máy ảo ([[readme-ung-dung-flutter]]).
- Không dùng gói `flutter_tesseract_ocr` vì không dựng được với AGP 9 ([[readme-ung-dung-flutter]]).
- APK phải loại thư viện armeabi-v7a của Tesseract bằng `packaging.jniLibs.excludes` (máy 32-bit cài được nhưng mở ra chết) (`NHAT-KY.md` dự án).
- Độ khớp: trên máy ảo trùng 99,4% ký tự với Tesseract PC (`tesseract -l vie --psm 3`) cho cùng ảnh mau1 ([[du-lieu-kiem-thu]]).
- Chưa đo tốc độ trên điện thoại thật.
