# Gợi ý trình bày kết quả

## Trình bày trong khoảng năm phút

1. Đặt câu hỏi của đề: vì sao chọn 7, 10 hoặc ngưỡng khác trên chính cài đặt và máy của mình?
2. Chỉ vào điều kiện hi - lo < cutoff trong MergeSort.java. Giải thích độ dài đoạn đóng và tính ổn định của nhánh chèn, nhánh trộn.
3. Nêu thiết kế ba pha đã định trước: sàng lọc 69 ngưỡng, chốt ba ứng viên, chọn trên tập mới rồi xác nhận lựa chọn đã đóng băng. Seed và kích thước tách biệt cả ba pha.
4. Trình bày kết quả: shortlist 40, 48, 32; tập chọn chọn 32. Trên xác nhận, C32 speedup 1,0653 trước C7 và 1,0620 trước C10. C32 và C40 chưa phân biệt rõ.
5. Mở demo: chọn 33 phần tử, thử C7, C10, C32 và C40. Dùng Tiếp để xem compareTo từ mã Java thật, Đến cuối để kiểm tra thứ tự # của các khóa bằng nhau. Cây độ dài là phần minh họa cấu trúc.
6. Kết thúc bằng bản đồ phân phối: C32 có lợi tổng hợp nhưng có thể chậm hơn C10 trên mảng giảm dần. Kết luận phụ thuộc workload và trọng số.

## Các câu hỏi cần hiểu

**CUTOFF 10 nhận đoạn nào?** Độ dài không quá 10. Vì chỉ số cuối được tính vào đoạn, hi - lo + 1 <= cutoff tương đương hi - lo < cutoff.

**Tại sao C1 là đường cơ sở?** Nó đưa đệ quy tới đoạn đơn phần tử trong cùng bản tham số hóa. Không tuyên bố đã đo một hàm MergeSort thuần được tối ưu riêng.

**Tại sao ổn định?** Chèn không đổi chỗ hai khóa bằng nhau; trộn lấy phần tử bên trái trước khi bằng khóa. Các đối tượng cùng khóa giữ thứ tự ban đầu.

**Vì sao cần nhiều phân phối?** Mảng tăng dần ít đổi chỗ khi chèn, mảng giảm dần có nhiều nghịch thế. CUTOFF lớn có thể giúp loại này và làm hại loại kia. Trọng số bằng nhau là một lựa chọn workload được công bố.

**Tại sao sàng lọc chọn 40 nhưng cuối cùng đề xuất 32?** Sàng lọc chỉ tạo shortlist, không chốt kết luận cuối. Pha chọn riêng được thiết kế từ đầu và chọn 32 trong ba ứng viên đã chốt. Sau đó 32 được giữ nguyên khi xác nhận; không đổi sang 40 vì thấy một thời gian nhỏ hơn ở pha cuối.

**32 có nhanh hơn 40 không?** Trên pha xác nhận, tỷ số thời gian C40/C32 khoảng 0,9994, khoảng 95% từ 0,9968 đến 1,0024. Khoảng chứa 1 nên chưa phân biệt rõ. Với các N cuối, mọi cutoff 30 đến 47 tạo cùng cấu trúc; khác biệt số đo nhỏ không đủ để chọn một giá trị tối ưu duy nhất.

**3% có phải mức ý nghĩa thống kê?** Không. Đây là ngưỡng chênh lệch thực dụng được ghi trước thí nghiệm. Khoảng bootstrap mô tả biến động theo JVM và seed, giữ cố định phân phối và N; nó không chứng minh đồng thời toàn bộ lưới tối ưu.

**Speedup 1,062 nghĩa là giảm 6,2% thời gian?** Tỷ lệ giảm thời gian là 1 - 1/speedup, ở đây khoảng 5,83%. Hai cách nói có mẫu số khác nhau.

**Có tính clone và oracle vào thời gian không?** Không. Clone chỉ khôi phục cùng input. Cấp phát aux thuộc MergeSort.sort nên được tính. Sau đồng hồ, mọi output được đối chiếu toàn bộ với oracle.

**Demo có tự viết một MergeSort khác không?** Không. Token implements Comparable ghi compareTo rồi gọi đúng MergeSort.sort. StackWalker xác định so sánh đang nằm ở insertionSort hay merge. Trace không dùng để đo hiệu năng vì việc ghi log có chi phí lớn.

**Tại sao mảng trong demo đôi khi lặp phần tử?** Snapshot chụp mảng đích ngay trước một phép so sánh. Khi merge ghi dở, nguồn đúng còn trong aux nên trạng thái trung gian có thể lặp; kết quả cuối được kiểm tra với oracle ổn định.

**AI làm phần nào?** Cài đặt MergeSort do sinh viên thực hiện. AI tạo các thành phần hỗ trợ gồm kiểm thử, công cụ thí nghiệm, bộ sinh dữ liệu, phân tích, đồ thị và demo, đồng thời biên soạn bản thảo báo cáo và tài liệu. Phạm vi được công bố trong AI_DISCLOSURE.md và nhật ký trao đổi AI.

## Kiểm tra và tái lập

Các lệnh test và verify kiểm tra mã nguồn, dữ liệu và tính nhất quán của kết quả. Demo và PDF được mở từ cấu trúc thư mục của repository. Khi thay máy hoặc JVM, cần thực hiện phiên đo riêng và diễn giải kết quả theo cấu hình của phiên đó.
