# Kết quả kiểm thử và xác minh

## Nguồn gốc

Các phép đo sử dụng cài đặt trong src/MergeSort.java. Mỗi pha lưu bản chụp mã nguồn và hash để đối chiếu giữa cài đặt, cấu hình, dữ liệu đầu vào và số đo.

SHA-256 mã giữ nguyên: 797fa52661500ca38bca2ea8cdf02497b3c8f54cb5bac8e63a032b85463a9d45.

Mã này khớp source-snapshot của cả ba pha. CREATION_LEDGER.csv ở thư mục gốc phân loại nguồn tạo từng tệp trong gói cuối; CHECKSUMS.txt dùng để xác minh nội dung.

## Thuật toán và thống kê

- javac -g -encoding UTF-8 -Xlint:all biên dịch thành công, không có cảnh báo.
- Bộ kiểm thử Java đạt 15.693 kiểm tra; gồm vét cạn dãy nhỏ, mọi cutoff 1 đến 128, biên, ổn định, generic và tham số không hợp lệ.
- Tám kiểm thử Python đạt: bốn kiểm thử về chữ ký cây, bảo toàn độ dài, bootstrap và phân vị; bốn kiểm thử về bảo vệ baseline và kiểm tra danh sách tệp.
- Sàng lọc: 60 mảng, 62.100 quan sát, 93.150 sort trong vùng đo.
- Chọn: 60 mảng mới, 14.700 quan sát, 18.375 sort.
- Xác nhận: 60 mảng mới khác hai pha trước, 14.700 quan sát, 14.700 sort.
- Tổng 180 mảng, 91.500 quan sát và 126.225 sort trong vùng đo. Tất cả output được đối chiếu toàn bộ với oracle, giữ mọi quan sát.
- Kiểm toán xác nhận đủ ma trận mẫu, không trùng quan sát, thứ tự cutoff là hoán vị, batch đúng, checksum kết quả khớp dữ liệu gốc, và hash nguồn/cấu hình/dataset đúng.
- Các quyết định chốt có hash nguồn phân tích và thời điểm sớm hơn pha tương ứng; không dùng tập xác nhận để chọn lại.

## Khả năng chạy một phiên mới

Lệnh study --new-run đã được kiểm tra bằng một giao thức thử nhỏ trong thư mục tách biệt. Chương trình tạo phiên đo riêng, chạy đủ ba pha, phân tích, chốt lựa chọn và kiểm toán. Dữ liệu kiểm tra chức năng được tách khỏi số liệu dùng trong báo cáo.

## Báo cáo

Bản Word được xuất sang PDF để kiểm tra bố cục. Báo cáo gồm 10 trang, bảng 20 ca và bốn đồ thị. Toàn bộ trang được kiểm tra về tiêu đề, tiếng Việt, bảng, hình, ngắt trang, mã minh họa và số trang. Kiểm tra tọa độ PDF không phát hiện chữ vượt lề ngang. Các bảng số liệu và giá trị định lượng được đối chiếu giữa các phiên bản biên tập.

## Demo

Java đã chạy trực tiếp MergeSort.sort 768 lần với Comparable ghi compareTo và kiểm tra kết quả bằng oracle ổn định. Gộp theo chuỗi sự kiện giống hệt, còn 45 bản ghi. Không có một MergeSort khác được viết để mô phỏng phần sắp xếp.

Bộ kiểm tra JavaScript đạt:

- 768 tổ hợp N, phân phối và cutoff.
- Duyệt đủ 45 bản ghi khác nhau với 4716 bước chuyển.
- Kiểm tra dấu so sánh, số đếm, giá trị cuối và thứ tự # khi khóa bằng nhau.
- Kiểm tra tiến/lùi, đầu/cuối, tự chạy/tạm dừng/kết thúc, đổi điều khiển và các nút mốc.
- Liên kết CSS, JavaScript, PDF, README đều tồn tại, không có tài nguyên mạng trong href/src.

Phạm vi kiểm thử gồm trace Java thực và logic tương tác với DOM tối thiểu. Bộ kiểm thử này không xác minh bố cục HTML/CSS hoặc khả năng hiển thị trong trình duyệt.

## Gói cuối

Gói ZIP được kiểm tra CRC và SHA-256 từng thành viên sau khi đóng gói. Các thư mục scratch, compiled, reruns, cache Python, lớp Java và ảnh kiểm tra bố cục được loại khỏi sản phẩm nộp.
