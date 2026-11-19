# Mục lục sản phẩm nộp

Project thực nghiệm CUTOFF cho MergeSort, gồm các nhóm sản phẩm trong ảnh đề. Báo cáo và số liệu được đo ngày 13/11/2026; cấu trúc GitHub được chuẩn bị ngày 19/11/2026.

| Tiêu chí | Sản phẩm để kiểm tra |
|---|---|
| Báo cáo mô tả, phân tích và tổng kết | [PDF](report/Cutoff_Study.pdf), [Word](report/Cutoff_Study.docx), [Markdown](report/Cutoff_Study.md) |
| Bảng và đồ thị | [Bốn hình](report/charts/), [thống kê mô tả](measurements/confirm/descriptive-times.csv), [khoảng tin cậy](measurements/confirm/paired-effects.csv) |
| Cài đặt MergeSort được cung cấp | [Mã nguồn nguyên bản](src/MergeSort.java), [nguồn gốc và hash](docs/ORIGIN.json) |
| Script chạy thí nghiệm | [cutofflab.py](cutofflab.py), [labcore](labcore/), [giao thức](study.json) |
| Bộ dữ liệu | [180 mảng CSV](datasets/), index và SHA-256 trong từng pha |
| Số đo gốc và cấu hình máy | [measurements](measurements/), evidence.json và process-*.csv của ba pha |
| Log dùng AI | [Nhật ký lần làm lại](docs/AI_SESSION_LOG.md), [công bố phạm vi AI](docs/AI_DISCLOSURE.md), [chuẩn bị GitHub](docs/GITHUB_PREPARATION.md) |
| Phân tích có kiểm chứng | [Giao thức ba pha](docs/PROTOCOL.md), [kết quả xác nhận](measurements/confirm/summary.json) |
| Demo tương tác | Clone hoặc tải repository, mở [demo/index.html](demo/index.html) |

Đề xuất C32 cho workload đã đo; C40 chưa phân biệt rõ. Không nhận số đo runner GitHub Actions làm số đo trên máy sinh viên. Thông tin cá nhân trên bìa đang để trống theo lựa chọn của người dùng.

Các lệnh kiểm tra đầy đủ nằm ở [README](README.md). Trước khi nộp liên kết, xem [hướng dẫn đẩy và chốt tag](docs/GITHUB_GUIDE.md). Nếu repository là private, cấp quyền đọc cho giảng viên theo cách nộp của học phần.
