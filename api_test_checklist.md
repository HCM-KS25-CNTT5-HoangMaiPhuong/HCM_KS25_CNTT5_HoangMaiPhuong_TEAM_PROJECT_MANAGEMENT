# API Test Checklist (Swagger/Postman)

Checklist này bao phủ các luồng chính của ứng dụng, bao gồm cả các case thành công (happy path) và các case lỗi (edge/error cases) cho từng endpoint.

> [!TIP]
> **Hướng dẫn chung:**
> - Các request yêu cầu xác thực cần truyền `Authorization: Bearer <access_token>` trong Header.
> - Các case lỗi chung như `401 Unauthorized` (chưa đăng nhập/token hết hạn) và `422 Unprocessable Entity` (truyền sai format dữ liệu) áp dụng cho hầu hết các API và được ngầm hiểu.

## 1. Authentication (Xác thực)

### 1.1 POST `/auth/register` (Đăng ký tài khoản)
- [ ] **Case đúng (201 Created):** Truyền đúng format `email` (chưa tồn tại) và `password`.
- [ ] **Case lỗi (400 Bad Request):** Đăng ký với `email` đã tồn tại trong hệ thống.
- [ ] **Case lỗi (422 Unprocessable Entity):** Truyền thiếu trường (ví dụ thiếu email hoặc password), hoặc email sai định dạng.

### 1.2 POST `/auth/login` (Đăng nhập)
- [ ] **Case đúng (200 OK):** Truyền đúng `email` và `password` đã đăng ký. Kiểm tra response trả về `access_token` và `refresh_token`.
- [ ] **Case lỗi (401 Unauthorized / 400 Bad Request):** Truyền sai mật khẩu.
- [ ] **Case lỗi (404 Not Found / 400 Bad Request):** Truyền email không tồn tại trong hệ thống.

---

## 2. Users (Người dùng)

### 2.1 GET `/users/me` (Lấy thông tin cá nhân)
- [ ] **Case đúng (200 OK):** Truyền hợp lệ Access Token trong Header. Kiểm tra thông tin trả về khớp với người dùng đang đăng nhập.
- [ ] **Case lỗi (401 Unauthorized):** Không truyền token hoặc token không hợp lệ/đã hết hạn.

### 2.2 GET `/users` (Lấy danh sách người dùng)
- [ ] **Case đúng (200 OK):** Đăng nhập với tài khoản có role `admin`. Kiểm tra danh sách trả về.
- [ ] **Case đúng (200 OK) - Có filter:** Test các filter `keyword` (tìm theo tên, email) và `is_active` (true/false).
- [ ] **Case lỗi (403 Forbidden):** Đăng nhập với tài khoản role `user` (không phải admin) và gọi API.

---

## 3. Projects (Dự án)

### 3.1 POST `/projects` (Tạo Project mới)
- [ ] **Case đúng (201 Created):** Truyền `name` và `description`. Kiểm tra project được tạo, người tạo tự động trở thành `OWNER`.
- [ ] **Case lỗi (422 Unprocessable Entity):** Tên project rỗng hoặc vượt quá 255 ký tự.
- [ ] **Case lỗi (401 Unauthorized):** Chưa đăng nhập.

### 3.2 GET `/projects` (Lấy danh sách Project)
- [ ] **Case đúng (200 OK):** Gọi API để lấy danh sách. Đảm bảo chỉ trả về các project mà user đang đăng nhập có tham gia (là OWNER hoặc MEMBER).
- [ ] **Case đúng (200 OK) - Tìm kiếm:** Truyền query `name` để tìm kiếm project theo tên.

### 3.3 GET `/projects/{project_id}` (Chi tiết Project)
- [ ] **Case đúng (200 OK):** User nằm trong project gọi API với `project_id` hợp lệ.
- [ ] **Case lỗi (403 Forbidden):** User không tham gia project này cố tình gọi để xem.
- [ ] **Case lỗi (404 Not Found):** Truyền `project_id` không tồn tại.

### 3.4 PATCH `/projects/{project_id}` (Cập nhật Project)
- [ ] **Case đúng (200 OK):** User là `OWNER` cập nhật `name` hoặc `description`.
- [ ] **Case lỗi (403 Forbidden):** User là `MEMBER` (hoặc người ngoài) cố tình cập nhật.
- [ ] **Case lỗi (404 Not Found):** Cập nhật `project_id` không tồn tại.

### 3.5 DELETE `/projects/{project_id}` (Xóa Project)
- [ ] **Case đúng (200 OK):** User là `OWNER` xóa project thành công.
- [ ] **Case lỗi (403 Forbidden):** User là `MEMBER` (hoặc người ngoài) cố tình xóa.

---

## 4. Project Members (Thành viên dự án)

### 4.1 POST `/projects/{project_id}/members` (Thêm thành viên)
- [ ] **Case đúng (201 Created):** `OWNER` thêm một `user_id` hợp lệ vào dự án.
- [ ] **Case lỗi (400/409 Conflict):** `user_id` đã là thành viên của project.
- [ ] **Case lỗi (404 Not Found):** `user_id` không tồn tại trong hệ thống.
- [ ] **Case lỗi (403 Forbidden):** `MEMBER` cố tình thêm thành viên.

### 4.2 GET `/projects/{project_id}/members` (Danh sách thành viên)
- [ ] **Case đúng (200 OK):** Bất kỳ thành viên nào trong project đều có thể xem danh sách thành viên.
- [ ] **Case lỗi (403 Forbidden):** Người dùng không thuộc project gọi API.

### 4.3 DELETE `/projects/{project_id}/members/{user_id}` (Xóa thành viên)
- [ ] **Case đúng (200 OK):** `OWNER` xóa một `MEMBER` thành công.
- [ ] **Case lỗi (400 Bad Request / 403 Forbidden):** `OWNER` tự xóa chính mình.
- [ ] **Case lỗi (403 Forbidden):** `MEMBER` cố tình xóa thành viên khác.
- [ ] **Case lỗi (404 Not Found):** `user_id` không nằm trong project.

---

## 5. Tasks (Công việc)

### 5.1 POST `/projects/{project_id}/tasks` (Tạo Task mới)
- [ ] **Case đúng (201 Created):** `OWNER` tạo task với `title`, `priority` và các trường tuỳ chọn hợp lệ.
- [ ] **Case lỗi (403 Forbidden):** `MEMBER` cố tình tạo task.
- [ ] **Case lỗi (422 Unprocessable Entity):** Truyền `priority` không đúng Enum (ví dụ: LOW, MEDIUM, HIGH).

### 5.2 GET `/projects/{project_id}/tasks` (Danh sách Task)
- [ ] **Case đúng (200 OK):** Thành viên project lấy danh sách task.
- [ ] **Case đúng (200 OK) - Bộ lọc & Phân trang:** Test lọc theo `task_status`, `priority`, `assignee`, `title`. Test phân trang (`limit`, `offset`) và sắp xếp (`sort_by`, `sort_order`).
- [ ] **Case lỗi (403 Forbidden):** Người dùng không thuộc project gọi API.

### 5.3 GET `/tasks/{task_id}` (Chi tiết Task)
- [ ] **Case đúng (200 OK):** Thành viên thuộc project của task xem chi tiết task.
- [ ] **Case lỗi (403 Forbidden):** Người dùng không thuộc project của task gọi API xem chi tiết.
- [ ] **Case lỗi (404 Not Found):** Truyền `task_id` không tồn tại.

### 5.4 POST `/tasks/{task_id}/assign` (Phân công Task)
- [ ] **Case đúng (200 OK):** `OWNER` phân công task cho một `assignee_id` thuộc project.
- [ ] **Case lỗi (400 Bad Request):** Phân công cho `assignee_id` không phải là thành viên của project.
- [ ] **Case lỗi (403 Forbidden):** `MEMBER` cố tình đổi người được phân công.
- [ ] **Case lỗi (404 Not Found):** Truyền `task_id` hoặc `assignee_id` không tồn tại.

### 5.5 PATCH `/tasks/{task_id}` (Cập nhật Task)
- [ ] **Case đúng (200 OK):** `OWNER` cập nhật trạng thái (`status`), `title`, `priority`, v.v.
- [ ] **Case lỗi (403 Forbidden):** `MEMBER` cố tình cập nhật task.
- [ ] **Case lỗi (404 Not Found):** Truyền `task_id` không tồn tại.

### 5.6 DELETE `/tasks/{task_id}` (Xóa Task)
- [ ] **Case đúng (200 OK):** `OWNER` xóa task.
- [ ] **Case lỗi (403 Forbidden):** `MEMBER` cố tình xóa task.
