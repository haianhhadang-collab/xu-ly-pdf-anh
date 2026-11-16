# Nhật ký dự án: Ứng dụng xử lý PDF ảnh

Mục mới ghi ở đầu file.

## 2026-11-16 · Đưa dự án lên GitHub (công khai) để dùng ở máy khác
- **Yêu cầu**: đẩy lên git, để chế độ chia sẻ, dùng ở máy khác (người dùng cũng hỏi cài bản 0.7.9 lên iOS: APK không cài được lên iPhone; bản iOS cần máy Mac để dựng, chưa làm).
- **Đã làm**: hai kho công khai trên tài khoản GitHub `haianhhadang-collab` (người commit đặt riêng trong mỗi kho, dùng địa chỉ noreply của GitHub):
  - https://github.com/haianhhadang-collab/xu-ly-pdf-anh : thư mục dự án (kế hoạch, nhật ký, yêu cầu, wiki, thiết kế, nguyên mẫu PC). Không đưa lên: `apk/`, `ket-qua/`, ảnh trang sách chụp thật `ung-dung/kiem_thu/trang_sach/`, ảnh thử tổng hợp sinh lại được, liên kết `ung-dung-flutter` (`.gitignore`). README có mục *Lấy dự án về máy khác*.
  - https://github.com/haianhhadang-collab/xu-ly-pdf-anh-flutter : mã Flutter (`D:\DevTools\src\xlpdf`, để riêng vì Gradle lỗi với đường dẫn có dấu). Bỏ `android/build/`, `*.log`. Thẻ `v0.7.9`, mục Releases có `xu-ly-pdf-anh-0.7.9.apk`.
  - Đã dò trước khi đẩy: không có email, số điện thoại, khóa ký; bộ ảnh thử `D:\DevTools\src\xlpdf_kiemthu` (ảnh của người dùng) không đưa lên.
- **Từ nay**: sửa xong thì commit và đẩy cả hai kho (`git push`); APK mới đưa lên Releases của kho Flutter.

## 2026-11-16 · Báo nhòe ngay trên màn camera, dò trang chụp trùng, rung báo đúng lúc chụp (bản Android 0.7.9, nguyên mẫu PC)
- **Yêu cầu**: báo nhòe ngay trên màn camera; tự rà soát xem còn cần làm gì thì làm luôn.
- **Rà soát** (hồ sơ 214 trang `Hồ sơ 15-11 19-33.pdf`, mã màn camera):
  - Màn camera rung báo "đã chụp" ngay lúc **bắt đầu lấy nét**, trước khi máy chụp thật (lấy nét có thể tới 1,5 giây). Người dùng tưởng đã chụp, lật trang luôn: đây nhiều khả năng là nguyên nhân trang 145, 146 nhòe.
  - Phép đo nhòe của 0.7.8 (lõi nét xám sau khi làm sạch) chỉ bắt được nhòe rất nặng: thử làm nhòe ảnh chụp thật, ảnh rung gần một cỡ chữ vẫn lọt (bước làm sạch kéo đậm lại nét). Chế độ Đen trắng không đo được.
  - Hồ sơ 214 trang có **11 cặp trang chụp trùng** (trang sách 146, 180, 181, 212, 213, 258, 259, 260, 261, 263, 294 mỗi trang hai lần; thứ tự trong PDF: 26–27, 56–58, 57–59, 90–92, 91–93, 137–139, 138–140, 141–143, 142–144, 146–148, 176–177). Lượt trước chỉ thấy cặp 180/181.
- **Đã làm**:
  - **Rung, nháy, tiếng chụp phát khi máy đã chụp xong** ảnh dùng được (lấy nét hụt thì sau lần chụp lại); lúc lấy nét hiện "Giữ yên, đang chụp…".
  - **Phép đo nhòe mới trên ảnh gốc** (`chat_luong.do_mo_mep` / `doMoMep`): độ rộng mép nét chữ theo 4 hướng, lấy hướng rộng nhất (rung tay chỉ nhòe theo một hướng); trang thu về 1600 px, ô 96 px; báo khi độ rộng trung vị quá 4,8 px. Ảnh chụp thật nét 2,4–2,9 px; rung 10 px 5,1–8,8 px. Đo được ở mọi chế độ làm sạch (kể cả Đen trắng). Dùng cùng phép đo cũ (giữ vì đã kiểm trên trang 145, 146 thật).
  - **Báo ngay trên màn camera** (`quy_trinh.kiem_tra_anh_chup` / `kiemTraAnhChup`): sau mỗi ảnh, isolate tìm mép, nắn phối cảnh, tách cặp trang rồi đo nhòe, tay che (không nắn cong, không cắt chữ). Có lỗi thì rung hai lần và hiện thanh cam "Trang N: chữ nhòe. Nên chụp lại." với nút **Chụp lại**: lần chụp tới thay ảnh của trang đó (trang giữ chỗ), tự chụp được phép chụp lại đúng trang vừa rồi. Chạy cả khi bật *Chụp xong mới xử lý*. Trên máy ảo 0,25–1,7 giây mỗi ảnh, không chặn lần chụp sau. Nguyên mẫu PC: thanh báo trong cửa sổ camera, nút "Chụp lại ảnh này (R)".
  - **Dò trang chụp trùng** (`chat_luong.dac_trung`, `diem_khop` / `dacTrung`, `diemKhop`, `trangTrung`): điểm đặc trưng ORB (trang 1000 px, 2000 điểm), đếm cặp khớp theo một phép đồng dạng (tự viết, tất định, thử mọi cặp trong 50 cặp khớp tốt nhất). Mỗi trang xử lý xong được so với 3 trang hai bên; giống hệt thì trang đứng sau báo "Giống hệt trang N, có thể chụp trùng" ở Xem nhanh, kèm nút xóa (hỏi lại trước khi xóa). PC: cột trạng thái ghi "trùng?", ô thông tin ghi "CÓ THỂ CHỤP TRÙNG". Ngưỡng 40 điểm khớp: cặp trùng 110–588, cặp trang khác nhau tối đa 26; cặp 146–148 (trang 146 có tay che nửa trang) chỉ 36 nên không báo trùng (trang đó đã có báo tay che). Chọn ngưỡng chặt vì báo nhầm có thể làm người dùng xóa mất trang thật.
  - Bản Android dựng thêm mô-đun OpenCV `features2d` (kèm `flann`) cho ORB (`pubspec.yaml`, `hooks.user_defines.dartcv4`); không thêm `calib3d` (nên tự viết bước khớp đồng dạng thay `findHomography`).
- **Kiểm thử**:
  - Bộ ảnh mới `ung-dung/kiem_thu/tao_anh_rung.py`: `xlpdf_kiemthu/mo_chup` (22 ảnh chụp thật làm nhòe như rung tay 12 px, 6 ảnh lấy nét hụt) và `xlpdf_kiemthu/trung` (35 trang của hồ sơ 214 trang quanh các cặp trùng).
  - `kiem_thu_chat_luong.py` và Android `chat_luong_test.dart`: 22 ảnh chụp thật không bị báo; 28 ảnh làm nhòe đều bị báo; đúng 10 cặp trùng, không thừa; 12 trang cũ, 21 ảnh sách mở vẫn đạt. So một cặp trang trên máy ảo khoảng 45 ms.
  - Luồng đầy đủ `xu_ly_anh` trên ảnh chụp thật `sach`, `sach2`: không trang nào bị báo nhầm. `kiem_thu_loi.py`, `kiem_thu_tach_trang.py` (33/33), `kiem_thu_sach_mo.py` đạt.
- **APK**: `apk/xu-ly-pdf-anh-0.7.9.apk` (99,4 MB, thêm 2,4 MB do mô-đun features2d, flann). Android `loi_test`, `cat_chu_test`, `tach_trang_test` (33/33) vẫn đạt.
- **Chưa làm**: báo trước khi chụp (trên khung xem trước độ phân giải thấp chưa đo được nhòe chữ); vết móng tay mờ ở lề dưới vài trang; chưa thử 0.7.7–0.7.9 trên điện thoại thật.

## 2026-11-15 · Tối ưu prompt OCR, soát chính tả, gõ lại bản scan thành PDF
<!-- phien:local_322bc354-9b57-4f4c-84aa-298c5e356625 ngay:2026-11-15 -->
- **Yêu cầu**: dùng skill `toi-uu-prompt` viết lại prompt "OCR, kiểm tra chính tả, gõ lại bản scan giữ nguyên trình bày, số trang, chú thích, in đậm, in nghiêng, ngoặc kép; mỗi 10 trang một file PDF tên Phần 1, Phần 2…".
- **Đã làm**: trả prompt mới (chế độ Người dùng, Lập kế hoạch) gồm vai trò, bối cảnh, 5 bước (OCR, soát chính tả chỉ sửa lỗi OCR và lỗi đánh máy hiển nhiên, gõ lại giữ trình bày, tách file 10 trang, kiểm tra) và yêu cầu báo lại chỗ sửa, chỗ `[không đọc được]`.
- **Chưa làm**: người dùng cần điền đường dẫn bản scan và thư mục lưu; chưa chạy thử prompt, chưa OCR tài liệu nào. Không tạo hay sửa tệp nào.

## 2026-11-15 · Báo trang nhòe, tay che trang, nút Chụp lại (bản Android 0.7.8, nguyên mẫu PC)
<!-- phien:local_2c7d86a1-499c-42df-a556-872685fbecd6 ngay:2026-11-15 -->
- **Yêu cầu**: người dùng đồng ý làm tiếp phần báo trang nhòe, có tay ngay sau khi chụp (còn tồn tại từ lượt dò hồ sơ 214 trang: trang 145, 146 chụp lúc tay đang lật trang).
- **Đã làm** (`ung-dung/loi_xu_ly/chat_luong.py`, `lib/loi/chat_luong.dart`):
  - **Nhòe**: đo trên ảnh đã làm sạch (Giữ màu, Xám). Chữ in nét có lõi nét gần đen; chữ nhòe loang mực, lõi chỉ còn xám. Chia trang thành ô chừng 6 dòng chữ; báo khi trên 45% ô có chữ có điểm tối nhất trên 60, hoặc lõi trung vị trên 55. Phép đo độ rộng mép nét chữ (thử trước) không dùng được: bước làm sạch đã kéo tương phản nên mép chữ nhòe vẫn sắc. Ảnh Đen trắng không đo được.
  - **Tay**: đo trên ảnh màu trước khi làm sạch, như `tiLeTay` của tự chụp (màu da trong vùng giữa trang, thuộc mảng chạm dải mép). Báo khi trên 5%: ngón cái giữ mép sách chỉ 0–3,4% (bước cắt chữ đã tự xóa).
  - Kết quả mỗi trang ghi vào `TrangTL.canhBaoAnh`; màn Xem nhanh, màn Các trang báo "Chữ nhòe, nên chụp lại" / "Tay che trang, nên chụp lại".
  - **Nút Chụp lại** (biểu tượng máy ảnh ở trang bị báo, màn Xem nhanh): mở camera, chụp một ảnh thay ảnh gốc (`Kho.thayAnh`), trang giữ chỗ trong hồ sơ, rồi quay về.
  - Nguyên mẫu PC: ô thông tin trang ghi "NÊN CHỤP LẠI: chữ nhòe / tay che trang" (`tt["canh_bao"]` của `xu_ly_anh`).
- **Kiểm thử**:
  - Thử trên cả 214 trang kết quả của người dùng: chỉ trang 145, 146 bị báo nhòe (ô lõi xám 0,58 và 0,64); trang tốt trung vị 0,05, cao nhất 0,36 (chữ in nhạt).
  - Bộ thử mới `kiem_thu/kiem_thu_chat_luong.py` và Android `integration_test/chat_luong_test.dart`: 12 trang đại diện lưu ở `xlpdf_kiemthu/chat_luong` (2 trang nhòe, 5 trang chữ nhạt dễ báo nhầm, 5 trang tốt) và 21 ảnh sách mở tổng hợp (tay đặt lên trang 32%, ngón cái giữ mép tối đa 3,4%). Python và Android đều đạt hết; số đo Android gần trùng Python.
  - Android `loi_test`, `cat_chu_test`, `tach_trang_test` vẫn đạt. Python `kiem_thu_loi.py`, `kiem_thu_tach_trang.py` 33/33 đạt.
  - Phép đo thêm khoảng 15–120 ms mỗi trang trên máy ảo (`loi_test` xử lý công văn 1,8 → 2,2 giây).
- **APK**: `apk/xu-ly-pdf-anh-0.7.8.apk`.
- **Chưa làm**: báo nhòe ngay trên màn camera trước khi chụp (hiện báo sau khi xử lý); chưa thử trên điện thoại thật.

## 2026-11-15 · Tách cặp trang đúng khe gáy, lề vừa, chụp xong mới xử lý, Xử lý lại cả hồ sơ (bản Android 0.7.7, nguyên mẫu PC)
- **Dữ liệu**: người dùng gửi `D:\Zalo Data\7b2d1456-…_Hồ sơ 15-11 19-33.pdf` (214 trang, 55,9 MB): cả cuốn sách chụp từng cặp trang, hồ sơ loại Sách (tự tách trang). Yêu cầu: dò các trang lỗi, tìm cách cải thiện; lề không cần cắt sát quá; làm vuông giấy có thể để sau khi chụp mới xử lý không.
- **Dò lỗi** (tách 214 trang ra ảnh bằng pypdf, ghép tờ thu nhỏ, xem từng trang):
  - **Tách gáy sai, lỗi nhiều nhất** (khoảng 70–80 trang): trang trái dính một dải chữ cái đầu dòng của trang phải; trang phải mất một hai chữ cái đầu dòng. Ví dụ trang 242/243, 218/219, 150/151. Nguyên nhân: `tach_trang_doi` cắt ở cột tối nhất (bóng gáy) trong khoảng 35–65% bề ngang, mà bóng gáy thường nằm lệch sang trang phải, đè lên chữ đầu dòng. Cặp trang nghiêng thì gáy xiên, một đường cắt thẳng đứng không đi lọt khe.
  - **Trang ngắn bị cắt còn mẩu**: trang cuối chương ít dòng (trang 195, 2 trang tài liệu tham khảo cuối) bị cắt sát chữ còn một dải 976×440.
  - **Lề sát, khổ trang không đều**: tỉ lệ cao/rộng các trang từ 1,3 đến 1,8.
  - **Ngón tay, ảnh nhòe** (trang 145, 146): tay đang lật trang lúc chụp, ảnh nhòe. Ảnh gốc hỏng, xử lý không cứu được, phải chụp lại.
  - **Trang trùng**: 180, 181 có hai lần (chụp lại một cặp trang).
- **Đã làm**:
  - **Tách cặp trang theo khe gáy** (`_khe_gay`, `cat_theo_duong` trong `nan_phang.py`; `kheGay`, `catTheoDuong` trong `lib/loi/nan_phang.dart`):
    - Lấy nét chữ (ngưỡng thích nghi, không bị bóng ảnh hưởng; bỏ nếp gáy, mép giấy, đốm). Tìm khe trắng rộng nhất ở giữa (30–70% bề ngang), hai bên đều phải có chữ.
    - Đo tâm khe theo 12 dải ngang, bỏ dải có khe quá rộng (dòng ngắn), khớp một đường thẳng (có loại điểm lệch); gáy nghiêng tối đa khoảng 6°.
    - Cắt theo đường xiên đó; phần của nửa này nằm bên kia đường cắt được lấp bằng điểm ảnh trên đường cắt (nền khe), không lẫn chữ trang bên.
    - Khổ gần vuông (không tìm được mép, cặp trang hẹp) vẫn tách nếu thấy rõ khe. Không thấy khe thì dùng cách cũ.
    - Bước nắn cong cặp trang (`nan_trang_cong`, khi không bật tách trang) cũng cắt theo khe này.
  - **Lề trang** (`cat_sat_chu(le=…, giu_kho=…)` / `catSatChu(le:, giuKho:)`): `sat` (như cũ), **`vua` (mặc định)** giữ lề thật của trang (khoảng cách chữ tới mép giấy) tới 6% cạnh dài, `trang` giữ trọn tới mép. Lề vẫn là nền trắng mới nên vết ngoài vùng chữ vẫn mất. Ảnh đã cắt theo mép giấy hoặc là một nửa cặp trang: trang ít chữ giữ khổ trang, không còn bị cắt thành mẩu. Tùy chọn `TuyChon.le`.
  - **Bản Android: chụp xong mới xử lý** (`Kho.batDauChup` / `ketThucChup`, `tamDung`): đang ở màn chụp thì chỉ lưu ảnh gốc; hàng đợi xử lý và đoán chiều chữ tạm dừng, máy dành cho camera. Rời màn chụp mới cắt, nắn vuông, tách trang, làm sạch. Cài đặt › *Chụp xong mới xử lý* (bật sẵn). Màn Các trang báo "Chụp xong sẽ xử lý n trang".
  - **Bản Android: Xử lý lại cả hồ sơ** (nút đũa thần ở màn Các trang, `Kho.xuLyLaiHoSo`): xử lý lại mọi trang từ ảnh gốc đã lưu theo cách mới nhất, chọn lề. Trang đã sửa chữ được giữ nguyên. Hồ sơ 214 trang của người dùng chạy lại được ngay, không phải chụp lại.
  - **Cài đặt › Lề trang**: Sát chữ / Vừa / Giữ cả trang (cho trang mới).
  - **Nguyên mẫu PC**: ô chọn *Lề trang* trong cửa sổ chính; `nan_lai_pdf.py --le=sat|vua|trang`.
- **Kiểm thử**:
  - Mới: `ung-dung/kiem_thu/kiem_thu_tach_trang.py`: đếm nét chữ chạm đường cắt trên 33 cặp trang (18 tổng hợp `anh_sach_mo`, 7 thật `sach`, 8 thật `sach2`). Cách cũ: 3 cặp chụp thật bị cắt qua chữ (goc4, goc7, doc4: 18–24 nét chạm). Cách mới: đạt 33/33.
  - Android mới: `integration_test/tach_trang_test.dart` (đáp án Python `xlpdf_kiemthu/tach_trang_python.json` do `ghi_dap_an_tach.py` ghi): đường cắt trùng bản Python trong vài điểm ảnh, đạt 33/33 (ca 12 tổng hợp: 2 mảnh bóng gáy đen chạm mép, không phải chữ; ngưỡng ≤ 2 nét mỗi bên, cách cũ chạm 18–24).
  - Đáp án cắt chữ cho bộ thử Android (`sach/`, `sach2/dap_an_python.json`) ghi lại theo lề mới bằng `ghi_dap_an_cat.py`; `cat_chu_test.dart` đạt, kích thước cắt trùng bản Python từng điểm ảnh (ngưỡng điểm xanh chữ ký ở phép thử công văn hạ còn 95% vì nhiễu nén JPEG; bản Python không mất điểm nào). `loi_test`, `le_khoi_test` (1,55% → 0,12%), `nua_trang_test`, `mep_cong_test` 17/17 đều đạt.
  - Python: `kiem_thu_loi.py` đạt hết; `do_cong.py` 17/17; `kiem_thu_sach_mo.py` đạt hết; `do_le.py` trung vị lệch lề 1,55% → 0,12%.
- **APK**: `apk/xu-ly-pdf-anh-0.7.7.apk`.
- **Chưa làm**: báo trang nhòe, có tay ngay sau khi chụp (trang 145, 146); vết móng tay mờ ở lề dưới vài trang còn sót; chưa thử 0.7.7 trên điện thoại thật.

## 2026-11-15 · Nắn vuông khối chữ, không cắt lẹm vào chữ; script nắn lại PDF có sẵn (bản Android 0.7.6, nguyên mẫu PC)
- **Dữ liệu**: người dùng gửi lại `D:\Zalo Data\mới.pdf`, 11 trang sách mở chụp bằng bản 0.7.2 (đã có trong bộ thử `xlpdf_kiemthu/sach2`). Hỏi: một số trang bị cắt lẹm vào chữ, có cách nào chỉnh méo, nắn vuông lại khối văn bản không.
- **Nhận xét**:
  - Khối chữ méo: lề trái, lề phải xiên hoặc cong (độ lệch lề trung vị 1,55% bề ngang trang, lớn nhất 4,2%). Hai trang của cùng cặp nghiêng mỗi trang một kiểu.
  - Bước nắn cong cũ chỉ dời theo chiều dọc. Bước sửa nghiêng xoay cả cặp trang theo một góc chung, nên chỉ thẳng được một trang.
  - Trang 17 bị cụt chữ ở mép phải: khi nắn phẳng, mép trang cong phình ra ngoài đường thẳng nối hai góc nên bị cắt. Nét chữ đã mất trong PDF cũ, không lấy lại được.
- **Đã làm** (`ung-dung/loi_xu_ly/nan_cong.py`, `nan_phang.py`, `quy_trinh.py`, `cat_chu.py`; `lib/loi/nan_cong.dart`, `nan_phang.dart`, `quy_trinh.dart`, `cat_chu.dart`):
  - **Nắn vuông khối chữ** (`nan_le` / `nanLe`):
    - Lấy đầu và cuối từng dòng chữ, khớp đường lề trái, lề phải (bậc 2), bỏ dòng thụt đầu đoạn, dòng cuối đoạn ngắn, tiêu đề.
    - Kéo ngang từng hàng điểm ảnh cho hai lề thẳng, vuông góc với dòng chữ, dòng nào cũng rộng bằng nhau.
    - Nới khung hai bên, tô màu nền, để không đẩy chữ ra ngoài ảnh.
    - Không nắn khi: lề lệch dưới 0,4%; lệch trên 8% (coi như khớp sai); khối chữ hẹp bất thường; chỗ lệch thành bậc đột ngột trên vài dòng liền (không phân biệt được với đoạn thụt lề).
  - **Cặp trang sách mở**: mỗi trang được nắn và xoay thẳng riêng theo dòng chữ của nó (`_xoay_thang` / `_xoayThang`, nới khung), rồi ghép lại, trang thấp hơn đệm màu nền.
  - **Không cắt lẹm khi nắn phẳng**:
    - Khung do máy tự tìm được nới thêm 2,5% mỗi cạnh (`NOI_KHUNG` / `noiKhung`).
    - Trong dải nới, mảng lớn tối hoặc có màu chạm mép ảnh (nền bàn, bìa sách) được tô màu giấy (`_xoa_nen_noi` / `_xoaNenNoi`). Nét chữ mảnh được giữ.
    - Khung người dùng tự kéo thì cắt đúng khung.
  - **Cắt sát chữ**: vết hình khung bao quanh gần cả ảnh thì không tô kín lòng (trước đây làm trắng cả trang).
  - **Script nắn lại PDF có sẵn**: `ung-dung/nan_lai_pdf.py` và `nan-lai-pdf.bat` (kéo thả PDF vào), ghi `<tên>_nan.pdf` cạnh tệp gốc; `--tach` tách cặp trang. Bản Android: nhập PDF ở màn Hồ sơ, ứng dụng xử lý lại theo cách mới.
  - Kết quả cho tệp của người dùng: `ket-qua/mới_nan.pdf`.
- **Kiểm thử**:
  - Python `ung-dung/kiem_thu/do_le.py` (mới, đo độ lệch lề trước và sau quy trình) trên 11 trang `sach2`: trung vị 1,55% → 0,17%.
    - Trang 10 (doc4) còn 4,8%: sáu dòng đầu hẹp lại thành bậc, cố ý không nắn.
  - Trên bộ ảnh sách mở tổng hợp: trung vị 1,01% → 0,52%. Các ảnh còn cao là do ngón tay giả đè lên chữ làm dòng ngắn, không phải méo.
  - `kiem_thu_loi.py`: đạt hết. Lỗi trang trắng do vết hình khung đã sửa trong lúc làm.
  - `do_cong.py` 17/17, `kiem_thu_sach_mo.py` đạt hết.
  - Android `integration_test/le_khoi_test.dart` (mới): trung vị 1,55% → 0,11%, đạt.
  - Android các bộ khác: `loi_test` 5/5, `mep_cong_test` 4/4, `cat_chu_test` 3/3 (khớp bản Python), `nua_trang_test`, `chieu_test` 2/2, `tu_chup_test` đạt.
- **APK**: `apk/xu-ly-pdf-anh-0.7.6.apk`.
- **Chưa làm**:
  - Chưa nắn được chỗ khối chữ lệch thành bậc đột ngột.
  - Ba dòng đầu trang 16 vẫn hơi cong ở góc trên trái: mặt cong dọc bậc 2 chưa theo kịp chỗ cong gắt.
  - Chưa thử trên điện thoại thật.

## 2026-11-14 · Chụp sách chỉ nhận một nửa cặp trang: nối trang bên kia gáy, nhắc lùi máy (bản Android 0.7.5, nguyên mẫu PC)
- **Dữ liệu**: người dùng gửi `D:\Zalo Data\a49b7bcb-…_mới.pdf` (15 trang, chụp bằng 0.7.4). Góp ý: kết quả đã khá tốt, nhưng khi chụp sách có lúc ứng dụng chỉ nhận 1/2 trang.
- **Nhận xét**:
  - Trang 1 là cả cặp trang 120/121. Trang 2, 3 chỉ có trang 122 và 124, mất 123 và 125. Từ trang 126 trở đi người dùng chụp từng trang một.
  - PDF trước (`Hồ sơ 14-11 20-26.pdf`, bản 0.7.3) cũng thiếu như vậy: chỉ còn 122, 124, 126.
  - Không có ảnh gốc, nên đã thử lần lượt các bước:
    - Bộ tìm mép trên khung video cũ, Python và Dart: lấy đủ cặp trang.
    - Tách trang, lưu kết quả, xuất PDF: không bỏ trang nào.
    - Bộ ảnh tổng hợp sách mở mới: lấy đủ hai trang khi cả cặp nằm trong khung, kể cả gáy rất tối và trang cong mạnh.
  - Tái hiện được khi chụp sát và mép ngoài một trang lọt ra ngoài khung. Bộ tìm mép chọn trang còn nguyên, có đủ bốn mép trong khung. Tự chụp thấy trang đó không bị cắt nên chụp luôn, và trang kia mất hẳn.
- **Đã làm** (`ung-dung/loi_xu_ly/tim_mep.py`, `lib/loi/tim_mep.dart`):
  - Sau khi chọn tứ giác, xét từng cạnh (`_canh_noi` / `_canhNoi`). Cạnh được coi là gáy của một cặp trang bị cắt khi đủ ba điều kiện:
    - bên kia cạnh là giấy (trên 60% điểm giống giấy) có chữ (mật độ mực trên 35% bên trong);
    - trang bên kia chạy tới biên ảnh;
    - phần trang bên kia thấy được bằng 50–102% bề rộng trang (một bên cho tới 130%, vì trang gần máy trông rộng hơn).
  - Khi đó kéo cạnh ấy ra tới biên ảnh dọc theo hai cạnh kề (`_noi_canh` / `_noiCanh`).
  - Ảnh ra giữ cả phần trang bên kia thấy được.
  - Lúc tự chụp, khung nối có hai góc trên mép khung hình, nên ứng dụng nhắc "Lùi máy ra cho thấy đủ trang" và không chụp nửa cặp trang.
  - Chụp từng trang thì trang bên cạnh thường chỉ lộ dưới 50%, không nối.
- **Kiểm thử**:
  - Bộ ảnh mới `ung-dung/kiem_thu/tao_anh_sach_mo.py`, 21 ảnh, ghép từ các trang sách người dùng chụp (`kiem_thu/trang_sach`). Gồm nền đen, gỗ, vải; cầm máy dọc và ngang; gáy tối; trang cong; tràn khung; chụp từng trang.
  - Python `kiem_thu_sach_mo.py`: đạt hết. Trước khi sửa, hai ảnh tràn khung chỉ ra một trang.
  - Hai ảnh chụp từng trang (20, 21) để dạng tham khảo, không tính đạt hay trượt. Bộ tìm mép có từ 0.7.0 lấy cả mẩu trang bên cạnh ở ảnh 20 và không thấy trang ở ảnh 21; lỗi này không do phần nối.
  - `do_mep.py`: 17/17. Bộ ngẫu nhiên: 24/24. `kiem_thu_loi.py`: đạt hết.
  - `kiem_thu_tu_chup.py`: các mục chức năng đạt. Mục tốc độ vẫn hỏng như trước (138 ms).
  - Android `integration_test/nua_trang_test.dart` (mới, ảnh ở `xlpdf_kiemthu/sach_mo`): đạt (21 ảnh, hai ảnh tràn khung ra đủ hai trang và tự chụp nhắc lùi máy). Các bộ khác: `mep_cong_test` 4/4, `loi_test` 5/5, `tu_chup_test` (phát lại video) đạt, `cat_chu_test` 3/3, `chieu_test` 2/2.
- **APK**: `apk/xu-ly-pdf-anh-0.7.5.apk`.
- **Chưa làm**: chưa thử trên ảnh gốc của chính lần chụp lỗi (người dùng chưa gửi ảnh gốc) và chưa thử trên điện thoại thật. Trang 136 của PDF có vài chữ bị trắng mất ở nửa trái; cần ảnh gốc mới biết là ngón tay che chữ hay do bước xóa vết.

## 2026-11-14 · Tự chụp nhanh, không đứng chờ; nhận lật trang, tay trên trang; rung báo (bản Android 0.7.4, nguyên mẫu PC)
- **Dữ liệu**: người dùng gửi `Hồ sơ 14-11 20-26.pdf` (13 trang, sách mở đặt trên nền đen, chụp bằng 0.7.3, chất lượng chữ tốt) và video quay màn hình lúc chụp (76 giây, 6 cặp trang). Góp ý: phát hiện khung hình lâu, báo giữ yên sách rồi chạy lại, có lần rất lâu mới chụp; muốn giảm thời gian chờ hoặc có báo rung.
- **Nhận xét từ video** (tách khung hình, chạy lại lõi tự chụp trên từng khung):
  - Sách nằm yên mà vẫn báo "Giữ yên máy": phép đo rung là chênh lệch thô giữa hai khung, sách trắng trên nền đen tương phản mạnh nên tay cầm máy run nhẹ đã vượt ngưỡng 5.
  - Mỗi khung hỏng (tìm mép trượt một khung, rung thoáng qua) làm đồng hồ giữ yên chạy lại từ đầu; góc trang lệch quá 1,5% so với lúc bắt đầu (tay trôi chậm) cũng chạy lại.
  - Sau khi lật sang cặp trang mới vẫn báo "Đã chụp trang này" (giây 17–34): hai cặp trang sách in cùng khổ chỉ khác nhau 0,22–0,33 theo bản đồ mật độ mực, sát ngưỡng 0,24; cặp trang 3 chờ 18 giây mới chụp được.
- **Đã làm** (`lib/loi/tu_chup.dart`, `ung-dung/loi_xu_ly/tu_chup.py`):
  - Đo rung theo độ dời (chênh lệch chia độ dốc sáng, không phụ thuộc tương phản), ngưỡng 2,5 điểm ảnh; thêm độ dời trong từng ô lưới 4×4 (ngưỡng 5) để bắt tay đang vuốt, lật trang.
  - Thời gian chịu 0,4 giây: khung tìm mép trượt, mất trang thoáng qua không làm đếm lại (rung và tay thì đếm lại ngay). Khung trang so với khung trung bình trượt, cho lệch 3%.
  - Nhận động tác lật trang: cộng các chuỗi khung xáo trộn liền nhau từ 0,25 giây (mất trang, trang bị cắt, rung, có tay, khác trang vừa chụp trên 0,45). Đủ 1 giây thì trang mới chỉ cần khác 0,18 (chưa lật vẫn đòi 0,24, va máy về trang cũ không chụp lại).
  - Nhận tay trên trang (`tiLeTay` / `ti_le_tay`): điểm màu da (sắc 6–25, bỏ đỏ của mực dấu, bão hòa cao hơn giấy 30) thuộc mảng chạm dải mép trang; che quá 0,5% phần trong của trang thì nhắc "Bỏ tay ra khỏi trang", không chụp. Giấy phủ kín khung thì không xét.
  - Thời gian giữ yên: Nhanh / Vừa / Chắc = 0,3 / 0,5 / 0,9 giây (trước 0,5 / 0,8 / 1,2), mặc định Vừa.
  - Rung báo (Android): kênh `xlpdf/rung` gọi `Vibrator` (quyền VIBRATE), rung nhẹ 25 ms khi bắt được trang (bắt đầu đếm giữ yên), 70 ms khi chụp; tắt ở Cài đặt › *Rung báo*.
- **Kiểm thử**:
  - Android `integration_test/tu_chup_test.dart` (mới): chạy lại 688 khung hình video (`xlpdf_kiemthu/video`, đã bỏ khung màn trắng lúc chụp của bản cũ). Bản mới chụp đủ 6 cặp trang lúc 6,9 / 12,5 / 18,5 / 40,3 / 50,9 / 59,1 giây (bản 0.7.3: 7,3 / 13,3 / 34,5 / 43,2 / 53,8 / 61,0), không chụp khi tay trên trang; còn 2 lần chụp lại cùng trang do video nén và khung màu vẽ đè làm cùng trang lệch 0,22–0,27 (ảnh camera thật bản 0.7.3 không chụp trùng). Đạt.
  - `loi_test.dart` 5/5 (chuỗi mô phỏng chụp đúng 2 trang), `mep_cong_test.dart` 4/4 (sát mép không báo lùi máy).
  - Python `kiem_thu_tu_chup.py`: các mục chức năng đạt; mục tốc độ (≤ 60 ms/khung) hỏng 133 ms do bộ tìm mép `nan_phang.tim_mep_giay` của bản PC (132 ms, có từ trước, không đổi lần này; phần nhận tay thêm 6 ms).
- **APK**: `apk/xu-ly-pdf-anh-0.7.4.apk`. Chưa thử trên điện thoại thật.
- **Lưu ý dựng**: `chay_kiem_thu.sh` đẩy cả `xlpdf_kiemthu` (thêm ~45 MB khung hình video).

## 2026-11-14 · Tự xoay ảnh chụp cầm máy ngang, xóa ngón tay, bóng mép, đường gáy, giữ tiêu đề (bản Android 0.7.3, nguyên mẫu PC)
- **Dữ liệu**: người dùng gửi `D:\Zalo Data\mới.pdf` (11 trang sách mở chụp bằng bản 0.7.2, không kèm lời nhắn).
- **Nhận xét**:
  - Cả 11 trang nằm ngang (chữ chạy dọc). Người dùng cầm máy ngang để chụp trang sách mở; ứng dụng khóa màn hình dọc nên ảnh ra dọc, chữ nằm ngang. Ứng dụng chỉ báo "sai chiều", không tự xoay.
  - Vì chữ chạy dọc, các bước cần dòng chữ ngang đều hỏng: tìm gáy (ảnh dọc), nắn cong, sửa nghiêng, cắt sát chữ.
  - Còn sót: ngón tay sau làm sạch thành mảng cam nhạt, có chỗ đè lên chữ ở bìa; vệt bóng cong xám ở mép (bóng ngón tay); mẩu đen ở góc; vệt gáy đứt quãng giữa hai trang.
  - Tiêu đề "MỞ ĐẦU" bị cắt mất vì cách thân bài xa hơn ngưỡng gộp khối.
- **Đã làm**:
  - **Nhận dòng chữ dọc**: `ung-dung/loi_xu_ly/chieu_chu.py`, `lib/loi/chieu_chu.dart`. Nối chữ theo chiều ngang rồi chiều dọc, chiều nào ra nhiều dải dài, mảnh hơn hẳn thì là chiều dòng. Bước này chạy ngay sau nắn phối cảnh; chữ dọc thì xoay 90° trước khi tách trang, nắn cong, sửa nghiêng, cắt sát chữ. Chạy khoảng 0,04 s.
  - **Tự lật theo Tesseract** (Android, `kho.kiemChieu`): nếu đoán cần xoay, đủ 12 từ, chưa sửa chữ và người dùng chưa tự xoay, thì tự xoay một lần mỗi trang (trước đây chỉ cảnh báo). Tùy chọn trang `tuXoay`, bật sẵn.
  - **Người dùng tự xoay** (nút Xoay, xoay theo khổ) thì tắt tự xoay của trang đó, gộp phần đã tự xoay vào góc xoay tay để trang quay đúng góc người dùng thấy.
  - **Cắt sát chữ, xóa vết** (`cat_chu.py`, `lib/loi/cat_chu.dart`):
    - Bán kính nét: chữ in, kể cả tiêu đề đậm, dưới 0,35 chiều cao chữ. Nét dày mà nhạt (bóng ngón tay, vệt bóng cong) là vết, kể cả khi nằm trong vùng chữ (nếu nhỏ, không kín như ảnh minh họa). Nét dày, rất tối, sát mép là mẩu đen.
    - Tiêu đề, chú thích nằm trong bề ngang vùng chữ được gộp ở khoảng cách tới 12% chiều cao trang.
    - Nét chạm mép ảnh không kéo rộng vùng cắt.
    - Dải gáy: dải giữa không có chữ, rộng từ 4 chiều cao chữ, hai bên đều có chữ. Nét trong dải bị xóa, trừ nét màu và nét vắt qua dải.
    - Ngón tay (`xoa_da_tay` / `xoaDaTay`): mảng màu da đặc, đủ lớn (sắc 5–30, bão hòa 35–200), nới theo phần da nhạt nối liền, tô trắng. Nét chữ cỡ chữ bị ngón tay đè được giữ, chuyển xám. Dấu đỏ (sắc 0–4, rỗng ruột) và dòng tô sáng (mảnh) không bị tính.
    - Vùng chữ vẫn tìm trên ảnh gốc, chỉ tô trắng ngón tay trên ảnh ra. Tô trắng trước làm sót mẩu viền, kéo rộng khung cắt ở 2/8 trang sách cũ.
  - Python: `xu_ly_anh` thêm `tt["xoay_doc"]`; `kiem_thu_loi.py` thêm mẫu 2b (ảnh lệch 90°, 270°).
  - Android: `chieu_test.dart` (trang lệch 90°, 270°, 180° tự về đúng chiều), `cat_chu_test.dart` thêm 11 trang lần này (`xlpdf_kiemthu/sach2/doc0–10.jpg`, `dap_an_python.json`). `pubspec.yaml` 0.7.3+12, `apk/xu-ly-pdf-anh-0.7.3.apk`.
- **Kiểm tra**:
  - Python: nhận chữ dọc đúng 22/22 trên 11 trang (và đúng khi xoay về), 0 báo nhầm trên các ảnh thử đã nắn phẳng. Tìm gáy 8/8 trang sách mở sau khi xoay. Giữ lại "MỞ ĐẦU". Xóa vệt bóng cong, mẩu đen, đường gáy, ngón tay (bìa, trang 16–17). 8 trang sách lần trước: kết quả như cũ (một trang hẹp hơn 2%, không lẹm chữ). `kiem_thu_loi.py` TẤT CẢ ĐẠT.
  - Android máy ảo: 9 bộ kiểm thử đều đạt: chieu_test 2/2 (trang lệch 90° và 270° tự xoay dòng chữ về ngang, trang lệch 90° và 180° tự lật theo Tesseract, đoán lại đều 0°), cat_chu_test 3/3 (11 trang lần này: nhận chữ dọc 11/11 khoảng 0,04 s, cắt trùng bản Python, gáy lệch dưới 25 điểm ảnh; 8 trang lần trước như cũ; công văn giữ đủ dấu đỏ, chữ ký), loi, lam_sach, mep_cong, sua_ky_tu 10/10, sua_chu 7/7, nhan_dang, so_trang. PC: kiem_thu_sua_pdf.py dựng trang mẫu không cắt sát chữ (5 mục sai từ bản 0.7.2 hết); còn 3 mục sai ở cách sửa cũ viết lại khối (đọc lại bằng OCR), có từ trước, lần này không đổi phần đó.
- **Chưa làm, chưa kiểm**:
  - Chữ bị ngón tay che kín (bìa sách) không khôi phục được.
  - Còn vệt bóng xám rất nhạt sát ngón tay; chấm nhỏ ở đầu gáy.
  - Tự lật dựa vào Tesseract: trang ít chữ (dưới 12 từ) vẫn chỉ cảnh báo.
  - Chưa thử lại trên điện thoại thật.

## 2026-11-14 · Cắt sát chữ, xóa vết đen, nắn cong sách mở hai trang (bản Android 0.7.2, nguyên mẫu PC)
- **Yêu cầu** (người dùng chụp thử bản 0.7.1, gửi `Hồ sơ 14-11 14-01.pdf`, 8 trang sách mở hai trang): chất lượng chữ đã tốt; cắt và làm phẳng trang cần tốt hơn: cắt sát vào chữ hơn, tự động loại bỏ vết, vệt đen trong ảnh.
- **Nhận xét ảnh**: ảnh đã đủ nét (~2340 điểm ảnh bề ngang). Còn: dải nền tối, trang sách khác ở mép trên (khung cắt bám mép giấy cong), ô đen, bậc thang đen ở góc, nêm đen ở đầu gáy sách, ngón tay giữ sách ở mép dưới; dòng chữ vẫn võng 0,4–0,6% chiều cao vì ảnh hai trang có hai mặt cong ngược nhau nên bộ nắn cong (một mặt cong chung) bỏ qua 7/8 ảnh.
- **Đã làm**:
  - Cắt sát chữ `ung-dung/loi_xu_ly/cat_chu.py`, `lib/loi/cat_chu.dart` (bước cuối, sau sửa nghiêng): tìm nét mực và vùng tối; nhận vết theo số đo trên chính ảnh người dùng (nét chữ xám 85–110, bão hòa ~0; nêm đen, góc đen xám 16–22; ngón tay màu da bão hòa 50–95, sắc 8–35; dấu đỏ, chữ ký bão hòa ~155 không bị tính): khối lớn lấp kín khung bao, rất tối, màu da, vệt sáng dài, nét lớn chạm mép; mảnh vụn sát vết cũng là vết. Nối chữ thành khối, giữ khối nhiều chữ, gộp khối nhỏ ở gần (số trang, chú thích), nới vùng cho trọn mọi nét chạm vào (dấu chấm cuối dòng từng bị lẹm). Ảnh ra = vùng chữ + lề trắng 1,5 chiều cao chữ (ít nhất 1,5% cạnh dài); vết lấn vào vùng được tô trắng kín. Tùy chọn `catSatChu` / `cat_sat_chu`, bật sẵn; nút *Cắt sát chữ* ở màn Chỉnh trang, ô chọn ở PC.
  - Nắn cong ảnh sách mở: `timGay` / `tim_gay` tìm gáy (ảnh khổ ngang, dải giữa có mực dưới 0,3 lần trung bình; ảnh người dùng 0,05–0,15, trang đơn > 1), nắn từng trang rồi ghép lại.
  - Sửa lỗi lưu hồ sơ (`kho.luu`): hai lần lưu đồng thời ghi chung tệp tạm, lần sau lỗi PathNotFoundException; nay xếp hàng từng hồ sơ.
  - Kiểm thử cũ đo tỉ lệ A4, nền trắng cả trang, kích thước trang sau khi xoay: chạy với `catSatChu: false` (tính năng đó vẫn kiểm như trước); `kiem_thu_loi.py` thêm 3 mục cắt sát chữ.
  - Android 0.7.2: `apk/xu-ly-pdf-anh-0.7.2.apk`, `pubspec.yaml` 0.7.2+11; ảnh thử `D:\DevTools\src\xlpdf_kiemthu\sach\` (8 trang sách đã xử lý từ PDF người dùng, kèm `dap_an_python.json`).
- **Kiểm tra**:
  - Python trên 8 ảnh người dùng: nắn cong theo gáy 7/8 ảnh, võng 0,11–0,34% → 0,02–0,05% (ảnh trang đơn không tách); cắt sát chữ xóa hết dải nền tối, nêm đen, góc đen, phần lớn ngón tay; công văn mẫu còn 52% diện tích, giữ đủ dấu đỏ, chữ ký, mép ảnh trắng. `kiem_thu_loi.py` TẤT CẢ ĐẠT, `do_cong.py` 17/17.
  - Android máy ảo `integration_test/cat_chu_test.dart` 2/2: 8 ảnh cắt ra đúng kích thước bản Python, mép ảnh không còn điểm tối, gáy trùng bản Python, 0,15–0,5 s/trang; công văn: đỏ 13084→13101, xanh 426→443 điểm. Các bộ cũ đều đạt: loi_test, chieu_test (khung tay xoay đo khi không cắt sát), lam_sach_test, mep_cong_test 4/4, sua_ky_tu_test 10/10, nhan_dang_test, so_trang_test, sua_chu_test 7/7 (đổi chuỗi tìm khối 'Kính gửi', 'TRƯỞNG PHÒNG', 'Đồng ý' sang phần ít dấu, vì từ 0.7.0 góc khung lệch tới 3 px so với bộ tìm mép cũ làm Tesseract đọc sai một dấu: 'Kinh gửi', 'TRƯỚNG', 'Đỏng ý').
- **Chưa làm, chưa kiểm**:
  - Còn sót vệt rất nhỏ cạnh số trang ở vài trang (mảnh nhỏ hơn ngưỡng vết), viền ngón tay rất mờ.
  - Cắt sát chữ làm trang không còn đúng tỉ lệ A4; khi xuất khổ A4 ảnh được co giãn vừa trang (chữ to hơn bản gốc). Tắt *Cắt sát chữ* nếu cần giữ nguyên khổ giấy.
  - Ảnh minh họa tối đặc chạm mép trang có thể bị xem là vết; trang không đủ chữ thì không cắt.
  - Ảnh hai trang chụp ở chế độ *Giấy rời* vẫn ra một trang PDF ngang; muốn mỗi trang sách một trang PDF thì chọn *Sách* khi chụp.
  - Chưa thử lại trên điện thoại thật.

## 2026-11-14 · Ảnh chụp mờ, tự chụp báo lùi máy sai, tách nhận dạng chữ (bản Android 0.7.1)
- **Yêu cầu** (người dùng chụp thử bằng điện thoại thật, gửi `Hồ sơ 14-11 13-23.pdf`, 3 trang): (1) ảnh bị out nét lúc chụp, kết quả quá mờ; (2) khung hình đã bao trọn trang giấy nhưng chế độ tự động vẫn báo lùi máy, không chụp hoặc khó chụp; (3) ảnh kém nên OCR kém, sai: tách OCR thành chức năng riêng, không làm ngay khi xuất.
- **Nguyên nhân**:
  - Ảnh trong PDF chỉ khoảng 1030×1430 điểm ảnh: camera mở ở `ResolutionPreset.veryHigh` (1080p) nên trang A4 chỉ ~120 dpi; lại không lấy nét trước khi chụp, không kiểm tra ảnh mờ.
  - Bộ tự chụp báo "lùi máy" khi mép giấy cách mép khung dưới 1% dù trang vẫn trọn trong khung. Bản 0.7.0 còn cho bộ tự chụp dùng bộ tìm mép mới đầy đủ, chậm (máy ảo 184 ms/khung, trước đó 15 ms) nên khó giữ đủ lâu để chụp.
  - Xuất PDF mặc định bật "Thêm lớp chữ" nên lần nào xuất cũng chạy OCR.
- **Đã làm**:
  - `lib/man_hinh/chup.dart`: camera mở ở độ phân giải tối đa (`ResolutionPreset.max`), không mở được thì lùi về 1080p; chế độ lấy nét tự động; chạm vào khung xem trước để lấy nét, đo sáng (vòng tròn vàng); trước mỗi lần chụp lấy nét vào giữa khung và chờ xong (tối đa 1,5 s); chụp xong đo độ mờ, mờ thì lấy nét lại, chụp lại một lần, giữ ảnh nét hơn, vẫn mờ thì nhắc chụp lại.
  - Đo độ mờ `tiLeNet` (`lib/loi/tu_chup.dart`): độ nét vùng giữa ảnh ở 1280 px chia cho ở 640 px. Thử trên Python: ảnh nét 0,67–0,93, mờ kiểu lấy nét hụt (σ ≥ 3 px trên ảnh 3000 px) 0,45–0,59; ngưỡng 0,55. Không phụ thuộc lượng chữ trên trang.
  - Tự chụp: dùng bộ tìm mép bản nhanh (`timTuGiac(tinh: false, canh: 400)`, 57–60 ms/khung trên máy ảo); chỉ báo "Lùi máy ra cho thấy đủ trang" khi trang thật sự bị cắt: hai góc cùng sát một mép khung, hoặc một góc bị kẹp đúng vào mép (`_biCat`).
  - OCR tách riêng: màn Xuất PDF không còn hai công tắc "Thêm lớp chữ", "Xuất kèm .txt" và không tự nhận dạng (xuất nhanh, PDF ảnh trang). Màn Các trang có nút **Nhận dạng chữ** (thay nút nhỏ trên thanh tiêu đề): xem, chép, chia sẻ, **Lưu .txt**, **PDF có chữ** (mở màn Xuất kèm lớp chữ ẩn đã nhận dạng); báo trang máy đọc kém (độ tin cậy trung bình dưới 70%) để chụp lại. Thanh nút: Sắp xếp, Nhận dạng chữ; Xuất PDF rộng hết hàng.
  - Android 0.7.1: `apk/xu-ly-pdf-anh-0.7.1.apk`, `pubspec.yaml` 0.7.1+10; ảnh máy ảo `apk/anh-chup-may-ao/0.7.1-*.png`. Python `tim_mep.tim_tu_giac` thêm tham số `canh` như bản Dart.
- **Kiểm tra** (máy ảo): `mep_cong_test.dart` thêm hai phép, đạt 4/4: tự chụp với khung hình ôm sát trang (mép giấy cách mép khung 0,4%) thì chụp, không báo lùi máy; khung hình cắt mất góc trang thì báo `cat_mep` (3 ảnh mẫu); đo mờ: ảnh nét 0,92 và 0,66, làm mờ 0,39, ảnh nhỏ hơn 1280 px không đo. `loi_test` đạt (tự chụp 57 ms/khung). Bấm thử: camera mở ở mức tối đa, chạm lấy nét hiện vòng tròn, bấm chụp lưu được trang; Nhận dạng chữ, PDF có chữ mở màn Xuất kèm lớp chữ; Xuất thường ghi chú "PDF gồm ảnh trang, không nhận dạng chữ".
- **Chưa làm, chưa kiểm**:
  - Máy ảo không có camera thật: chưa kiểm được lấy nét thật, độ phân giải thật của ảnh chụp, tốc độ phân tích khung ở độ phân giải tối đa trên điện thoại (khung lớn hơn thì chép sang isolate tốn hơn).
  - Ngưỡng đo mờ 0,55 chọn trên ảnh tổng hợp; ảnh điện thoại thật (có làm sắc, nén JPEG) có thể lệch, cần ảnh thật để chỉnh.
  - Trang 1 trong PDF người dùng gửi (trang bìa sách) bị nằm nghiêng 90°: có lẽ do ảnh mờ nên đoán chiều chữ trượt; chưa kiểm lại với ảnh nét.

## 2026-11-14 · Tự căn chỉnh, làm phẳng kiểu CamScanner (bản Android 0.7.0, nguyên mẫu PC)
- **Yêu cầu**: chạy bản Android trên máy thật, tự xoay cho khối chữ vuông góc và làm trắng đã đạt nhưng ảnh chưa được làm phẳng; muốn tự căn chỉnh, làm phẳng như CamScanner.
- **Nguyên nhân**: bộ tìm mép cũ chỉ lấy đường bao lớn nhất của ảnh cạnh hoặc vùng sáng ít màu. Trên bộ ảnh tổng hợp khó mới dựng, bộ cũ đạt 10/15 ảnh cố định, 12/30 và 16/29 ảnh ngẫu nhiên: trượt khi giấy nằm trên bàn trắng, nền lộn xộn, giấy chồng giấy, bìa sổ; không tìm được thì trang để nguyên, không nắn. Chưa có nắn trang cong.
- **Đã làm**:
  - Bộ ảnh thử `ung-dung/kiem_thu/tao_anh_mep.py`: chiếu trang công văn qua máy ảnh lỗ kim (phẳng hoặc cong như sách mở) lên các nền gỗ, bàn trắng, lộn xộn, vải, tối; có ngón tay, bóng đổ, góc ra ngoài khung, giấy kín khung, giấy chồng giấy, sổ bìa tối, ảnh tối mờ; kèm đáp án 4 góc (`anh_mau_mep/`, 17 ảnh; `ngau_nhien N hạt` tạo bộ ngẫu nhiên). Đo bằng `do_mep.py`, `do_cong.py`.
  - Bộ tìm mép mới `ung-dung/loi_xu_ly/tim_mep.py` và `lib/loi/tim_mep.dart`: xóa chữ bằng phép đóng, đổi Lab; ứng viên từ Canny 3 mức, Otsu sáng/tối, k-means 2 và 3 cụm, ghép 4 đường Hough; chấm theo độ bám mép dọc từng cạnh (ngưỡng theo độ nhiễu hai bên mép, đạo hàm cùng dấu), cộng phần diện tích và phần giống giấy; tờ giấy nằm trên vật khác thì chọn tứ giác trong khi vành ngoài không có chữ; tinh chỉnh từng cạnh ở ảnh 1280 px rồi giao lại ra góc. Kiểm tra "ngoài khung còn giấy có chữ" (chụp kín hai trang sách) sửa để không tính mép bìa sổ, tờ giấy lót.
  - Nắn trang cong `nan_cong.py` / `nan_cong.dart`: tìm dòng chữ, khớp đường cong bậc 3 từng dòng, khớp mặt độ lệch dọc trơn cho cả trang (bậc 4 theo x, bậc 2 theo y), ánh xạ ngược; trang phẳng (lệch < 0,3% chiều cao) để nguyên. Chạy sau nắn phối cảnh, trước làm sạch; tùy chọn `nanCong` / `nan_cong`, bật sẵn.
  - Xóa viền nền bàn (`xoaVienToi`, `xoa_vien_toi`): xóa cả mảnh nền chạm sát mép ảnh (mép trang cong để lại vệt đứt đoạn).
  - Android, màn Chỉnh trang: thẻ đổi tên *Cắt, nắn phẳng*; kéo 4 góc hoặc giữa cạnh (dời cả cạnh theo pháp tuyến); kính lúp phóng 2,5 lần có chữ thập ở góc phía không có ngón tay; phần ngoài khung tối đi; nút *Nắn trang cong*.
  - PC: ô *Nắn trang cong (theo dòng chữ)*; cửa sổ camera dùng bộ tìm mép mới không tinh chỉnh, 15 khung một lần.
  - Lỗi tìm thấy khi chuyển sang Dart: (1) `Mat.data`, `f32` chỉ là cửa sổ vào bộ nhớ Mat, Mat tạm bị thu hồi làm ứng dụng chết SIGSEGV: thêm `u8Chep`, `f32Chep`, `i32Chep` (`lib/loi/anh.dart`); (2) phép hình thái của `opencv_dart` mặc định coi ngoài ảnh là màu 0 (Python thì bỏ qua), phép đóng tạo dải tối giả quanh mép ảnh nên chọn nhầm khung toàn ảnh: dùng `borderType: BORDER_REPLICATE`.
  - Android 0.7.0: `apk/xu-ly-pdf-anh-0.7.0.apk` (92 MB), `pubspec.yaml` 0.7.0+9; ảnh máy ảo `apk/anh-chup-may-ao/0.7.0-*.png`.
- **Kiểm tra**:
  - Python: `do_mep.py` 17/17 (lệch góc lớn nhất 3–6 px trên ảnh 1500×2000), hai bộ ngẫu nhiên 24/24 và 29/29 (bỏ ảnh có góc giấy ra ngoài khung quá 3%); khoảng 0,25–0,45 s/ảnh trên PC. `do_cong.py`: trang cong mạnh võng trung vị 0,66% → 0,06%, 0,24% → 0,06% chiều cao; 15 trang phẳng không bị nắn. `kiem_thu_loi.py` vẫn TẤT CẢ ĐẠT.
  - Android máy ảo: `integration_test/mep_cong_test.dart` đạt cả hai phép: tìm mép 17/17 (lệch 3,3–10,1 px, trung bình 0,44 s/ảnh), nắn cong 0,66% → 0,07%, 0,29% → 0,07%, trang phẳng để nguyên. `loi_test` (tìm mép ảnh mẫu cũ lệch 1,7 px, trước 5,4 px), `chieu_test`, `lam_sach_test` đều đạt. Bấm thử: nhập 2 ảnh (nền lộn xộn, sách cong) tự cắt, nắn đúng; kéo góc, kéo giữa cạnh, kính lúp, *Tự tìm khung*.
- **Chưa làm, chưa kiểm**:
  - Chưa thử ảnh chụp thật, điện thoại thật; bộ ảnh thử là ảnh tổng hợp (cần ảnh chụp thật của người dùng để chỉnh ngưỡng).
  - Nắn cong chỉ kéo thẳng theo chiều dọc: chữ bị co ngang gần gáy sách chưa giãn lại; trang không có dòng chữ (ảnh, bảng) không nắn được; mép trang cong ngoài vùng chữ vẫn theo đường thẳng nối góc.
  - Tìm mép trên điện thoại khoảng 0,4–1 s/ảnh, chạy ở nền; khung xem trước lúc chụp (tự động chụp) vẫn dùng bộ dò nhanh riêng trong `tu_chup.dart`.
  - Chưa có bước "cắt ngay sau khi chụp" như CamScanner: khung tự tìm được dùng luôn, chỉnh lại ở thẻ *Cắt, nắn phẳng*.

## 2026-10-30 · Đổi phông, cỡ chữ đoạn bôi chọn khi sửa ký tự (bản Android 0.6.0, nguyên mẫu PC)
<!-- phien:local_1e5aa893-fdf3-4f2c-af88-e55783bf9f84 ngay:2026-10-30 -->
- **Yêu cầu**: thêm chức năng đổi phông, cỡ chữ. Người dùng chọn phạm vi "đoạn chữ bôi chọn" trong Sửa ký tự (đổi cỡ thì phóng, thu chính nét gốc; đổi phông thì chỉ đoạn chọn vẽ lại bằng phông mới), làm cả PC và Android.
- **Đã làm** (cả `ung-dung/loi_xu_ly/sua_ky_tu.py` và `lib/loi/sua_ky_tu.dart`):
  - Phiên sửa dòng có đoạn bôi chọn (`moc` + con trỏ): Shift + ← → / Home / End, kéo chuột, Ctrl+A (PC); chạm giữ rồi kéo trong dòng, hoặc bật nút Bôi chọn rồi ← → (Android). Gõ khi đang chọn thì thay đoạn chọn; Backspace, Delete xóa cả đoạn.
  - `dinh_dang_chon` / `dinhDangChon`: giữ nét gốc thì mỗi ký tự trong đoạn thành mảnh chép chính nét của nó (chỉ nét của dòng, nền và lõi mực đo trên cả dòng) phóng, thu theo tỉ lệ; phần sau tự dồn. Trả cỡ về 1 thì mảnh gốc trở lại nguyên chỗ, dòng như chưa sửa. Đổi phông thì đoạn chọn vẽ lại bằng phông, kiểu, cỡ đã chọn, màu mực và độ nhòe (PC) hoặc viền đậm (Android) đoán từ chính đoạn đó; mỗi mảnh nhớ bản gốc để trả về nét gốc.
  - `kieu_doan_chon` / `kieuDoanChon`: đoán phông, cỡ của đoạn chọn trên các ký tự gốc (vẽ thử, so hình như cũ). Chữ gõ thêm ngay sau đoạn đã đổi theo định dạng đó (như trình soạn thảo).
  - Chữ phóng to được vẽ ra ngoài dải dòng; vẫn không vẽ đè nét dòng khác trong dải. Android: `SuaDong.vungVe` tính các hàng bị vẽ lại, xem trước phủ đúng vùng đó.
  - PC (`sua_pdf.py`): bôi chọn xong thì khung Chữ nạp Phông/Kiểu "Tự đoán" (giữ nét gốc) và cỡ đoán được (pt); đổi Cỡ là phóng, thu nét gốc; chọn Phông hoặc Kiểu là vẽ lại đoạn chọn; Ctrl+] / Ctrl+[ tăng, giảm 1 pt; dải chọn tô xanh.
  - Android (`lib/man_hinh/sua_trang.dart`): thanh định dạng hiện khi có đoạn chọn: "đoạn chọn", A− / cỡ (pt) / A+ (bước 0,5 pt), menu phông (Giữ nét gốc + 8 phông Liberation). Nút Bôi chọn đặt ở hàng ô gõ để hàng nút không tràn trên máy 360 dp. Đoán phông cho Sửa ký tự bỏ kiểm tra mực màu theo khối (dòng đã được xét theo cả dòng; trước đây có thể báo nhầm "có con dấu" và không vẽ được ký tự thiếu).
  - Android 0.6.0: `apk/xu-ly-pdf-anh-0.6.0.apk`, `pubspec.yaml` 0.6.0+8; ảnh `apk/anh-chup-may-ao/0.6.0-doi-co-phong.png` (máy ảo: bôi chọn "nhựa", 17,3 → 21,5 pt), `0.6.0-kiem-thu-doi-co-phong.png`.
- **Kiểm tra**:
  - PC `kiem_thu_sua_pdf.py` thêm mục 1f (dòng nghiêng): chọn đúng "nhựa", đoán Times New Roman 17 pt; phóng 1,5: cao 36 → 54 px, rộng 87 → 131 px, phần trước đoạn chọn giữ nguyên từng điểm ảnh, chữ dòng khác 0 điểm mực đổi; trả cỡ 1 thì như chưa sửa; đổi sang Arial đậm, gõ "X" theo phông đó, đọc lại "nhựaX Melamine". Toàn bộ: TẤT CẢ ĐẠT. Thử cửa sổ bằng sự kiện giả lập: kéo chuột chọn, khung Chữ nạp 17,5 pt, đổi cỡ, Ctrl+[, đổi phông, trả về nét gốc thì không ghi thao tác.
  - Android `sua_ky_tu_test.dart` thêm (i), đạt 10/10 trên máy ảo: rộng 87 → 132 px, vùng vẽ 119–275 (dải 156–260), xem trước khớp ảnh kết quả, phần trước đoạn chọn và nét dòng khác không đổi, trả cỡ về gốc như chưa sửa, đổi phông Liberation Sans đậm, đọc lại "nhựaX Melamine". Bấm thử trên máy ảo: bôi chọn, đoán 17,3 pt, A+ tám lần thành 21,5 pt, chữ phóng nhô lên trên dải dòng không bị cắt.
- **Chưa làm, chưa kiểm**: chưa thử trên điện thoại thật; chưa bấm thử menu đổi phông trên máy ảo (máy ảo tự tắt giữa chừng; đổi phông đã có kiểm thử (i)); đổi phông dùng chữ máy đọc, đọc sai thì vẽ sai (cần soát); chữ phóng to có thể chạm dòng trên, dòng dưới nếu phóng nhiều (không đè nét trong dải dòng nhưng ngoài dải thì có thể); PC dùng phông Windows Times/Arial, Android dùng Liberation.

## 2026-10-30 · Gõ tiếng Việt khi sửa ký tự: lỗi phông, lỗi đậm nhạt (bản Android 0.5.2, nguyên mẫu PC)
- **Yêu cầu**: người dùng báo phần sửa chữ khi gõ tiếng Việt bị lỗi phông, lỗi đậm nhạt.
- **Nguyên nhân** (tái hiện trên ảnh chụp nhãn hàng người dùng gửi và trang tổng hợp có dòng chữ đậm xen dòng chữ thường, làm mờ như ảnh chụp):
  - khung ký tự LSTM của Tesseract lệch ngang tới nửa chữ (khung "ư" trong "tướng" trùm sang "t", khung "ộ" lấn sang "m"), nên mẫu chép kèm nét chữ bên cạnh, dấu của chữ bên cạnh: trông như sai phông;
  - chọn mẫu theo độ đậm trung bình cả dòng, đo bằng biến đổi khoảng cách (chỉ ra bội 1 điểm ảnh) nên không phân biệt được chữ đậm, chữ thường khi nét chỉ dày 3–4 điểm ảnh: "p", "h", "ớ" lấy từ dòng in đậm, "T", "h" từ dòng nét mảnh;
  - mẫu giữ nguyên độ đậm mực của chỗ chép (ảnh chụp sáng tối không đều);
  - chữ có dấu hiếm (ố, é, ộ…) chỉ có một mẫu, thường ở dòng khác kiểu, hoặc không có thì vẽ bằng phông đoán sai.
- **Đã làm** (cả `ung-dung/loi_xu_ly/sua_ky_tu.py` và `lib/loi/sua_ky_tu.dart`):
  - `nan_khung` / `nanKhung`: nắn khung ký tự theo nét mực thật. Mỗi từ: nét chính (cao từ nửa chữ thường, chạm đường chân) ghép với chữ theo thứ tự bằng quy hoạch động so mép trái, phải (một chữ nhiều nét đứt, nhiều chữ dính một nét); dấu thanh, chấm, móc, dấu nặng theo chữ đứng dưới, trên; chữ phải chia chung một nét đánh dấu kém tin khi làm mẫu.
  - Độ đậm: bề dày nét = 2 × diện tích / chu vi, đo riêng từng ký tự (Android đệm trong `kt_*.json`, phiên bản đệm 4); so trung vị vài chữ quanh chỗ chèn với vài chữ quanh mẫu (nhân tỉ lệ cỡ); có mẫu chênh dưới 18% thì bỏ mẫu chênh nhiều. Loại mẫu dáng lạ (so hình 16×16 với các mẫu cùng tên, chỗ máy đọc nhầm).
  - Mẫu chép bỏ nét nằm hẳn trên, dưới khung ký tự và dấu lọt từ chữ bên cạnh (chữ không dấu); tô bằng màu mực lõi nét các chữ quanh chỗ chèn.
  - `ghep_dau` / `ghepDau`: chữ có dấu không có sẵn, chỉ có ở kiểu nét khác hoặc ở trang khác thì ghép thân chữ (ưu tiên chữ không dấu; chữ cùng thân khác dấu thì bỏ dấu cũ) với cụm dấu trên, dấu dưới chép từ chữ khác, đặt so với thân như ở chữ nguồn. Android: bảng tách dấu, bảng ghép dấu sinh bằng `unicodedata` (Dart không có chuẩn hóa Unicode).
  - Gõ dấu rời (bộ gõ Unicode tổ hợp): ghép thành chữ dựng sẵn; dấu gõ sau chữ vừa chèn thì gộp vào chữ đó.
  - Nét dời đi, chữ chèn không đè lên nét dòng khác ở chỗ mới.
  - Android 0.5.2: `apk/xu-ly-pdf-anh-0.5.2.apk`, `pubspec.yaml` 0.5.2+7; ảnh `apk/anh-chup-may-ao/0.5.2-go-tieng-viet.png`.
- **Kiểm tra**:
  - Trang tổng hợp (`trang_dam_nhat()`; Android `xlpdf_kiemthu/mau7-dam-nhat.png`), gõ " bé dưới bô" + dấu nặng rời vào dòng chữ thường: ra đúng "bédướibộ", mọi chữ chép từ trang; "é" chỉ có ở dòng đậm nên được ghép từ "e" thường + dấu sắc; bề dày nét chữ chèn trung vị 2,8 px so với chữ thường 2,6 px (dòng đậm 3,7 px); đọc lại "bé dưói bộ" ("ớ" chỉ có ở chữ dính nét nên móc ngắn). Trước khi sửa: "é" lấy từ dòng đậm, "ư", "ớ", "ộ" kèm nét chữ bên cạnh, đọc lại "bé dturd b‹".
  - Ảnh chụp người dùng gửi (chỉ thử trong thư mục tạm): gõ " thành phố" vào dòng "TP Hồ Chí Minh": các chữ cùng độ đậm (trước: "h", "p" đậm lẫn nhạt).
  - `kiem_thu_sua_pdf.py` thêm mục 1e, đạt toàn bộ; bấm thử cửa sổ trên bản sao tệp hồ sơ thật vẫn đạt; trang mục lục thật vẫn 0 cột chồng.
  - Android `sua_ky_tu_test.dart` thêm (h), đạt 9/9 trên máy ảo; APK 0.5.2 đã cài lên máy ảo (versionName 0.5.2).
- **Chưa làm, chưa kiểm**: chưa thử trên điện thoại thật; ký tự cả trang không có và không ghép được (như "đ" trên ảnh nhãn hàng) vẫn vẽ bằng phông đoán, có thể lệch kiểu (viền vàng, chọn mẫu tay được); chữ dính nét chữ bên cạnh khi làm mẫu vẫn có thể thiếu một phần (móc "ơ"); ảnh mờ, máy đọc sai nặng thì mẫu có thể sai chữ (chỉ loại được khi có từ 3 mẫu cùng tên).

## 2026-10-30 · Sửa ký tự trên dòng nghiêng (bản Android 0.5.1, nguyên mẫu PC)
- **Yêu cầu**: người dùng thử bản 0.5.0 trên điện thoại thật với ảnh chụp nhãn hàng (dòng nghiêng, dòng sát nhau), gửi ảnh chụp màn hình: chữ sửa xong bị lệch dòng; những chữ không sửa cần được giữ nguyên.
- **Nguyên nhân**: mỗi dòng được coi là một dải ngang thẳng. Dời phần sau chỗ sửa là dời cả cột điểm ảnh trong dải, nên kéo theo nét của dòng trên, dòng dưới lọt vào dải (dòng "Thành phẩm…" bị nát); ký tự chèn đặt theo một đường chân nằm ngang (trung vị cả dòng) nên lệch khỏi dòng nghiêng; mẫu chép lấy cả nét dòng bên cạnh trong cùng cột.
- **Đã làm** (cả `ung-dung/loi_xu_ly/sua_ky_tu.py` và `lib/loi/sua_ky_tu.dart`):
  - Dòng có độ nghiêng: đường chân xiên đo bằng Theil–Sen qua đáy khung các ký tự không có nét xuống (bỏ g, p, y, chữ có dấu nặng, dấu phẩy…); dải xiên trên, dưới đường chân phủ trọn dấu thanh, nét xuống; dải dọc của dòng nới ra chứa trọn phần xiên. Đệm khung ký tự Android lên phiên bản 3 (đệm cũ tự đọc lại).
  - `net_cua_dong` / `netCuaDong` (mới): phân nét mực trong dải dòng thành của dòng và của chỗ khác (thành phần liên thông theo khung ký tự của dòng nào phủ nhiều nhất; không chạm khung thì theo dải xiên; nét dính hai dòng tách từng điểm; đường kẻ dài, nét quá cao không thuộc dòng nào).
  - Dựng dòng: mảnh đứng nguyên chỗ không đụng tới; mảnh phải dời thì chỉ nét của dòng (nới 1 điểm ảnh, không lấn nét chỗ khác) được xóa chỗ cũ, vá nền (PC: `cv2.inpaint`; Android: trung bình điểm nền gần nhất bốn hướng) rồi dán sang chỗ mới, lệch dọc theo độ dốc. Ký tự chép đặt theo đường chân tại chỗ chèn; mẫu chép chỉ lấy nét của chính dòng nguồn. Dòng dựng lại để sửa tiếp giữ độ nghiêng.
  - Giao diện (PC, Android): khung dòng, viền dòng đang sửa, con trỏ đỏ vẽ nghiêng theo dòng; chạm chọn dòng theo dải xiên.
  - Android 0.5.1: `apk/xu-ly-pdf-anh-0.5.1.apk` (khoảng 96 MB), `pubspec.yaml` 0.5.1+6.
- **Kiểm tra**:
  - Trang tổng hợp năm dòng sát nhau xoay 2,5° (`trang_nghieng()`; Android `xlpdf_kiemthu/mau6-dong-nghieng.png`): đo độ nghiêng −0,0441 (thật −0,0437); chèn " nhựa ăn": ngoài dải dòng và nét dòng trên, dòng dưới trong dải không đổi điểm ảnh nào, phần trước chỗ sửa giữ nguyên, ký tự chèn lệch đường chân dưới 1 px, đọc lại đúng. Trước khi sửa, cùng thao tác làm đổi 3604 điểm mực của dòng bên cạnh và máy đọc lại thành chữ loạn.
  - Ảnh chụp màn hình người dùng gửi (phần dòng chưa bị sửa, chỉ thử trong thư mục tạm): chèn " nhà" vào dòng "Địa chỉ…": dòng bên cạnh không đổi điểm mực nào.
  - `kiem_thu_sua_pdf.py` thêm mục 1d, đạt toàn bộ (mục 1c đổi cách so phần sau chỗ sửa: so nét chữ, nền giữ tại chỗ). Bấm thử cửa sổ trên bản sao tệp hồ sơ thật vẫn đạt.
  - Android `sua_ky_tu_test.dart` thêm (g), đạt 8/8 trên máy ảo: như bản PC, thêm xem trước khớp ảnh kết quả, sửa tiếp trên dòng dựng lại (xóa " ăn") vẫn không đổi gì ngoài dải. APK 0.5.1 đã cài lên máy ảo (versionName 0.5.1).
- **Chưa làm, chưa kiểm**: chưa thử lại trên điện thoại thật; khung dòng nghiêng trên màn hình chưa xem bằng mắt trên máy ảo; dòng cong (sách mở) mới xấp xỉ bằng đường thẳng; ảnh mờ làm hai ký tự dính nhau thì mẫu chép có thể kèm một phần ký tự bên cạnh (có từ trước).

## 2026-10-30 · Tham khảo ONLYOFFICE: đối tượng, vùng scan, chú thích, thao tác trang (nguyên mẫu PC)
- **Yêu cầu**: tham khảo chức năng chỉnh chữ và đối tượng trong PDF của ONLYOFFICE DesktopEditors. Người dùng chọn cả bốn hướng: đối tượng chọn lại được; dời, xóa vùng có sẵn trên bản scan; chú thích không phá bản gốc; thao tác trang kiểu ONLYOFFICE. ONLYOFFICE dùng giấy phép AGPL-3.0 nên chỉ học cách làm, không lấy mã.
- **Đã làm** (thư mục `ung-dung/`):
  - `loi_xu_ly/doi_tuong.py` (mới): khung, dời, đổi cỡ cho chữ thêm, ảnh chèn, khung che, tô sáng; thao tác `HinhVe` (chữ nhật, elip, đường, mũi tên); `tim_vung` tự đánh dấu vùng trên bản scan (mỗi dòng chữ, ảnh, bảng một vùng, vùng có mực màu bị khóa); `DoiVung` chép nét mực gốc (có độ trong) sang chỗ mới, vá nền chỗ cũ, hoặc chỉ xóa.
  - `sua_pdf_doi_tuong.py` (mới, lớp trộn của cửa sổ Sửa PDF): công cụ *Chọn, dời, đổi cỡ*: bấm chọn, kéo dời, kéo ô vuông đổi cỡ, Delete, phím mũi tên, Ctrl+C / Ctrl+V, bấm đúp sửa chữ đã thêm (ô sửa tại chỗ điền sẵn chữ cũ), đổi phông, kiểu, cỡ, màu áp ngay cho chữ đang chọn; Ctrl+Y làm lại. Vùng scan tìm trên ảnh chưa có chữ thêm, hình vẽ, chú thích để không bị gộp nhầm.
  - `loi_xu_ly/chu_thich.py` (mới): ghi chú (/Text), bút phê (/FreeText), tô sáng (/Highlight), chữ nhật, elip (/Square, /Circle), đường, mũi tên (/Line), dấu "ĐÃ XEM" kèm ngày (/Stamp). Hình hiển thị /AP vẽ bằng reportlab (nhúng tập con Times New Roman, đủ dấu tiếng Việt) rồi chuyển thành Form XObject; xem trước trên màn hình dựng chính hình ấy bằng PDFium nên thấy sao lưu vậy. Chú thích nằm trong danh sách thao tác (chọn, dời, hoàn tác như đối tượng) nhưng không tính là sửa nội dung: trang PDF gốc vẫn chép nguyên, Subject không ghi "đã chỉnh sửa", chỉ ghi `/XuLyPdfAnhChuThich`.
  - `loi_xu_ly/tai_lieu_pdf.py`: đổi điểm ảnh sang điểm PDF theo ba trường hợp (ảnh scan đặt đúng chỗ cũ; trang dựng lại thành ảnh hoặc trang trắng; trang PDF chép nguyên có /Rotate và hộp cắt lệch gốc), hình hiển thị xoay ngược góc /Rotate để người đọc thấy thẳng; xoay trang có chú thích thì đổi tọa độ chú thích theo; chỉ lấy thẳng ảnh gốc khi trang không có /Rotate; thêm `di_chuyen`, `chep`, `dan` (mỗi lần dán là bản sao riêng).
  - `sua_pdf_trang.py` (mới, lớp trộn): kéo thả ảnh trang đổi thứ tự (vạch cam chỉ chỗ thả, kéo cả nhóm trang đã chọn, tự cuộn ở mép), menu chuột phải (xoay, chèn trang trắng trước / sau cùng khổ trang bên cạnh, chèn tệp trước / sau, nhân đôi, chép, cắt, dán trước / sau, lưu ra tệp mới, xóa), Ctrl+C / X / V / Delete; bộ nhớ trang dùng chung các cửa sổ Sửa PDF.
  - `sua_pdf.py`: thêm công cụ *Chọn, dời, đổi cỡ*, *Vẽ hình*, *Chú thích (không sửa bản gốc)*, khung *Chú thích*, nút *Làm lại (Ctrl+Y)*; ảnh hiện = ảnh đã sửa + chú thích vẽ chồng (ảnh dùng để sửa ký tự, tìm vùng không có chú thích).
- **Kiểm tra**:
  - `kiem_thu_sua_pdf.py` đạt toàn bộ, thêm mục 5 (dời, đổi cỡ đối tượng; 15 vùng trên trang mẫu, 3 vùng con dấu bị khóa; dời một vùng không đổi điểm ảnh nào ngoài chỗ cũ, chỗ mới), mục 6 (đủ 5 loại chú thích chuẩn; nội dung trang chép nguyên; không ghi dấu đã sửa; trang /Rotate 0, 90 và trang trắng: PDFium dựng bản lưu, chú thích trùng chỗ xem trước 100%; xoay đi rồi về chú thích về đúng chỗ), mục 7 (kéo thả nhiều trang, chép dán hai lần sang tài liệu khác, trang dán chép nguyên).
  - Thêm phép thử riêng trên 6 kiểu trang (kể cả trang hộp cắt lệch gốc, trang ảnh scan của tệp người dùng, trang đã sửa nội dung): chú thích lưu ra trùng chỗ xem trước 100%.
  - Bấm thử cửa sổ bằng script trên bản sao tệp `Hồ sơ 29-10 22-09.pdf`: chọn, dời, đổi cỡ chữ thêm và mũi tên, dời một dòng có sẵn, hoàn tác / làm lại, chép / dán / xóa, bấm đúp sửa chữ; tạo 5 loại chú thích, dời dấu, sửa lời ghi chú, lưu ra 5 chú thích, trang gốc chép nguyên; hai cửa sổ: kéo trang 5 lên vị trí 2, chèn trang trắng, nhân đôi, chép 2 trang dán sang cửa sổ kia, lưu ra chép nguyên. Các phép thử cửa sổ cũ (sửa ký tự trên tệp thật) vẫn đạt.
- **Chưa làm, chưa kiểm**: menu chuột phải mới kiểm bằng lệnh, chưa bấm tay; chưa đọc lại chú thích có sẵn trong PDF mở vào (chỉ giữ nguyên, chưa sửa được); đổi cỡ vùng scan là phóng ảnh nét mực nên chữ có thể nhòe; chưa làm các tính năng này trên bản Android.

## 2026-10-30 · Sửa ký tự giữ nguyên bản gốc (nguyên mẫu PC; bản Android)
- **Yêu cầu**: người dùng gửi tệp `Hồ sơ 29-10 22-09.pdf` (7 trang ảnh, xuất từ bản Android, ảnh khoảng 100–127 dpi; trang 1 là mục lục luận án) và nhận xét: chức năng sửa chữ gây mất hết định dạng, cỡ chữ, OCR sai nội dung; cần công cụ giữ nguyên nội dung, hình dạng, kích thước của bản scan, bản chụp và chỉ thêm, bớt ký tự, nội dung.
- **Nguyên nhân cách cũ hỏng**: viết lại cả khối từ chữ máy đọc rồi vẽ bằng phông, nên máy đọc sai đâu sai đó (ở 127 dpi Tesseract đọc dãy chấm thành chữ loạn, "giữa" thành "glữ"), và dáng chữ bản scan (chữ hẹp, đậm, nhòe) không có trong bộ phông.
- **Đã làm, nguyên mẫu PC**:
  - `loi_xu_ly/sua_ky_tu.py` (mới): dòng chia thành mảnh liền nhau (mỗi ký tự, khoảng trắng là một dải điểm ảnh gốc; khung ký tự từ hOCR `hocr_char_boxes`). Xóa = bỏ mảnh; chèn = chép nguyên hình ký tự từ chính trang, rồi các trang khác (đánh dấu chưa chắc), cuối cùng mới vẽ phông; người dùng chọn mẫu bằng chuột phải. Dãy chấm dẫn co giãn ở cuối dãy để số trang đứng nguyên chỗ.
  - Các bẫy gặp trên tệp thật và cách xử lý: phóng ảnh lên khoảng 300 dpi chỉ để nhận dạng; tìm dãy chấm theo hình dạng (bỏ "chữ" đọc nhầm trong đó, kể cả khi scan nghiêng, chấm nhòe to); nối dài dòng theo nét mực vì Tesseract bỏ sót số trang đứng lẻ; gộp dòng tách rời cùng hàng; đo cỡ chữ bằng chữ thường không dấu đọc chắc; tính đường chân chữ sau cùng; mẫu chép chỉ lấy nét chạm khung ký tự; loại mẫu chữ, số quá nhỏ (chỗ đọc nhầm); bỏ mảnh rộng 0.
  - `sua_pdf.py`: công cụ chính *Sửa ký tự (giữ nguyên bản gốc)*: bấm vào dòng đặt con trỏ, phím mũi tên, Backspace, Delete, gõ để chèn, Enter xong, Esc hủy, xem trước ngay, tự cuộn tới con trỏ, viền vàng ký tự chưa chắc, chuột phải chọn mẫu. Công cụ viết lại khối đổi tên "Viết lại cả khối chữ (vẽ lại bằng phông)".
  - `loi_xu_ly/tai_lieu_pdf.py`: trang PDF chỉ gồm một ảnh (bản scan) được sửa trên chính ảnh gốc (PDFium `get_bitmap(render=False)`), lưu ra đúng kích thước, đúng chỗ đặt cũ; trang khác dựng theo độ phân giải ảnh thay vì luôn 300 dpi.
- **Kiểm tra (PC)**:
  - Trên tệp thật (bản sao): "giữ" → "giữa", "956" → "95" (số trang vẫn thẳng lề phải, dãy chấm giãn liền mạch): ngoài dải dòng sửa không đổi điểm ảnh nào, trong dòng phần trước chỗ sửa không đổi điểm ảnh nào. "74" → "75": trang không có mẫu "5" đọc được, mẫu lấy từ trang khác lệch kiểu chữ, được viền vàng để người dùng chọn mẫu khác. Lưu ra: ảnh trang 1 vẫn 1057×1482, trang 2–7 chép nguyên, Subject "2 chỗ sửa ký tự"; dựng lại trang so với gốc chỉ khác ở hai dải dòng đã sửa.
  - `kiem_thu_sua_pdf.py` thêm mục 1c, đạt toàn bộ: "15" → "20" chép từ chính trang, phần sau dời đúng chênh bề rộng giữ nguyên điểm ảnh, đọc lại đúng; trang mục lục tổng hợp: nhận 62 chấm theo hình dạng, "156" → "15" mép phải lệch 1 px, chèn "các " trước "Mục tiêu" số trang đứng nguyên, chữ chèn đúng cỡ, đúng đường chân.
- **Chưa làm, chưa kiểm (PC)**: chưa chọn được vùng tùy ý làm mẫu (chỉ chuột phải lên ký tự máy tách được); dòng dài quá lề chỉ cảnh báo, chưa tự xuống dòng; trang không phải một ảnh (PDF chữ thật) vẫn dựng lại ở độ phân giải ảnh hoặc 300 dpi.
- **Đã làm, bản Android 0.5.0** (giao một tác tử con; mã ở `D:\DevTools\src\xlpdf`):
  - `MainActivity.kt`: kênh nhận dạng thêm tham số `kyTu`, trả hOCR kèm khung từng ký tự.
  - `lib/loi/sua_ky_tu.dart` (mới): chuyển trọn thuật toán bản PC (phóng ảnh chỉ để nhận dạng, dãy chấm theo hình dạng, nối dài dòng theo nét mực, gộp dòng cùng hàng, cỡ chữ, đường chân, mẫu chỉ lấy nét chạm khung, loại mẫu quá nhỏ), phiên sửa một dòng, dựng lại dòng sau khi sửa để sửa tiếp không cần nhận dạng lại. Đệm khung ký tự riêng từng ảnh (`kt_<ảnh>.json`); các trang khác nhận dạng dần ở nền để lấy mẫu.
  - Màn Chỉnh trang: mặc định *Sửa ký tự (giữ nguyên bản gốc)*: chạm dòng đặt con trỏ đỏ, nút ← → ⌫ ⌦, ô gõ + *Chèn*, *Xong* / *Hủy*, viền vàng và dòng nhắc cho ký tự chưa chắc, chạm giữ chọn mẫu, tự cuộn theo con trỏ, khóa dòng có mực màu, nút quay lại không bỏ ngang chỗ đang sửa. Cách cũ đổi tên *Vẽ lại bằng phông*. PDF xuất ra ghi Subject đếm riêng "chỗ sửa ký tự", "chỗ sửa chữ".
  - Hai lỗi tác tử phát hiện khi chạy tệp thật, đã sửa ở bản Dart và **sửa luôn ở bản PC** (`manh_dong`, `khe_trong_tu` trong `ung-dung/loi_xu_ly/sua_ky_tu.py`): (1) từ máy đọc chồng lên từ sau, bỏ một mảnh rộng 0 để lộ chỗ chồng với mảnh trước nữa, vài cột điểm ảnh bị dán hai lần thành vệt lạ; trên tệp người dùng, cách cũ chồng 381–399 cột ở các trang 1–3 (dòng mục lục), cách mới 0; (2) khe chuẩn giữa hai ký tự tính cả khe giữa các chấm dẫn nên ký tự chèn trên trang mục lục bị giãn thưa: nay bỏ khe cạnh dấu chấm.
- **Kiểm tra (Android)**: `sua_ky_tu_test.dart` 7/7 (đã chạy lại độc lập trên máy ảo): "15" → "20" ngoài dải dòng và phần trước chỗ sửa không đổi điểm ảnh nào, "2", "0" chép từ chính trang, đọc lại đúng; mục lục "156" → "15" mép phải lệch −1 px, chèn "các " số trang đứng nguyên, chữ chèn cùng cỡ, cùng đường chân; ký tự lấy từ trang khác được đánh dấu chưa chắc, chọn mẫu tay chạy đúng; dòng có mực màu bị khóa; sửa tiếp trên dòng vừa dựng lại đọc đúng. Nhận dạng khung ký tự một trang công văn khoảng 2,2 s, chèn một ký tự khoảng 13 ms. 6 bộ cũ vẫn đạt (theo tác tử). Trên ảnh trang mục lục của tệp người dùng: "giữ" → "giữa", "956" → "95" mép phải lệch 1 px. APK `apk/xu-ly-pdf-anh-0.5.0.apk` (khoảng 96 MB), đã cài lại lên máy ảo; ảnh `apk/anh-chup-may-ao/0.5.0-*.png`. Bản PC sau khi sửa hai lỗi: `kiem_thu_sua_pdf.py` đạt toàn bộ, bấm thử trên tệp thật vẫn đạt.
- **Chưa làm, chưa kiểm (Android)**: chưa thử điện thoại thật và bộ gõ tiếng Việt thật (adb không gõ được tiếng Việt); nhập ảnh mục lục qua ứng dụng thì bước làm sạch (xóa đốm bụi) xóa bớt chấm dẫn nhỏ nên số trang không tự đứng nguyên chỗ (lỗi của bước làm sạch, có từ trước, chưa sửa).

## 2026-10-30 · Sửa chữ theo khối, gõ ngay trên trang (nguyên mẫu PC; bản Android)
- **Yêu cầu**: gộp các chữ cùng dòng, các dòng cùng đoạn vào một khối, sửa trực tiếp cả khối; nếu được thì sửa ngay trên giao diện trang; làm tương tự cho bản APK.
- **Đã làm, nguyên mẫu PC** (`ung-dung/`):
  - `loi_xu_ly/sua_noi_dung.py`: `tim_khoi` gộp từ theo đoạn của Tesseract, đoán căn lề (trái, giữa, đều hai bên, phải), thụt đầu dòng; thao tác `SuaKhoi`: đoán phông, cỡ, màu theo dòng dài nhất, đo khoảng cách dòng theo đường chân chữ, xóa nét cả khối, dàn lại chữ mới (ngắt dòng theo từ, Enter là ngắt cứng, căn như cũ), số dòng đổi thì dời phần trang bên dưới. Giữ `SuaChu` (theo từ) cho tương thích.
  - `sua_pdf.py`: công cụ *Sửa chữ* hiện khung từng khối; bấm khối mở ô gõ chữ đặt ngay trên trang (cùng phông, cỡ, màu, căn lề, khoảng cách dòng theo tỉ lệ phóng); Ctrl+Enter hoặc bấm ra ngoài để áp, Esc hủy; phóng to khi đang sửa vẫn giữ chữ. *Thêm chữ* cũng gõ ngay trên trang. Bỏ hộp thoại sửa chữ cũ.
- **Phát hiện khi kiểm chứng**:
  - Đoạn 2 dòng căn trái bị nhận nhầm căn đều (với 2 dòng thì "các dòng trừ dòng cuối chạm lề phải" luôn đúng): đổi điều kiện, đuôi các dòng phải trùng nhau (lệch ≤ 0,6% bề rộng trang) và khoảng trống giữa từ giãn rộng hơn dòng cuối ≥ 12%.
  - Chữ dàn lại rộng hơn gốc khoảng 3% (cỡ đo theo chiều cao nét chỉ vài chục điểm ảnh) nên ngắt dòng sớm: dòng dài chỉnh cỡ theo bề rộng cả dòng; nay ngắt đúng chỗ cũ ("… đề nghị").
  - Dòng đơn căn trái dài thêm bị ngắt dòng vì giới hạn bằng độ dài dòng cũ: cho dàn tới mép phải vùng chữ của trang.
- **Kiểm tra (PC)**: `kiem_thu_sua_pdf.py` đạt toàn bộ, thêm mục 1b: quốc hiệu, tiêu ngữ thành một khối 2 dòng căn giữa; đoạn "Căn cứ…" khối 2 dòng căn trái; viết thêm một câu → 4 dòng, dòng đầu ngắt đúng chỗ cũ, phần dưới dời 150 px nguyên vẹn, phần trên không đổi; tiêu đề dài hơn vẫn đậm, căn giữa (lệch 1 px). Bấm thử cửa sổ bằng script: mở ô tại chỗ, gõ thêm câu, phóng to, Ctrl+Enter, Esc hủy, bấm ra ngoài áp, thêm chữ tại chỗ; ảnh `kiem_thu/ket_qua/giao-dien-sua-khoi.png`.
- **Chưa làm (PC)**: khối có chữ đậm, nghiêng lẫn trong đoạn sẽ ra một kiểu chữ; dời phần dưới theo cả bề ngang trang (cột bên cạnh, con dấu cũng dời theo).
- **Đã làm, bản Android 0.4.0** (giao một tác tử con làm song song; mã ở `D:\DevTools\src\xlpdf`, mới `lib/loi/sua_chu.dart`, `lib/loi/ve_chu.dart`):
  - Màn Chỉnh trang thêm chế độ *Sửa chữ*: khung từng khối (đoạn theo `ocr_par`, dòng đơn) trên ảnh phóng to được; khối có con dấu, chữ ký viền cam và bị khóa. Chạm khối → ô gõ phủ đúng chỗ, đúng phông, cỡ, màu, căn lề; bàn phím mở thì tự phóng, cuộn cho ô hiện rõ; thanh dưới: Hủy, chọn phông (8 phông hoặc tự đoán), Xong; Hoàn tác. Dòng gợi ý liệt kê chữ máy đọc chưa chắc (cả khối được viết lại nên cần soát).
  - Phông đóng gói: Liberation Serif, Liberation Sans × 4 kiểu (SIL OFL, cùng kích thước chữ với Times New Roman, Arial), lấy từ `C:\Windows\Fonts`, có dòng giấy phép trong `assets/phong/GIAY-PHEP.txt`. Times New Roman, Arial không được phép đóng gói.
  - Áp sửa: xóa nét bằng màu nền (bản Android không có `inpaint` vì module `photo` của OpenCV bị loại), dàn chữ bằng dart:ui, dời phần dưới khi số dòng đổi; mỗi lần sửa lưu ảnh PNG mới (không mất chất lượng khi sửa nhiều lần), giữ ảnh cũ để hoàn tác; ghi luôn chữ mới vào đệm nhận dạng. Xử lý lại trang đã sửa thì hỏi xác nhận. PDF xuất ra có Subject "Đã chỉnh sửa nội dung…".
  - Cỡ chữ khớp theo bề rộng nét dòng dài nhất; độ đậm nét khớp bằng viền mảnh thêm vào cho bằng diện tích mực bản gốc.
- **Kiểm tra (Android)**: `sua_chu_test.dart` 7/7 (đã chạy lại độc lập): đoán Liberation Serif thường khoảng 14,4 pt cho thân bài, đậm khoảng 15,3 pt cho tiêu đề, 300–770 ms một khối; "Kính gửi…" dài thêm 1 → 2 dòng, dời 75 px, đọc lại đúng 100%, phía trên và phần dời không đổi điểm ảnh nào; tiêu đề căn giữa lệch 0,5 px; đoạn 3 → 4 dòng không chồng chữ, đọc lại 99,2%; bút phê đỏ và tên ký đè con dấu bị khóa. 5 bộ cũ vẫn đạt. Bấm thử trên máy ảo: vào Sửa chữ, chạm khối, sửa tại chỗ, Xong, Hoàn tác. APK `apk/xu-ly-pdf-anh-0.4.0.apk` (khoảng 96 MB); ảnh `apk/anh-chup-may-ao/0.4.0-*.png`.
- **Chưa làm, chưa kiểm (Android)**: chưa thử điện thoại thật; adb không gõ được tiếng Việt nên bấm thử chỉ gõ thêm chữ không dấu; chưa thử trang sách (2 ảnh), xóa trắng cả khối, nền màu, chữ viết tay. Cách nhận căn lề khác bản PC một chút (đoạn "Căn cứ…" bản Android nhận là căn đều, bản PC nhận là căn trái).

## 2026-10-30 · Nguyên mẫu PC: cửa sổ Sửa PDF (sửa chữ, thêm chữ, che, chèn ảnh, sửa trang)
- **Yêu cầu**: ứng dụng (chay-ung-dung.bat) chưa có chức năng sửa PDF. Người dùng chọn cả ba hướng: sửa chữ trên trang (làm trước); thêm chữ, che, chèn ảnh; sửa trang của PDF có sẵn.
- **Đã làm** (thư mục `ung-dung/`):
  - `loi_xu_ly/sua_noi_dung.py`: tìm từ (Tesseract `image_to_data`); lấy nét mực của chữ cũ (thành phần liên thông, có cả dấu thanh Tesseract để ngoài khung); đoán phông trong tập Times New Roman, Arial × thường, đậm, nghiêng, đậm nghiêng bằng cách vẽ thử chính chữ cũ rồi so hình (giao/hợp); cỡ theo chiều cao nét; màu theo lõi nét; độ nhòe theo độ sắc cạnh; vá nền (`cv2.inpaint`); dồn nét mực phần sau của dòng (dòng căn giữa dồn đều hai bên); vẽ chữ mới siêu mẫu 4×. Chặn vùng có mực màu (con dấu, chữ ký). Thêm chữ, che, tô sáng, chèn ảnh (bỏ nền trắng bằng nhân màu). Mỗi việc là một thao tác, áp lần lượt nên hoàn tác, xóa từng thao tác được.
  - `loi_xu_ly/tai_lieu_pdf.py`: tài liệu gồm trang PDF gốc, trang ảnh, trang trắng; gộp nhiều tệp, chèn, xóa, xoay, đảo thứ tự, tách. Trang PDF chưa sửa nội dung chép nguyên bằng pypdf (xoay chỉ đổi /Rotate); trang sửa nội dung dựng 300 dpi bằng PDFium, ghi lại bằng reportlab, có lớp chữ. Siêu dữ liệu ghi "Đã chỉnh sửa nội dung…: n chỗ sửa chữ, m chỗ che…". Lưu đè lên chính tệp nguồn được.
  - `sua_pdf.py` (cửa sổ Sửa PDF, tkinter), nút "✏ Sửa PDF…" ở giao diện chính, `sua-pdf.bat`.
- **Phát hiện khi kiểm chứng**:
  - Tesseract có khi để dấu hỏi, dấu nặng ra ngoài khung từ (chữ vector của PDF): đo thiếu chiều cao nên đoán nhầm Arial đậm nghiêng 10,9 pt. Đã nhận thêm nét nhỏ sát trên/dưới khung (trong 1/4 chiều cao chữ): đoán lại đúng Times 14,1 pt (thật 14 pt).
  - Chọn độ nhòe bằng so hình luôn ra nhòe nhất (vì chữ vẽ thử lệch vài phần điểm ảnh); đổi sang so độ sắc cạnh nét.
  - Dòng tiêu đề căn giữa bị lệch trái sau khi sửa: thêm nhận biết dòng căn giữa.
  - Bấm thử giao diện bằng script phát hiện lỗi kéo chuột (khung che chỉ lấy lần di chuyển đầu); đã sửa. Màn hình máy 1080×1920 (dọc) hẹp hơn cửa sổ đặt sẵn: đổi sang mở phóng to.
- **Kiểm tra**: `kiem_thu/kiem_thu_sua_pdf.py` đạt toàn bộ:
  - sửa 3 cụm trên trang công văn mẫu: đoán đúng Times thường (thân bài), Times đậm (tiêu đề); nhận dạng lại dòng sau sửa đúng bằng dòng cũ thay cụm chữ; các dòng khác giữ nguyên từng điểm ảnh; dòng căn giữa vẫn ở giữa (lệch 1 px);
  - nhận ra vùng con dấu, không chặn chữ đen; chữ thêm đọc lại được; che, tô sáng, chèn chữ ký bỏ nền;
  - PDF có sẵn: gộp 2 tệp, xóa, chèn trang trắng, đảo thứ tự, xoay giữ /Rotate 90, trang chưa sửa chép nguyên luồng nội dung, chưa sửa thì không ghi dấu; sửa chữ vector rồi lưu có lớp chữ mới, giữ khổ A4, ghi dấu đã chỉnh sửa; tách 2 trang.
  - Bấm thử cửa sổ bằng script (giả lập chuột): tìm 144 từ, chọn 3 từ bằng Shift, sửa, che, xoay, lưu; ảnh `kiem_thu/ket_qua/giao-dien-sua-pdf.png`.
- **Chưa làm, chưa kiểm**:
  - Chưa thử trên ảnh chụp thật và PDF thật của người dùng; tập phông mới có Times New Roman, Arial.
  - Chữ sửa chỉ trên một dòng; không tự xuống dòng khi chữ mới quá dài (có cảnh báo vượt lề).
  - Hộp thoại sửa chữ, thêm chữ chưa được bấm bằng tay (script thay hộp thoại bằng kết quả giả).
  - Bản Android chưa có các chức năng này.

## 2026-10-29 · Bản Android 0.3.0: tự chèn số trang khi xuất PDF
- **Yêu cầu**: thêm chức năng tự chèn số trang vào văn bản; người dùng xác định trang đầu tiên được đánh số; chọn Vị trí lề trên/dưới; Căn giữa/trái/phải/so le (chẵn trái, lẻ phải hoặc ngược lại).
- **Đã làm**:
  - Lõi `DanhSo` trong `lib/loi/xuat_pdf.dart`: trang bắt đầu, số in trên trang đó, vị trí, căn, so le. Số in phông Times cỡ 13, cách mép giấy nửa lề (ít nhất 8 mm); căn trái, phải theo mép vùng nội dung (ít nhất 20 mm). Trang PDF đổi sang lề 0 + `Padding` để vẽ được số trong vùng lề.
  - Khối *Đánh số trang* ở màn Xuất (`lib/man_hinh/danh_so.dart`): dải ảnh trang, chạm để chọn trang đầu được đánh số; mỗi ảnh hiện số sẽ in đúng vị trí (xem trước), trang trước đó mờ đi. Số đầu mặc định theo thứ tự trang, có nút *Bắt đầu từ 1*. Vị trí, căn, so le lưu trong Cài đặt; trang bắt đầu, số đầu lưu theo hồ sơ.
  - Script kiểm thử: bộ nào ghi tệp vào `kiem_thu/ra/` (`integration_test/ra.dart`) thì `chay_kiem_thu.sh` lấy về `build/kiem_thu_ra/`.
  - `GIAY-PHEP.txt` thêm dòng cho `osd.traineddata` (Apache 2.0), gỡ mục `[cần xác minh]` của wiki.
- **Kiểm tra**:
  - `so_trang_test.dart` (máy ảo) tạo 3 PDF 4 trang; `integration_test/kiem_so_trang.py` (PDFium trên PC) đo đủ 12 trang: số đúng, trang trước trang bắt đầu không có số, tâm số lệch dưới 2 pt so với vị trí tính trước (lề trên/dưới; giữa, phải, so le chẵn trái).
  - Bộ nhận dạng chạy lại sau khi đổi cấu trúc trang: lớp chữ vẫn lệch trung vị 0,90 pt như trước.
  - Bấm thử trong ứng dụng: bật đánh số, chọn trang 2, lề trên, so le chẵn trái → bấm Chia sẻ → lấy PDF trong bộ nhớ đệm ra đo: trang 1 không số, trang 2 và 4 số ở trái, trang 3 ở phải, vẫn có lớp chữ.
- **Kết quả**: `apk/xu-ly-pdf-anh-0.3.0.apk`.
- **Chưa làm**: chưa chọn được phông, cỡ chữ, kiểu số (vd. "Trang 2", "- 2 -"); chưa đánh số dạng La Mã cho phần đầu.

## 2026-10-29 · Bản Android 0.2.0: nhận dạng chữ, khử nhiễu, tự xoay, Bấm chụp, Xem nhanh
- **Yêu cầu**:
  - thêm nhận dạng chữ vào ứng dụng;
  - (nêu giữa chừng) tăng tương phản, khử nhiễu cho chữ; tự xoay toàn bộ trang có chọn ngang/dọc; chế độ tự chụp và chế độ người bấm mới chụp; xem trước (preview) cho văn bản lớn để thấy nhanh trang lệch, sai chiều mà sửa, xoay.
- **Đã làm** (mã ở `D:\DevTools\src\xlpdf`, chi tiết trong README ở đó):
  - *Nhận dạng chữ*: Tesseract 5.5.1 (Tesseract4Android, tệp `.aar`) gọi qua kênh riêng trong `MainActivity.kt`, trả hOCR; `lib/loi/nhan_dang.dart` đọc thành dòng, từ, vị trí. Nút *Văn bản* (một trang, cả hồ sơ): xem, chép, chia sẻ. Xuất PDF có *Thêm lớp chữ* (chữ ẩn đặt đúng vị trí, phông DejaVu Sans) và *Xuất kèm .txt*. Kết quả lưu đệm theo ảnh trang.
  - *Khử nhiễu, tương phản*: lọc trung vị 3×3; đường cong tương phản dốc gấp đôi; xóa đốm đứng riêng, khoảng "gần chữ" tính theo cỡ chữ để giữ dấu thanh. Thêm thanh *Khử nhiễu*. Thử phương án trên nguyên mẫu Python trước rồi mới chuyển sang Dart; nguyên mẫu PC chưa đổi theo.
  - *Tự xoay*: sau khi xử lý, Tesseract `psm 1` (dữ liệu `osd`) đoán chiều chữ từng trang ở nền. Nút *Xoay toàn bộ*: theo chiều chữ, *Tất cả khổ dọc*, *Tất cả khổ ngang*. Xoay giữ khung cắt tay.
  - *Chụp*: bộ chọn *Tự chụp* / *Bấm chụp* trên màn camera thay công tắc cũ; Bấm chụp vẫn hiện khung trang và lời nhắc.
  - *Xem nhanh*: lưới trang cỡ Lớn/Vừa/Nhỏ, lọc *Cần xem*, nhãn *Ngược chiều*, *Chữ nằm nghiêng 90°*, *Khổ ngang/dọc* (khác đa số), *Chưa thấy mép giấy*; xoay, sửa chiều ngay trên ô; *Sửa chiều tất cả*.
- **Sự cố đã gỡ**:
  - Gói `flutter_tesseract_ocr` dùng jcenter, AGP 7 nên không dựng được với AGP 9: bỏ gói, gọi thẳng `.aar`.
  - Trong ứng dụng, một trang mất 9–10 giây (kiểm thử chỉ 1 giây): OpenMP của Tesseract tranh CPU với luồng vẽ. Đặt `OMP_THREAD_LIMIT=1`, còn 2,3–3 giây.
  - `abiFilters` bị Flutter đặt lại nên APK lẫn thư viện armeabi-v7a của Tesseract (máy 32-bit cài được nhưng mở ra chết): loại bằng `packaging.jniLibs.excludes`.
- **Kiểm tra trên máy ảo** (4 bộ, 15 phép thử, đều đạt; chạy bằng `integration_test/chay_kiem_thu.sh`):
  - Nhận dạng ảnh mẫu công văn trùng 99,4% ký tự với Tesseract trên PC. PDF lớp chữ: PDFium chép được chữ, tìm được "CỘNG HÒA", "đóng dấu đỏ"; chữ ẩn lệch ngang trung vị 0,9 pt so với chữ trên ảnh.
  - Làm sạch, trên ảnh chụp kém tự tạo `mau4-chup-kem.jpg`: đốm nhiễu 743 → 117, nhận dạng đúng 71% → 91,6%, chữ đen hơn (trung vị độ sáng 55 → 43). Ảnh chụp tốt vẫn đọc đúng 99,4%; dấu đỏ giữ nguyên.
  - Đoán chiều đúng cả 4 góc 0°, 90°, 180°, 270°, khoảng 1,2 giây một trang. Luồng trang ngược → cảnh báo → Xoay toàn bộ → đúng chiều đạt.
  - Bấm thử giao diện: nhập 4 ảnh (2 ảnh sai chiều) → màn Các trang báo 2 trang cần xem → Xem nhanh → *Sửa chiều tất cả* → cả 4 trang đứng thẳng; *Tất cả khổ ngang* rồi *Tất cả khổ dọc*; Bấm chụp; xem văn bản cả hồ sơ.
- **Kết quả**: `apk/xu-ly-pdf-anh-0.2.0.apk` (khoảng 88 MB, arm64 + x86_64; tăng so với 0.1.0 vì có Tesseract và 18 MB dữ liệu nhận dạng).
- **Chưa làm, chưa kiểm**:
  - Chưa chạy trên điện thoại thật; tốc độ nhận dạng thật chưa đo.
  - Ảnh chụp kém là ảnh tổng hợp; cần ảnh chụp thật để chỉnh ngưỡng khử nhiễu.
  - Trang không đủ chữ (ảnh, bảng vẽ) không đoán được chiều, chỉ xoay được theo khổ.
  - Nguyên mẫu PC chưa có khử nhiễu và đường cong tương phản mới.

## 2026-10-29 · Thiết kế giao diện (Claude Design) và bản Android đầu tiên (.apk)
- **Yêu cầu**: thiết kế giao diện UX bằng Claude Design; tạo tệp .apk cho Android. Người dùng chọn hướng Flutter và đồng ý tải công cụ vào ổ D.
- **Thiết kế**: canvas *Giao diện Xử lý PDF ảnh – Android* (https://claude.ai/artifact/ERLBGLiUQStuk1FBM7E3hN) gồm 5 màn hình điện thoại bấm thử được: Hồ sơ, Chụp/tự động chụp, Các trang, Chỉnh trang, Xuất PDF. Bản gốc lưu ở `thiet-ke-giao-dien/`.
- **Công cụ đã cài** vào `D:\DevTools`: Flutter 3.47.8, Android SDK 36, NDK 28.2, CMake 3.31.6, máy ảo Android 15 x86_64. JDK 17 cài qua winget. Đã chấp nhận giấy phép Android SDK.
- **Ứng dụng**:
  - Mã Flutter ở `D:\DevTools\src\xlpdf`; thư mục `ung-dung-flutter` trong dự án là junction tới đó.
  - Lõi xử lý chuyển từ Python sang Dart + OpenCV (`opencv_dart`, OpenCV biên dịch từ mã nguồn): làm sạch giữ màu, tìm mép, nắn phối cảnh Zhang–He, sửa nghiêng, xóa viền, tách trang đôi, tự động chụp (isolate riêng, khung YUV), xuất PDF (`pdf`).
- **Sự cố đã gỡ**:
  - Gradle không chạy được trong đường dẫn có chữ có dấu, nên chuyển mã sang `D:\DevTools\src\xlpdf`.
  - Kotlin biên dịch tăng dần lỗi vì Pub cache (ổ C) và thư mục build (ổ D) khác ổ; đã đặt `kotlin.incremental=false`.
  - Hộp thoại xin quyền camera làm mở hai bộ điều khiển camera; đã thêm cờ chặn.
  - Closure gửi sang isolate dính `State` màn hình làm xuất PDF lỗi; đã chuyển thành hàm cấp cao nhất.
- **Kiểm tra trên máy ảo**:
  - `integration_test/loi_test.dart` đạt cả 5 mục:
    - tìm mép lệch 5,4 px;
    - trang ra tỉ lệ 1,415, nền trắng 99,4%, giữ dấu đỏ, xử lý 0,7 s;
    - tách trang đôi ở 50%;
    - tự động chụp đúng 2 trang mới, 15 ms một khung;
    - xuất được PDF.
  - Bấm thử giao diện: nhập ảnh từ thư viện, xử lý, chỉnh 4 góc, chụp tay, camera phân tích khung trực tiếp, xuất và chia sẻ PDF.
- **Kết quả**: `apk/xu-ly-pdf-anh-0.1.0.apk` (64 MB, arm64 + x86_64). Ảnh chụp màn hình máy ảo ở `apk/anh-chup-may-ao/`.
- **Chưa làm, chưa kiểm**:
  - Chưa chạy trên điện thoại thật và camera thật, nên tự động chụp chưa thử với trang giấy thật.
  - Chưa có nhận dạng chữ, tự xoay 90°/180°, nắn trang cong, nhận tệp chia sẻ thẳng từ Zalo.
  - APK đang ký bằng khóa debug.

## 2026-10-29 · Thêm chế độ tự động chụp
- **Yêu cầu**: thêm chế độ tự động chụp cho Android, iOS: ứng dụng tự chụp trang sách khi đủ điều kiện.
- **Đã làm**:
  - `ung-dung/loi_xu_ly/tu_chup.py` (lớp `BoTuChup`): xét lần lượt các điều kiện thấy trang, đủ lớn, không cắt mép, không nghiêng, đủ sáng, không lóa, đứng yên, đủ nét, khác trang vừa chụp. Giữ đạt 0,8 giây thì chụp khung nét nhất. Có lời nhắc tiếng Việt cho từng điều kiện.
  - Cửa sổ *Chụp camera* trên PC có ô *Tự động chụp* (bật sẵn), hiện lời nhắc và vòng tiến độ.
  - Viết đặc tả chuyển sang Flutter + C++ trong `03-tu-dong-chup.md`: luồng khung YUV, giao diện FFI, `takePicture` sau khi kích hoạt, khóa lấy nét.
- **Phát hiện khi kiểm chứng**: so hai trang bằng ảnh nhỏ 48×64 rất nhạy với xê dịch dưới một điểm ảnh, vì khoảng cách dòng chữ gần bằng ô lưới. Ảnh mờ trước khi thu nhỏ và so có dịch ±2 ô thì giải quyết được. Cùng một trang chụp lại có độ khác ≤ 0,21, trang khác ≥ 0,37; ngưỡng đặt 0,24.
- **Kiểm tra**: `kiem_thu/kiem_thu_tu_chup.py` dùng đoạn phim mô phỏng 20 giây và đạt toàn bộ: chụp đúng 4 trang mới, không chụp trùng, báo đúng lời nhắc khi tối, lóa, cắt mép, xa, nghiêng; ảnh chụp là khung nét; 12 ms một khung. Đã chạy cửa sổ camera với camera giả: ứng dụng tự chụp 4 trang và xử lý xong. `kiem_thu_loi.py` vẫn đạt.
- **Chưa làm**: bản Android, iOS thật, vì máy chưa có Flutter. Chưa thử với camera thật.

## 2026-10-29 · Dựng nguyên mẫu Windows chạy được (Python + OpenCV + Tesseract)
- **Yêu cầu**: rà soát thư mục rồi tạo ứng dụng.
- **Rà soát**: thư mục mới có tài liệu kế hoạch, chưa có mã. Máy không có Flutter và trình biên dịch C++, nhưng có Python 3.13, OpenCV 5.0, Tesseract 5.4 (có `vie`, `eng`, `osd`), pypdfium2, reportlab, pypdf, watchdog. Vì vậy dựng nguyên mẫu bằng Python, đúng bước 3 trong CLAUDE.md; lõi xử lý tách riêng để chuyển sang C++ sau.
- **Đã làm**: thư mục `ung-dung/` gồm lõi `loi_xu_ly/` (làm sạch giữ màu, tìm mép giấy, sửa phối cảnh theo Zhang & He, tự xoay bằng Tesseract OSD, sửa nghiêng bằng phép chiếu, tách trang đôi, xóa viền nền bàn, đọc PDF bằng PDFium, ghi PDF có khổ giấy, lề, lớp chữ); giao diện `giao_dien.py` (mở, kéo thả, chụp webcam, kéo 4 góc khung cắt, sắp xếp, xoay, xóa trang, xuất PDF, thư mục theo dõi); `tu_dong.py` (xử lý theo lô, theo dõi thư mục); tệp `cai-dat.bat`, `chay-ung-dung.bat`, `them-vao-send-to.ps1`.
- **Phát hiện khi kiểm chứng**:
  - Tesseract chạy `vie+eng` mất dấu tiếng Việt nặng ("Doc lap — Tw do"); chạy riêng `vie` đọc gần đúng hết, kể cả dòng tiếng Anh. Mặc định đổi sang `vie`.
  - Ước lượng tỉ lệ trang bằng độ dài cạnh lệch 6% khi chụp nghiêng. Chuyển sang công thức tiêu cự của Zhang & He: đúng tuyệt đối với phép chiếu camera mô phỏng.
  - Ảnh chụp kín hai trang sách bị bộ tìm mép cắt mất một trang. Đã thêm bước kiểm tra: ngoài khung còn giấy có chữ thì không cắt.
- **Kiểm tra**: `kiem_thu/kiem_thu_loi.py` đạt toàn bộ trên ảnh mẫu tổng hợp: nền trắng 100% kể cả chỗ bóng đổ, sắc độ dấu đỏ lệch 3,9°, tỉ lệ A4 1,414, tự xoay 180°, nghiêng còn dưới 0,5°, OCR đọc đúng quốc hiệu có dấu, PDF có lớp chữ tìm được tiếng Việt. Đã chạy thử giao diện thật (chụp màn hình), xử lý theo lô và thư mục theo dõi.
- **Chưa làm**: nắn trang sách cong; sửa chữ khớp font (tính năng 5A); trình soạn thảo định dạng (tính năng 6); bản Flutter cho Android, iOS. Chưa thử trên ảnh chụp thật và chưa thử camera thật.
