# MergeSort Cutoff Lab

Thực nghiệm lựa chọn ngưỡng chuyển sang Insertion sort trong cài đặt MergeSort do sinh viên cung cấp. Project gồm mã Java, công cụ Python, dữ liệu và số đo gốc, báo cáo cùng demo tương tác ngoại tuyến.

**Kết quả đã đo ngày 13/11/2026:** đề xuất CUTOFF 32 cho workload Integer[] trên MacBook Air M3 16 GB, Oracle Java 25.0.2. C32 và C40 chưa phân biệt rõ. Bản chuẩn bị GitHub ngày 19/11/2026 giữ nguyên mã và toàn bộ bằng chứng của bản làm lại từ đầu.

## Đọc nhanh

| Mục đích | Điểm bắt đầu |
|---|---|
| Chấm bài và đối chiếu yêu cầu | [SUBMISSION.md](SUBMISSION.md) |
| Xem báo cáo | [PDF 10 trang](report/Cutoff_Study.pdf), [Word](report/Cutoff_Study.docx), [Markdown](report/Cutoff_Study.md) |
| Xem kết quả thống kê | [Tập xác nhận](measurements/confirm/summary.json), [so sánh ghép cặp](measurements/confirm/paired-effects.csv) |
| Xem thuật toán | [MergeSort.java](src/MergeSort.java) |
| Dùng demo | Tải hoặc clone project, mở [demo/index.html](demo/index.html) bằng trình duyệt |
| Đẩy lên GitHub để nộp | [Hướng dẫn từng bước](docs/GITHUB_GUIDE.md) |
| Xem phạm vi AI | [Công bố AI](docs/AI_DISCLOSURE.md), [log lần làm lại](docs/AI_SESSION_LOG.md), [ghi nhận chuẩn bị GitHub](docs/GITHUB_PREPARATION.md) |

GitHub hiển thị mã nguồn khi mở HTML ở trang Code. Demo chạy khi mở tệp trên máy; hướng dẫn có thêm lựa chọn GitHub Pages nếu muốn một đường dẫn demo online.

## Kết quả trong phạm vi thí nghiệm

| Mốc so sánh | Speedup của C32 | Khoảng bootstrap 95% |
|---|---:|---:|
| C1 | 1.2821 | 1.2703 đến 1.2972 |
| C7 | 1.0653 | 1.0606 đến 1.0706 |
| C10 | 1.0620 | 1.0578 đến 1.0669 |
| C40 | 0.9994 | 0.9968 đến 1.0024 |

Speedup = thời gian mốc / thời gian C32. Trước C10, mức giảm thời gian khoảng 5,83%. Kết luận giới hạn trong cài đặt, dữ liệu và cấu hình đã đo; không khẳng định một cutoff tối ưu duy nhất cho mọi máy.

![Khoảng tin cậy trên tập xác nhận](report/charts/final_intervals.png)

Ba pha được chốt trước: sàng lọc 69 ngưỡng → chọn trong ba đại diện trên tập mới → xác nhận lựa chọn đã đóng băng. Có **180 mảng CSV, 91.500 quan sát batch và 126.225 sort trong vùng đo**. Seed và kích thước tách biệt giữa ba pha; giữ mọi quan sát, kể cả các quan sát chậm.

## Cấu trúc repository

```text
mergesort-cutoff-lab/
├── .github/
│   ├── workflows/ci.yml         # Kiểm tra trên JDK 17 và 25
│   ├── ISSUE_TEMPLATE/          # Mẫu báo lỗi
│   └── pull_request_template.md
├── src/                        # MergeSort nguyên bản và harness đo Java
├── tests/                      # Kiểm thử Java, Python và viewer
├── labcore/                    # Sinh dữ liệu, đo, thống kê, kiểm toán, báo cáo
├── tools/                      # Ghi trace, kiểm tra repo, đóng gói
├── datasets/                   # 180 mảng CSV cùng index và hash
│   ├── screen/
│   ├── choose/
│   └── confirm/
├── measurements/               # Raw CSV, thống kê, metadata, log và snapshot
├── report/                     # PDF, DOCX, Markdown và bốn đồ thị
├── demo/                       # HTML/CSS/JS; trace được nhúng sẵn
├── docs/                       # Giao thức, nguồn gốc, log AI và hướng dẫn
├── cutofflab.py                # Điểm vào CLI của thí nghiệm
├── study.json                  # Giao thức ba pha đã định trước
├── SUBMISSION.md               # Mục lục sản phẩm nộp
├── CONTRIBUTING.md             # Cách chỉnh sửa metadata và kiểm tra lại
├── Makefile                    # Các lệnh tắt trên macOS/Linux
├── index.html                  # Điểm vào demo nếu bật GitHub Pages
├── .gitattributes              # Giữ byte để bảo toàn SHA-256
├── .gitignore                  # Loại build/cache; giữ dữ liệu và log thí nghiệm
├── CHECKSUMS.txt               # Hash của bản repository hiện tại
└── CREATION_LEDGER.csv          # Nguồn tạo của từng tệp
```

Các đường dẫn của thí nghiệm được giữ nguyên để báo cáo, demo và metadata tiếp tục khớp. [Baseline SHA-256](docs/BASELINE_SHA256.txt) bảo vệ 308 tệp của bản làm lại; các tệp quản trị GitHub được bổ sung riêng.

## Kiểm tra trên máy

Cần JDK 17+, Python 3.10+ và Node.js 22+ để chạy đủ các kiểm tra. Đo, phân tích và xác minh dùng thư viện chuẩn; Node chỉ dùng các module có sẵn.

```sh
python3 cutofflab.py test
python3 -m unittest discover -s tests -p 'test_*.py' -v
node --test tests/test_viewer.cjs
python3 cutofflab.py verify
python3 tools/repository_check.py check
```

Hoặc trên macOS/Linux:

```sh
make check
```

Kiểm thử gồm 15.693 kiểm tra Java, các ca thống kê và quản lý repository, cùng 768 tổ hợp viewer với 4.716 bước chuyển. [Workflow CI](.github/workflows/ci.yml) chạy khi push main, mở pull request hoặc được chạy thủ công. CI kiểm tra tính đúng và dữ liệu đã lưu, giữ nguyên số đo máy M3; không dùng thời gian trên runner để thay kết quả báo cáo.

## Đo lại trên máy khác

```sh
python3 cutofflab.py study --new-run lan_do_moi
```

Phiên mới được tạo dưới reruns/ và chạy đủ ba pha. Thư mục này được Git bỏ qua để dữ liệu thử không lẫn vào bản nộp đã chốt. Muốn công bố một phiên đo khác, cần mô tả riêng cấu hình và phạm vi kết luận.

```java
Integer[] data = {8, 3, 7, 3, 1};
MergeSort.sort(data, 32);
```

Chỉ src/MergeSort.java được giữ nguyên từ mã người dùng cung cấp trong lần làm lại. Xem [ORIGIN.json](docs/ORIGIN.json), [yêu cầu sản phẩm](docs/REQUIREMENTS.md) và [hướng dẫn bảo vệ](docs/DEFENSE_NOTES.md).

## Dựng lại báo cáo và demo

PDF và demo có sẵn để mở. Dựng lại demo bằng:

```sh
python3 cutofflab.py demo
```

Muốn dựng Word và bốn đồ thị, cài các gói trong [doc-build-requirements.txt](doc-build-requirements.txt), rồi chạy `python3 cutofflab.py report`; xuất DOCX sang PDF bằng Word hoặc LibreOffice. Phiên bản thư viện gốc nằm trong [BUILD_ENVIRONMENT.json](docs/BUILD_ENVIRONMENT.json). Việc dựng lại có thể thay byte của sản phẩm sinh tự động, nên thực hiện trong bản làm việc riêng khi muốn giữ nguyên bản nộp.

## Đóng gói và bảo toàn dữ liệu

```sh
python3 tools/package_submission.py
```

ZIP được tạo trong dist/, có kiểm tra CRC và SHA-256, không gồm lịch sử Git, build, cache hoặc lượt đo thử. Sau khi chỉnh tài liệu hay cấu hình GitHub, cập nhật bảng hash bằng `python3 tools/repository_check.py refresh`. Lệnh này từ chối cập nhật nếu bằng chứng trong baseline đã thay đổi.

Thông tin bìa vẫn để trống theo lựa chọn trước đó. Phạm vi kiểm tra demo và báo cáo được ghi tại [VALIDATION.md](docs/VALIDATION.md); logic viewer đã kiểm tra, bố cục trình duyệt chưa được kiểm tra trực tiếp do giới hạn công cụ ở phiên dựng bản gốc.
