# Chế độ tự động chụp (Android, iOS, PC)

Yêu cầu (2026-10-29): ứng dụng tự chụp trang sách khi đủ điều kiện. Người dùng chỉ giữ máy và lật trang; mỗi trang mới được chụp một lần.

Thuật toán đã viết và kiểm thử trong nguyên mẫu: `ung-dung/loi_xu_ly/tu_chup.py` (lớp `BoTuChup`). Bản PC dùng ngay trong cửa sổ *Chụp camera* (ô *Tự động chụp*, bật sẵn). Bản Android, iOS chuyển nguyên thuật toán này sang lõi C++ theo mục 4.

## 1. Điều kiện chụp

Mỗi khung hình xem trước được xét theo thứ tự dưới đây. Điều kiện đầu tiên chưa đạt quyết định lời nhắc hiện trên màn hình.

| # | Điều kiện | Cách đo (trên ảnh thu nhỏ, cạnh dài 640 px) | Ngưỡng mặc định | Lời nhắc khi chưa đạt |
|---|---|---|---|---|
| 1 | Thấy trang | Tìm 4 góc mép giấy (`tim_mep_giay`). Không thấy mép nhưng giấy có chữ phủ ≥ 75% khung hình thì coi là chụp kín (sách mở chụp sát) | — | Chưa thấy trang giấy |
| 2 | Trang đủ lớn | Diện tích tứ giác / diện tích khung hình | ≥ 20% | Đưa máy lại gần trang |
| 3 | Không cắt mép | Khoảng cách từ góc trang tới mép khung hình | ≥ 1% cạnh dài | Lùi máy ra cho thấy đủ trang |
| 4 | Cầm máy song song | Tỉ số hai cạnh đối diện của tứ giác | ≤ 1,45 | Cầm máy song song với trang |
| 5 | Đủ sáng | Trung vị độ sáng trong trang | ≥ 70/255 | Thiếu sáng, bật thêm đèn |
| 6 | Không lóa | Tỉ lệ điểm cháy sáng (≥ 248 và sáng hơn trung vị 15) trong trang | ≤ 1,5% | Bị lóa, nghiêng máy một chút |
| 7 | Đứng yên | Độ dời ước tính giữa hai khung liên tiếp: chênh lệch trung bình (ảnh 160 px, làm mờ) chia độ dốc sáng trung bình, không phụ thuộc tương phản cảnh (từ 0.7.4; trước đây chênh lệch thô ≤ 5/255, sách trên nền đen tay run nhẹ đã vượt) | ≤ 2,5 điểm ảnh | Giữ yên máy |
| 8 | Đủ nét | Trung bình trị tuyệt đối Laplace trong trang | ≥ 6 | Chưa nét, giữ yên để máy lấy nét |
| 9 | Trang mới | Độ khác bản đồ mật độ mực (48×64, so có dịch ±2 ô) so với trang vừa chụp | ≥ 0,24; ≥ 0,18 khi đã thấy lật trang | Đã chụp trang này, lật sang trang mới |
| 10 | Giữ đủ lâu | Cả 9 điều kiện đạt; khung hỏng thoáng qua dưới 0,4 giây không làm đếm lại; góc trang lệch ≤ 3% đường chéo so với khung trung bình trượt | 0,5 giây | Giữ yên, sắp chụp… (kèm vòng tiến độ) |

Hết thời gian giữ thì lấy **khung nét nhất** trong khoảng giữ yên, không lấy khung cuối. Nhờ vậy những khung còn mờ lúc máy đang lấy nét bị bỏ qua.

Kiểm tra *trang mới* giúp không chụp trùng. Va máy rồi trở về trang cũ thì không chụp lại. Lật sang trang khác thì chụp ngay khi trang đứng yên. Trên ảnh mô phỏng, cùng một trang chụp lại có độ khác dưới 0,21. Hai trang sách khác nhau có độ khác từ 0,37 trở lên.

## 2. Máy trạng thái

```
khong_thay / xa / cat_mep / nghieng / toi / loa / rung / mo   (chưa đạt: hủy lượt giữ)
        │ đạt cả 8
        ▼
  khác trang vừa chụp? ── không ──► cho_trang_moi
        │ có
        ▼
  dang_giu (đếm 0,5 s; góc lệch quá 3% so với khung trung bình thì đếm lại; khung hỏng < 0,4 s bỏ qua; nhớ khung nét nhất)
        │ đủ 0,5 s
        ▼
  da_chup → nhớ chữ ký trang → quay lại chờ trang mới
```

## 3. Kết quả kiểm thử trên nguyên mẫu

`ung-dung/kiem_thu/kiem_thu_tu_chup.py` dựng một đoạn phim 15 khung/giây, dài 20 giây, gồm các tình huống sau:
- bàn trống, rồi đưa trang vào;
- giữ yên, 4 khung đầu còn mờ;
- va máy rồi trở về trang cũ;
- lật trang, có tay che;
- trang thiếu sáng, bị lóa, bị cắt mép, ở quá xa, cầm nghiêng;
- chụp kín hai trang sách.

Kết quả đạt toàn bộ:
- Chụp đúng 4 trang mới, mỗi trang một lần.
- Không chụp ở các tình huống chưa đạt, và mỗi tình huống báo đúng lời nhắc.
- Ảnh chụp là khung nét: độ nét 26 so với 5 của khung mờ.
- Phân tích một khung hình 960×720 mất 12 ms trên PC (Python).

Đã chạy cửa sổ camera thật với camera giả phát đoạn phim này: ứng dụng tự chụp 4 trang và xử lý xong cả 4.

**Chưa kiểm chứng**: ảnh camera thật, giấy bóng, đèn huỳnh quang nhấp nháy, sách dày cong mạnh, tay giữ trang lọt vào khung. Các ngưỡng ở mục 1 cần tinh chỉnh trên bộ ảnh thật (Giai đoạn 0 của kế hoạch).

## 4. Chuyển sang Android, iOS (Flutter + lõi C++)

### Luồng khung hình
- Dùng plugin `camera` của Flutter: `controller.startImageStream()` nhận khung YUV420 (Android) hoặc BGRA8888 (iOS). Đặt độ phân giải xem trước khoảng 1280×720 (`ResolutionPreset.high`).
- Mỗi khung chỉ cần:
  - mặt phẳng Y (độ sáng), làm ảnh xám;
  - mặt phẳng U, V thu nhỏ, để đo độ bão hòa màu khi tìm giấy (thay cho kênh S của HSV).
- Không chuyển sang RGB toàn khung, đỡ tốn thời gian.
- Phân tích trong một isolate riêng hoặc ở luồng C++. Đang bận thì bỏ khung mới, không xếp hàng; phân tích khoảng 10–15 khung/giây là đủ.
- Truyền thời điểm khung hình (timestamp của camera) vào `nhan_khung`, không dùng đồng hồ của luồng phân tích.

### Giao diện lõi C++ (gọi qua `dart:ffi`)
```c
typedef struct {
  int   ma;            // 0 khong_thay, 1 xa, 2 cat_mep, 3 nghieng, 4 toi, 5 loa, 6 rung, 7 mo,
                       // 8 cho_trang_moi, 9 dang_giu, 10 da_chup
  float tien_do;       // 0..1
  float khung[8];      // 4 góc (x, y) theo tọa độ khung xem trước; kin_khung = 1 thì bỏ qua
  int   kin_khung;
  int   so_trang;
} TrangThaiTuChup;

void*           tu_chup_tao(const CauHinhTuChup* ch);
void            tu_chup_dat_lai(void* bo, int quen_trang_cuoi);
TrangThaiTuChup tu_chup_nhan_khung(void* bo,
                    const uint8_t* y, int rong, int cao, int buoc_y,
                    const uint8_t* u, const uint8_t* v, int buoc_uv, int buoc_diem_uv,
                    double thoi_diem_giay);
void            tu_chup_huy(void* bo);
```

### Khi `ma == da_chup`
1. Gọi `takePicture()` lấy ảnh độ phân giải gốc, thường 8–12 MP, để làm PDF. Ảnh xem trước 720p không đủ cho 200 dpi khổ A4.
2. Lúc chờ ảnh về (200–500 ms), tiếp tục xét điều kiện *đứng yên*. Máy rung trong lúc đó thì bỏ ảnh và chờ lượt sau.
3. Đổi tọa độ khung trang từ ảnh xem trước sang ảnh gốc theo tỉ lệ hai kích thước (cùng tỉ lệ khung hình thì chỉ cần nhân hệ số). Sau đó chạy luồng làm sạch, nắn phẳng.
4. Phản hồi người dùng: rung (Android 0.7.4: kênh `xlpdf/rung` gọi `Vibrator`, rung nhẹ 25 ms khi bắt được trang, 70 ms khi chụp; tắt được ở Cài đặt › Rung báo), nháy màn hình, âm chụp. Ở một số nước, iOS bắt buộc có âm chụp.
5. Thêm ảnh nhỏ vào dải trang ở cuối màn hình; người dùng xóa được trang chụp hỏng ngay.

### Điều khiển camera
- Khi đang giữ yên, khóa lấy nét và đo sáng vào giữa trang (`setFocusPoint`, `setExposurePoint`). Mở khóa khi trang thay đổi.
- Thiếu sáng (lời nhắc 5) kéo dài quá 2 giây: gợi ý bật đèn flash ở chế độ đèn pin. Không bật flash lúc chụp, vì flash gây lóa trên giấy bóng.
- Giữ màn hình sáng suốt lượt chụp (`wakelock_plus`).

### Tùy chọn cho người dùng
- Bật, tắt tự động chụp. Nút chụp tay vẫn luôn dùng được.
- Độ nhạy *nhanh / vừa / chắc*: thời gian giữ 0,3 / 0,5 / 0,9 giây (từ 0.7.4; trước đây 0,5 / 0,8 / 1,2).
- Chế độ *sách*: bật tách trang đôi, chấp nhận chụp kín khung. Chế độ *giấy rời*: bắt buộc thấy đủ 4 mép.

### Việc cần làm khi dựng bản di động
1. Viết lõi C++ cho `tu_chup` và `tim_mep_giay`, dùng chung bộ kiểm thử với bản Python: chạy cùng đoạn phim mô phỏng, so kết quả từng khung.
2. Đo thời gian trên máy Android tầm trung (mục tiêu dưới 40 ms một khung 720p) và trên iPhone đời cũ nhất còn hỗ trợ.
3. Thu 20–30 đoạn phim chụp thật, lật sách ở thư viện và đặt lần lượt công văn ở văn phòng, rồi tinh chỉnh ngưỡng: độ nét, độ khác trang, chuyển động.

## Nhận động tác lật trang (bản 0.7.4, 2026-11-14)
Video chụp thật của người dùng (sách mở trên nền đen) cho thấy hai cặp trang sách in cùng khổ chỉ khác nhau 0,22–0,33 theo bản đồ mật độ mực, sát ngưỡng 0,24: trang mới lúc được nhận, lúc bị coi là trang cũ, đồng hồ giữ yên chạy lại liên tục (một cặp trang chờ 18 giây). Cách sửa: sau mỗi lần chụp, cộng thời gian các khung có dấu hiệu lật trang (không thấy trang, trang ra khỏi khung hoặc bị cắt, dịch chuyển mạnh, hay khác trang vừa chụp trên 0,45 vì tay che). Chỉ cộng chuỗi khung xáo trộn liền nhau từ 0,25 giây (một khung tìm mép trượt không tính); đủ 1 giây thì coi là đã lật (lật trang thật trong video 1,2–4 giây, tay chạm vuốt trang 0,7 giây), ngưỡng trang mới hạ xuống 0,18. Va máy rồi về trang cũ (khác dưới 0,16, thường chưa đủ 1 giây xáo trộn) vẫn không bị chụp lại.

## Tay trên trang, rung theo ô (bản 0.7.4)
- **Tay trên trang** ("Bỏ tay ra khỏi trang"): điểm màu da (sắc 6–25 theo thang 0–180 của OpenCV, bỏ đỏ của mực dấu; bão hòa cao hơn giấy 30; sáng ≥ 80) thuộc mảng chạm dải mép trang (8% ngoài cùng), vì tay luôn thò vào từ ngoài; phần trong của trang bị che quá 0,5% thì không chụp, đếm lại. Không xét khi giấy phủ kín khung (không có mép trang). Video chụp thật: khung có tay 1–28%, khung sạch 0%.
- **Rung theo ô**: độ dời trong từng ô lưới 4×4 của ảnh 160 px (sàn độ dốc 2), quá 5 điểm ảnh là "Giữ yên máy". Bắt tay đang vuốt, lật trang mà độ dời trung bình cả khung còn nhỏ (tay 7–35, sách nằm yên dưới 4).
- Rung và tay thì đếm lại ngay; thời gian chịu 0,4 giây chỉ cho các khung tìm mép trượt, mất trang, mờ, tối, lóa thoáng qua.
