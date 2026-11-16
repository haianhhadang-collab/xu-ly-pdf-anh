---
type: nguon
tep_goc: "D:\\Zalo Data\\7b2d1456-…_Hồ sơ 15-11 19-33.pdf (không chép vào dự án)"
ngay_nap: 2026-11-15
loai: dữ liệu
---
# Hồ sơ 15-11 19-33.pdf: cả cuốn sách chụp bằng bản Android (214 trang)

- PDF xuất từ bản Android, 214 trang, 55,9 MB, mỗi trang một ảnh JPEG. Người dùng chụp từng cặp trang sách mở, hồ sơ loại Sách nên ứng dụng tự tách thành hai trang (`NHAT-KY.md` dự án, 2026-11-15).
- Yêu cầu kèm theo: dò các trang lỗi, cải thiện kết quả; lề không cần cắt sát quá; làm vuông giấy để sau khi chụp mới xử lý ([[yeu-cau-nguoi-dung]]).
- Cách dò: tách ảnh từng trang (pypdf), ghép tờ thu nhỏ 24 trang một tờ, xem từng trang; script đếm dải chữ trang bên, trang bị cắt còn mẩu, màu da.

## Lỗi tìm thấy
- **Tách gáy sai** (khoảng 70–80 trang, lỗi nhiều nhất): trang trái dính một dải chữ cái đầu dòng của trang phải, trang phải mất một hai chữ cái đầu dòng. Do cắt theo cột tối nhất (bóng gáy), mà bóng gáy lệch sang trang phải ([[nan-phang-va-xoay]]).
- **Trang ít chữ bị cắt còn mẩu**: 3 trang (ví dụ trang cuối chương còn 976×440).
- **Khổ trang không đều**, lề sát: tỉ lệ cao/rộng 1,3–1,8.
- **Tay đang lật trang, ảnh nhòe**: 2 trang; ảnh gốc hỏng, phải chụp lại.
- Một cặp trang chụp hai lần.

## Dùng làm gì
- Căn cứ sửa bước tách trang (cắt giữa khe gáy theo đường xiên), lề "Vừa", chụp xong mới xử lý, nút Xử lý lại cả hồ sơ ở bản 0.7.7 ([[ban-android-flutter]], [[kiem-thu]]).
- Ảnh trang kết quả không giữ trong dự án (chỉ là đầu ra đã cắt hỏng, không có ảnh gốc).

## Cập nhật (0.7.8)
- 12 trang đại diện (2 trang nhòe, 5 trang chữ in nhạt, 5 trang tốt) lưu làm ảnh thử ở `D:\DevTools\src\xlpdf_kiemthu\chat_luong` cho phép đo báo trang nên chụp lại ([[kiem-thu]]).

## Cập nhật (0.7.9, 2026-11-16)
- Dò lại cả hồ sơ: 11 cặp trang chụp trùng (trang sách 146, 180, 181, 212, 213, 258–261, 263, 294 mỗi trang hai lần), không chỉ cặp 180/181. Bản 0.7.9 báo trang chụp trùng ở Xem nhanh (10 cặp; cặp có trang bị tay che nửa trang dưới ngưỡng) ([[kiem-thu]]).
- Nguyên nhân nhiều khả năng của trang 145, 146 nhòe: màn camera rung báo trước khi máy chụp thật; đã sửa ([[tu-dong-chup]]).
