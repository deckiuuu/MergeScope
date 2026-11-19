# Đối chiếu với yêu cầu sản phẩm

Bảng dưới đây đối chiếu yêu cầu của bài thực nghiệm với mã nguồn, dữ liệu, báo cáo và tài liệu kèm theo.

| Yêu cầu của đề | Sản phẩm để kiểm tra |
|---|---|
| Thí nghiệm chọn CUTOFF trên cấu hình máy và cài đặt MergeSort | study.json cùng ba pha sàng lọc, chọn và xác nhận, metadata phần cứng/JVM |
| Dùng cài đặt MergeSort của sinh viên | src/MergeSort.java giữ nguyên, hash được kiểm tra ở ba pha |
| Báo cáo mô tả, phân tích và tổng kết | report/Cutoff_Study.pdf, .docx, .md |
| Bảng thống kê và đồ thị | Bảng median/mean/SD/quantile/MAD, tỷ số ghép cặp, bootstrap và bốn hình PNG/SVG |
| Mã nguồn và script thí nghiệm | src/, tests/, labcore/, cutofflab.py |
| Bộ dữ liệu | 180 CSV, seed, index SHA-256 và generation.json |
| Log trao đổi AI | docs/AI_SESSION_LOG.md và docs/GITHUB_PREPARATION.md ghi các trao đổi và cập nhật; nhật ký kỹ thuật trong measurements/ |
| Phân tích có kiểm chứng | Ba pha được định trước, dữ liệu tách biệt, lựa chọn đóng băng trước xác nhận và quy tắc dừng |
| Demo tương tác | demo/index.html; 768 lượt chạy từ mã MergeSort thật và 45 bản ghi khác nhau |

Mốc 1, 7 và 10 có trong cả ba pha. Quicksort được nhắc ở phần dẫn nhập của đề, còn phần giao việc thực nghiệm yêu cầu MergeSort.
