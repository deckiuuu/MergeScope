# Công bố phần thực hiện trong lần làm lại

## Phần giữ nguyên

Người dùng chỉ định giữ src/MergeSort.java và mô tả đây là mã do mình thực hiện. File được sao chép nguyên byte, không sửa thuật toán hoặc thêm mã ghi log. SHA-256 gốc được ghi trong ORIGIN.json và khớp source-snapshot của cả ba pha.

## Phần AI tạo mới

AI viết mới bộ kiểm thử, harness Java, giao thức, bộ sinh dữ liệu, công cụ chạy, thống kê, kiểm toán, báo cáo, bốn hình, demo và hướng dẫn. Dữ liệu cùng thời gian đo được sinh/chạy mới; không dùng lại số đo, code hỗ trợ, mẫu báo cáo, demo, PDF bài giảng hoặc log của project trước.

Demo dùng đối tượng Comparable ghi compareTo, gọi trực tiếp MergeSort.sort. Cây độ dài trên giao diện chỉ là minh họa cấu trúc. Không có một cài đặt MergeSort thay thế được AI viết để làm trace; Arrays.sort chỉ làm oracle và chuẩn bị đầu vào ngoài vùng đo.

## Nhật ký và nguồn tham khảo

AI_SESSION_LOG.md ghi đầy đủ lời người dùng và lời trợ lý hiển thị từ yêu cầu làm lại, với tóm tắt các lượt công cụ. Metadata và console log của phép đo được giữ trong measurements/. Nhật ký không chứa suy luận nội bộ hoặc chỉ dẫn hệ thống, và không phải bản xuất toàn bộ lịch sử ứng dụng trước yêu cầu làm lại.

Nguồn tham khảo ngoài mã được cung cấp chỉ là Java API chính thức về System.nanoTime và StackWalker. Không nhập một cài đặt MergeSort từ nguồn khác. Phạm vi AI được trình bày để người đọc biết phần nào là mã sinh viên cung cấp, phần nào được hỗ trợ trong phiên này.
