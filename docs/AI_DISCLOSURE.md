# Công bố phạm vi hỗ trợ AI

## Cài đặt MergeSort

Cài đặt trong src/MergeSort.java do sinh viên thực hiện và được sử dụng thống nhất trong thí nghiệm. Thuật toán và mã nguồn không thay đổi giữa các phép đo. SHA-256 được ghi trong ORIGIN.json và khớp source-snapshot của cả ba pha.

## Các thành phần do AI hỗ trợ

AI tạo bộ kiểm thử, harness Java, giao thức thí nghiệm, bộ sinh dữ liệu, công cụ chạy, thống kê, kiểm toán, bốn đồ thị và demo; đồng thời biên soạn bản thảo báo cáo và tài liệu hướng dẫn. Dữ liệu đầu vào được sinh theo cấu hình đã công bố; các thời gian đo được thu từ việc chạy chương trình Java trên máy được mô tả trong báo cáo.

Demo dùng đối tượng Comparable ghi compareTo, gọi trực tiếp MergeSort.sort. Cây độ dài trên giao diện chỉ là minh họa cấu trúc. Không có một cài đặt MergeSort thay thế được AI viết để làm trace; Arrays.sort chỉ làm oracle và chuẩn bị đầu vào ngoài vùng đo.

## Nhật ký và nguồn tham khảo

AI_SESSION_LOG.md ghi các trao đổi trong giai đoạn xây dựng bộ thí nghiệm, kèm tóm tắt thao tác công cụ. Metadata và console log của phép đo được lưu trong measurements/.

Tài liệu tham khảo kỹ thuật là Java API chính thức về System.nanoTime và StackWalker. Cài đặt MergeSort được xác định bằng đường dẫn và SHA-256 nêu trên; phần công bố này phân biệt mã thuật toán của sinh viên với các thành phần được AI hỗ trợ.
