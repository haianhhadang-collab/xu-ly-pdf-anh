---
type: chu-de
---
# Tự động chụp

- Yêu cầu (2026-10-29): ứng dụng tự chụp trang khi đủ điều kiện, cho Android, iOS; người dùng chỉ giữ máy và lật trang ([[yeu-cau-nguoi-dung]], [[dac-ta-tu-dong-chup]]).
- Thuật toán: lớp `BoTuChup` (`loi_xu_ly/tu_chup.py`) xét lần lượt 10 điều kiện: thấy trang, đủ lớn, không cắt mép, song song, đủ sáng, không lóa, đứng yên, đủ nét, trang mới, giữ đủ 0,8 giây (0,5 giây từ bản 0.7.4). Điều kiện đầu chưa đạt quyết định lời nhắc tiếng Việt. Hết thời gian giữ thì lấy khung nét nhất, không lấy khung cuối ([[dac-ta-tu-dong-chup]]).
- Chống chụp trùng: so bản đồ mật độ mực 48×64 có dịch ±2 ô; ngưỡng 0,24. Phát hiện: so ảnh nhỏ rất nhạy với xê dịch dưới một điểm ảnh, làm mờ trước khi thu nhỏ và so có dịch thì giải quyết được ([[dac-ta-tu-dong-chup]]; `NHAT-KY.md` dự án).
- PC: ô *Tự động chụp* (bật sẵn) trong cửa sổ *Chụp camera*, có lời nhắc và vòng tiến độ ([[readme]]).
- Di động: khung YUV qua plugin `camera`, lõi C++ gọi FFI, `takePicture()` lấy ảnh gốc sau khi kích hoạt, khóa lấy nét và đo sáng khi giữ yên, tùy chọn độ nhạy nhanh/vừa/chắc (0,5/0,8/1,2 giây), chế độ sách/giấy rời ([[dac-ta-tu-dong-chup]], [[flutter-loi-cpp]]).
- Bản Android thực tế (khác kế hoạch): lõi tự chụp viết bằng Dart + `opencv_dart` (`lib/loi/tu_chup.dart`, `BoTuChup`, đổi YUV → BGR), chạy trong isolate riêng, không qua C++/FFI ([[readme-ung-dung-flutter]], [[ban-android-flutter]]).
- Bản Android 0.2.0 (cập nhật 2026-10-29): theo yêu cầu có cả tự chụp lẫn bấm chụp ([[yeu-cau-nguoi-dung]]), màn camera có bộ chọn *Tự chụp* / *Bấm chụp* thay công tắc cũ. *Bấm chụp* vẫn vẽ khung trang và lời nhắc, khi đủ điều kiện nhắc *Đủ rõ, bấm nút tròn để chụp*. Chế độ mở mặc định chọn trong Cài đặt ([[readme-ung-dung-flutter]]). Đã bấm thử Bấm chụp trên máy ảo (`NHAT-KY.md` dự án).
- Chưa kiểm chứng: camera thật, giấy bóng, đèn huỳnh quang nhấp nháy, sách dày cong mạnh, tay lọt vào khung ([[dac-ta-tu-dong-chup]]).

## Góp ý chụp thật, bản 0.7.1 (2026-11-14)
- Người dùng chụp bằng điện thoại thật: ảnh out nét, kết quả quá mờ; tự chụp vẫn báo lùi máy dù trang đã trọn trong khung ([[yeu-cau-nguoi-dung]]).
- Nguyên nhân: camera mở ở 1080p (trang A4 ~1000 điểm ảnh bề ngang), không lấy nét trước khi chụp; luật cũ báo lùi máy khi mép giấy cách mép khung dưới 1%; bản 0.7.0 cho tự chụp dùng bộ tìm mép đầy đủ, chậm (`NHAT-KY.md` dự án 2026-11-14).
- Sửa: độ phân giải tối đa, chạm để lấy nét, lấy nét trước khi chụp, đo ảnh mờ (tỉ lệ độ nét 1280 px / 640 px, ngưỡng 0,55) rồi chụp lại; chỉ báo lùi máy khi trang bị cắt; bộ tìm mép bản nhanh 57–60 ms/khung trên máy ảo ([[ban-android-flutter]], [[kiem-thu]]).
- Chưa kiểm trên camera thật.

## Video chụp thật, bản 0.7.4 (2026-11-14)
- Người dùng chụp sách mở đặt trên nền đen bằng 0.7.3, gửi PDF và video quay màn hình: báo giữ yên rồi chạy lại, có cặp trang chờ 18 giây ([[yeu-cau-nguoi-dung]], [[du-lieu-kiem-thu]]).
- Nguyên nhân đo được trên video: phép đo rung thô quá nhạy với cảnh tương phản mạnh; một khung lỗi làm đếm lại; hai cặp trang sách in giống nhau chỉ khác 0,22–0,33, sát ngưỡng chống chụp trùng 0,24 (`NHAT-KY.md` dự án 2026-11-14).
- Sửa: đo rung theo độ dời (toàn khung ≤ 2,5, từng ô ≤ 5), chịu 0,4 giây khung tìm mép trượt, nhận động tác lật trang (đủ 1 giây thì ngưỡng 0,18), nhận tay trên trang theo màu da chạm mép trang, giữ yên 0,3/0,5/0,9 giây, rung báo trên Android ([[dac-ta-tu-dong-chup]], [[ban-android-flutter]]).
- Kết quả phát lại video: 6/6 cặp trang, cặp trang 3 chụp ở 18,5 giây thay vì 34,5; không chụp khi tay trên trang ([[kiem-thu]]). Chưa thử trên điện thoại thật.

## Chụp xong mới xử lý (0.7.7, 2026-11-15)
- Người dùng hỏi làm vuông giấy để sau khi chụp mới xử lý được không ([[ho-so-15-11-sach-214-trang]]). Bản 0.7.7: đang ở màn chụp thì chỉ lưu ảnh gốc, hàng đợi xử lý và đoán chiều chữ tạm dừng; rời màn chụp mới chạy. Tắt được ở Cài đặt ([[ban-android-flutter]]).

## Báo trang nên chụp lại (0.7.8, 2026-11-15)
- Sau khi xử lý, trang chữ nhòe (lõi nét chỉ còn xám) hoặc tay che trên 5% vùng giữa trang được báo ở Xem nhanh, có nút Chụp lại. Trên 214 trang của người dùng chỉ hai trang chụp lúc đang lật trang bị báo ([[ho-so-15-11-sach-214-trang]], [[ban-android-flutter]]).

## Báo nhòe ngay sau khi chụp, rung đúng lúc (0.7.9, 2026-11-16)
- Rung, nháy, tiếng chụp phát khi máy đã chụp xong ảnh dùng được; trước đây rung lúc bắt đầu lấy nét (có thể 1,5 giây trước khi chụp), người dùng tưởng đã chụp nên lật trang sớm, ảnh nhòe ([[ho-so-15-11-sach-214-trang]]).
- Sau mỗi ảnh, máy kiểm tra nhanh (tìm mép, nắn, tách cặp trang, đo nhòe theo độ rộng mép nét chữ trên ảnh gốc, đo tay che) trong 0,25–1,7 giây; lỗi thì rung hai lần, hiện thanh báo có nút Chụp lại thay đúng ảnh đó ([[ban-android-flutter]], [[nguyen-mau-windows]]).
- Chưa báo được trước khi chụp: khung xem trước độ phân giải thấp, chưa đo được nhòe nét chữ.
