# Kế hoạch phát triển ứng dụng quét và chỉnh sửa tài liệu

## Bối cảnh và giả định

| Mục | Nội dung |
|---|---|
| Nền tảng | Android, iOS và PC (Windows; macOS nếu cần) — một mã nguồn chung bằng Flutter |
| Người dùng | Cán bộ, nhân viên hành chính (công văn, hợp đồng, giấy tờ có dấu đỏ, chữ ký, bút phê); thủ thư (trang sách, tạp chí, tài liệu đóng gáy) |
| Ngôn ngữ văn bản | Tiếng Việt có dấu và tiếng Anh |
| Nơi xử lý | Toàn bộ trên thiết bị, không gửi dữ liệu lên máy chủ |
| Nguồn file nhận | *Giả định*: chia sẻ từ Zalo, email, trình quản lý file, thư viện ảnh; trên PC là kéo thả và "Mở bằng" |
| Nhân lực | *Giả định*: 3 người — 2 lập trình viên ứng dụng, 1 kỹ sư xử lý ảnh / học máy |

Hai nhóm người dùng đặt yêu cầu khác nhau: hành chính cần **giữ màu dấu, chữ ký** và **sửa chữ khớp font**; thủ thư cần **nắn trang sách cong** và **tách trang đôi**. Kế hoạch dưới đây phục vụ cả hai.

---

## 1. Phân tích từng tính năng

### Tính năng 1 — Chụp ảnh, xuất PDF
- **Điện thoại**: plugin `camera` của Flutter, chụp độ phân giải gốc rồi chuyển sang luồng xử lý (tính năng 2, 3).
- **Tự động chụp** (yêu cầu bổ sung 2026-10-29): tự chụp khi trang đứng yên, rõ nét, đủ sáng, không chụp trùng trang khi lật sách. Đặc tả và cách chuyển sang Flutter + C++: `03-tu-dong-chup.md`; thuật toán mẫu: `ung-dung/loi_xu_ly/tu_chup.py`.
- **PC**: chụp qua webcam / camera tài liệu (document camera, thường có ở thư viện) hoặc nhập ảnh từ máy scan, thư mục. Hỗ trợ camera của Flutter trên máy tính hạn chế hơn điện thoại — cần thử sớm trên Windows.
- **Xuất PDF**: thư viện `pdf` (Dart), chạy được trên cả ba nền tảng.
- Không dùng trình quét sẵn của hệ điều hành (ML Kit Document Scanner, VisionKit) làm luồng chính, vì chúng áp bộ lọc riêng, khó giữ màu dấu và không có trên PC.
- **Mức khó**: thấp (điện thoại), trung bình (camera trên PC).

### Tính năng 2 — Làm sáng nền, tăng tương phản, giữ màu mực
- **Cách làm** (không chuyển về đen trắng):
  1. *Ước lượng nền*: thu nhỏ ảnh, dùng phép đóng hình thái học (morphological closing — "xóa" nét chữ để chỉ còn nền) hoặc lọc trung vị kích thước lớn, được một ảnh nền có cả bóng đổ và vùng tối.
  2. *Chia cho nền*: lấy ảnh gốc chia cho ảnh nền theo từng kênh màu → nền trắng đều, bóng đổ biến mất (gồm cả bóng ở gáy sách).
  3. *Tách điểm có màu*: chuyển sang không gian màu Lab/HSV; điểm có độ bão hòa cao (dấu đỏ, mực xanh, bút đỏ, hình minh họa màu trong sách) được đánh dấu "cần giữ màu".
  4. *Tăng tương phản có chọn lọc*: điểm xám (chữ in đen) kéo về đen đậm; điểm có màu chỉ tăng độ đậm, giữ nguyên sắc độ (hue).
- **Công cụ**: OpenCV (Apache 2.0), viết bằng C++ dùng chung cho cả ba nền tảng.
- **Mức khó**: trung bình. Phần khó là ngưỡng cho dấu đỏ mờ, mực xanh nhạt, giấy ngả vàng của sách cũ — cần bộ ảnh mẫu thật để tinh chỉnh.

### Tính năng 3 — Xoay, nắn phẳng, gộp PDF
- **Tìm mép giấy**: phát hiện cạnh và đường viền (OpenCV); mô hình nhỏ phân vùng trang khi nền bàn rối.
- **Sửa phối cảnh**: biến đổi phối cảnh (perspective transform) đưa bốn góc về hình chữ nhật đúng tỉ lệ khổ giấy.
- **Xoay đúng chiều 90°/180°**: bộ phân loại hướng chữ (ví dụ bộ phân loại góc của PaddleOCR, hoặc OSD của Tesseract).
- **Sửa nghiêng nhỏ**: đo góc dòng chữ (biến đổi Hough hoặc chiếu hình) rồi xoay.
- **Trang sách cong** (quan trọng với thủ thư): cần mô hình học sâu nắn trang (các mô hình nghiên cứu như DocTr, UVDoc — cần kiểm tra giấy phép và tốc độ trên điện thoại). Phương án nhẹ hơn: ước lượng độ cong từ các dòng chữ rồi nắn theo dòng.
- **Tách trang đôi**: phát hiện gáy sách khi chụp hai trang mở, tách thành hai trang PDF.
- **Không mất nội dung**: luôn chừa lề an toàn khi cắt; so khung bao nội dung trước và sau, nội dung chạm mép thì nới khung.
- **Gộp PDF**: sắp thứ tự trang bằng kéo thả, ghi một file PDF nhiều trang.
- **Mức khó**: trung bình (phối cảnh, nghiêng, tách trang đôi), cao (trang cong).

### Tính năng 4 — Tự động xử lý file nhận được
- **Android**: intent filter nhận `image/*` và `application/pdf`.
- **iOS**: Share Extension; bị giới hạn bộ nhớ nên chỉ nhận file, chuyển vào ứng dụng chính xử lý.
- **PC**: kéo thả vào cửa sổ, đăng ký "Mở bằng" cho PDF/ảnh, và tùy chọn **thư mục theo dõi** — file mới vào thư mục được tự xử lý (tiện khi nối máy scan ở thư viện, văn phòng).
- **Xử lý**: PDF được kết xuất từng trang thành ảnh, chạy luồng tính năng 2–3, ghi PDF mới. Người dùng chọn "tự động" hoặc "hỏi trước"; có xử lý theo lô.
- **Công cụ**: PDFium (giấy phép BSD) để kết xuất trang. Tránh MuPDF nếu phát hành thương mại (giấy phép AGPL).
- **Mức khó**: thấp–trung bình.

### Tính năng 5 — Nhận dạng và sửa chữ, khớp font

**a) Nhận dạng chữ Việt–Anh trên thiết bị (OCR)**

| Lựa chọn | Ghi chú |
|---|---|
| Tesseract (gói `vie` + `eng`) | Apache 2.0; chạy mọi nền tảng; ổn với bản in sạch, kém hơn với ảnh chụp |
| PaddleOCR (qua ONNX Runtime) | Apache 2.0; chất lượng tốt; mức hỗ trợ tiếng Việt cần kiểm tra lại |
| VietOCR | Chuyên tiếng Việt, nhận dấu tốt; giấy phép, độ nặng và khả năng chuyển sang ONNX cần kiểm tra |
| ML Kit (Android, iOS) / Apple Vision (iOS, macOS) | Nhanh, miễn phí; không có trên Windows; mức hỗ trợ dấu tiếng Việt cần kiểm tra |

Đề xuất: một mô hình chạy qua ONNX Runtime để giống nhau trên cả ba nền tảng; trên PC dùng bản mô hình lớn hơn vì máy mạnh hơn. Chọn mô hình cụ thể sau khi chấm trên bộ ảnh mẫu Việt–Anh.

**b) Sửa chữ mà giữ định dạng và khớp font**
- **Hướng A — Sửa trực tiếp trên ảnh** (sửa vài chữ, vài dòng):
  1. Xóa chữ cũ bằng vá nền (inpainting): OpenCV inpaint cho nền trắng sạch; mô hình LaMa (Apache 2.0) cho nền phức tạp — trên điện thoại cần thử tốc độ, trên PC chạy được tốt hơn.
  2. Đoán font: bộ phân loại chọn font gần nhất trong tập font giới hạn (Times New Roman, Arial, Calibri, Tahoma, và vài font sách phổ biến).
  3. Đo cỡ chữ từ chiều cao chữ thường và khoảng dòng; lấy màu mực trung vị của chữ lân cận.
  4. Vẽ chữ mới đúng đường cơ sở (baseline), thêm độ mờ và nhiễu nhẹ cho khớp ảnh chụp.
- **Hướng B — Tái dựng thành tài liệu chỉnh sửa được**: OCR + phân tích bố cục (đoạn, bảng, tiêu đề) → lớp văn bản sửa được; con dấu, chữ ký, hình minh họa giữ dưới dạng lớp ảnh. Phục vụ trực tiếp tính năng 6.

**Đánh giá khả thi thẳng thắn**
- *Làm tốt*: văn bản in máy, font phổ biến. Văn bản hành chính Việt Nam theo quy định thể thức dùng phông Times New Roman — trường hợp thuận lợi nhất.
- *Chỉ gần đúng*: font sách cũ, font trang trí, chữ in mờ, trang cong chưa nắn hết; cỡ và độ đậm chữ có thể lệch nhẹ.
- *Chưa làm được tin cậy*: sửa chữ viết tay cho giống nét người viết; sửa chữ đè lên con dấu, chữ ký. Các mô hình sinh chữ trong ảnh (AnyText, TextDiffuser...) quá nặng để chạy trên điện thoại và chất lượng dấu tiếng Việt chưa được kiểm chứng.
- *Phương án thay thế*: chuyển sang hướng B và cho người dùng tự chọn font, cỡ chữ.

### Tính năng 6 — Điều chỉnh màu, font, lề, cỡ chữ, khổ giấy
- Trình soạn thảo trên bản tái dựng (hướng B): đổi font, cỡ, màu chữ, căn lề, khổ giấy (A4, A5, Letter); xem trước tức thì; xuất PDF và DOCX.
- Phải nhúng font Unicode vào PDF để dấu tiếng Việt hiển thị đúng trên mọi máy.
- Trên điện thoại ưu tiên chỉnh nhanh (font, cỡ, lề); chỉnh chi tiết bố cục, bảng biểu làm tốt nhất trên PC.
- **Mức khó**: trung bình–cao (phụ thuộc chất lượng phân tích bố cục).

---

## 2. Tổng hợp khả thi

| Tính năng | Khả thi | Ghi chú |
|---|---|---|
| 1. Chụp, xuất PDF | Cao | Camera trên PC cần thử sớm |
| 2. Làm sáng nền, giữ màu | Cao | Tinh chỉnh theo ảnh thật |
| 3. Xoay, nắn phẳng, gộp | Cao (phẳng) / Trung bình (trang sách cong) | Trang cong là ưu tiên của thủ thư |
| 4. Tự xử lý file nhận | Cao | Giới hạn bộ nhớ trên iOS |
| 5. Sửa chữ khớp font | Trung bình với chữ in; thấp với chữ tay | Rủi ro nhất; xử lý trên thiết bị làm khó thêm |
| 6. Chỉnh định dạng | Trung bình | Phụ thuộc phân tích bố cục |

---

## 3. Kiến trúc

**Thành phần**
- *Giao diện*: Flutter (Dart) cho Android, iOS, Windows (macOS nếu cần).
- *Lõi xử lý ảnh*: C++ với OpenCV, gọi qua FFI (giao tiếp hàm gốc), một mã dùng chung cả ba nền tảng.
- *Chạy mô hình học máy*: ONNX Runtime (có bản cho điện thoại và máy tính); mô hình lượng tử hóa cho điện thoại, bản đầy đủ cho PC.
- *PDF*: thư viện `pdf` (ghi), PDFium (đọc, kết xuất trang).
- *Lưu trữ*: SQLite cho danh sách tài liệu và lịch sử chỉnh sửa; file lưu trong vùng riêng của ứng dụng, có mã hóa.
- *Không có máy chủ*: mô hình được đóng gói cùng ứng dụng hoặc tải một lần khi cài, sau đó chạy ngoại tuyến hoàn toàn.

**Luồng dữ liệu**
```
Chụp ảnh / Nhận file chia sẻ / Thư mục theo dõi (PC)
        │  (PDF → kết xuất từng trang thành ảnh)
        ▼
Tìm mép giấy → Sửa phối cảnh → Tách trang đôi → Nắn cong
→ Xoay đúng chiều → Sửa nghiêng                                 (tính năng 3)
        ▼
Ước lượng nền → Chia nền → Giữ màu mực → Tăng tương phản        (tính năng 2)
        ▼
Xem lại, sắp xếp trang ──► Xuất PDF gộp                         (tính năng 1, 3)
        ▼ (khi người dùng muốn sửa)
OCR Việt–Anh + phân tích bố cục
   ├─► Hướng A: sửa trên ảnh (vá nền + vẽ chữ khớp font)        (tính năng 5)
   └─► Hướng B: bản tái dựng → trình soạn thảo                   (tính năng 5, 6)
        ▼
Xuất PDF (có lớp chữ tìm kiếm được) / DOCX
```

---

## 4. Chia giai đoạn

Thời gian ước tính cho nhóm 3 người, mang tính tham khảo; điều chỉnh sau giai đoạn 0.

| Giai đoạn | Nội dung | Thời gian |
|---|---|---|
| 0. Chuẩn bị | Thu 300–500 trang thật: công văn có dấu đỏ, mực xanh; trang sách cong, giấy vàng; văn bản Việt và Anh; dựng khung dự án, lõi C++; thử camera trên PC | 2–3 tuần |
| 1. MVP | Tính năng 1, 2, 3 (phối cảnh, nghiêng, xoay, tách trang đôi), 4; xuất PDF gộp — trên cả ba nền tảng | 10–12 tuần |
| 2. Nhận dạng và sửa chữ | OCR Việt–Anh trên thiết bị; PDF có lớp chữ; sửa chữ hướng A với tập font giới hạn | 6–8 tuần |
| 3. Chỉnh sửa định dạng | Phân tích bố cục, hướng B, trình soạn thảo tính năng 6, xuất DOCX; nắn trang sách cong | 8–10 tuần |
| 4. Hoàn thiện | Tối ưu tốc độ, dùng thử với nhóm hành chính và thư viện, sửa lỗi, phát hành | 4 tuần |
| **Tổng** | | **khoảng 8–9 tháng** |

Thêm PC kéo dài MVP khoảng 2 tuần nhưng đổi lại có môi trường mạnh để chạy OCR và vá nền chất lượng cao.

---

## 5. Rủi ro và kiểm thử

### Rủi ro chính
| Rủi ro | Hướng xử lý |
|---|---|
| OCR sai dấu tiếng Việt, lẫn Việt–Anh | Chấm nhiều mô hình trên bộ mẫu; cho người dùng sửa tay kết quả nhận dạng |
| Mô hình quá nặng cho điện thoại khi không có máy chủ | Lượng tử hóa; chia mô hình nhẹ (điện thoại) và đầy đủ (PC); giới hạn tính năng nặng trên máy yếu |
| Dung lượng cài đặt lớn do đóng gói mô hình | Tải mô hình theo nhu cầu một lần sau khi cài |
| Chữ sửa không khớp font | Tập font giới hạn; luôn có xem trước và hoàn tác; chuyển sang hướng B khi không đạt |
| Khác biệt giữa ba nền tảng | Lõi xử lý C++ dùng chung; kiểm thử tự động cùng bộ ảnh trên cả ba |
| Giấy phép thư viện, mô hình | Kiểm tra từng giấy phép trước khi dùng; tránh AGPL |
| **Sửa chữ trên văn bản có dấu, chữ ký có thể bị lợi dụng làm sai lệch giấy tờ** | Ghi dấu "đã chỉnh sửa" vào siêu dữ liệu PDF; lưu lịch sử chỉnh sửa; không cho sửa vùng chồng lên con dấu, chữ ký |

### Bảo mật dữ liệu
- Tài liệu không rời thiết bị; ứng dụng không cần kết nối mạng sau khi đã có mô hình.
- File lưu trong máy được mã hóa; không thu thập nội dung tài liệu.

### Tiêu chí kiểm thử (đề xuất, tinh chỉnh sau giai đoạn 0)
| Tính năng | Tiêu chí đạt |
|---|---|
| 1 | Xử lý và lưu một trang dưới 2 giây trên điện thoại tầm trung, dưới 1 giây trên PC |
| 2 | Nền gần trắng tuyệt đối trên ≥ 95% diện tích nền; dấu đỏ, mực xanh giữ sắc độ (lệch hue ≤ 10°); không chữ màu nào bị chuyển thành đen |
| 3 | Góc nghiêng còn lại < 0,5°; không mất chữ ở mép (số ký tự OCR sau cắt không ít hơn trước); xoay đúng chiều ≥ 99%; tách trang đôi đúng ≥ 95% |
| 4 | Xử lý đúng PDF 50 trang và lô 20 ảnh nhận từ Zalo, email; trên PC tự xử lý file mới trong thư mục theo dõi |
| 5 | Tỉ lệ lỗi ký tự (CER) < 3% với văn bản in tiếng Việt và tiếng Anh; người đánh giá không nhận ra chữ đã sửa trong ≥ 80% trường hợp font Times New Roman |
| 6 | PDF xuất ra mở đúng trên Adobe Acrobat, Foxit và trình xem của điện thoại; dấu tiếng Việt hiển thị đúng; lề, khổ giấy đúng thông số |

---

**Cần kiểm tra lại trước khi chốt công nghệ**: mức hỗ trợ tiếng Việt của PaddleOCR, ML Kit, Apple Vision; giấy phép và độ nặng của VietOCR, DocTr, UVDoc; tốc độ LaMa trên điện thoại; hỗ trợ camera của Flutter trên Windows.
