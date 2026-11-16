# Ứng dụng xử lý PDF ảnh

Ứng dụng quét, làm sạch, nắn phẳng, nhận dạng và chỉnh sửa tài liệu. Mọi xử lý chạy trên máy, không gửi dữ liệu đi đâu.

## Lấy dự án về máy khác
Dự án nằm ở hai kho GitHub công khai (mã Flutter để riêng vì Gradle lỗi với đường dẫn có dấu):
- Tài liệu, nhật ký, wiki, nguyên mẫu PC: https://github.com/haianhhadang-collab/xu-ly-pdf-anh
- Mã ứng dụng Flutter (Android, iOS): https://github.com/haianhhadang-collab/xu-ly-pdf-anh-flutter
- Tệp APK mới nhất: mục *Releases* của kho Flutter (tải thẳng trên điện thoại Android).

```bash
git clone https://github.com/haianhhadang-collab/xu-ly-pdf-anh.git "Xử lý PDF"
git clone https://github.com/haianhhadang-collab/xu-ly-pdf-anh-flutter.git xlpdf
```

Trên Windows đặt `xlpdf` ở đường dẫn không dấu (ví dụ `D:\DevTools\src\xlpdf`), rồi tạo lại liên kết `ung-dung-flutter` trong thư mục dự án nếu cần (`mklink /J ung-dung-flutter D:\DevTools\src\xlpdf`).

Không có trên kho: các tệp APK (`apk/`); kết quả và ảnh chụp của người dùng (`ket-qua/`, `ung-dung/kiem_thu/trang_sach/`, bộ ảnh thử `D:\DevTools\src\xlpdf_kiemthu`); ảnh thử tổng hợp sinh lại được bằng `python ung-dung/kiem_thu/tao_anh_mep.py`, `tao_anh_sach_mo.py`.

## Nội dung thư mục
- `01-prompt-ke-hoach.md`: prompt lập kế hoạch.
- `02-ke-hoach-ung-dung.md`: bản kế hoạch phát triển (Flutter + C++/OpenCV cho Android, iOS, PC).
- `03-tu-dong-chup.md`: đặc tả chế độ tự động chụp và cách chuyển sang Android, iOS.
- `thiet-ke-giao-dien/`: bản thiết kế 5 màn hình điện thoại (Claude Design, canvas *Giao diện Xử lý PDF ảnh – Android*).
- `ung-dung-flutter/`: **bản Android** (Flutter + OpenCV). Đây là liên kết tới `D:\DevTools\src\xlpdf`; xem README trong đó.
- `apk/xu-ly-pdf-anh-0.6.0.apk`: tệp cài đặt Android dựng sẵn, bản mới nhất (0.3.0 chưa có sửa chữ; 0.2.0 chưa có đánh số trang; 0.1.0 chưa có nhận dạng chữ).
- `ung-dung/`: **nguyên mẫu chạy được trên Windows** (Python + OpenCV + Tesseract), làm trước để thử thuật toán trên ảnh thật rồi mới chuyển sang C++/Flutter.
- `NHAT-KY.md`: nhật ký dự án.

## Cài bản Android
- Chép `apk/xu-ly-pdf-anh-0.6.0.apk` sang điện thoại (Android 7 trở lên, 64-bit) rồi mở tệp. Nếu máy hỏi, cho phép *cài ứng dụng không rõ nguồn gốc*. Cài đè lên bản cũ được, hồ sơ cũ vẫn giữ.
- Bản này đang ký bằng khóa thử nghiệm. Muốn phát hành qua cửa hàng thì cần ký lại.
- Bản mới nhất: `apk/xu-ly-pdf-anh-0.7.9.apk` (cài đè lên bản cũ, hồ sơ vẫn giữ).
- Bản 0.7.9: báo nhòe, tay che **ngay trên màn camera** sau mỗi ảnh (thanh cam, nút *Chụp lại* thay ảnh vừa rồi); rung báo khi máy đã chụp xong; báo trang chụp trùng ở Xem nhanh, có nút xóa.
- Bản 0.7.8: báo trang nên chụp lại (chữ nhòe, tay che trang) ở màn Xem nhanh, kèm nút *Chụp lại* (biểu tượng máy ảnh): chụp một ảnh thay trang đó, trang giữ nguyên chỗ.
- Bản 0.7.7: tách cặp trang sách giữa khe gáy (không còn dính chữ trang bên, mất chữ đầu dòng); lề mặc định "Vừa" (Cài đặt › Lề trang: Sát chữ / Vừa / Giữ cả trang), trang ít chữ giữ khổ trang; *Chụp xong mới xử lý* (bật sẵn): lúc chụp chỉ lưu ảnh gốc, rời màn camera mới cắt, nắn, làm sạch; nút *Xử lý lại cả hồ sơ* (đũa thần, màn Các trang) chạy lại mọi trang từ ảnh gốc, không phải chụp lại.
- Bản 0.6.0: đổi phông, cỡ chữ một đoạn khi *Sửa ký tự*. Đang sửa dòng, chạm giữ rồi kéo trong dòng (hoặc bật nút Bôi chọn cạnh ô gõ rồi dùng ← →) để chọn một đoạn; thanh định dạng hiện ra: A− / A+ đổi cỡ từng 0,5 pt bằng cách phóng, thu chính nét chữ gốc; menu phông vẽ lại riêng đoạn đó bằng một trong 8 phông Liberation, cùng màu mực (chọn *Giữ nét gốc* để trả về). Chữ gõ thêm ngay sau đoạn đã đổi theo định dạng đó. Bản PC: kéo chuột hoặc Shift + ← → rồi đổi Cỡ, Phông ở khung Chữ.
- Bản 0.5.2: gõ tiếng Việt khi sửa ký tự không còn lẫn phông, lẫn đậm nhạt. Chữ chèn chọn mẫu theo độ đậm nét của các chữ ngay quanh chỗ chèn và tô theo màu mực ở đó. Chữ có dấu không có sẵn (hoặc chỉ có ở chữ đậm) được ghép từ thân chữ và dấu chép trên trang. Bàn phím gõ dấu rời cũng ra đúng chữ.
- Bản 0.5.1: sửa ký tự trên ảnh chụp có dòng nghiêng, dòng sát nhau. Chữ chèn và phần chữ dời đi nằm đúng hàng chữ của dòng; chữ không sửa, kể cả dòng trên, dòng dưới, giữ nguyên. Khung dòng và con trỏ đỏ vẽ nghiêng theo dòng.
- Bản 0.5.0: *Sửa ký tự (giữ nguyên bản gốc)* thành cách sửa chữ mặc định, như bản PC: chạm vào dòng để đặt con trỏ đỏ, dùng các nút ← → ⌫ ⌦, gõ chữ vào ô rồi bấm *Chèn*, xong thì bấm *Xong* (hoặc *Hủy*). Chữ không sửa giữ nguyên từng điểm ảnh; ký tự chèn được chép nguyên hình từ chính trang, không có thì lấy ở trang khác, khi đó ký tự có viền vàng, chạm giữ vào một ký tự đúng như vậy trên trang để chọn làm mẫu. Dãy chấm mục lục tự co giãn để số trang đứng nguyên chỗ. Cách cũ đổi tên thành *Vẽ lại bằng phông*.
- Bản 0.4.0 thêm *Sửa chữ* ở màn Chỉnh trang: chạm một khối chữ (dòng hoặc đoạn), sửa ngay tại chỗ, bấm Xong; có Hoàn tác; không sửa được chỗ có con dấu, chữ ký.
- Bản 0.3.0 thêm *Đánh số trang* khi xuất PDF (chọn trang đầu được đánh số, lề trên/dưới, căn giữa/trái/phải/so le).
- Từ bản 0.2.0 có: nhận dạng chữ (xem, chép chữ; PDF có lớp chữ; xuất .txt), khử nhiễu và tăng tương phản chữ, tự xoay toàn bộ trang (theo chiều chữ, hoặc ép khổ dọc / ngang), hai chế độ *Tự chụp* / *Bấm chụp*, màn *Xem nhanh* đánh dấu trang ngược, nằm nghiêng, khác khổ. Chi tiết trong README của `ung-dung-flutter/`.

## Cài đặt và chạy nguyên mẫu PC
1. Cần Python 3.10 trở lên và Tesseract OCR có gói tiếng Việt (`vie`). Máy này đã có sẵn cả hai.
2. Chạy `ung-dung/cai-dat.bat` một lần để cài thư viện.
3. Mở ứng dụng bằng `ung-dung/chay-ung-dung.bat`. Muốn mở thẳng cửa sổ **Sửa PDF** thì chạy `ung-dung/sua-pdf.bat` (kéo tệp PDF thả lên tệp .bat cũng được).
4. Nếu muốn, chạy `ung-dung/them-vao-send-to.ps1` (chuột phải > Run with PowerShell) để thêm mục *Gửi tới > Xử lý PDF ảnh* vào menu chuột phải của File Explorer.

## Nguyên mẫu làm được gì

| Tính năng | Trạng thái trong nguyên mẫu |
|---|---|
| 1. Chụp ảnh, xuất PDF | Chụp từ webcam hoặc camera tài liệu (khung giấy hiện trực tiếp); **tự động chụp** khi trang đứng yên, rõ nét, đủ sáng, không chụp trùng trang; mở ảnh JPG, PNG, TIFF nhiều trang, HEIC, WebP; xuất PDF gộp |
| 2. Làm sáng nền, giữ màu | Nền trắng đều, xóa bóng đổ, chữ đen đậm; giữ màu dấu đỏ, chữ ký, mực xanh, bút phê. Có các chế độ giữ màu, xám, đen trắng; chỉnh được độ trắng nền và độ đậm chữ |
| 3. Xoay, nắn phẳng, gộp | Tự tìm mép giấy, sửa phối cảnh (tỉ lệ trang tính theo hình học phối cảnh, khớp A4), tự xoay 90°/180°, sửa nghiêng, tách trang đôi, xóa viền nền bàn. Chỉnh khung cắt bằng cách kéo 4 góc; sắp xếp, xoay, xóa trang. Từ 2026-11-14: bộ tìm mép kiểu CamScanner (`loi_xu_ly/tim_mep.py`, tìm được giấy trên bàn trắng, nền lộn xộn, giấy chồng giấy) và nắn trang cong theo dòng chữ (`loi_xu_ly/nan_cong.py`, ô *Nắn trang cong*). Đo: `kiem_thu/do_mep.py`, `kiem_thu/do_cong.py` trên ảnh tạo bằng `kiem_thu/tao_anh_mep.py`. Sách mở chụp sát, một trang lọt ra ngoài khung: bộ tìm mép nối thêm trang bên kia gáy tới biên ảnh, tự chụp nhắc lùi máy (2026-11-14, `kiem_thu/tao_anh_sach_mo.py`, `kiem_thu/kiem_thu_sach_mo.py`). Nắn vuông khối chữ: hai lề thẳng, vuông góc dòng chữ; cặp trang sách mở được xoay thẳng từng trang; khung tự tìm được nới 2,5% để không cắt lẹm vào chữ ở mép trang cong (2026-11-15). Nắn lại PDF có sẵn: `python nan_lai_pdf.py <tệp.pdf> [--tach]` hoặc kéo thả vào `nan-lai-pdf.bat`. Đo: `kiem_thu/do_le.py` |
| 4. Tự xử lý tệp nhận được | Kéo thả tệp vào cửa sổ, *Gửi tới* từ File Explorer, xử lý theo lô bằng dòng lệnh, thư mục theo dõi (tự xử lý tệp mới từ máy scan hoặc tệp tải từ Zalo, email) |
| 5. Nhận dạng, sửa chữ | Nhận dạng chữ Việt–Anh, tạo PDF có lớp chữ tìm kiếm được, xuất .txt. **Sửa ký tự giữ nguyên bản gốc** (cửa sổ Sửa PDF): thêm, bớt ký tự ngay trên bản scan, chữ cũ giữ nguyên, ký tự chèn chép nguyên hình từ chính tài liệu; dãy chấm mục lục tự co giãn; không cho sửa đè con dấu, chữ ký. Công cụ phụ: viết lại cả khối bằng phông |
| 6. Chỉnh định dạng | Chọn khổ giấy (A4, A5, Letter, Legal, theo tỉ lệ ảnh), lề, chất lượng ảnh khi xuất. **Chưa có** trình soạn thảo đổi font, cỡ chữ |

## Dùng giao diện
- **Chụp camera, tự động chụp**: bấm *Chụp camera*. Ô *Tự động chụp* bật sẵn: đặt trang dưới camera, giữ yên chừng một giây là ứng dụng tự chụp; lật trang là chụp trang tiếp theo. Dòng chữ ở cuối khung hình nhắc cần làm gì (lại gần, giữ yên, bật đèn…). Bấm Space để chụp tay. Có thể dùng điện thoại làm webcam (DroidCam, Iriun) để thử.
- **Mở tệp**: bấm *Mở ảnh, PDF…*, hoặc kéo thả tệp và thư mục vào cửa sổ. Trang được xử lý ngay theo tùy chọn ở cột phải.
- **Chỉnh khung cắt**: chọn trang, bật *Ảnh gốc và khung cắt*, rồi kéo 4 góc màu cam. Thả chuột là trang được xử lý lại. Nút *Giữ nguyên ảnh* dùng khi không muốn cắt.
- **Đổi tùy chọn làm sạch**: chỉnh xong thì bấm *Áp dụng trang chọn* hoặc *Tất cả*.
- **Xuất**: bấm *Xuất PDF…*. Nếu bật *Thêm lớp chữ*, PDF sẽ tìm kiếm và chép chữ được.

## Sửa PDF (cửa sổ riêng)
Mở bằng nút **✏ Sửa PDF…** trên thanh công cụ (hỏi có đưa các trang đang mở sang không) hoặc bằng `sua-pdf.bat`.
- **Sửa trang của PDF có sẵn**: mở hoặc kéo thả nhiều PDF, ảnh vào cửa sổ (gộp); chèn trang trắng; xoay ⟲ ⟳; đưa lên ▲, xuống ▼; xóa trang; *Lưu PDF…* hoặc *Lưu trang đang chọn ra tệp mới…* (tách). Trang chưa sửa nội dung được chép nguyên, không giảm chất lượng, giữ cả chữ chép được của tệp gốc.
  - Cách làm như ONLYOFFICE: **kéo thả ảnh trang** trong danh sách bên trái để đổi thứ tự (vạch cam chỉ chỗ thả, kéo được nhiều trang đã chọn); **bấm chuột phải lên ảnh trang** để xoay, chèn trang trắng trước / sau (cùng khổ với trang bên cạnh), chèn tệp trước / sau, nhân đôi, chép, cắt, dán, lưu ra tệp mới, xóa; **Ctrl+C / Ctrl+X / Ctrl+V** chép, cắt, dán trang, kể cả sang cửa sổ Sửa PDF khác (tệp khác) mở trong cùng một lần chạy chương trình (hai lần chạy `sua-pdf.bat` riêng thì không dán sang nhau được); Delete xóa trang.
- **Sửa ký tự, giữ nguyên bản gốc** (công cụ chính): chọn *Sửa ký tự (giữ nguyên bản gốc)*, chờ ứng dụng tìm dòng chữ (khung xanh nét đứt). Bấm vào đúng chỗ cần sửa trên dòng: con trỏ đỏ hiện ra. Phím ← → để di chuyển, Home/End về đầu/cuối dòng, **Backspace / Delete xóa ký tự**, **gõ để chèn** (gõ tiếng Việt bằng Unikey được), **Enter để xong**, Esc để hủy. Kết quả hiện ngay khi gõ. Gõ tiếng Việt: chữ chèn lấy mẫu cùng độ đậm nét với các chữ quanh chỗ chèn (dòng có chữ in đậm xen chữ thường không bị lẫn), tô theo màu mực ở đó; chữ có dấu không có sẵn thì ghép thân chữ với dấu chép trên trang; khung ký tự của máy đọc được nắn theo nét mực thật nên không chép nhầm nét chữ bên cạnh. Ảnh chụp có dòng nghiêng vẫn sửa được: ký tự chèn đặt theo đường chân nghiêng của dòng, chỉ nét của dòng đang sửa bị dời, dòng trên, dòng dưới giữ nguyên.
  - Chữ không sửa giữ nguyên từng điểm ảnh của bản scan (chỉ dời ngang khi chèn, xóa phía trước); ký tự chèn được **chép nguyên hình từ chính trang** (cùng cỡ, cùng nét, cùng độ nhòe), không có thì lấy ở trang khác của tệp, cả tệp không có mới vẽ bằng phông.
  - Ký tự có **viền vàng** là mẫu chưa chắc (lấy từ trang khác hoặc vẽ phông): **bấm chuột phải lên một ký tự đúng như vậy trên trang** để dùng làm mẫu.
  - Dòng mục lục có dãy dấu chấm dẫn: dãy chấm tự co giãn để số trang đứng nguyên chỗ (vd. "956" → "95" vẫn thẳng lề phải).
  - Máy đọc chữ (OCR) chỉ dùng để biết ranh giới từng ký tự; máy đọc sai cũng không làm đổi chỗ không sửa.
  - Trang PDF chỉ gồm một ảnh scan được sửa đúng trên ảnh gốc (không dựng lại, không phóng), lưu ra đúng kích thước, đúng chỗ cũ.
- **Viết lại cả khối chữ (vẽ lại bằng phông)**: công cụ phụ; gộp dòng, đoạn thành khối, gõ lại cả khối. Chữ được vẽ lại bằng Times New Roman / Arial nên **không giữ được dáng chữ bản scan**; chỉ dùng khi cần viết lại cả đoạn.
- **Thêm chữ**: bấm vào chỗ cần thêm, gõ ngay trên trang (nhiều dòng được), Ctrl+Enter để xong; phông, kiểu, cỡ (pt), màu chọn ở khung *Chữ*.
- **Che thông tin** (trắng hoặc đen), **Tô sáng**: kéo chuột quanh vùng. Chỗ bị che bị xóa hẳn khỏi trang khi lưu.
- **Chèn ảnh**: *Chọn ảnh để chèn…* rồi kéo chuột đặt ảnh (giữ tỉ lệ). Ô *Bỏ nền trắng* dùng cho ảnh chữ ký, con dấu chụp trên giấy trắng.
- **Vẽ hình**: chữ nhật, elip, đường, mũi tên; chọn loại, độ dày ở khung *Hình, che, chèn ảnh*, màu theo nút *Màu chữ*.
- **Chọn, dời, đổi cỡ** (như ONLYOFFICE): chữ đã thêm, ảnh đã chèn, khung che, tô sáng, hình vẽ, chú thích đều **chọn lại được** (viền tím): bấm để chọn, kéo để dời, kéo ô vuông ở góc, cạnh để đổi cỡ, Delete để xóa, phím mũi tên nhích 1 điểm ảnh (Shift: 10), Ctrl+C / Ctrl+V nhân bản; bấm đúp chữ đã thêm để sửa chữ, đổi phông, kiểu, cỡ, màu ở khung *Chữ* là áp ngay cho chữ đang chọn.
  - **Vùng có sẵn trên bản scan** (viền xám: mỗi dòng chữ, ảnh, bảng một vùng; muốn lấy nhiều dòng thì kéo khung trên chỗ trống) cũng dời, đổi cỡ, xóa được: nét mực gốc được chép nguyên sang chỗ mới, chỗ cũ vá nền; ngoài hai chỗ đó không đổi điểm ảnh nào. Vùng có mực màu (con dấu, chữ ký, bút phê; viền đỏ) bị khóa.
- **Chú thích (không sửa bản gốc)**: ghi chú (bấm chỗ đặt, gõ lời), bút phê (kéo khung, gõ lời; chữ nghiêng màu đỏ hoặc theo *Màu chữ*, cỡ theo *Cỡ (pt)*), tô sáng, chữ nhật, elip, mũi tên, dấu "ĐÃ XEM" kèm ngày (bấm chỗ đặt). Chú thích lưu thành **chú thích PDF chuẩn** (Acrobat, Foxit, trình duyệt hiện, ẩn, sửa, xóa được); trang gốc vẫn chép nguyên, tệp không bị ghi là "đã chỉnh sửa nội dung". Chọn, dời, xóa chú thích bằng công cụ *Chọn*; bấm đúp ghi chú, bút phê để sửa lời.
- Mỗi việc là một thao tác trong danh sách *Thao tác trên trang này*: xóa từng thao tác, Ctrl+Z hoàn tác, **Ctrl+Y làm lại**.
- Trang đã sửa nội dung được lưu dạng ảnh 300 dpi, có lớp chữ nếu bật ô *Lớp chữ cho trang đã sửa*. Tệp lưu ra ghi rõ trong thuộc tính PDF (Subject) là đã chỉnh sửa nội dung, kèm số chỗ sửa, để tránh bị lợi dụng làm sai lệch giấy tờ.

## Dùng dòng lệnh (xử lý theo lô, thư mục theo dõi)
```bash
cd ung-dung
python tu_dong.py xu-ly anh1.jpg cong-van.pdf thu-muc-anh -o ket-qua --ocr
python tu_dong.py xu-ly thu-muc-anh --gop ho-so.pdf --kho a4 --le 10 --ocr --txt
python tu_dong.py theo-doi "D:/May scan" -o "D:/Da xu ly" --ocr
```
Xem đủ tùy chọn bằng `python tu_dong.py xu-ly -h`.

## Kiểm thử
```bash
cd ung-dung/kiem_thu
python tao_anh_mau.py
python kiem_thu_loi.py
python kiem_thu_tu_chup.py
python kiem_thu_sua_pdf.py
```
Bộ ảnh mẫu tổng hợp gồm công văn chụp nghiêng trên bàn có bóng đổ, bản quét lộn ngược, và sách mở hai trang. Kết quả ảnh và PDF ghi vào `kiem_thu/ket_qua/`. Ảnh tổng hợp chưa thay được ảnh chụp thật: cần thu bộ ảnh thật (Giai đoạn 0 của kế hoạch) để tinh chỉnh ngưỡng.

## Cấu trúc mã
```
ung-dung/
  giao_dien.py        giao diện Windows (tkinter)
  sua_pdf.py          cửa sổ Sửa PDF (sửa trang, sửa chữ, thêm chữ, che, chèn ảnh, chú thích)
  sua_pdf_doi_tuong.py  công cụ Chọn, dời, đổi cỡ đối tượng và vùng có sẵn; làm lại
  sua_pdf_trang.py    thao tác trang: kéo thả, menu chuột phải, chép / dán trang giữa các cửa sổ
  tu_dong.py          xử lý theo lô, thư mục theo dõi
  loi_xu_ly/          lõi xử lý, sẽ chuyển sang C++
    lam_sach.py       tính năng 2
    nan_phang.py      tính năng 3
    nhan_dang.py      OCR (Tesseract)
    doc_ghi.py        đọc ảnh, PDF (PDFium); ghi PDF (reportlab, pypdf)
    quy_trinh.py      ghép các bước
    tu_chup.py        tự động chụp (xét điều kiện từng khung hình camera)
    sua_ky_tu.py      sửa ký tự giữ nguyên bản gốc: dòng, mảnh ký tự, chép ký tự mẫu, dãy chấm dẫn
    sua_noi_dung.py   sửa nội dung trang: viết lại khối bằng phông, thêm chữ, che, tô sáng, chèn ảnh
    doi_tuong.py      đối tượng chọn lại được (khung, dời, đổi cỡ), hình vẽ, tìm và dời vùng có sẵn trên bản scan
    chu_thich.py      chú thích không phá bản gốc: ghi chú, bút phê, tô sáng, hình, dấu "ĐÃ XEM" → chú thích PDF chuẩn
    tai_lieu_pdf.py   tài liệu để sửa: trang PDF gốc / ảnh / trắng, chèn, xóa, xoay, gộp, tách, chép / dán trang, lưu
  kiem_thu/           ảnh mẫu và kiểm thử
```
Theo kế hoạch, mã không dùng MuPDF (giấy phép AGPL): đọc PDF bằng PDFium, ghi PDF bằng reportlab và pypdf.

## Tự xoay ảnh chụp cầm máy ngang, xóa ngón tay (2026-11-14)
- `ung-dung/loi_xu_ly/chieu_chu.py`: nhận trang có dòng chữ chạy dọc; `xu_ly_anh` xoay 90° ngay sau nắn phối cảnh (khi bật tự xoay), sau đó Tesseract lật 180° nếu cần.
- `ung-dung/loi_xu_ly/cat_chu.py`: thêm xóa ngón tay màu da (`xoa_da_tay`, giữ nét chữ bị đè), vệt bóng cong, mẩu đen sát mép, đường gáy giữa hai trang; giữ tiêu đề cách xa thân bài.
- Kiểm thử: `python ung-dung/kiem_thu/kiem_thu_loi.py` (mẫu 2b: ảnh lệch 90°, 270°).

## Tự chụp nhanh hơn, nhận lật trang, tay trên trang (2026-11-14)
- `ung-dung/loi_xu_ly/tu_chup.py`: đo rung theo độ dời (cả khung và từng ô 4×4), thời gian chịu 0,4 giây cho khung lỗi lẻ, nhận động tác lật trang (ngưỡng trang mới 0,18 sau khi lật), không chụp khi tay đặt trên trang (`ti_le_tay`), giữ yên mặc định 0,5 giây.
- Kiểm thử: `python ung-dung/kiem_thu/kiem_thu_tu_chup.py` (mục tốc độ còn hỏng do bộ tìm mép cũ của bản PC, 132 ms/khung).

## Tách cặp trang theo khe gáy, lề trang (2026-11-15)
- `ung-dung/loi_xu_ly/nan_phang.py`: `tach_trang_doi` cắt giữa khe trắng giữa hai khối chữ (`_khe_gay`, đo theo 12 dải ngang, khớp đường xiên), `cat_theo_duong` cắt theo đường xiên; không còn cắt theo bóng gáy.
- `ung-dung/loi_xu_ly/cat_chu.py`: `cat_sat_chu(le="sat"|"vua"|"trang", giu_kho=…)`, mặc định "vua" (giữ lề thật tới 6% cạnh dài); `TuyChon.le`; ô *Lề trang* trong cửa sổ chính; `nan_lai_pdf.py --le=…`.
- Kiểm thử: `python ung-dung/kiem_thu/kiem_thu_tach_trang.py` (33 cặp trang, đếm nét chữ chạm đường cắt). Đáp án cho bản Android: `ghi_dap_an_tach.py`, `ghi_dap_an_cat.py`.

## Báo trang nên chụp lại (2026-11-15)
- `ung-dung/loi_xu_ly/chat_luong.py`: `la_nhoe` (lõi nét chữ xám trên ảnh đã làm sạch), `do_tay` (màu da vùng giữa trang). `xu_ly_anh` trả `tt["canh_bao"]`; cửa sổ chính ghi "NÊN CHỤP LẠI" ở ô thông tin trang.
- Kiểm thử: `python ung-dung/kiem_thu/kiem_thu_chat_luong.py` (ảnh `D:\DevTools\src\xlpdf_kiemthu\chat_luong`).

## Báo nhòe ngay sau khi chụp, trang chụp trùng (2026-11-16)
- `loi_xu_ly/quy_trinh.py`: `kiem_tra_anh_chup(anh, tach_trang_doi)` kiểm tra nhanh ảnh vừa chụp; cửa sổ camera hiện thanh báo, phím R chụp lại ảnh đó.
- `loi_xu_ly/chat_luong.py`: `do_mo_mep`, `la_nhoe_goc` (độ rộng mép nét chữ trên ảnh gốc); `dac_trung`, `diem_khop` (so trùng trang). Cửa sổ chính ghi "trùng?" ở cột trạng thái và "CÓ THỂ CHỤP TRÙNG" ở ô thông tin.
- Kiểm thử: `python ung-dung/kiem_thu/kiem_thu_chat_luong.py` (tạo ảnh thử: `python ung-dung/kiem_thu/tao_anh_rung.py [thư mục trang hồ sơ 214 trang]`).
