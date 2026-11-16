---
type: chu-de
---
# Kiểm thử

## Tiêu chí đề xuất (tinh chỉnh sau giai đoạn 0)
| Tính năng | Tiêu chí |
|---|---|
| 1 | Một trang dưới 2 giây trên điện thoại tầm trung, dưới 1 giây trên PC |
| 2 | Nền gần trắng trên ≥ 95% diện tích nền; dấu đỏ, mực xanh lệch hue ≤ 10° |
| 3 | Nghiêng còn < 0,5°; không mất chữ ở mép; xoay đúng ≥ 99%; tách trang đôi đúng ≥ 95% |
| 4 | Xử lý đúng PDF 50 trang và lô 20 ảnh |
| 5 | CER < 3% với văn bản in; ≥ 80% chữ sửa không bị nhận ra (Times New Roman) |
| 6 | PDF mở đúng trên Acrobat, Foxit, trình xem điện thoại; dấu tiếng Việt đúng |

Nguồn: [[ke-hoach-ung-dung]].

## Bộ kiểm thử của nguyên mẫu
- `tao_anh_mau.py` dựng ảnh tổng hợp: công văn chụp nghiêng có bóng đổ, bản quét lộn ngược, sách mở hai trang ([[readme]], [[du-lieu-kiem-thu]]).
- `kiem_thu_loi.py`: đạt toàn bộ trên ảnh tổng hợp — nền trắng 100%, dấu đỏ lệch 3,9°, tỉ lệ A4 1,414, xoay 180°, nghiêng < 0,5°, OCR đúng quốc hiệu có dấu, PDF có lớp chữ tìm được tiếng Việt (`NHAT-KY.md` dự án, 2026-10-29).
- `kiem_thu_tu_chup.py`: phim mô phỏng 20 giây, chụp đúng 4 trang, không trùng, báo đúng lời nhắc ([[dac-ta-tu-dong-chup]]).
- `kiem_thu_sua_pdf.py` (thêm 2026-10-30): đạt toàn bộ; kết quả ghi vào `kiem_thu/ket_qua/sua-*` ([[cua-so-sua-pdf]]; `NHAT-KY.md` dự án, 2026-10-30):
  - Sửa chữ: sửa 3 cụm trên trang công văn mẫu; đoán đúng Times thường (thân bài), Times đậm (tiêu đề); nhận dạng lại dòng sau sửa đúng bằng dòng cũ thay cụm chữ; các dòng khác giữ nguyên từng điểm ảnh; dòng căn giữa vẫn ở giữa (lệch 1 px) ([[nhan-dang-va-sua-chu]]).
  - Nhận ra vùng con dấu, không chặn chữ đen; chữ thêm đọc lại được; che, tô sáng, chèn chữ ký bỏ nền.
  - PDF có sẵn: gộp 2 tệp, xóa, chèn trang trắng, đảo thứ tự; xoay giữ /Rotate 90; trang chưa sửa chép nguyên luồng nội dung; chưa sửa thì không ghi dấu; sửa chữ vector rồi lưu có lớp chữ mới, giữ khổ A4, ghi dấu đã chỉnh sửa; tách 2 trang.
  - Bấm thử cửa sổ bằng script giả lập chuột: tìm 144 từ, chọn 3 từ bằng Shift, sửa, che, xoay, lưu; ảnh `kiem_thu/ket_qua/giao-dien-sua-pdf.png`. Script này phát hiện lỗi kéo chuột (khung che chỉ lấy lần di chuyển đầu), đã sửa.
  - Kiểm chứng đoán phông: trên chữ vector của PDF, dấu thanh ngoài khung từ làm đoán nhầm Arial đậm nghiêng 10,9 pt; sau khi sửa đoán đúng Times 14,1 pt (thật 14 pt).
  - Chưa kiểm: hộp thoại sửa chữ, thêm chữ chưa bấm bằng tay (script thay bằng kết quả giả); chưa thử ảnh chụp, PDF thật của người dùng. Chưa đo tiêu chí "≥ 80% chữ sửa không bị nhận ra" ở bảng trên.
  - Mục 1b, sửa chữ theo khối (thêm 2026-10-30, lần 2; cả bộ vẫn đạt toàn bộ) (`NHAT-KY.md` dự án, 2026-10-30, mục sửa theo khối; [[nhan-dang-va-sua-chu]]):
    - quốc hiệu, tiêu ngữ thành một khối 2 dòng căn giữa; đoạn "Căn cứ…" thành khối 2 dòng căn trái;
    - viết thêm một câu → 4 dòng; dòng đầu ngắt đúng chỗ cũ ("… đề nghị"); phần dưới dời 150 px nguyên vẹn; phần trên không đổi;
    - tiêu đề dài hơn vẫn đậm, căn giữa (lệch 1 px).
  - Bấm thử ô gõ tại chỗ bằng script (2026-10-30, lần 2): mở ô tại chỗ, gõ thêm câu, phóng to, Ctrl+Enter, Esc hủy, bấm ra ngoài áp, thêm chữ tại chỗ; ảnh `kiem_thu/ket_qua/giao-dien-sua-khoi.png`. Hộp thoại cũ đã bỏ nên điểm "chưa bấm hộp thoại bằng tay" ở trên không còn áp dụng; ô gõ tại chỗ cũng mới bấm bằng script, chưa bấm bằng tay.
- Giới hạn: ảnh tổng hợp chưa thay được ảnh chụp thật; chưa thử ảnh và camera thật ([[readme]]).

## Bộ kiểm thử của bản Android (cập nhật 2026-10-29)
Chạy trên máy ảo bằng `integration_test/chay_kiem_thu.sh <bộ>.dart` (vì `flutter test` gỡ ứng dụng sau mỗi lần chạy); dữ liệu ở `D:\DevTools\src\xlpdf_kiemthu` ([[readme-ung-dung-flutter]], [[du-lieu-kiem-thu]]). Bản 0.2.0: 4 bộ, 15 phép thử, đều đạt (`NHAT-KY.md` dự án).

| Bộ | Kiểm gì | Kết quả ghi nhận |
|---|---|---|
| `loi_test.dart` (từ 0.1.0) | tìm mép, xử lý trọn trang, tách trang đôi, tự động chụp, xuất PDF | tìm mép lệch 5,4 px; tỉ lệ trang 1,415, nền trắng 99,4%, giữ dấu đỏ, 0,7 s; tách trang đôi ở 50%; tự chụp đúng 2 trang mới, 15 ms một khung; xuất được PDF |
| `nhan_dang_test.dart` (mới) | đọc hOCR; Tesseract trên máy so với PC; PDF có lớp chữ | trùng 99,4% ký tự với Tesseract PC; PDFium chép được chữ, tìm được "CỘNG HÒA", "đóng dấu đỏ"; chữ ẩn lệch ngang trung vị 0,9 pt |
| `lam_sach_test.dart` (mới) | độ đen chữ, đốm nhiễu, nền trắng, dấu đỏ, nhận dạng trên ảnh chụp tốt và kém | ảnh kém: đốm 743 → 117, nhận dạng 71% → 91,6%, trung vị độ sáng chữ 55 → 43; ảnh tốt vẫn 99,4%; dấu đỏ giữ nguyên |
| `chieu_test.dart` (mới) | đoán chiều 4 góc; trang ngược tự phát hiện, Xoay toàn bộ, giữ khung cắt tay, ép khổ dọc | đúng cả 0°, 90°, 180°, 270°, khoảng 1,2 giây một trang; luồng trang ngược → cảnh báo → Xoay toàn bộ đạt |
| `so_trang_test.dart` (0.3.0) + `kiem_so_trang.py` (PC) | quy tắc số, căn so le; 3 PDF 4 trang có số trang, đo vị trí bằng PDFium | 12/12 trang đúng số, trang trước trang bắt đầu không số, tâm số lệch dưới 2 pt (`NHAT-KY.md` dự án) |
| `sua_chu_test.dart` (0.4.0) | gộp khối, căn lề; đoán phông; sửa "Kính gửi" dài ra; tiêu đề vẫn ở giữa; đoạn thêm dòng; khối có con dấu bị khóa; lưu, hoàn tác, ghi chú PDF, xử lý lại thì bỏ sửa; ảnh ra `build/kiem_thu_ra/sc_*` ([[readme-ung-dung-flutter]]) | 7/7, đã chạy lại độc lập; Liberation Serif thường khoảng 14,4 pt (thân bài), đậm khoảng 15,3 pt (tiêu đề); 300–770 ms một khối; "Kính gửi…" 1 → 2 dòng, dời 75 px, đọc lại đúng 100%, phía trên và phần dời không đổi điểm ảnh nào; tiêu đề lệch 0,5 px; đoạn 3 → 4 dòng không chồng chữ, đọc lại 99,2%; bút phê đỏ và tên ký đè con dấu bị khóa. 5 bộ cũ vẫn đạt (`NHAT-KY.md` dự án, 2026-10-30) |

- Bấm thử giao diện 0.2.0: nhập 4 ảnh (2 ảnh sai chiều) → màn Các trang báo 2 trang cần xem → Xem nhanh → *Sửa chiều tất cả* → cả 4 trang đứng thẳng; *Tất cả khổ ngang* rồi *Tất cả khổ dọc*; Bấm chụp; xem văn bản cả hồ sơ (`NHAT-KY.md` dự án).
- Lưu ý cách đo: "99,4%" của nhận dạng là độ khớp với đầu ra Tesseract trên PC (`mau1.txt`), không phải độ đúng so với chữ chuẩn, nên chưa đối chiếu được với tiêu chí CER < 3% ở bảng trên ([[du-lieu-kiem-thu]]). Ảnh chụp kém là ảnh tổng hợp.
- Bấm thử giao diện 0.4.0 trên máy ảo: vào Sửa chữ, chạm khối, sửa tại chỗ, Xong, Hoàn tác; ảnh `apk/anh-chup-may-ao/0.4.0-*.png`. adb không gõ được tiếng Việt nên chỉ gõ thêm chữ không dấu (`NHAT-KY.md` dự án, 2026-10-30).
- Chưa kiểm: điện thoại thật, tốc độ nhận dạng thật, ảnh chụp thật (`NHAT-KY.md` dự án). Sửa chữ 0.4.0 chưa thử trang sách (2 ảnh), xóa trắng cả khối, nền màu, chữ viết tay (`NHAT-KY.md` dự án, 2026-10-30).

## Sửa ký tự giữ nguyên bản gốc (cập nhật 2026-10-30, lần 3)
- `kiem_thu_sua_pdf.py` mục 1c đạt toàn bộ: "15" → "20" chép từ chính trang, phần sau dời đúng chênh bề rộng, giữ nguyên điểm ảnh, đọc lại đúng; trang mục lục tổng hợp: nhận 62 chấm theo hình dạng, "156" → "15" mép phải lệch 1 px, chèn "các " trước "Mục tiêu" số trang đứng nguyên, chữ chèn đúng cỡ, đúng đường chân ([[sua-ky-tu]]).
- Thử trên tệp thật của người dùng (bản sao, 7 trang ảnh, khoảng 100–127 dpi): dựng lại trang so với gốc chỉ khác ở hai dải dòng đã sửa; Subject ghi "2 chỗ sửa ký tự" (`NHAT-KY.md` dự án, 2026-10-30).
- Đầu ra mới: `sua-ky-tu-ngay.png`, `sua-ky-tu-muc-luc.png`; các PDF `sua-nguon.pdf`, `sua-nguon-2.pdf`, `sua-ket-qua.pdf`, `sua-ket-qua-da-sua.pdf`, `sua-tach.pdf` được sinh lại ([[du-lieu-kiem-thu]]).

## Đối tượng, chú thích, thao tác trang (cập nhật 2026-10-30, lần 4)
`kiem_thu_sua_pdf.py` vẫn đạt toàn bộ sau khi thêm ba mục mới (`NHAT-KY.md` dự án, 2026-10-30, mục "Tham khảo ONLYOFFICE"; tên phép thử trong `kiem_thu_sua_pdf.py`):
- **Mục 5, đối tượng chọn lại được, dời vùng có sẵn** ([[doi-tuong-tren-trang]]): dời chữ đã thêm đúng 50, 30 px; kéo góc gấp đôi khung thì cỡ chữ 40 → khoảng 80 px; dời mũi tên giữ chiều; trang mẫu tự đánh dấu 15 vùng, 3 vùng con dấu bị khóa (vùng khóa đều có mực màu); dời một vùng 40 px: ngoài chỗ cũ, chỗ mới không đổi điểm ảnh nào; xóa vùng: chỗ cũ vá nền.
- **Mục 6, chú thích PDF chuẩn** ([[chu-thich-pdf]]): PDF nguồn 2 trang (trang 2 xoay /Rotate 90) cộng một trang trắng; mỗi trang thêm ghi chú, bút phê, tô sáng, mũi tên, dấu. Kết quả: chú thích không tính là sửa nội dung; ghi đủ 5 loại /Text, /FreeText, /Highlight, /Line, /Stamp; luồng nội dung 2 trang gốc chép nguyên; không có Subject; PDFium dựng bản lưu (có và không có chú thích), chỗ chú thích trùng chỗ xem trước 100% ở cả trang /Rotate 0, /Rotate 90 và trang trắng (ngưỡng đạt trong script là trên 90%); xoay trang 90° rồi 270°, chú thích về đúng chỗ.
- **Mục 7, thao tác trang kiểu ONLYOFFICE** ([[thao-tac-trang]]): PDF nguồn 5 trang; kéo trang 4, 5 lên trước trang 2 → 1, 4, 5, 2, 3; kéo trang đầu xuống cuối; chép 2 trang, dán hai lần sang tài liệu khác (9 trang); mỗi lần dán là trang riêng; trang dán có luồng nội dung trùng trang gốc.
- **Phép thử riêng** trên 6 kiểu trang (kể cả trang hộp cắt lệch gốc, trang ảnh scan của tệp hồ sơ thật của người dùng (bản sao, chỉ để thử), trang đã sửa nội dung): chú thích lưu ra trùng chỗ xem trước 100%.
- **Bấm thử cửa sổ bằng script** trên tệp hồ sơ thật của người dùng (bản sao, chỉ để thử):
  - đối tượng: chọn, dời, đổi cỡ chữ thêm và mũi tên; dời một dòng có sẵn; hoàn tác, làm lại; chép, dán, xóa; bấm đúp sửa chữ;
  - chú thích: tạo 5 loại, dời dấu, sửa lời ghi chú; lưu ra 5 chú thích, trang gốc chép nguyên;
  - hai cửa sổ: kéo trang 5 lên vị trí 2, chèn trang trắng, nhân đôi, chép 2 trang dán sang cửa sổ kia; lưu ra chép nguyên.
  - Các phép thử cửa sổ cũ (sửa ký tự trên tệp thật) vẫn đạt.
- Đầu ra mới trong `kiem_thu/ket_qua/`: `ct-nguon.pdf`, `ct-ra.pdf` (mục 6), `tt-nguon.pdf`, `tt-ra.pdf` (mục 7) ([[du-lieu-kiem-thu]]).
- Chưa kiểm: **menu chuột phải mới kiểm bằng lệnh, chưa bấm tay**; mục 6 chưa thử chữ nhật, elip (/Square, /Circle); chưa đọc chú thích có sẵn trong PDF mở vào nên chưa có phép thử cho việc này; chưa có trên Android (`NHAT-KY.md` dự án, 2026-10-30).

## Tìm mép, nắn cong (2026-11-14)
- Python: `do_mep.py` 17/17, hai bộ ngẫu nhiên 24/24, 29/29 (bộ tìm mép cũ: 10/15, 12/30, 16/29); `do_cong.py` trang cong 0,66% → 0,06%, trang phẳng không bị nắn; `kiem_thu_loi.py` vẫn đạt ([[du-lieu-kiem-thu]]).
- Android máy ảo: `mep_cong_test.dart` 17/17 (0,44 s/ảnh), nắn cong 0,66% → 0,07%; `loi_test` lệch góc 1,7 px (trước 5,4 px), `chieu_test`, `lam_sach_test` đạt ([[nan-phang-va-xoay]]).

## Tự chụp, ảnh mờ (0.7.1, 2026-11-14)
- `mep_cong_test.dart` 4/4 trên máy ảo: khung hình ôm sát trang (cách mép 0,4%) thì chụp; trang bị cắt góc thì báo lùi máy (3 ảnh mẫu); đo mờ: nét 0,92 / 0,66, mờ 0,39. `loi_test` đạt, tự chụp 57 ms/khung ([[tu-dong-chup]]).

## Cắt sát chữ (0.7.2, 2026-11-14)
- Python `kiem_thu_loi.py` thêm 3 mục cắt sát chữ, TẤT CẢ ĐẠT. Android `cat_chu_test.dart` 2/2: trùng kích thước bản Python trên 8 trang sách thật, mép ảnh không còn điểm tối; công văn giữ đủ dấu đỏ, chữ ký. Các bộ cũ đều đạt: loi_test, chieu_test (khung tay xoay đo khi không cắt sát), lam_sach_test, mep_cong_test 4/4, sua_ky_tu_test 10/10, nhan_dang_test, so_trang_test, sua_chu_test 7/7 (đổi chuỗi tìm khối 'Kính gửi', 'TRƯỞNG PHÒNG', 'Đồng ý' sang phần ít dấu, vì từ 0.7.0 góc khung lệch tới 3 px so với bộ tìm mép cũ làm Tesseract đọc sai một dấu: 'Kinh gửi', 'TRƯỚNG', 'Đỏng ý'). ([[nan-phang-va-xoay]]).

## Tự xoay, xóa ngón tay (0.7.3, 2026-11-14)
- Python `kiem_thu_loi.py` mẫu 2b (ảnh lệch 90°, 270° ra trang đứng, đọc đúng chữ), TẤT CẢ ĐẠT. Android: 9 bộ kiểm thử đều đạt: chieu_test 2/2 (trang lệch 90° và 270° tự xoay dòng chữ về ngang, trang lệch 90° và 180° tự lật theo Tesseract, đoán lại đều 0°), cat_chu_test 3/3 (11 trang lần này: nhận chữ dọc 11/11 khoảng 0,04 s, cắt trùng bản Python, gáy lệch dưới 25 điểm ảnh; 8 trang lần trước như cũ; công văn giữ đủ dấu đỏ, chữ ký), loi, lam_sach, mep_cong, sua_ky_tu 10/10, sua_chu 7/7, nhan_dang, so_trang. PC: kiem_thu_sua_pdf.py dựng trang mẫu không cắt sát chữ (5 mục sai từ bản 0.7.2 hết); còn 3 mục sai ở cách sửa cũ viết lại khối (đọc lại bằng OCR), có từ trước, lần này không đổi phần đó. ([[nan-phang-va-xoay]]).

## Tự chụp trên video chụp thật (0.7.4, 2026-11-14)
- Android `tu_chup_test.dart` đạt: chụp đủ 6 cặp trang, sớm hơn bản cũ (cặp 3: 18,5 giây thay vì 34,5), không chụp khi tay trên trang; `loi_test` 5/5, `mep_cong_test` 4/4. Python `kiem_thu_tu_chup.py`: chức năng đạt, tốc độ hỏng do bộ tìm mép cũ của bản PC ([[tu-dong-chup]]).

## Sách mở hai trang (0.7.5, 2026-11-14)
- Bộ ảnh tổng hợp `kiem_thu/tao_anh_sach_mo.py`: 21 ảnh ghép từ trang sách người dùng chụp. Có nền đen, gỗ, vải; cầm máy dọc và ngang; gáy tối; trang cong; tràn khung; chụp từng trang ([[du-lieu-kiem-thu]]).
- Python `kiem_thu_sach_mo.py`: kiểm khung (IoU ≥ 0,85), ảnh ra đủ hai trang (rộng/cao ≥ 1,1, chụp từng trang < 0,9), và tự chụp nhắc lùi máy khi trang tràn khung. Kết quả: đạt hết. Hai ảnh chụp từng trang để dạng tham khảo, do lỗi có từ bộ tìm mép 0.7.0.
- Android `integration_test/nua_trang_test.dart`: cùng các phép kiểm trên ảnh `xlpdf_kiemthu/sach_mo` ([[nan-phang-va-xoay]]).

## Nắn vuông khối chữ (0.7.6, 2026-11-15)
- `kiem_thu/do_le.py` đo độ lệch lề (so với hai đường thẳng vuông góc dòng chữ) trước và sau quy trình. Trên 11 trang sách thật `sach2`: trung vị 1,55% → 0,17% (Android `le_khoi_test.dart`: 1,55% → 0,11%) ([[nan-phang-va-xoay]], [[du-lieu-kiem-thu]]).

## Tách cặp trang (0.7.7, 2026-11-15)
- `kiem_thu/kiem_thu_tach_trang.py`: đếm nét chữ chạm đường cắt gáy trên 33 cặp trang (18 tổng hợp, 15 chụp thật). Cách cũ: goc4, goc7, doc4 bị cắt qua chữ (18–24 nét chạm). Cách mới: 33/33 đạt ([[nan-phang-va-xoay]], [[ho-so-15-11-sach-214-trang]]).
- Android `integration_test/tach_trang_test.dart`: cùng phép đếm, so đường cắt với đáp án Python `xlpdf_kiemthu/tach_trang_python.json` (`ghi_dap_an_tach.py`): 33/33 đạt, đường cắt trùng bản Python trong vài điểm ảnh.
- Đáp án cắt chữ của `cat_chu_test.dart` ghi lại theo lề "Vừa" (`ghi_dap_an_cat.py`); các bộ Android khác vẫn đạt.

## Báo trang nên chụp lại (0.7.8, 2026-11-15)
- `kiem_thu/kiem_thu_chat_luong.py`, Android `integration_test/chat_luong_test.dart`: 12 trang đại diện của hồ sơ 214 trang (`xlpdf_kiemthu/chat_luong`): chỉ 2 trang nhòe bị báo; 21 ảnh sách mở tổng hợp: chỉ ảnh tay đặt lên trang bị báo tay. Đều đạt ([[ho-so-15-11-sach-214-trang]]).

## Báo nhòe sau khi chụp, trang chụp trùng (0.7.9, 2026-11-16)
- `kiem_thu/tao_anh_rung.py` tạo `xlpdf_kiemthu/mo_chup` (ảnh chụp thật làm nhòe như rung tay, lấy nét hụt) và `xlpdf_kiemthu/trung` (35 trang quanh các cặp chụp trùng của [[ho-so-15-11-sach-214-trang]]).
- `kiem_thu_chat_luong.py`, Android `chat_luong_test.dart`: 22 ảnh chụp thật không bị báo, 28 ảnh làm nhòe đều bị báo; đúng 10 cặp trùng, không thừa ([[tu-dong-chup]]).
