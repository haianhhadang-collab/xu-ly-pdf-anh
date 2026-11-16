# Xử lý PDF ảnh – Ứng dụng quét và làm sạch tài liệu

## Tổng quan dự án
Ứng dụng quét, làm sạch, nắn phẳng, nhận dạng và chỉnh sửa tài liệu cho cán bộ hành chính và thủ thư; văn bản tiếng Việt và tiếng Anh; xử lý hoàn toàn trên thiết bị. Sáu tính năng: (1) chụp, xuất PDF; (2) làm sáng nền, giữ màu mực; (3) xoay, nắn phẳng, gộp; (4) tự xử lý tệp nhận được; (5) nhận dạng, sửa chữ khớp font; (6) chỉnh định dạng.

Trạng thái (2026-10-29): đã có kế hoạch, nguyên mẫu Windows chạy được (Python + OpenCV + Tesseract) và bản Android Flutter (Dart + opencv_dart + Tesseract 5.5.1, APK 0.2.0); tính năng 1–4 gần đủ, có tự chụp và bấm chụp; Android đã có OCR, lớp chữ PDF, khử nhiễu, tự xoay toàn bộ, màn Xem nhanh; chưa có nắn trang cong, sửa chữ, trình soạn thảo; chưa thử ảnh thật, điện thoại thật. Đích: Flutter cho Android, iOS, PC.

Cập nhật 2026-10-30: nguyên mẫu PC có cửa sổ Sửa PDF: sửa trang PDF có sẵn (gộp, chèn, xóa, xoay, đảo, tách), sửa chữ khớp phông (hướng A), thêm chữ, che, tô sáng, chèn ảnh; bản Android chưa có. Còn chưa có: nắn trang cong, trình soạn thảo định dạng; chưa thử ảnh, PDF thật.

Cập nhật 2026-10-30 (lần 2): sửa chữ đổi sang **sửa theo khối** (dòng, đoạn), gõ ngay trên trang; chữ mới dàn lại nhiều dòng, giữ căn lề, phần dưới dời theo. Có ở nguyên mẫu PC và bản Android 0.4.0 (phông Liberation, SIL OFL). Android chưa thử điện thoại thật.

Cập nhật 2026-10-30 (lần 3): người dùng chê sửa theo khối làm mất định dạng; nguyên mẫu PC đổi công cụ chính sang **sửa ký tự giữ nguyên bản gốc** (chép nguyên hình ký tự từ tài liệu, chữ không sửa giữ nguyên điểm ảnh). Viết lại khối bằng phông thành công cụ phụ.

Cập nhật 2026-10-30 (lần 4): tham khảo ONLYOFFICE DesktopEditors (AGPL-3.0, chỉ học cách làm, không lấy mã), nguyên mẫu PC thêm: đối tượng chọn lại được, dời / xóa vùng có sẵn trên bản scan, vẽ hình; chú thích PDF chuẩn không phá bản gốc; thao tác trang kéo thả, menu chuột phải, chép / dán trang giữa hai cửa sổ. Chưa có trên Android; chưa đọc chú thích có sẵn trong PDF mở vào; menu chuột phải chưa bấm tay.

## Nguồn
- [[readme]] – README dự án: cài đặt, trạng thái tính năng, cách dùng, cửa sổ Sửa PDF (sửa ký tự giữ nguyên bản gốc, đổi phông, cỡ đoạn chọn), APK 0.6.0 (mục cài chưa đổi); 2026-11-14 thêm tìm mép kiểu CamScanner, nắn trang cong; mục tự xoay ảnh cầm máy ngang, xóa ngón tay (PC); tự chụp nhanh, nhận lật trang, tay trên trang (PC); sách mở nửa cặp trang (PC); 2026-11-15 nắn vuông khối chữ, `nan_lai_pdf.py`; tách cặp trang theo khe gáy, lề trang, báo trang nên chụp lại (PC), mục cài trỏ APK 0.7.8; 2026-11-16 báo nhòe ngay sau khi chụp, trang chụp trùng (PC), mục cài trỏ APK 0.7.9
- [[readme-ung-dung-flutter]] – README bản Android (Flutter) 0.6.0: tính năng (Sửa ký tự giữ nguyên bản gốc, Vẽ lại bằng phông), cấu trúc, dựng APK, kiểm thử; 0.7.0 tìm mép, nắn cong; 0.7.1 chụp nét, OCR tách riêng; 0.7.2 cắt sát chữ, xóa vết, nắn cong sách mở; 0.7.3 tự xoay ảnh cầm máy ngang, xóa ngón tay; 0.7.4 tự chụp nhanh, nhận lật trang, tay trên trang, rung báo; 0.7.5 sách mở nửa cặp trang (nối trang bên kia gáy, nhắc lùi máy); 0.7.6 nắn vuông khối chữ, nới khung 2,5%; 0.7.7 tách cặp trang theo khe gáy, lề "Vừa", chụp xong mới xử lý; 0.7.8 báo trang nên chụp lại, nút Chụp lại; 0.7.9 báo nhòe ngay trên màn camera, trang chụp trùng; kèm `GIAY-PHEP.txt` (có phông Liberation)
- [[ke-hoach-ung-dung]] – Kế hoạch phát triển (khả thi, kiến trúc, giai đoạn, rủi ro)
- [[prompt-ke-hoach]] – Prompt lập kế hoạch
- [[dac-ta-tu-dong-chup]] – Đặc tả chế độ tự động chụp (cập nhật 0.7.4: đo rung theo độ dời, giữ yên 0,3/0,5/0,9 giây, nhận lật trang, tay trên trang, rung báo)
- [[yeu-cau-nguoi-dung]] – Yêu cầu của người dùng (mới nhất 2026-11-14: làm phẳng ảnh kiểu CamScanner, nắn trang cong, chỉnh 4 góc; ảnh mờ, báo lùi máy, tách OCR; cắt sát chữ, xóa vết đen; tự chụp nhanh hơn, báo rung; lấy đủ hai trang sách mở; 2026-11-15 không cắt lẹm chữ, nắn vuông khối văn bản; lề không cắt sát quá, chụp xong mới xử lý)
- [[ho-so-15-11-sach-214-trang]] – Hồ sơ 214 trang sách chụp bằng bản Android (15/11): dò lỗi tách gáy, trang bị cắt còn mẩu, tay lật trang
- [[du-lieu-kiem-thu]] – PDF mẫu, PDF kết quả; ảnh chụp kém tổng hợp và đáp án nhận dạng cho bản Android; bộ ảnh tìm mép, nắn cong (`anh_mau_mep`); ảnh sách mở hai trang (`anh_sach_mo`, `trang_sach`); PDF kết quả nguyên mẫu PC `ket-qua/mới_nan.pdf` (11 trang, 2026-11-15)
- [[onlyoffice-desktopeditors]] – ONLYOFFICE DesktopEditors (AGPL-3.0): chỉ tham khảo ý tưởng đối tượng, chú thích, thao tác trang; không lấy mã

## Chủ đề
- [[lam-sach-giu-mau]] – Làm sáng nền, giữ màu mực
- [[nan-phang-va-xoay]] – Xoay, nắn phẳng, gộp PDF (0.7.0: tìm mép kiểu CamScanner, nắn trang cong)
- [[tu-dong-chup]] – Tự động chụp
- [[nhan-dang-va-sua-chu]] – OCR và sửa chữ khớp font (hướng A; sửa theo khối, gõ tại chỗ trên PC và Android 0.4.0)
- [[giay-phep-thu-vien]] – Giấy phép thư viện, phông (tránh AGPL; Liberation thay Times, Arial trên Android)
- [[kiem-thu]] – Tiêu chí và kết quả kiểm thử

## Đối tượng
- [[nguyen-mau-windows]] – Nguyên mẫu Windows (`ung-dung/`)
- [[cua-so-sua-pdf]] – Cửa sổ Sửa PDF của nguyên mẫu PC: sửa trang, sửa ký tự giữ nguyên bản gốc, viết lại khối, thêm chữ, che, chèn ảnh, vẽ hình, chú thích
- [[sua-ky-tu]] – Sửa ký tự giữ nguyên bản gốc (`sua_ky_tu.py`): xóa, chèn ký tự chép từ tài liệu, dãy chấm mục lục
- [[doi-tuong-tren-trang]] – Đối tượng chọn lại được (dời, đổi cỡ, xóa, bấm đúp sửa chữ, Ctrl+Y), vẽ hình, dời / xóa vùng có sẵn trên bản scan (`doi_tuong.py`, `sua_pdf_doi_tuong.py`)
- [[chu-thich-pdf]] – Chú thích PDF chuẩn không phá bản gốc (`chu_thich.py`): loại chú thích, hình hiển thị /AP, đổi điểm ảnh sang điểm PDF theo /Rotate và hộp cắt, vì sao không ghi "đã chỉnh sửa"
- [[thao-tac-trang]] – Thao tác trang kiểu ONLYOFFICE (`sua_pdf_trang.py`): kéo thả, menu chuột phải, chép / dán trang giữa hai cửa sổ
- [[tesseract-ocr]] – Tesseract OCR
- [[flutter-loi-cpp]] – Kiến trúc đích Flutter + lõi C++
- [[ban-android-flutter]] – Bản Android Flutter (`ung-dung-flutter/`, APK 0.1.0 đến 0.7.6; có mục màn Xem nhanh, Đánh số trang, Sửa chữ, Sửa ký tự)
