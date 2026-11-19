# Ghi chú khi chỉnh sửa project

## Bản thí nghiệm đã chốt

Giữ nguyên 308 tệp được liệt kê trong docs/BASELINE_SHA256.txt. Chúng gồm mã Java đã đo, dữ liệu, số đo, báo cáo và các công cụ của bản làm lại. Những nội dung này cần khớp nhau để có thể kiểm tra kết luận.

Một lượt đo mới được tạo bằng `python3 cutofflab.py study --new-run ten_moi`. Ghi cấu hình và kết quả của lượt đó riêng; không thay thời gian hoặc hash của lượt đã nộp bằng kết quả của máy khác.

## Chỉnh tài liệu và cấu hình GitHub

README, SUBMISSION, hướng dẫn GitHub, workflow và công cụ quản lý repository có thể được cập nhật trong phạm vi chuẩn bị bài nộp. Sau thay đổi:

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 tools/repository_check.py refresh
python3 tools/repository_check.py check
```

refresh cập nhật CREATION_LEDGER.csv và CHECKSUMS.txt sau khi kiểm tra baseline. Vì vậy thay đổi byte của CSV, mã đã đo hoặc PDF sẽ không được hợp thức hóa bằng lệnh này.

## Kiểm tra trước khi push

```sh
make check
```

Nếu không dùng Make, chạy các lệnh riêng trong [README](README.md). Kiểm thử viewer dùng DOM tối thiểu để kiểm tra logic; khi đổi HTML/CSS cần kiểm tra giao diện bằng trình duyệt trên máy của người sửa.

.gitattributes giữ nguyên byte của các tệp thay vì tự đổi LF/CRLF. Điều này bảo toàn SHA-256 của các index CSV có CRLF. .gitignore vẫn cho phép commit CSV và log thí nghiệm; chỉ loại build, cache, môi trường ảo và các lượt đo thử.

Nếu tạo phiên bản nghiên cứu khác với baseline hiện tại, mô tả phiên bản đó như một thí nghiệm mới, kèm báo cáo và bằng chứng tương ứng.
