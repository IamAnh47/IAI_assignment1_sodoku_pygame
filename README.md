# Sudoku Solver với Pygame

Giải bài toán Sudoku sử dụng hai thuật toán chính: DFS (Depth-First Search) và MRV (Minimum Remaining Values).


## Giới Thiệu

Dự án được hiên thực bởi nhóm BTL_TTNT_HK242
---

## Thuật toán
Quy tắc: không lặp lại trong cùng hàng, cột và khối 3x3
### DFS

### MRV
- Quét bảng và xác định ô trống:
Duyệt qua toàn bộ bảng Sudoku để tìm các ô trống (ô có giá trị 0).

- Tính số lựa chọn hợp lệ cho mỗi ô trống:
Với mỗi ô trống, kiểm tra các giá trị từ 1 đến 9 có thể điền vào mà không vi phạm quy tắc. Đếm số lượng các giá trị hợp lệ đó.

- Chọn ô có ít lựa chọn nhất:
Ô trống có số lựa chọn hợp lệ ít nhất được coi là "ô khó nhất" và ưu tiên giải trước. 
=> Nếu ô chỉ có một vài lựa chọn, nếu bị sai sẽ nhanh chóng phát hiện -> giúp quá trình giải đệ quy hiệu quả hơn.

- Thử từng giá trị khả thi:
Với ô đã chọn, lần lượt điền từng giá trị hợp lệ, sau đó đệ quy giải phần còn lại.

- Quay lui nếu cần:
Nếu việc điền giá trị không dẫn đến lời giải (tức đệ quy trả về fail), backtracking bằng cách đặt lại ô đó về giá trị trống và thử giá trị khác.

- Hoàn thành nếu không còn ô trống:
Nếu không còn ô trống nào, Sudoku đã xong.
---

## Cài Đặt

### Yêu Cầu
- Python 3
- Pygame

### Cài Đặt Thư Viện
Chạy lệnh sau để cài đặt Pygame:
```bash
pip install pygame
```
### Chạy dự án
```bash
python main.py
```