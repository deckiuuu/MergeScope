# Đối chiếu với yêu cầu sản phẩm

Đề được đọc từ ảnh người dùng gửi trong chat hiện tại. Tệp bài giảng, báo cáo, script và log cũ không được nhập vào bản làm lại. Nội dung đề là yêu cầu học phần; phạm vi thao tác của lần làm lại lấy từ yêu cầu trực tiếp của người dùng.

| Yêu cầu trong ảnh | Sản phẩm của bản này |
|---|---|
| Thí nghiệm chọn CUTOFF trên cấu hình máy và cài đặt MergeSort | study.json cùng ba pha sàng lọc, chọn và xác nhận, metadata phần cứng/JVM |
| Dùng cài đặt sinh viên cung cấp | src/MergeSort.java giữ nguyên, hash được kiểm tra ở ba pha |
| Báo cáo mô tả, phân tích và tổng kết | report/Cutoff_Study.pdf, .docx, .md |
| Bảng thống kê và đồ thị | Bảng median/mean/SD/quantile/MAD, tỷ số ghép cặp, bootstrap và bốn hình PNG/SVG |
| Mã nguồn và script thí nghiệm | src/, tests/, labcore/, cutofflab.py |
| Bộ dữ liệu | 180 CSV, seed, index SHA-256 và generation.json |
| Log trao đổi AI | docs/AI_SESSION_LOG.md ghi phần trao đổi hiển thị của lần làm lại, kèm nhật ký kỹ thuật trong measurements/ |
| Phân tích có kiểm chứng đã duyệt | Ba pha được định trước, dữ liệu tách biệt, lựa chọn đóng băng trước xác nhận và quy tắc dừng |
| Demo tương tác đã duyệt | demo/index.html; 768 lượt chạy từ mã MergeSort thật và 45 bản ghi khác nhau |

Mốc 1, 7 và 10 có trong cả ba pha. Quicksort được nhắc ở phần dẫn nhập của đề, còn phần giao việc thực nghiệm yêu cầu MergeSort. Bìa để trống thông tin cá nhân theo lựa chọn của người dùng.
