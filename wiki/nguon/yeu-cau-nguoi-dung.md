---
type: nguon
tep_goc: "..\\YEU-CAU-NGUOI-DUNG.md"
ngay_nap: 2026-10-29
ngay_cap_nhat: 2026-11-14
loai: ghi chú yêu cầu
---
# Yêu cầu của người dùng

**Tóm tắt.** Danh sách yêu cầu người dùng đã nêu (ngày 2026-10-29), xếp theo nhóm. Cập nhật 2026-10-29: thêm 5 yêu cầu mới cho bản Android (mục cuối nhóm Yêu cầu chi tiết). Cập nhật 2026-10-30: thêm yêu cầu sửa PDF trên nguyên mẫu PC (yêu cầu ghi ngày 2026-10-29). Cập nhật 2026-10-30 (lần 2): thêm yêu cầu sửa chữ theo khối. Cập nhật 2026-10-30 (lần 4): thêm yêu cầu tham khảo ONLYOFFICE (bốn hướng). Cập nhật 2026-11-14: thêm yêu cầu làm phẳng ảnh kiểu CamScanner sau khi chạy bản Android trên máy thật.

- Trình bày: trao đổi và tài liệu bằng tiếng Việt.
- Yêu cầu chi tiết: làm sạch không chuyển về đen trắng, giữ màu chữ, con dấu, chữ ký, mực khác màu ([[lam-sach-giu-mau]]); nắn phẳng theo mép giấy không mất nội dung ([[nan-phang-va-xoay]]); xử lý toàn bộ trên thiết bị; văn bản Việt–Anh, người dùng là cán bộ hành chính, thủ thư; gửi kèm script Python chạy sẵn; có chế độ tự động chụp cho Android, iOS ([[tu-dong-chup]]); thiết kế giao diện bằng Claude Design và dựng tệp .apk cho Android, theo hướng Flutter, công cụ cài ở ổ D ([[ban-android-flutter]]).
- Yêu cầu chi tiết mới (2026-10-29), cho bản Android:
  - thêm nhận dạng chữ vào ứng dụng ([[nhan-dang-va-sua-chu]]);
  - bản mobile tăng thêm độ tương phản, khử nhiễu cho chữ ([[lam-sach-giu-mau]]);
  - tự xoay toàn bộ trang, có chọn ngang/dọc ([[nan-phang-va-xoay]]);
  - có cả chế độ tự chụp lẫn chế độ người bấm mới chụp ([[tu-dong-chup]]);
  - xem trước (preview) cho văn bản lớn, thấy nhanh trang lệch, sai chiều để sửa, xoay ([[ban-android-flutter]], mục Xem nhanh);
  - tự chèn số trang: người dùng xác định trang đầu tiên được đánh số; vị trí lề trên/dưới; căn giữa/trái/phải/so le (chẵn trái, lẻ phải hoặc ngược lại) ([[ban-android-flutter]], mục Đánh số trang).
- Yêu cầu chi tiết, nguyên mẫu PC (ghi ngày 2026-10-29, nạp vào wiki 2026-10-30): `chay-ung-dung.bat` cần chức năng sửa PDF; người dùng chọn cả ba hướng ([[cua-so-sua-pdf]]):
  - (1) sửa chữ trên trang: xóa chữ cũ, vá nền, vẽ chữ mới khớp phông, cỡ, màu; làm trước ([[nhan-dang-va-sua-chu]]);
  - (2) thêm chữ, che thông tin, chèn ảnh (chữ ký, con dấu), tô sáng;
  - (3) sửa trang của PDF có sẵn (chèn, xóa, xoay, đảo thứ tự, gộp, tách) mà giữ nguyên chất lượng.
- Yêu cầu chi tiết (2026-10-30), cho cả nguyên mẫu PC và bản APK Android ([[nhan-dang-va-sua-chu]], [[cua-so-sua-pdf]], [[ban-android-flutter]]):
  - sửa chữ theo khối: gộp các chữ cùng dòng, các dòng cùng đoạn vào một khối; sửa trực tiếp cả khối, thay cho chọn từng từ;
  - nếu được, sửa ngay trên giao diện trang (gõ tại chỗ, không qua hộp thoại).
- Không được làm: dùng MuPDF/PyMuPDF (AGPL) trong mã ứng dụng ([[giay-phep-thu-vien]]).
- Yêu cầu chi tiết (2026-10-30, lần 3; thay yêu cầu sửa theo khối): sửa chữ phải giữ nguyên nội dung, hình dạng, kích thước bản scan, bản chụp; chỉ thêm, bớt ký tự, nội dung; chữ máy đọc sai không được làm đổi chỗ không sửa ([[sua-ky-tu]]).
- Yêu cầu chi tiết (2026-10-30): gõ tiếng Việt khi sửa ký tự không được lỗi phông, lỗi đậm nhạt; chữ chèn cùng kiểu chữ, độ đậm với chữ quanh ([[sua-ky-tu]], mục Gõ tiếng Việt).
- Yêu cầu chi tiết (2026-10-30, sau khi thử bản Android 0.5.0 trên điện thoại thật với ảnh chụp có dòng nghiêng): chữ sửa xong không được lệch dòng; chữ không sửa phải giữ nguyên, kể cả dòng trên, dòng dưới sát dòng đang sửa ([[sua-ky-tu]], mục Dòng nghiêng).
- Không được làm (2026-10-30): viết lại, vẽ lại chữ của bản scan khi sửa; chỗ không sửa phải giữ nguyên.
- Yêu cầu chi tiết (2026-10-30): thêm chức năng đổi phông, cỡ chữ. Người dùng chọn áp cho đoạn chữ bôi chọn trong Sửa ký tự (đổi cỡ: phóng, thu nét gốc; đổi phông: chỉ đoạn chọn vẽ lại bằng phông mới), làm cả PC và Android ([[sua-ky-tu]], mục Đổi phông, cỡ chữ).
- Yêu cầu chi tiết (2026-10-30, lần 4), nguyên mẫu PC: tham khảo chức năng chỉnh chữ và đối tượng PDF của ONLYOFFICE DesktopEditors, chỉ học cách làm, không dùng mã AGPL ([[onlyoffice-desktopeditors]]). Người dùng chọn đưa vào cả bốn:
  - (1) đối tượng chọn lại được (chữ thêm, ảnh chèn, khung che, tô sáng, hình vẽ): bấm chọn, kéo dời, kéo góc đổi cỡ, Delete xóa, bấm đúp sửa chữ và định dạng; có làm lại Ctrl+Y ([[doi-tuong-tren-trang]]);
  - (2) dời, đổi cỡ, xóa vùng có sẵn trên bản scan (tự đánh dấu đoạn chữ, ảnh, bảng); vùng có con dấu, chữ ký vẫn khóa ([[doi-tuong-tren-trang]]);
  - (3) chú thích không phá bản gốc (ghi chú, bút phê, tô sáng, hình, dấu "Đã xem"), lưu thành chú thích PDF chuẩn ([[chu-thich-pdf]]);
  - (4) thao tác trang kiểu ONLYOFFICE: kéo thả đổi thứ tự, menu chuột phải trên ảnh trang, chèn trang trắng trước/sau, chép/dán trang giữa các tệp ([[thao-tac-trang]]).
- Yêu cầu chi tiết (2026-11-14, sau khi chạy bản Android trên máy thật): tự xoay cho khối chữ vuông góc và làm trắng đã đạt; ảnh **chưa được làm phẳng**. Cần tự căn chỉnh, làm phẳng như CamScanner: tự tìm đúng mép giấy, cắt và nắn phẳng phối cảnh, nắn trang cong; chỉnh tay 4 góc dễ dàng ([[nan-phang-va-xoay]], [[ban-android-flutter]]).
- Yêu cầu chi tiết (2026-11-14, sau khi chụp thử bằng điện thoại thật): ảnh bị out nét lúc chụp nên kết quả quá mờ; phải lấy nét đúng, ảnh chụp đủ nét, đủ độ phân giải ([[tu-dong-chup]]).
- Yêu cầu chi tiết (2026-11-14): tự động chụp không được báo "lùi máy" khi khung hình đã bao trọn trang giấy; phải chụp được dễ dàng ([[tu-dong-chup]]).
- Yêu cầu chi tiết (2026-11-14): tách nhận dạng chữ (OCR) thành chức năng riêng, người dùng tự chọn khi cần; không chạy OCR ngay khi xuất kết quả (ảnh kém thì OCR sai) ([[nhan-dang-va-sua-chu]]). Ba yêu cầu này đã làm ở bản Android 0.7.1 ([[ban-android-flutter]]).
- Yêu cầu chi tiết (2026-11-14, sau khi chụp thử bản 0.7.1): chất lượng chữ đã tốt; cắt và làm phẳng trang cần tốt hơn: cắt sát vào chữ hơn, tự động loại bỏ vết, vệt đen trong ảnh. Đã làm ở bản 0.7.2 (*Cắt sát chữ*) ([[nan-phang-va-xoay]], [[ban-android-flutter]]).
- Yêu cầu chi tiết (2026-11-14, sau khi chụp thử bản 0.7.3, sách đặt trên nền đen, kèm PDF và video quay màn hình): tự chụp phát hiện khung hình chậm, báo giữ yên rồi chạy lại từ đầu, có lần rất lâu mới chụp; cần giảm thời gian chờ giữ yên và có **báo rung** khi bắt được trang, khi chụp. Đã làm ở bản 0.7.4 ([[tu-dong-chup]], [[ban-android-flutter]]).
- Yêu cầu chi tiết (2026-11-14, sau khi chụp thử bản 0.7.4, kèm PDF): kết quả đã khá tốt; chụp sách không được chỉ nhận một nửa cặp trang: phải lấy đủ hai trang, hoặc nhắc lùi máy khi một trang lọt ra ngoài khung. Đã làm ở bản 0.7.5 ([[nan-phang-va-xoay]], [[ban-android-flutter]]).
- Yêu cầu chi tiết (2026-11-15, gửi lại `mới.pdf` chụp bằng bản 0.7.2): không được cắt lẹm vào chữ; phải chỉnh méo, nắn vuông lại khối văn bản: lề trái, lề phải thẳng, khối chữ vuông. Đã làm ở bản 0.7.6 và nguyên mẫu PC (`nan_lai_pdf.py`) ([[nan-phang-va-xoay]], [[ban-android-flutter]]).

## Cập nhật 2026-11-15 (tối)
- Lề không cần cắt sát quá (thay yêu cầu cắt sát chữ ngày 14/11); làm vuông giấy sau khi chụp xong mới xử lý ([[ho-so-15-11-sach-214-trang]]) Theo `YEU-CAU-NGUOI-DUNG.md`: mặc định lề "Vừa", giữ lề thật của trang tới 6% cạnh dài; trang ít chữ giữ khổ trang. Đã làm ở bản 0.7.7 và nguyên mẫu PC ([[nan-phang-va-xoay]], [[ban-android-flutter]]).

## Cập nhật 2026-11-16
- Báo nhòe ngay trên màn camera; tự rà soát còn gì cần làm thì làm luôn. Đã làm ở bản 0.7.9: báo ngay sau mỗi ảnh, rung đúng lúc chụp, báo trang chụp trùng ([[tu-dong-chup]], [[ban-android-flutter]]).
