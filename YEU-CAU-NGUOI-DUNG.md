# Yêu cầu của người dùng

## Trình bày
- 2026-10-29: Trao đổi và tài liệu bằng tiếng Việt (theo CLAUDE.md dự án).

## Văn phong
- (chưa có yêu cầu riêng)

## Yêu cầu chi tiết
- 2026-10-29: Làm sạch không chuyển về đen trắng; giữ màu chữ, con dấu, chữ ký, mực khác màu (CLAUDE.md, tính năng 2).
- 2026-10-29: Nắn phẳng theo mép giấy mà không mất nội dung (CLAUDE.md, tính năng 3).
- 2026-10-29: Xử lý toàn bộ trên thiết bị, không có máy chủ.
- 2026-10-29: Văn bản tiếng Việt và tiếng Anh; người dùng là cán bộ hành chính, thủ thư.
- 2026-10-29: Gửi kèm script Python chạy sẵn, không chỉ hướng dẫn.
- 2026-10-29: Có chế độ tự động chụp cho Android, iOS: ứng dụng tự chụp trang sách khi đủ điều kiện.
- 2026-10-29: Thiết kế giao diện UX bằng Claude Design; dựng tệp .apk cho Android (người dùng chọn hướng Flutter, đồng ý tải công cụ vào ổ D).
- 2026-10-29: Thêm nhận dạng chữ vào ứng dụng (bản Android).
- 2026-10-29: Bản mobile cần tăng thêm độ tương phản, khử nhiễu cho chữ.
- 2026-10-29: Thêm chức năng tự xoay toàn bộ trang (chọn ngang/dọc).
- 2026-10-29: Thêm chế độ tự chụp, người bấm thì chụp (có cả tự chụp lẫn bấm chụp).
- 2026-10-29: Thêm chức năng xem trước (preview) cho văn bản lớn: quan sát nhanh trang nào bị lệch, không đúng chiều để chỉnh sửa, xoay nhanh.
- 2026-10-29: Nguyên mẫu PC (chay-ung-dung.bat) cần chức năng sửa PDF; người dùng chọn cả ba: (1) sửa chữ trên trang (xóa chữ cũ, vá nền, vẽ chữ mới khớp phông, cỡ, màu), làm trước; (2) thêm chữ, che thông tin, chèn ảnh (chữ ký, con dấu), tô sáng; (3) sửa trang của PDF có sẵn (chèn, xóa, xoay, đảo thứ tự, gộp, tách) mà giữ nguyên chất lượng.
- 2026-10-30: Tham khảo chức năng chỉnh chữ và đối tượng PDF của ONLYOFFICE DesktopEditors (chỉ học cách làm; mã AGPL không dùng). Người dùng chọn đưa vào cả bốn: (1) đối tượng chọn lại được (chữ thêm, ảnh chèn, khung che, tô sáng, hình vẽ: bấm chọn, kéo dời, kéo góc đổi cỡ, Delete xóa, bấm đúp sửa chữ và định dạng; có làm lại Ctrl+Y); (2) dời, đổi cỡ, xóa vùng có sẵn trên bản scan (tự đánh dấu đoạn chữ, ảnh, bảng; vùng có con dấu, chữ ký vẫn khóa); (3) chú thích không phá bản gốc (ghi chú, bút phê, tô sáng, hình, dấu "Đã xem", lưu thành chú thích PDF chuẩn); (4) thao tác trang kiểu ONLYOFFICE (kéo thả đổi thứ tự, menu chuột phải trên ảnh trang, chèn trang trắng trước/sau, chép/dán trang giữa các tệp).
- 2026-10-30: Thêm chức năng đổi phông, cỡ chữ. Người dùng chọn: áp cho **đoạn chữ bôi chọn** trong Sửa ký tự (đổi cỡ: phóng, thu chính nét chữ gốc, phần sau tự dồn; đổi phông: chỉ đoạn chọn được vẽ lại bằng phông mới, cùng màu mực, đúng hàng chữ); chỗ không chọn giữ nguyên. Làm cả PC và Android.
- 2026-10-30: Gõ tiếng Việt khi sửa ký tự không được lỗi phông, lỗi đậm nhạt: chữ chèn phải cùng kiểu chữ, cùng độ đậm nét, độ đậm mực với chữ quanh chỗ chèn.
- 2026-10-30: (Sau khi thử bản Android 0.5.0 trên điện thoại thật, ảnh chụp nhãn hàng có dòng nghiêng) Chữ sửa xong không được lệch dòng: ký tự chèn, phần chữ dời đi phải nằm đúng hàng chữ của dòng. Những chữ không sửa phải giữ nguyên, kể cả chữ của dòng trên, dòng dưới sát dòng đang sửa.
- 2026-10-30: (Thay yêu cầu sửa theo khối bên dưới) Sửa chữ phải **giữ nguyên nội dung, hình dạng, kích thước của bản scan, bản chụp**, chỉ thêm, bớt ký tự, nội dung. Không được làm mất định dạng, cỡ chữ; không được để chữ máy đọc sai (OCR) làm đổi nội dung chỗ không sửa. Người dùng nhận xét: cách sửa theo khối (viết lại cả khối bằng phông) gây mất hết định dạng, cỡ chữ, OCR sai nội dung.
- 2026-10-30: Sửa chữ theo khối: gộp các chữ cùng dòng, các dòng cùng đoạn vào một khối; khi sửa thì sửa trực tiếp cả khối (thay cho chọn từng từ). Nếu được, sửa trực tiếp trên giao diện trang (gõ ngay tại chỗ, không qua hộp thoại). Làm cho cả nguyên mẫu PC và bản APK Android.
- 2026-10-29: Thêm chức năng tự chèn số trang vào văn bản: người dùng phải xác định trang đầu tiên được đánh số; chọn Vị trí: lề trên / lề dưới; chọn Căn: giữa / trái / phải / so le (chẵn trái, lẻ phải hoặc ngược lại).
- 2026-11-14: (Sau khi chạy bản Android trên máy thật) Tự xoay cho khối chữ vuông góc và làm trắng đã đạt; ảnh **chưa được làm phẳng**. Cần chức năng tự căn chỉnh, làm phẳng như CamScanner: tự tìm đúng mép giấy, cắt và nắn phẳng phối cảnh, nắn trang cong; chỉnh tay 4 góc dễ dàng. (Đã làm ở bản 0.7.0: tìm mép mới, nắn trang cong, kéo góc / giữa cạnh có kính lúp.)
- 2026-11-14: (Sau khi chụp thử bằng điện thoại thật, gửi `Hồ sơ 14-11 13-23.pdf`) Ảnh bị out nét lúc chụp nên kết quả quá mờ: phải lấy nét đúng, ảnh chụp đủ nét, đủ độ phân giải.
- 2026-11-14: Chế độ tự động chụp: khung hình đã bao trọn trang giấy thì không được báo "lùi máy"; phải chụp được dễ dàng.
- 2026-11-14: Tách nhận dạng chữ (OCR) thành chức năng riêng, người dùng tự chọn khi cần; không chạy OCR ngay khi xuất kết quả (ảnh kém thì OCR sai).
- 2026-11-14: (Sau khi chụp thử bản 0.7.1, gửi `Hồ sơ 14-11 14-01.pdf`) Chất lượng chữ đã tốt. Cắt và làm phẳng trang cần tốt hơn: cắt bỏ phần ngoài trang (nền, viền); tự động loại bỏ vết, vệt đen trong ảnh. (Phần "cắt sát vào chữ hơn" đã được thay bằng yêu cầu ngày 15/11: lề không cần cắt sát quá.)
- 2026-11-14: (Sau khi chụp thử bản 0.7.3, sách đặt trên nền đen, gửi `Hồ sơ 14-11 20-26.pdf` và video quay màn hình) Tự chụp phát hiện khung hình chậm: báo giữ yên rồi chạy lại từ đầu, có lần rất lâu mới chụp. Cần giảm thời gian chờ giữ yên và có **báo rung** (khi bắt được trang, khi chụp).
- 2026-11-14: (Sau khi chụp thử bản 0.7.4, gửi `a49b7bcb-…_mới.pdf`) Kết quả đã khá tốt; khi chụp sách không được chỉ nhận 1/2 cặp trang: phải lấy đủ hai trang (hoặc nhắc lùi máy khi một trang lọt ra ngoài khung).
- 2026-11-15: (Gửi lại `mới.pdf` chụp bằng bản 0.7.2) Không được cắt lẹm vào chữ. Cần chỉnh méo, nắn vuông lại khối văn bản: lề trái, lề phải thẳng, khối chữ vuông.
- 2026-11-15: (Gửi `Hồ sơ 15-11 19-33.pdf`, 214 trang sách) Dò các trang lỗi, cải thiện kết quả. **Lề không cần cắt sát quá** (thay yêu cầu "cắt sát vào chữ hơn" ngày 14/11: nay mặc định lề "Vừa", giữ lề thật của trang tới 6% cạnh dài; trang ít chữ giữ khổ trang). Làm vuông giấy (cắt, nắn, làm sạch) để **sau khi chụp xong** mới xử lý.
- 2026-11-15: Báo trang nhòe, tay che trang để chụp lại (đã làm ở 0.7.8: báo sau khi xử lý, nút Chụp lại thay đúng trang đó).
- 2026-11-16: **Báo nhòe ngay trên màn camera** (ngay sau khi chụp, không đợi xử lý xong), kèm chụp lại thay ảnh vừa rồi; tự rà soát xem còn cần làm gì thì làm luôn (đã làm thêm: báo trang chụp trùng, rung báo đúng lúc máy chụp xong).

## Không được làm
- 2026-10-30: Không viết lại, vẽ lại chữ của bản scan khi sửa (làm mất định dạng, cỡ chữ, sai nội dung theo OCR); chỗ không sửa phải giữ nguyên.
- 2026-10-29: Không dùng MuPDF/PyMuPDF (giấy phép AGPL) trong mã ứng dụng.
