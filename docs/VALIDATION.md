# Kết quả kiểm tra bản làm lại

## Nguồn gốc

Thư mục làm việc của bản này được tạo rỗng. Chỉ src/MergeSort.java được nhập từ tệp người dùng cung cấp; toàn bộ file phụ trợ được viết hoặc sinh trong lần làm lại. Không nhập PDF bài giảng, script, dữ liệu, report, demo hoặc log cũ.

SHA-256 mã giữ nguyên: 797fa52661500ca38bca2ea8cdf02497b3c8f54cb5bac8e63a032b85463a9d45.

Mã này khớp source-snapshot của cả ba pha. CREATION_LEDGER.csv ở thư mục gốc phân loại nguồn tạo từng tệp trong gói cuối; CHECKSUMS.txt dùng để xác minh nội dung.

## Thuật toán và thống kê

- javac -g -encoding UTF-8 -Xlint:all biên dịch thành công, không có cảnh báo.
- Bộ kiểm thử Java mới đạt 15.693 kiểm tra; gồm vét cạn dãy nhỏ, mọi cutoff 1 đến 128, biên, ổn định, generic và tham số không hợp lệ.
- Bốn kiểm tra Python cho chữ ký cây, bảo toàn độ dài, bootstrap trên tỷ số hằng biết trước và phân vị đều đạt.
- Sàng lọc: 60 mảng, 62.100 quan sát, 93.150 sort trong vùng đo.
- Chọn: 60 mảng mới, 14.700 quan sát, 18.375 sort.
- Xác nhận: 60 mảng mới khác hai pha trước, 14.700 quan sát, 14.700 sort.
- Tổng 180 mảng, 91.500 quan sát và 126.225 sort trong vùng đo. Tất cả output được đối chiếu toàn bộ với oracle, giữ mọi quan sát.
- Kiểm toán xác nhận đủ ma trận mẫu, không trùng quan sát, thứ tự cutoff là hoán vị, batch đúng, checksum kết quả khớp dữ liệu gốc, và hash nguồn/cấu hình/dataset đúng.
- Các quyết định chốt có hash nguồn phân tích và thời điểm sớm hơn pha tương ứng; không dùng tập xác nhận để chọn lại.

## Khả năng chạy một phiên mới

Đã kiểm tra toàn bộ lệnh study --new-run trong một workspace thử nhỏ tách biệt ở scratch. Chương trình tự sao chép nguồn mới của bản này, chạy ba pha, phân tích, chốt và kiểm toán. Workspace gốc không phát sinh hay bị ghi đè measurements. Dữ liệu thử nhỏ không được dùng trong báo cáo và không đóng gói.

## Báo cáo

Bản DOCX mới được xuất bằng LibreOffice đi kèm runtime qua render_docx.py, thành 10 trang PNG và PDF. Đã quan sát toàn bộ trang ở độ phân giải đầy đủ: tiêu đề, tiếng Việt, bảng 20 ca, bốn đồ thị, ngắt trang, code và số trang sạch. Kiểm tra tọa độ PDF không phát hiện chữ vượt lề ngang. PDF cuối lấy từ chính lượt render đã kiểm tra; thông tin bìa để trống theo yêu cầu.

## Demo

Java đã chạy trực tiếp MergeSort.sort 768 lần với Comparable ghi compareTo và kiểm tra kết quả bằng oracle ổn định. Gộp theo chuỗi sự kiện giống hệt, còn 45 bản ghi. Không có một MergeSort khác được viết để mô phỏng phần sắp xếp.

Bộ kiểm tra JavaScript mới đạt:

- 768 tổ hợp N, phân phối và cutoff.
- Duyệt đủ 45 bản ghi khác nhau với 4716 bước chuyển.
- Kiểm tra dấu so sánh, số đếm, giá trị cuối và thứ tự # khi khóa bằng nhau.
- Kiểm tra tiến/lùi, đầu/cuối, tự chạy/tạm dừng/kết thúc, đổi điều khiển và các nút mốc.
- Liên kết CSS, JavaScript, PDF, README đều tồn tại, không có tài nguyên mạng trong href/src.

Phạm vi là trace Java thực và logic viewer với DOM tối thiểu. Lần làm lại không kiểm tra render HTML/CSS trực tiếp trong trình duyệt do hạn chế giao thức file đã biết của công cụ; không dùng bề mặt khác để lách hạn chế. Không tuyên bố kiểm thử VM xác minh layout.

## Gói cuối

Gói ZIP được kiểm tra CRC và SHA-256 từng thành viên sau khi đóng gói. Các thư mục scratch, compiled, reruns, cache Python, lớp Java và ảnh QA không được kèm. Bản gốc người dùng cùng các sản phẩm trước được giữ nguyên ngoài gói mới.
