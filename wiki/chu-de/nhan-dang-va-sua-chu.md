---
type: chu-de
---
# Nhận dạng và sửa chữ (tính năng 5, 6)

## Nhận dạng (OCR)
- Lựa chọn trong kế hoạch: Tesseract (`vie` + `eng`), PaddleOCR qua ONNX Runtime, VietOCR, ML Kit / Apple Vision; chọn sau khi chấm trên bộ ảnh mẫu ([[ke-hoach-ung-dung]]).
- Nguyên mẫu dùng [[tesseract-ocr]]: OCR Việt–Anh, PDF có lớp chữ tìm kiếm được, xuất .txt ([[readme]]).
- Đã kiểm chứng: chạy `vie+eng` mất dấu nặng; chạy riêng `vie` đọc gần đúng hết, kể cả dòng tiếng Anh → mặc định `vie` (`CLAUDE.md`, `NHAT-KY.md` dự án).
- PDF kết quả mẫu vẫn còn lỗi nhỏ ở lớp chữ ([[du-lieu-kiem-thu]]).

### Bản Android 0.2.0 (cập nhật 2026-10-29)
- Đã có OCR trên Android (trước đây ghi "bản Android chưa có OCR"): Tesseract 5.5.1 qua Tesseract4Android (`.aar`), gọi qua kênh `xlpdf/nhan_dang` trong `MainActivity.kt`, trả hOCR; `lib/loi/nhan_dang.dart` đọc thành dòng, từ, vị trí, góc chữ ([[readme-ung-dung-flutter]], [[tesseract-ocr]]).
- Dữ liệu `vie` (không dùng `vie+eng`, cùng lý do với bản PC) ([[readme-ung-dung-flutter]]).
- Giao diện: nút *Văn bản* (một trang) ở màn Chỉnh trang, nhận dạng cả hồ sơ ở màn Các trang; xem, chọn, chép, chia sẻ chữ. Kết quả lưu đệm theo ảnh trang; trang xử lý lại thì nhận dạng lại ([[readme-ung-dung-flutter]]).
- Xuất: *Thêm lớp chữ* (chữ ẩn đặt đúng vị trí, phông DejaVu Sans nhúng phần chữ đã dùng) và *Xuất kèm .txt*. Bản PC ghi lớp chữ bằng reportlab ([[readme]]), bản Android bằng thư viện `pdf` của Dart ([[readme-ung-dung-flutter]]).
- Kiểm thử trên máy ảo: chữ nhận dạng trùng 99,4% ký tự với Tesseract trên PC (đáp án `mau1.txt` là đầu ra Tesseract PC, không phải chữ chuẩn); PDF lớp chữ: PDFium chép được chữ, tìm được "CỘNG HÒA", "đóng dấu đỏ"; chữ ẩn lệch ngang trung vị 0,9 pt so với chữ trên ảnh ([[du-lieu-kiem-thu]], [[kiem-thu]]).
- Ảnh chụp kém tổng hợp: nhận dạng đúng 71% → 91,6% sau khi thêm khử nhiễu ([[lam-sach-giu-mau]]).
- Tốc độ: khoảng 2,5 giây một trang trên máy ảo sau khi đặt `OMP_THREAD_LIMIT=1` (NHAT-KY ghi 2,3–3 giây); chưa đo trên điện thoại thật ([[tesseract-ocr]]).

## Sửa chữ khớp font
- Hướng A, sửa trên ảnh: vá nền (OpenCV inpaint hoặc LaMa) → đoán font trong tập giới hạn (Times New Roman, Arial, Calibri, Tahoma…) → đo cỡ, lấy màu mực lân cận → vẽ chữ đúng đường cơ sở ([[ke-hoach-ung-dung]]).
- Hướng B, tái dựng tài liệu chỉnh sửa được (OCR + bố cục; dấu, chữ ký giữ dạng ảnh), phục vụ tính năng 6 ([[ke-hoach-ung-dung]]).
- Khả thi: tốt với văn bản in, font phổ biến (văn bản hành chính dùng Times New Roman); gần đúng với font sách cũ; chưa tin cậy với chữ tay, chữ đè dấu ([[ke-hoach-ung-dung]]).
- Rủi ro lạm dụng làm sai lệch giấy tờ → ghi dấu "đã chỉnh sửa", không cho sửa vùng chồng dấu, chữ ký ([[ke-hoach-ung-dung]]).
- Trạng thái (đến 2026-10-29): nguyên mẫu **chưa có** sửa chữ và trình soạn thảo định dạng; bước gợi ý tiếp theo là hướng A (vá nền + vẽ chữ Times New Roman) (`CLAUDE.md` dự án; [[readme]]). Bản Android 0.2.0 cũng chưa có sửa chữ khớp font ([[readme-ung-dung-flutter]]).

### Hướng A trên nguyên mẫu PC (cập nhật 2026-10-30)
Đã có trong cửa sổ Sửa PDF ([[cua-so-sua-pdf]]); thay cho trạng thái "chưa có sửa chữ" ở trên. Trình soạn thảo định dạng (hướng B, tính năng 6) vẫn chưa có ([[readme]]).
- **Tìm từ**: Tesseract `image_to_data` (`NHAT-KY.md` dự án, 2026-10-30).
- **Lấy nét mực chữ cũ**: thành phần liên thông chạm khung từ; nhận cả nét nhỏ sát trên/dưới khung (trong 1/4 chiều cao chữ), vì Tesseract có khi để dấu hỏi, dấu nặng ra ngoài khung (`NHAT-KY.md` dự án, 2026-10-30).
- **Đoán phông**: trong tập Times New Roman, Arial × thường, đậm, nghiêng, đậm nghiêng. Vẽ thử chính chữ cũ ở từng phông rồi so hình (giao/hợp). Tập này hẹp hơn tập kế hoạch (Times New Roman, Arial, Calibri, Tahoma…) ([[ke-hoach-ung-dung]]; `NHAT-KY.md` dự án, 2026-10-30).
- **Cỡ** theo chiều cao nét; **màu** theo lõi nét; **độ nhòe** theo độ sắc cạnh nét. Lúc đầu chọn độ nhòe bằng so hình nhưng luôn ra nhòe nhất (chữ vẽ thử lệch vài phần điểm ảnh), nên đổi sang so độ sắc cạnh (`NHAT-KY.md` dự án, 2026-10-30).
- **Vá nền** bằng `cv2.inpaint` (kế hoạch nêu OpenCV inpaint hoặc LaMa; nguyên mẫu dùng OpenCV) ([[ke-hoach-ung-dung]]; `NHAT-KY.md` dự án, 2026-10-30).
- **Dồn dòng**: dồn nét mực phần sau của dòng khi chữ mới dài, ngắn hơn; dòng căn giữa dồn đều hai bên (thêm sau khi thấy tiêu đề căn giữa bị lệch trái) (`NHAT-KY.md` dự án, 2026-10-30).
- **Vẽ chữ mới** siêu mẫu 4× rồi thu nhỏ: khử răng cưa, đặt chữ chính xác tới 1/4 điểm ảnh (`sua_noi_dung.py`).
- Người dùng có thể ép phông, kiểu ở khung *Chữ* thay cho *Tự đoán*; kết quả đoán báo ở thanh trạng thái ([[readme]]).
- **Chặn con dấu, chữ ký**: không cho sửa vùng có mực màu ([[readme]]; `sua_noi_dung.py`). Đúng biện pháp chống lạm dụng trong [[ke-hoach-ung-dung]].
- **Ghi dấu đã chỉnh sửa**: PDF lưu ra ghi ở thuộc tính Subject là đã chỉnh sửa nội dung, kèm số chỗ sửa ([[readme]], [[cua-so-sua-pdf]]).
- Kết quả kiểm chứng: dấu thanh ngoài khung từng làm đoán nhầm Arial đậm nghiêng 10,9 pt; sau khi sửa đoán đúng Times 14,1 pt (thật 14 pt). Trên trang công văn mẫu: đoán đúng Times thường (thân bài), Times đậm (tiêu đề) ([[kiem-thu]]; `NHAT-KY.md` dự án, 2026-10-30).
- Giới hạn: chữ sửa chỉ trên một dòng, không tự xuống dòng (có cảnh báo vượt lề); chưa thử ảnh chụp, PDF thật; chưa đo tiêu chí "≥ 80% chữ sửa không bị nhận ra" của kế hoạch ([[kiem-thu]]). Bản Android chưa có sửa chữ (`NHAT-KY.md` dự án, 2026-10-30). Cập nhật 2026-10-30 (lần 2): đã dàn được nhiều dòng theo khối, bản Android 0.4.0 đã có sửa chữ (mục dưới).

### Sửa theo khối, gõ tại chỗ (cập nhật 2026-10-30, lần 2)
Người dùng yêu cầu gộp chữ cùng dòng, dòng cùng đoạn thành một khối, sửa cả khối; nếu được thì gõ ngay trên trang; làm cho cả PC và APK ([[yeu-cau-nguoi-dung]]). Cách cũ ở mục trên là sửa theo từ, chữ mới chỉ trên một dòng, qua hộp thoại.

**Nguyên mẫu PC** ([[cua-so-sua-pdf]]):
- Nhận khối: `tim_khoi` gộp từ theo đoạn của Tesseract; đoán căn lề (trái, giữa, đều hai bên, phải) và thụt đầu dòng (`NHAT-KY.md` dự án, 2026-10-30, mục sửa theo khối).
- Nhận căn đều: lúc đầu đoạn 2 dòng căn trái bị nhận nhầm căn đều (với 2 dòng, "các dòng trừ dòng cuối chạm lề phải" luôn đúng). Đã đổi điều kiện: đuôi các dòng phải trùng nhau (lệch ≤ 0,6% bề rộng trang) và khoảng trống giữa từ giãn rộng hơn dòng cuối ≥ 12% (`NHAT-KY.md` dự án, 2026-10-30, mục sửa theo khối).
- Thao tác `SuaKhoi`: đoán phông, cỡ, màu theo dòng dài nhất; đo khoảng cách dòng theo đường chân chữ; xóa nét cả khối; dàn lại chữ mới (ngắt dòng theo từ, Enter là ngắt cứng, căn như cũ); số dòng đổi thì dời phần trang bên dưới. Giữ `SuaChu` (theo từ) cho tương thích (`NHAT-KY.md` dự án, 2026-10-30, mục sửa theo khối).
- Cỡ chữ: trước đây cỡ theo chiều cao nét (mục trên). Khi dàn lại, chữ rộng hơn gốc khoảng 3% (chiều cao nét chỉ vài chục điểm ảnh) nên ngắt dòng sớm. Nay dòng dài chỉnh cỡ theo bề rộng cả dòng; ngắt đúng chỗ cũ (`NHAT-KY.md` dự án, 2026-10-30, mục sửa theo khối).
- Dòng đơn căn trái dài thêm: trước giới hạn bằng độ dài dòng cũ nên bị ngắt dòng; nay cho dàn tới mép phải vùng chữ của trang (`NHAT-KY.md` dự án, 2026-10-30, mục sửa theo khối).
- Giao diện: bấm khối mở ô gõ ngay trên trang, cùng phông, cỡ, màu, căn lề, khoảng cách dòng theo tỉ lệ phóng; Ctrl+Enter hoặc bấm ra ngoài để áp, Esc hủy. Bỏ hộp thoại sửa chữ cũ ([[readme]]; `NHAT-KY.md` dự án, 2026-10-30, mục sửa theo khối).
- Kiểm thử mục 1b: quốc hiệu, tiêu ngữ thành một khối 2 dòng căn giữa; đoạn "Căn cứ…" là khối 2 dòng căn trái; viết thêm một câu → 4 dòng, dòng đầu ngắt đúng chỗ cũ, phần dưới dời 150 px nguyên vẹn, phần trên không đổi; tiêu đề dài hơn vẫn đậm, căn giữa (lệch 1 px) ([[kiem-thu]]).
- Chưa làm: khối có chữ đậm, nghiêng lẫn trong đoạn sẽ ra một kiểu chữ; dời phần dưới theo cả bề ngang trang, nên cột bên cạnh, con dấu cũng dời theo (`NHAT-KY.md` dự án, 2026-10-30, mục sửa theo khối).

**Bản Android 0.4.0** ([[ban-android-flutter]], [[readme-ung-dung-flutter]]):
- Khối: đoạn theo `ocr_par` của hOCR, hoặc dòng đứng riêng (tiêu đề). Dòng ngắt cứng (hai dòng quốc hiệu, mỗi câu một dòng) giữ xuống dòng.
- Phông: 8 phông Liberation Serif / Sans × thường, đậm, nghiêng, đậm nghiêng, cùng kích thước chữ với Times New Roman, Arial ([[giay-phep-thu-vien]]). Người dùng chọn được 8 phông hoặc để tự đoán.
- Đoán phông: vẽ thử chữ cũ của dòng dài nhất bằng 8 phông, ở cỡ khớp bề rộng nét mực; so hình nét (giao / hợp, làm mờ nhẹ) và chiều cao. Độ đậm: viền mảnh thêm vào cho bằng diện tích mực bản gốc.
- Xóa chữ: tô màu nền (trung vị điểm không phải mực quanh khối). Khác PC (`cv2.inpaint`), vì module `photo` của OpenCV bị loại khi dựng.
- Dàn chữ bằng dart:ui; khối một dòng khi dài ra dùng khoảng cách dòng chung của trang (trung vị các đoạn nhiều dòng), không có thì 1,2 × cỡ chữ. Số dòng đổi thì dời phần dưới; tràn mép dưới vẫn làm và báo.
- Mỗi lần sửa lưu ảnh PNG mới (sửa nhiều lần không mất chất lượng), giữ ảnh cũ để hoàn tác; chữ mới ghi luôn vào đệm nhận dạng, lớp chữ PDF dùng bản này.
- Khóa khối có mực màu (con dấu, chữ ký, bút phê); PDF xuất ghi Subject "Đã chỉnh sửa nội dung…". Dòng gợi ý liệt kê chữ máy đọc chưa chắc, vì cả khối được viết lại nên cần soát (`NHAT-KY.md` dự án, 2026-10-30).
- Kiểm thử `sua_chu_test.dart` 7/7: đoán Liberation Serif thường khoảng 14,4 pt (thân bài), đậm khoảng 15,3 pt (tiêu đề); 300–770 ms một khối; "Kính gửi…" 1 → 2 dòng, dời 75 px, đọc lại đúng 100%; tiêu đề căn giữa lệch 0,5 px; đoạn 3 → 4 dòng không chồng chữ, đọc lại 99,2%; bút phê đỏ và tên ký đè con dấu bị khóa ([[kiem-thu]]).

**Khác nhau giữa hai bản, chưa làm:**
- Cách nhận căn lề khác một chút: đoạn "Căn cứ…" bản Android nhận là căn đều, bản PC nhận là căn trái (`NHAT-KY.md` dự án, 2026-10-30).
- Phông: PC dùng Times New Roman, Arial của máy; Android dùng Liberation đóng gói ([[giay-phep-thu-vien]]).
- Android chưa thử điện thoại thật; bấm thử bằng adb chỉ gõ được chữ không dấu; chưa thử trang sách (2 ảnh), xóa trắng cả khối, nền màu, chữ viết tay (`NHAT-KY.md` dự án, 2026-10-30).
- Cả hai bản vẫn chưa thử ảnh chụp, PDF thật; chưa đo tiêu chí "≥ 80% chữ sửa không bị nhận ra" ([[kiem-thu]]).

### Sửa ký tự giữ nguyên bản gốc (cập nhật 2026-10-30, lần 3)
- Người dùng thử sửa theo khối trên tệp thật và nhận xét: mất hết định dạng, cỡ chữ, OCR sai nội dung. Yêu cầu mới: giữ nguyên nội dung, hình dạng, kích thước bản scan, chỉ thêm, bớt ký tự ([[yeu-cau-nguoi-dung]]).
- Nguyên nhân: cách khối viết lại cả khối từ chữ máy đọc rồi vẽ bằng phông, nên đọc sai đâu sai đó; dáng chữ scan (hẹp, đậm, nhòe) không có trong bộ phông (`NHAT-KY.md` dự án, 2026-10-30, mục "Sửa ký tự giữ nguyên bản gốc").
- Hướng mới trên PC: [[sua-ky-tu]], chữ không sửa giữ nguyên từng điểm ảnh, ký tự chèn chép nguyên hình từ tài liệu. Cách viết lại khối giữ lại làm công cụ phụ "Viết lại cả khối chữ (vẽ lại bằng phông)".
- Ý cũ ở các mục trên (hướng A khớp phông, sửa theo khối) vẫn đúng cho công cụ phụ và bản Android 0.4.0.

### Đối tượng, vùng scan, chú thích (cập nhật 2026-10-30, lần 4)
Tham khảo ONLYOFFICE DesktopEditors, chỉ học cách làm ([[onlyoffice-desktopeditors]]). Phần liên quan tới tính năng 5, 6 trên nguyên mẫu PC:
- Chữ đã thêm thành đối tượng chọn lại được: bấm đúp để sửa chữ; đổi phông, kiểu, cỡ, màu ở khung *Chữ* áp ngay cho chữ đang chọn; dời, đổi cỡ bằng chuột ([[doi-tuong-tren-trang]]). Đây chỉ là định dạng chữ do người dùng thêm, chưa phải trình soạn thảo định dạng cho chữ của bản gốc.
- Dời, đổi cỡ, xóa vùng có sẵn trên bản scan (mỗi dòng chữ, ảnh, bảng một vùng): nét mực gốc chép nguyên, không vẽ lại bằng phông, đúng yêu cầu giữ nguyên bản scan; vùng có mực màu bị khóa ([[doi-tuong-tren-trang]], [[yeu-cau-nguoi-dung]]).
- Chú thích (ghi chú, bút phê…) không sửa nội dung trang, không ghi dấu "đã chỉnh sửa" ([[chu-thich-pdf]]).
- Trình soạn thảo định dạng (hướng B, tính năng 6) **vẫn chưa có**; README dòng 6 vẫn ghi chưa có ([[readme]]).

## OCR thành chức năng riêng (bản Android 0.7.1, 2026-11-14)
- Người dùng: ảnh chụp kém thì OCR kém, sai; yêu cầu tách OCR ra riêng, không làm ngay khi xuất ([[yeu-cau-nguoi-dung]]).
- Xuất PDF không còn tự nhận dạng (bỏ "Thêm lớp chữ", "Xuất kèm .txt" ở màn Xuất). Nút *Nhận dạng chữ* ở màn Các trang: xem, chép, chia sẻ, lưu .txt, *PDF có chữ* (xuất kèm lớp chữ ẩn); báo trang có độ tin cậy trung bình dưới 70% để chụp lại ([[ban-android-flutter]]).
