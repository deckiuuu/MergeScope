# Đưa project lên GitHub để nộp

Hướng dẫn dùng thư mục chứa README.md, cutofflab.py và .github/. Gói này được chuẩn bị từ bản làm lại từ đầu, giữ nguyên thí nghiệm ngày 13/11/2026. Các bước bên dưới tạo và đẩy repository bằng tài khoản của chính bạn.

## 1 Chuẩn bị thư mục trên máy

Dùng thư mục MergeSortCutoff_GitHub đã chuẩn bị hoặc giải nén gói ZIP. Mở Terminal tại thư mục gốc project; các thư mục src, datasets, measurements, report, demo và .github cần nằm ngay ở cấp này.

Trên máy hiện tại, đường dẫn bản chuẩn bị là:

```sh
cd "/Users/wicckyy/Documents/Codex/2026-11-13/a/outputs/MergeSortCutoff_GitHub"
```

Nếu đã giải nén ở nơi khác, đổi đường dẫn cd tương ứng. Các tệp bên trong thư mục là nội dung cần commit, để GitHub hiển thị README, mã nguồn và workflow ngay từ gốc repository.

## 2 Đăng nhập GitHub trên macOS

Máy hiện tại có Git và Homebrew; GitHub CLI chưa được cài khi chuẩn bị gói. Cài CLI bằng lệnh chính thức cho Homebrew:

```sh
brew install gh
```

Đây là cách cài được mô tả trong [tài liệu GitHub CLI cho macOS](https://github.com/cli/cli/blob/trunk/docs/install_macos.md).

Đăng nhập qua trình duyệt và cấu hình Git dùng thông tin đăng nhập đó:

```sh
gh auth login --hostname github.com --git-protocol https --web --scopes workflow
gh auth setup-git
```

Làm theo mã xác nhận và trang đăng nhập mà CLI hiển thị. Scope workflow phục vụ push tệp .github/workflows/ci.yml. Việc đăng nhập thực hiện trên máy bạn qua GitHub; không cần gửi token hoặc mật khẩu vào chat. Các tùy chọn đăng nhập được mô tả trong [gh auth login](https://cli.github.com/manual/gh_auth_login).

## 3 Tạo commit đầu tiên

Từ thư mục gốc project:

```sh
git init -b main
python3 tools/repository_check.py check
git add .
git status --short
git commit -m "Submit MergeSort cutoff experiment"
```

Đây là quy trình Git cho [mã nguồn đã có trên máy](https://docs.github.com/en/migrations/importing-source-code/using-the-command-line-to-import-source-code/adding-locally-hosted-code-to-github). .gitignore đã giữ lại CSV và log thực nghiệm, đồng thời loại build, cache, môi trường ảo, dist và reruns.

Nếu Git báo Author identity unknown, đặt danh tính riêng cho repository này rồi chạy lại commit:

```sh
git config user.name "HO_TEN_CUA_BAN"
git config user.email "EMAIL_GITHUB_CUA_BAN"
git commit -m "Submit MergeSort cutoff experiment"
```

Thay hai giá trị bằng thông tin của bạn. Các lệnh không có --global nên chỉ áp dụng cho repository hiện tại.

## 4 Tạo repository và push

Cách dễ theo dõi là dùng chế độ hỏi đáp:

```sh
gh repo create
```

Chọn lần lượt:

1. Push an existing local repository to GitHub.
2. Local repository: dấu chấm hoặc đường dẫn thư mục hiện tại.
3. Repository name: mergesort-cutoff-lab, hoặc tên giảng viên yêu cầu.
4. Description: Thực nghiệm CUTOFF cho MergeSort với dữ liệu, báo cáo và demo.
5. Chọn Public hoặc Private theo quy định nộp bài. Nếu chọn Private, cấp quyền đọc cho giảng viên.
6. Thêm remote origin và đồng ý push các commit.

GitHub CLI hỗ trợ tạo repository từ nguồn cục bộ và push commit như mô tả trong [gh repo create](https://cli.github.com/manual/gh_repo_create).

Nếu đã quyết định dùng Public và muốn chạy một lệnh:

```sh
gh repo create mergesort-cutoff-lab --public --source=. --remote=origin --push
```

Với Private, thay --public bằng --private. Chỉ dùng một trong các cách tạo repo, tránh tạo trùng tên.

Nếu bạn đã tạo một repository trống trên trang GitHub, dùng remote của repository đó:

```sh
git remote add origin https://github.com/TEN_GITHUB/mergesort-cutoff-lab.git
git push -u origin main
```

Thay TEN_GITHUB và tên repo bằng thông tin thật. Repository tạo trên web nên để trống các tùy chọn sinh README, .gitignore và license, vì nội dung project đã có sẵn để commit.

## 5 Kiểm tra sau khi push

Mở URL repository mà CLI trả về. Kiểm tra:

- README và SUBMISSION hiển thị ở gốc.
- Báo cáo trong report/, dữ liệu trong datasets/, số đo trong measurements/ và log AI trong docs/ đều có.
- Tab Actions có workflow Verify submission; chờ cả JDK 17 và JDK 25 hoàn tất.
- Nếu lỗi, mở log của bước thất bại và sửa theo thông báo. Chưa có kết quả chạy Actions trên GitHub tại thời điểm đóng gói; các lệnh tương ứng được kiểm tra trên máy chuẩn bị.

CI kiểm thử thuật toán, thống kê, viewer, hash baseline và số đo đã lưu. Nó giữ nguyên metadata máy M3, không ghi đè kết quả bằng một benchmark chạy trên runner khác.

## 6 Chốt đúng phiên bản nộp

Khi commit đã sẵn sàng, tạo tag cho phiên bản nộp:

```sh
git tag -a submission-v1 -m "Submission version 1"
git push origin submission-v1
```

Nộp URL repository hoặc URL của tag theo yêu cầu giảng viên. Có thể kèm link report/Cutoff_Study.pdf và SUBMISSION.md để người chấm mở nhanh. Nếu sửa tiếp sau đó, tag submission-v1 vẫn chỉ đúng commit đã chốt.

Nếu cần ZIP để nộp thêm:

```sh
python3 tools/package_submission.py
```

File xuất ở dist/mergesort-cutoff-submission.zip, được kiểm tra CRC và hash từng tệp. dist/ được Git bỏ qua.

## 7 Demo online bằng GitHub Pages nếu muốn

Phần này dành cho repository Public mà bạn muốn công bố demo trên web. Cấu hình đã chuẩn bị không tự bật Pages.

1. Mở Settings của repository, vào Pages.
2. Source: Deploy from a branch.
3. Branch: main; thư mục /(root); chọn Save.
4. Đợi lần triển khai Pages hoàn tất. Mở URL Pages do GitHub hiển thị và thêm /demo/ ở cuối.

Ví dụ đường dẫn dự án cá nhân: `https://TEN_GITHUB.github.io/mergesort-cutoff-lab/demo/`. Tệp .nojekyll đã có để giữ nội dung tĩnh. Vì xuất từ root, các liên kết PDF và README tương đối của demo tiếp tục có đích. Xem [cấu hình nguồn GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

Bạn cũng có thể chạy demo ngoại tuyến sau khi clone hoặc tải project bằng cách mở demo/index.html. Mở file HTML ở tab Code trên GitHub sẽ hiển thị mã nguồn.

## 8 Các tình huống thường gặp

**remote origin already exists:** kiểm tra `git remote -v`; nếu cần sửa URL, dùng `git remote set-url origin URL_REPO_CUA_BAN`.

**src refspec main does not match any:** kiểm tra đã tạo commit đầu tiên thành công và nhánh hiện tại là main.

**GitHub từ chối cập nhật workflow:** bổ sung quyền bằng `gh auth refresh --hostname github.com --scopes workflow`, xác nhận trên GitHub rồi push lại.

**Checksum lệch sau khi đưa qua Git:** giữ .gitattributes trước lần git add đầu tiên. Một số index CSV có CRLF; tự đổi LF/CRLF sẽ làm sai hash. [Tài liệu Git](https://git-scm.com/docs/gitattributes) xác nhận -text tắt chuyển đổi xuống dòng khi commit và checkout.

**Đã sửa README hoặc hướng dẫn:** chạy `python3 tools/repository_check.py refresh`, rồi kiểm tra và commit thay đổi. Nếu baseline báo sai, cần đối chiếu lại bản thí nghiệm; refresh sẽ không ghi nhận các thay đổi ấy như dữ liệu gốc.

## Dung lượng

Bản chuẩn bị có tệp lớn nhất dưới 2 MiB. Tất cả dữ liệu thực nghiệm được đưa trực tiếp vào Git. Giới hạn hiện được GitHub công bố là cảnh báo trên 50 MiB và chặn trên 100 MiB cho mỗi tệp; tải một tệp qua web có giới hạn 25 MiB. Xem [giới hạn tệp của GitHub](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).
