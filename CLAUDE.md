# Bàn giao dự án: Ứng dụng xử lý PDF ảnh

File này tóm tắt phiên làm việc trên claude.ai để Claude Code tiếp tục. Đọc file này trước, sau đó đọc `02-ke-hoach-ung-dung.md`.

## Mục tiêu
Xây ứng dụng quét, làm sạch, nắn phẳng, nhận dạng và chỉnh sửa tài liệu. Có 6 tính năng:
1. Chụp ảnh, chuyển thành PDF
2. Làm sáng nền tối đa, tăng tương phản, giữ màu chữ, con dấu, chữ ký, mực khác màu (không chuyển về đen trắng)
3. Tự xoay, nắn phẳng theo mép giấy mà không mất nội dung; gộp nhiều ảnh thành một PDF
4. Tự động xử lý file PDF và ảnh nhận được
5. Nhận dạng và sửa chữ, giữ định dạng, chữ sửa tự khớp font, cỡ, màu với chữ xung quanh
6. Điều chỉnh màu, font, lề, cỡ chữ, khổ giấy

## Bối cảnh đã chốt (người dùng xác nhận)
- Nền tảng: Android, iOS, PC
- Người dùng: cán bộ, nhân viên hành chính, thủ thư
- Ngôn ngữ văn bản: tiếng Việt, tiếng Anh
- Xử lý: toàn bộ trên thiết bị, không có máy chủ

## Còn là giả định (chưa xác nhận)
- Nhân lực: 3 người (2 lập trình viên ứng dụng, 1 kỹ sư xử lý ảnh / học máy)
- Nguồn file nhận: Zalo, email, trình quản lý file, thư viện ảnh; PC: kéo thả, "Mở bằng", thư mục theo dõi
- PC là Windows (macOS nếu cần)

## Hướng kỹ thuật đề xuất
- Flutter cho giao diện cả 3 nền tảng
- Lõi xử lý ảnh C++ + OpenCV, gọi qua FFI
- ONNX Runtime chạy mô hình (bản nhẹ cho điện thoại, bản đầy đủ cho PC)
- `pdf` (Dart) ghi PDF, PDFium đọc PDF; tránh MuPDF (AGPL)
- Tính năng 5 theo hai hướng: A sửa trực tiếp trên ảnh (inpainting + đoán font trong tập giới hạn), B tái dựng tài liệu chỉnh sửa được (phục vụ tính năng 6)

## Trạng thái
- Xong: prompt lập kế hoạch (`01-prompt-ke-hoach.md`), bản kế hoạch (`02-ke-hoach-ung-dung.md`)
- Xong (2026-10-29): nguyên mẫu Windows chạy được trong `ung-dung/` (Python + OpenCV + Tesseract): tính năng 1–4 gần đủ, tính năng 5 mới có OCR và lớp chữ PDF, tính năng 6 mới có khổ giấy và lề khi xuất. Kiểm thử: `ung-dung/kiem_thu/kiem_thu_loi.py`. Chi tiết trong `README.md` và `NHAT-KY.md`
- Xong (2026-10-29): chế độ tự động chụp: thuật toán `ung-dung/loi_xu_ly/tu_chup.py`, đã gắn vào cửa sổ camera PC, kiểm thử `kiem_thu_tu_chup.py`; đặc tả cho Android, iOS ở `03-tu-dong-chup.md`
- Xong (2026-10-29): thiết kế 5 màn hình điện thoại bằng Claude Design (`thiet-ke-giao-dien/`); bản Android Flutter đầu tiên, mã ở `D:\DevTools\src\xlpdf` (junction `ung-dung-flutter`), APK ở `apk/`. Đã kiểm trên máy ảo, chưa thử điện thoại thật
- Xong (2026-10-29): bản Android 0.2.0 (`apk/xu-ly-pdf-anh-0.2.0.apk`): nhận dạng chữ Tesseract 5.5.1 trên máy (xem/chép chữ, PDF lớp chữ, .txt), khử nhiễu và tăng tương phản, đoán chiều chữ + Xoay toàn bộ (dọc/ngang), Tự chụp / Bấm chụp, màn Xem nhanh. Kiểm thử máy ảo: `integration_test/chay_kiem_thu.sh <bộ>` (4 bộ, 15 phép thử đạt). Tesseract trên Android phải đặt `OMP_THREAD_LIMIT=1` (không thì chậm 3–4 lần)
- Xong (2026-10-29): bản Android 0.3.0 (`apk/xu-ly-pdf-anh-0.3.0.apk`): thêm đánh số trang khi xuất PDF (`DanhSo` trong `lib/loi/xuat_pdf.dart`, khối `lib/man_hinh/danh_so.dart`); kiểm thử `so_trang_test.dart` + `kiem_so_trang.py`
- Xong (2026-10-30): nguyên mẫu PC có cửa sổ **Sửa PDF** (`ung-dung/sua_pdf.py`, `sua-pdf.bat`, nút "✏ Sửa PDF…"): sửa trang PDF có sẵn không mất chất lượng (gộp, tách, chèn, xóa, xoay, đảo), sửa chữ hướng A (đoán phông Times/Arial × 4 kiểu bằng vẽ thử chữ cũ rồi so hình; vá nền; dồn dòng; chặn vùng con dấu, chữ ký), thêm chữ, che, tô sáng, chèn ảnh. Kiểm thử `kiem_thu/kiem_thu_sua_pdf.py`
- Xong (2026-10-30): sửa chữ theo khối (gộp dòng, đoạn) và gõ ngay trên trang ở nguyên mẫu PC (`tim_khoi`, `SuaKhoi` trong `sua_noi_dung.py`; ô sửa tại chỗ trong `sua_pdf.py`)
- Xong (2026-10-30): bản Android 0.4.0 (`apk/xu-ly-pdf-anh-0.4.0.apk`): sửa chữ theo khối, gõ tại chỗ (`lib/loi/sua_chu.dart`, `lib/loi/ve_chu.dart`), phông Liberation Serif/Sans (SIL OFL) thay Times/Arial; kiểm thử `sua_chu_test.dart`
- Xong (2026-10-30): **sửa ký tự giữ nguyên bản gốc** ở nguyên mẫu PC (`ung-dung/loi_xu_ly/sua_ky_tu.py`, công cụ chính trong `sua_pdf.py`) theo nhận xét của người dùng: cách viết lại khối bằng phông làm mất định dạng, cỡ chữ, sai nội dung theo OCR. Chữ không sửa giữ nguyên điểm ảnh; ký tự chèn chép từ chính tài liệu; dãy chấm mục lục tự co giãn; OCR phóng ảnh lên ~300 dpi chỉ để lấy khung ký tự. Trang PDF một ảnh sửa trên ảnh gốc (không dựng lại)
- Xong (2026-10-30): tham khảo ONLYOFFICE DesktopEditors (AGPL: chỉ học cách làm, không lấy mã), nguyên mẫu PC thêm: đối tượng chọn lại được (dời, đổi cỡ, xóa, nhân bản, bấm đúp sửa chữ, Ctrl+Y làm lại; `sua_pdf_doi_tuong.py`, `loi_xu_ly/doi_tuong.py`), dời / xóa vùng có sẵn trên bản scan (vùng có mực màu bị khóa), vẽ hình, chú thích PDF chuẩn không phá bản gốc (`loi_xu_ly/chu_thich.py`: ghi chú, bút phê, tô sáng, hình, dấu "ĐÃ XEM"; hình hiển thị /AP vẽ bằng reportlab, đổi tọa độ theo /Rotate, hộp cắt, chỗ đặt ảnh), thao tác trang kiểu ONLYOFFICE (`sua_pdf_trang.py`: kéo thả, menu chuột phải, chép / dán trang giữa các cửa sổ). Kiểm thử `kiem_thu_sua_pdf.py` mục 5–7
- Xong (2026-10-30): bản Android 0.5.0 (`apk/xu-ly-pdf-anh-0.5.0.apk`): sửa ký tự giữ nguyên bản gốc chuyển từ bản PC (`lib/loi/sua_ky_tu.dart`, kênh nhận dạng thêm khung ký tự `hocr_char_boxes`, đệm `kt_<ảnh>.json`); kiểm thử `integration_test/sua_ky_tu_test.dart` 7/7. Hai lỗi bản Android phát hiện (mảnh chồng làm dán hai lần vài cột điểm ảnh; khe chấm dẫn làm ký tự chèn giãn thưa) đã sửa cả ở bản PC
- Xong (2026-10-30): bản Android 0.5.1 (`apk/xu-ly-pdf-anh-0.5.1.apk`) và bản PC: sửa ký tự trên dòng nghiêng (ảnh chụp thật của người dùng bị lệch dòng, làm nát dòng bên cạnh): đường chân xiên từng dòng, chỉ dời nét của chính dòng (`net_cua_dong` / `netCuaDong`), dời theo độ dốc. Kiểm thử `kiem_thu_sua_pdf.py` mục 1d, `sua_ky_tu_test.dart` (g), 8/8
- Xong (2026-10-30): bản Android 0.5.2 (`apk/xu-ly-pdf-anh-0.5.2.apk`) và bản PC: gõ tiếng Việt khi sửa ký tự không lẫn phông, đậm nhạt: nắn khung ký tự Tesseract theo nét mực (`nan_khung`), chọn mẫu theo bề dày nét quanh chỗ chèn (`dam_quanh`), tô màu mực chỗ chèn, ghép dấu cho chữ có dấu thiếu (`ghep_dau`), ghép dấu rời. Kiểm thử `kiem_thu_sua_pdf.py` mục 1e, `sua_ky_tu_test.dart` (h), 9/9
- Xong (2026-10-30): bản Android 0.6.0 (`apk/xu-ly-pdf-anh-0.6.0.apk`) và bản PC: **đổi phông, cỡ chữ đoạn bôi chọn** trong Sửa ký tự (người dùng chọn phạm vi này). Bôi chọn: Shift + ← →, kéo chuột (PC); chạm giữ rồi kéo, nút Bôi chọn (Android). Đổi cỡ = phóng, thu chính nét gốc (`dinh_dang_chon(ti_le)`), đổi phông = vẽ lại riêng đoạn chọn bằng phông, cùng màu mực (`dinh_dang_chon(kieu=…)`); trả cỡ về gốc thì như chưa sửa. PC dùng khung Chữ (Phông/Kiểu "Tự đoán" = giữ nét gốc), Android có thanh A− cỡ A+ và menu phông. Kiểm thử mục 1f, `sua_ky_tu_test.dart` (i), 10/10
- Xong (2026-11-14): bản Android 0.7.0 (`apk/xu-ly-pdf-anh-0.7.0.apk`) và bản PC: **tự căn chỉnh, làm phẳng kiểu CamScanner** theo góp ý chạy máy thật (ảnh chưa được làm phẳng). Bộ tìm mép mới `tim_mep.py` / `lib/loi/tim_mep.dart` (nhiều nguồn ứng viên, chấm theo độ bám mép, chọn tờ giấy nằm trên vật khác, tinh chỉnh cạnh); nắn trang cong theo dòng chữ `nan_cong.py` / `lib/loi/nan_cong.dart`; màn Chỉnh trang thẻ *Cắt, nắn phẳng* kéo góc hoặc giữa cạnh, kính lúp. Bộ ảnh thử tổng hợp `ung-dung/kiem_thu/tao_anh_mep.py` (đo `do_mep.py`, `do_cong.py`); Android `integration_test/mep_cong_test.dart`. Lưu ý `opencv_dart`: `Mat.data` là cửa sổ bộ nhớ (Mat tạm phải chép bằng `u8Chep`/`f32Chep`/`i32Chep`), phép hình thái cần `borderType: BORDER_REPLICATE`
- Xong (2026-11-14): bản Android 0.7.1 (`apk/xu-ly-pdf-anh-0.7.1.apk`) theo góp ý chụp thật: camera độ phân giải tối đa (trước 1080p), lấy nét trước khi chụp, chạm để lấy nét, đo ảnh mờ (`tiLeNet`) rồi chụp lại; tự chụp chỉ báo lùi máy khi trang thật sự bị cắt, dùng bộ tìm mép nhanh; **OCR tách thành chức năng riêng** (nút Nhận dạng chữ ở màn Các trang: xem, chép, .txt, PDF có chữ), xuất PDF không tự nhận dạng
- Xong (2026-11-14): bản Android 0.7.2 (`apk/xu-ly-pdf-anh-0.7.2.apk`) và bản PC: **cắt sát chữ, xóa vết** (nền tối, nêm đen ở gáy, góc đen, ngón tay) `cat_chu.py` / `lib/loi/cat_chu.dart`, nút *Cắt sát chữ* bật sẵn; nắn cong ảnh sách mở tách theo gáy (`timGay`); sửa lỗi lưu hồ sơ đồng thời. Kiểm thử `integration_test/cat_chu_test.dart` với 8 trang sách chụp thật của người dùng (`xlpdf_kiemthu/sach`)
- Xong (2026-11-14): bản Android 0.7.3 (`apk/xu-ly-pdf-anh-0.7.3.apk`) và bản PC: **tự xoay ảnh chụp cầm máy ngang** (nhận dòng chữ dọc `chieu_chu.py` / `lib/loi/chieu_chu.dart` trước khi tìm gáy, nắn cong, cắt; Android tự lật theo Tesseract, người dùng tự xoay thì tắt tự xoay của trang); cắt sát chữ xóa thêm ngón tay (`xoaDaTay`), vệt bóng cong, mẩu đen, đường gáy, giữ tiêu đề cách xa. Kiểm thử thêm 11 trang chụp thật `xlpdf_kiemthu/sach2`
- Xong (2026-11-14): bản Android 0.7.4 (`apk/xu-ly-pdf-anh-0.7.4.apk`) và bản PC: **tự chụp nhanh, không đứng chờ** theo video chụp thật của người dùng (sách trên nền đen): đo rung theo độ dời (toàn khung + từng ô), thời gian chịu 0,4 s cho khung tìm mép trượt, nhận động tác lật trang (đủ 1 s thì ngưỡng trang mới 0,18), nhận tay trên trang (`tiLeTay`), giữ yên 0,3/0,5/0,9 s, rung báo (`xlpdf/rung`, Cài đặt › Rung báo). Kiểm thử phát lại video `integration_test/tu_chup_test.dart` (`xlpdf_kiemthu/video`)
- Xong (2026-11-14): bản Android 0.7.5 (`apk/xu-ly-pdf-anh-0.7.5.apk`) và bản PC: **chụp sách không còn mất nửa cặp trang**. Khi chụp sát, một trang lọt ra ngoài khung thì bộ tìm mép nối thêm trang bên kia gáy tới biên ảnh (`_canh_noi` / `_canhNoi`), và tự chụp nhắc lùi máy. Kiểm thử bằng bộ ảnh sách mở tổng hợp `ung-dung/kiem_thu/tao_anh_sach_mo.py` + `kiem_thu_sach_mo.py`, Android `integration_test/nua_trang_test.dart` (`xlpdf_kiemthu/sach_mo`)
- Xong (2026-11-15): bản Android 0.7.6 (`apk/xu-ly-pdf-anh-0.7.6.apk`) và bản PC: **nắn vuông khối chữ** (`nan_le` / `nanLe`): hai lề thẳng, vuông góc dòng chữ. Cặp trang sách mở được xoay thẳng từng trang. Khi nắn phẳng, khung tự tìm được nới 2,5% để chữ ở mép trang cong không bị cắt lẹm (nền trong dải nới được xóa). Có script nắn lại PDF có sẵn: `ung-dung/nan_lai_pdf.py` / `nan-lai-pdf.bat`. Kiểm thử: `kiem_thu/do_le.py`, Android `integration_test/le_khoi_test.dart`
- Xong (2026-11-15): bản Android 0.7.7 (`apk/xu-ly-pdf-anh-0.7.7.apk`) và bản PC theo hồ sơ 214 trang chụp thật (`Hồ sơ 15-11 19-33.pdf`): **tách cặp trang giữa khe gáy** theo đường xiên (`_khe_gay`, `cat_theo_duong` / `kheGay`, `catTheoDuong`; trước đây cắt theo bóng gáy nên trang trái dính chữ trang phải, trang phải mất chữ đầu dòng); **lề "Vừa"** mặc định (`cat_sat_chu(le=…, giu_kho=…)`, giữ lề thật tới 6%, trang ít chữ giữ khổ; Sát chữ / Vừa / Giữ cả trang); Android **chụp xong mới xử lý** (`Kho.batDauChup`/`ketThucChup`, Cài đặt) và nút **Xử lý lại cả hồ sơ** từ ảnh gốc. Kiểm thử `kiem_thu_tach_trang.py` 33/33, `integration_test/tach_trang_test.dart`
- Xong (2026-11-15): bản Android 0.7.8 (`apk/xu-ly-pdf-anh-0.7.8.apk`) và bản PC: **báo trang nên chụp lại** (`chat_luong.py` / `lib/loi/chat_luong.dart`): chữ nhòe (lõi nét xám trên ảnh đã làm sạch), tay che trang (màu da vùng giữa trang > 5%); hiện ở Xem nhanh kèm nút **Chụp lại** (`Kho.thayAnh`, `ManChup(thayTrang:)`). Kiểm thử `kiem_thu_chat_luong.py`, `integration_test/chat_luong_test.dart` (ảnh `xlpdf_kiemthu/chat_luong`)
- Xong (2026-11-16): bản Android 0.7.9 (`apk/xu-ly-pdf-anh-0.7.9.apk`) và bản PC: **báo nhòe ngay trên màn camera** sau mỗi ảnh (`kiem_tra_anh_chup` / `kiemTraAnhChup`, nút Chụp lại thay ảnh vừa rồi); phép đo nhòe mới trên ảnh gốc (`do_mo_mep` / `doMoMep`, mọi chế độ); rung báo khi máy đã chụp xong (trước đây rung lúc bắt đầu lấy nét); **dò trang chụp trùng** bằng ORB (`dac_trung`, `diem_khop` / `trangTrung`; Android dựng thêm mô-đun OpenCV features2d + flann, không có calib3d). Kiểm thử `kiem_thu_chat_luong.py`, `chat_luong_test.dart` (ảnh `xlpdf_kiemthu/mo_chup`, `xlpdf_kiemthu/trung`, tạo bằng `tao_anh_rung.py`)
- Lưu ý dựng Android: Gradle lỗi với đường dẫn có dấu (nên mã đặt ở `D:\DevTools`); cần `kotlin.incremental=false`; công cụ ở `D:\DevTools` (Flutter, Android SDK, NDK, máy ảo `may_thu` trong `D:\DevTools\avd`)
- Đã kiểm chứng: Tesseract `vie` đọc tốt tiếng Việt in máy; **không dùng `vie+eng`** (mất dấu nặng)
- Chưa làm: các tính năng ONLYOFFICE trên bản Android; nắn trang cong mới kéo thẳng theo dọc (chưa giãn ngang gần gáy, chưa nắn trang không có chữ); sửa chữ khớp font trên Android, trình soạn thảo định dạng (hướng B, xuất Word), bản iOS; chưa thử ảnh chụp thật và điện thoại thật; nguyên mẫu PC chưa có khử nhiễu mới của bản Android; các mục "cần kiểm tra lại" khác ở cuối bản kế hoạch

## Bước tiếp theo gợi ý
1. Thu ảnh chụp thật (công văn có dấu, sách cong, giấy vàng) và chạy nguyên mẫu để tinh chỉnh ngưỡng
2. Sửa chữ hướng A (vá nền + vẽ chữ Times New Roman) trên nguyên mẫu
3. Kiểm chứng các mục "cần kiểm tra lại" còn lại, rồi dựng Flutter + lõi C++ theo thuật toán trong `ung-dung/loi_xu_ly/`

## Quy ước
- Trao đổi và tài liệu bằng tiếng Việt
- Người dùng thích nhận kèm script Python sẵn chạy, không chỉ có hướng dẫn
