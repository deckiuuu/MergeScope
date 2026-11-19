# Giao thức đã chốt trước khi đo

Nguồn máy đọc là study.json. Hash của tệp này được ghi trong evidence.json ở cả ba pha. Bản mô tả này giúp đọc nhanh quy trình; không thay dữ liệu cấu hình.

- Sàng lọc: 69 cutoff; bốn độ dài; ba seed; năm phân phối; ba JVM nối tiếp; năm vòng đo.
- Shortlist: chỉ dùng đại diện nhỏ nhất của mỗi chữ ký cây, lấy ba đại diện có điểm thấp nhất. Không gộp số đo của các cutoff tương đương vào thêm trọng số.
- Chọn: ba ứng viên đã chốt cùng mốc 1, 7, 10, 128; bốn N và ba seed mới; năm JVM; bảy vòng. Chọn đại diện có điểm thấp nhất trong shortlist.
- Xác nhận: giữ ứng viên thắng đã đóng băng; dùng bốn N và ba seed mới khác cả hai pha trước; năm JVM; bảy vòng.
- Dừng: đúng ba pha bất kể thứ hạng cuối. Không chọn lại bằng tập xác nhận và không thêm lượt tới khi được kết quả ưa thích.
- Thời gian: chỉ MergeSort.sort, có cấp phát aux; khôi phục input và oracle ngoài đồng hồ. Một batch là một quan sát.
- Điểm: median từng khối qua vòng, tỷ số ghép cặp với C1, trung bình nhân đều theo phân phối, N, seed và JVM.
- Độ tin cậy: 4.000 bootstrap theo JVM rồi seed; ma trận phân phối × N giữ cố định; khoảng từng cặp.
- Gần tối ưu: chậm hơn điểm tốt nhất không quá 3%, một quy ước thực dụng được định trước.

SHA-256 study.json: 7c02a5690a1bfa06ff93be5d6cb9b6348923072b368385685a8db88b56ac86b4
