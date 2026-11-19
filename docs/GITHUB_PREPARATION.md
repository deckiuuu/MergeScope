# Chuẩn bị repository GitHub ngày 19 tháng 11 năm 2026

## Yêu cầu hiện tại

> Tôi cần đẩy project này lên github để nộp, hãy hướng dẫn tôi và xây dựng 1 cấu trúc project github đầy đủ

## Nguồn dùng cho lần chuẩn bị

Nguồn duy nhất của bản nghiên cứu là MergeSortCutoff_FromScratch, tức bản làm lại từ đầu đã bàn giao trong chat này. Toàn bộ CHECKSUMS của nguồn đã được kiểm tra trước khi tạo thư mục chuẩn bị riêng. Không nhập project hoặc lịch sử trước lần làm lại.

308 tệp của bản nghiên cứu được giữ nguyên byte và liệt kê trong BASELINE_SHA256.txt, gồm các tệp Java đã đo, kiểm thử gốc, cấu hình, dữ liệu, số đo, báo cáo và demo. README, .gitignore cùng bảng hash/nguồn gốc được cập nhật cho cấu trúc GitHub. Các tệp quản trị repository được thêm mới, không chạy lại phép đo để thay số liệu.

## Nội dung thêm

- .github/workflows/ci.yml: kiểm thử trên JDK 17 và 25, Python 3.12, Node.js 24; chỉ quyền đọc nội dung.
- Mẫu issue và pull request để ghi lỗi hoặc thay đổi có thể tái hiện.
- .gitattributes giữ byte và đánh dấu tài nguyên sinh tự động trong diff.
- .gitignore cho build/cache/dist/môi trường ảo, vẫn giữ CSV và log thí nghiệm.
- README theo cách đọc repository, SUBMISSION cho người chấm, CONTRIBUTING cho việc bảo toàn bằng chứng.
- GITHUB_GUIDE hướng dẫn đăng nhập, tạo repo, push, chạy CI và gắn tag nộp.
- repository_check.py bảo vệ baseline, kiểm tra toàn bộ hash và liên kết điều hướng.
- package_submission.py đóng gói và kiểm tra CRC/SHA-256.
- Bốn kiểm thử Python mới cho công cụ quản trị repository; các kiểm thử thống kê ban đầu được giữ nguyên.
- Makefile cho các lệnh test, verify, check và package.
- .nojekyll và index.html để hỗ trợ lựa chọn Pages thủ công nếu người dùng muốn xuất demo của repository Public.

## Phạm vi thao tác

Chuẩn bị tệp và hướng dẫn cục bộ. Không đăng nhập tài khoản, tạo remote repository, push hoặc bật Pages thay người dùng trong lần này. GitHub CLI chưa được cài trên máy khi kiểm tra, nên hướng dẫn kèm lệnh cài chính thức qua Homebrew.

Các phiên bản action trong workflow được kiểm tra tồn tại qua nguồn chính thức của actions/checkout, setup-java, setup-python và setup-node.

## Kiểm tra bản chuẩn bị

- 308 tệp baseline giữ nguyên SHA-256; cả ba pha thí nghiệm vượt kiểm toán nguồn, dữ liệu, cấu hình và số đo đã lưu.
- 15.693 kiểm tra Java vượt qua trên JDK 25.0.2. Toàn bộ mã Java cũng biên dịch thành công với javac --release 17 -Xlint:all; đây là kiểm tra đích biên dịch, chưa phải chạy bằng runtime JDK 17.
- Tám kiểm thử Python vượt qua, gồm bốn kiểm thử thống kê gốc và bốn kiểm thử mới cho việc bảo vệ baseline và đóng gói repository.
- Viewer vượt kiểm tra 768 tổ hợp, 45 trace và 4.716 bước chuyển. Tệp kết quả viewer được giữ nguyên byte.
- YAML của workflow được kiểm tra trigger, quyền chỉ đọc, ma trận JDK 17/25 và các lệnh kiểm tra. GitHub Actions chưa được chạy trên GitHub; cần xem kết quả ở tab Actions sau khi push.
- Phép thử Git cục bộ đã add, commit và clone đủ 327 tệp, với core.autocrlf=true. Bản clone vượt kiểm tra 326 checksum hiện tại, 43 liên kết điều hướng và kiểm toán ba pha; index CSV có CRLF giữ nguyên byte, working tree sạch sau kiểm tra. Danh tính commit thử và lịch sử Git thử nằm ngoài gói bàn giao.
- Công cụ đóng gói kiểm tra CRC và SHA-256 từng thành viên của ZIP trước khi công bố tệp xuất. Không đưa .git, build, cache hoặc thư mục đo thử vào gói.

Không chạy lại benchmark trong lần chuẩn bị GitHub. Các kết luận hiệu năng vẫn thuộc cấu hình và lần đo đã ghi ngày 13/11/2026.
