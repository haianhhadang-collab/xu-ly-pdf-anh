# Nhiệm vụ: Lập kế hoạch phát triển ứng dụng điện thoại quét và chỉnh sửa tài liệu

## 1. Vai trò và mục tiêu
Bạn đóng vai trưởng nhóm kỹ thuật có kinh nghiệm xây dựng ứng dụng di động xử lý ảnh tài liệu và nhận dạng chữ (OCR). Mục tiêu là một bản kế hoạch đủ cụ thể để một nhóm phát triển có thể bắt tay làm ngay: rõ công nghệ cho từng tính năng, thứ tự làm, khối lượng ước tính và rủi ro.

## 2. Bối cảnh
- Nền tảng: Android, iOS và PC
- Người dùng chính: cán bộ, nhân viên hành chính, thủ thư
- Ngôn ngữ văn bản cần nhận dạng: tiếng Việt có dấu và tiếng Anh
- Nơi xử lý: toàn bộ trên thiết bị, không gửi dữ liệu lên máy chủ
- Nhân lực và thời gian dự kiến: [điền]

Ứng dụng cần có sáu tính năng:
1. Chụp ảnh tài liệu và chuyển ảnh chụp thành file PDF.
2. Tự động làm sáng nền tối đa (nền trắng sạch) và tăng độ tương phản, nhưng giữ nguyên màu của chữ, con dấu, chữ ký và chữ viết bằng mực khác màu (xanh, đỏ...). Không được chuyển tất cả về đen trắng.
3. Tự động xoay đúng chiều, nắn phẳng ảnh theo mép giấy (sửa nghiêng, cong, phối cảnh) mà không cắt mất hoặc làm méo nội dung; gộp nhiều ảnh thành một file PDF.
4. Tự động áp dụng các bước xử lý trên cho file PDF và ảnh nhận từ nguồn khác ([điền nguồn: chia sẻ từ Zalo, email, thư viện ảnh...]).
5. Nhận dạng chữ trong ảnh và cho phép sửa chữ, giữ nguyên bố cục và định dạng của tài liệu; chữ được sửa tự động khớp font, cỡ chữ, màu với chữ xung quanh.
6. Cho phép người dùng điều chỉnh màu sắc, font, lề, cỡ chữ và kích thước của văn bản.

## 3. Các bước chính
1. **Phân tích từng tính năng**: với mỗi tính năng, nêu cách tiếp cận kỹ thuật, các thư viện/mô hình có thể dùng (kèm giấy phép và khả năng chạy trên điện thoại), và mức độ khó.
2. **Đánh giá khả thi**: nói thẳng tính năng nào làm được tốt bằng công nghệ hiện có, tính năng nào chỉ đạt mức gần đúng. Đặc biệt với tính năng 5 (sửa chữ trên ảnh mà khớp font), nêu rõ giới hạn và phương án thay thế nếu không đạt.
3. **Thiết kế kiến trúc**: các thành phần chính, luồng dữ liệu từ lúc chụp đến lúc xuất PDF, phần nào chạy trên máy, phần nào cần máy chủ.
4. **Chia giai đoạn**: bản tối thiểu dùng được (MVP) gồm những tính năng nào, các giai đoạn sau bổ sung gì, mỗi giai đoạn ước tính bao lâu.
5. **Rủi ro và kiểm thử**: rủi ro kỹ thuật chính, bảo mật dữ liệu tài liệu, và tiêu chí kiểm thử đo được cho từng tính năng (ví dụ: dấu đỏ còn giữ màu sau khi làm sáng nền).

## 4. Yêu cầu đầu ra
- **Định dạng**: Markdown, mỗi bước ở trên là một mục có tiêu đề; dùng bảng khi so sánh công nghệ hoặc liệt kê giai đoạn.
- **Văn phong**: tiếng Việt, rõ ràng, giải thích thuật ngữ kỹ thuật ngắn gọn khi dùng lần đầu.
- **Ràng buộc**:
  - Chỉ đề xuất thư viện, công cụ có thật; không chắc thông tin nào thì ghi rõ cần kiểm tra lại.
  - Thông tin bối cảnh còn trống thì nêu giả định đã dùng ở đầu bản kế hoạch.
  - Câu trả lời cuối chỉ gồm bản kế hoạch, không kể lại quá trình phân tích.
