---
type: nguon
tep_goc: "..\\03-tu-dong-chup.md"
ngay_nap: 2026-10-29
ngay_cap_nhat: 2026-11-14
loai: đặc tả
---
# Đặc tả chế độ tự động chụp

**Tóm tắt.** Yêu cầu ngày 2026-10-29: ứng dụng tự chụp trang sách khi đủ điều kiện, người dùng chỉ giữ máy và lật trang. Đặc tả gồm 10 điều kiện chụp với ngưỡng mặc định và lời nhắc tiếng Việt, máy trạng thái, kết quả kiểm thử trên nguyên mẫu, và cách chuyển sang Flutter + lõi C++ (luồng khung YUV, giao diện FFI, điều khiển camera, tùy chọn người dùng). Thuật toán mẫu: `ung-dung/loi_xu_ly/tu_chup.py` (lớp `BoTuChup`).

## Số liệu chính
- Ảnh phân tích thu nhỏ cạnh dài 640 px; trang ≥ 20% khung; tỉ số hai cạnh đối ≤ 1,45; sáng ≥ 70/255; lóa ≤ 1,5%; chuyển động ≤ 5/255; độ nét Laplace ≥ 6; độ khác trang ≥ 0,24; giữ 0,8 giây (mục 1).
- Cùng trang chụp lại độ khác < 0,21; trang khác ≥ 0,37 (ảnh mô phỏng).
- Kiểm thử: phim mô phỏng 15 khung/giây, 20 giây; chụp đúng 4 trang, không trùng; khung nét 26 so với 5; 12 ms/khung 960×720 trên PC (mục 3).
- Mục tiêu di động: dưới 40 ms một khung 720p trên Android tầm trung (mục 4).

## Cập nhật bản 0.7.4 (2026-11-14)
- Điều kiện *đứng yên* (bảng điều kiện, dòng 7): nay đo độ dời ước tính giữa hai khung (chênh lệch trung bình ảnh 160 px làm mờ chia độ dốc sáng trung bình), ngưỡng ≤ 2,5 điểm ảnh; trước đây chênh lệch thô ≤ 5/255 bị vượt khi chụp sách trên nền đen, tay run nhẹ.
- Thời gian giữ *nhanh / vừa / chắc*: 0,3 / 0,5 / 0,9 giây (trước 0,5 / 0,8 / 1,2).
- Rung báo trên Android: kênh `xlpdf/rung` gọi `Vibrator`, 25 ms khi bắt được trang, 70 ms khi chụp; tắt ở Cài đặt › Rung báo.
- Mục mới *Nhận động tác lật trang*: hai cặp trang sách cùng khổ trong video chỉ khác 0,22–0,33 (sát ngưỡng 0,24), có cặp chờ 18 giây. Sau mỗi lần chụp, cộng thời gian các chuỗi khung xáo trộn liền nhau từ 0,25 giây; đủ 1 giây thì coi là đã lật, ngưỡng trang mới hạ còn 0,18. Va máy rồi về trang cũ (khác dưới 0,16) vẫn không bị chụp lại.
- Mục mới *Tay trên trang, rung theo ô*: điểm màu da chạm dải mép trang (8% ngoài cùng) che quá 0,5% phần trong trang thì không chụp ("Bỏ tay ra khỏi trang"); video thật: khung có tay 1–28%, khung sạch 0%. Rung theo ô lưới 4×4 quá 5 điểm ảnh là "Giữ yên máy". Rung và tay thì đếm lại ngay; thời gian chịu 0,4 giây chỉ cho khung tìm mép trượt, mất trang, mờ, tối, lóa thoáng qua.
- Phần *Số liệu chính* ở trên ghi theo bản nạp 2026-10-29; các ngưỡng mới thay ngưỡng chuyển động và thời gian giữ ở đó.

Xem tổng hợp: [[tu-dong-chup]], [[flutter-loi-cpp]], [[kiem-thu]].
