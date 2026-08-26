# API Test Checklist (Swagger/Postman)

Checklist này bao phủ các luồng chính của ứng dụng, bao gồm cả các case thành công (happy path) và các case lỗi (edge/error cases) cho từng endpoint. Đã được bổ sung thêm các ID và JSON tham khảo dựa trên dữ liệu mẫu từ `seed_data.py`.

> [!TIP]
> **Hướng dẫn chung:**
> - Các request yêu cầu xác thực cần truyền `Authorization: Bearer <access_token>` trong Header.
> - Các case lỗi chung như `401 Unauthorized` (chưa đăng nhập/token hết hạn) và `422 Unprocessable Entity` (truyền sai format dữ liệu) áp dụng cho hầu hết các API và được ngầm hiểu.

---

### Thông tin Dữ liệu Mẫu (từ `seed_data.py`)
- **Users:**
  - `id=1`: admin@example.com / admin123 (ADMIN)
  - `id=2`: user1@example.com / user123 (USER)
  - `id=3`: user2@example.com / user123 (USER)
  - `id=4`: user3@example.com / user123 (USER - Chưa tham gia project nào, dùng để test add member)
- **Projects:**
  - `id=1`: Dự án Alpha (Owner: admin `id=1`, Member: user1 `id=2`, user2 `id=3`)
  - `id=2`: Dự án Beta (Owner: user1 `id=2`, Member: user2 `id=3`)
- **Tasks:**
  - `id=1..3` thuộc Project Alpha (id=1)
  - `id=4..5` thuộc Project Beta (id=2)

---

## 1. Authentication (Xác thực)

### 1.1 POST `/auth/register` (Đăng ký tài khoản)
- [ ] **Case đúng (201 Created):** 
  ```json
  {
    "email": "newuser@example.com",
    "password": "password123",
    "full_name": "Người dùng Mới"
  }
  ```
- [ ] **Case lỗi (409 Conflict):** Đăng ký với email đã tồn tại (vd: `admin@example.com`).
  ```json
  {
    "email": "admin@example.com",
    "password": "password123",
    "full_name": "Người dùng Mới"
  }
  ```
- [ ] **Case lỗi (422 Unprocessable Entity):** Thiếu trường hoặc email sai định dạng (vd: `email: "not-an-email"`).
  ```json
  {
    "email": "not-an-email",
    "password": "password123"
  }
  ```

### 1.2 POST `/auth/login` (Đăng nhập)
- [ ] **Case đúng (200 OK):** 
  ```json
  {
    "email": "admin@example.com",
    "password": "admin123"
  }
  ```
- [ ] **Case lỗi (401 Unauthorized):** Truyền sai mật khẩu (vd: `admin@example.com` / `wrongpass`).
  ```json
  {
    "email": "admin@example.com",
    "password": "wrongpass"
  }
  ```
- [ ] **Case lỗi (401 Unauthorized):** Email không tồn tại (`notexist@example.com`).
  ```json
  {
    "email": "notexist@example.com",
    "password": "admin123"
  }
  ```

---

## 2. Users (Người dùng)

### 2.1 GET `/users/me` (Lấy thông tin cá nhân)
- [ ] **Case đúng (200 OK):** Lấy token của `admin@example.com` gọi API, trả về ID 1.
  > *(Đăng nhập lấy token)*
  > ```json
  > {"email": "admin@example.com", "password": "admin123"}
  > ```
- [ ] **Case lỗi (401 Unauthorized):** Không truyền token.

### 2.2 GET `/users` (Lấy danh sách người dùng)
- [ ] **Case đúng (200 OK):** Dùng token của `admin@example.com` gọi API.
  > *(Đăng nhập lấy token)*
  > ```json
  > {"email": "admin@example.com", "password": "admin123"}
  > ```
- [ ] **Case đúng (200 OK) - Có filter:** Thêm param `?keyword=admin&is_active=true`.
- [ ] **Case lỗi (403 Forbidden):** Dùng token của `user1@example.com` (role USER).
  > *(Đăng nhập lấy token)*
  > ```json
  > {"email": "user1@example.com", "password": "user123"}
  > ```

---

## 3. Projects (Dự án)

### 3.1 POST `/projects` (Tạo Project mới)
- [ ] **Case đúng (201 Created):** Dùng token của `user1@example.com`:
  > *(Đăng nhập lấy token)*
  > ```json
  > {"email": "user1@example.com", "password": "user123"}
  > ```
  ```json
  {
    "name": "Dự án Gamma",
    "description": "Dự án mới tạo để test"
  }
  ```
- [ ] **Case lỗi (422 Unprocessable Entity):** `"name": ""` (tên rỗng).
  ```json
  {
    "name": "",
    "description": "Dự án mới tạo để test"
  }
  ```

### 3.2 GET `/projects` (Lấy danh sách Project)
- [ ] **Case đúng (200 OK):** Dùng token của `user1@example.com` -> sẽ thấy Alpha và Beta.
  > *(Đăng nhập lấy token)*
  > ```json
  > {"email": "user1@example.com", "password": "user123"}
  > ```
- [ ] **Case đúng (200 OK) - Tìm kiếm:** Gửi query `?name=Alpha`.

### 3.3 GET `/projects/{project_id}` (Chi tiết Project)
- [ ] **Case đúng (200 OK):** Dùng token của `admin@example.com`, GET `/projects/1`.
  > *(Đăng nhập lấy token)*
  > ```json
  > {"email": "admin@example.com", "password": "admin123"}
  > ```
- [ ] **Case lỗi (403 Forbidden):** Dùng token của `user3@example.com` (chưa vào project 1), GET `/projects/1`.
  > *(Đăng nhập lấy token)*
  > ```json
  > {"email": "user3@example.com", "password": "user123"}
  > ```
- [ ] **Case lỗi (404 Not Found):** GET `/projects/999`.

### 3.4 PATCH `/projects/{project_id}` (Cập nhật Project)
- [ ] **Case đúng (200 OK):** Dùng token của `admin@example.com` (Owner), PATCH `/projects/1`:
  > *(Đăng nhập lấy token)*
  > ```json
  > {"email": "admin@example.com", "password": "admin123"}
  > ```
  ```json
  {
    "name": "Dự án Alpha (Cập nhật)"
  }
  ```
- [ ] **Case lỗi (403 Forbidden):** Dùng token của `user1@example.com` (Member, không phải Owner), PATCH `/projects/1`.
  > *(Đăng nhập lấy token)*
  > ```json
  > {"email": "user1@example.com", "password": "user123"}
  > ```
  ```json
  {
    "name": "Dự án Alpha (Thử cập nhật)"
  }
  ```

### 3.5 DELETE `/projects/{project_id}` (Xóa Project)
- [ ] **Case đúng (200 OK):** Dùng token của `admin@example.com` (Owner), DELETE `/projects/1` (Soft delete sẽ thành công, get lại `/projects/1` sẽ ra 404).
  > *(Đăng nhập lấy token)*
  > ```json
  > {"email": "admin@example.com", "password": "admin123"}
  > ```
- [ ] **Case lỗi (403 Forbidden):** Dùng token của `user1@example.com` (Member), DELETE `/projects/1`.
  > *(Đăng nhập lấy token)*
  > ```json
  > {"email": "user1@example.com", "password": "user123"}
  > ```

---

## 4. Project Members (Thành viên dự án)

### 4.1 POST `/projects/{project_id}/members` (Thêm thành viên)
- [ ] **Case đúng (201 Created):** Dùng token của `admin@example.com` (Owner project 1), POST `/projects/1/members`:
  > *(Đăng nhập lấy token)*
  > ```json
  > {"email": "admin@example.com", "password": "admin123"}
  > ```
  ```json
  {
    "user_id": 4
  }
  ```
  *(user_id 4 là user3@example.com chưa có trong nhóm)*
- [ ] **Case lỗi (400 Bad Request):** Thêm người đã có: `{"user_id": 2}`.
  ```json
  {
    "user_id": 2
  }
  ```
- [ ] **Case lỗi (403 Forbidden):** Dùng token của `user1@example.com` (Member) gọi API này.
  > *(Đăng nhập lấy token)*
  > ```json
  > {"email": "user1@example.com", "password": "user123"}
  > ```
  ```json
  {
    "user_id": 4
  }
  ```

### 4.2 GET `/projects/{project_id}/members` (Danh sách thành viên)
- [ ] **Case đúng (200 OK):** Dùng token của `user1@example.com` (Member project 1), GET `/projects/1/members`.
  > *(Đăng nhập lấy token)*
  > ```json
  > {"email": "user1@example.com", "password": "user123"}
  > ```

### 4.3 DELETE `/projects/{project_id}/members/{user_id}` (Xóa thành viên)
- [ ] **Case đúng (200 OK):** Dùng token của `admin@example.com` (Owner project 1), DELETE `/projects/1/members/3` (Xóa user2).
  > *(Đăng nhập lấy token)*
  > ```json
  > {"email": "admin@example.com", "password": "admin123"}
  > ```
- [ ] **Case lỗi (400 Bad Request):** `admin` tự xóa chính mình: DELETE `/projects/1/members/1`.
- [ ] **Case lỗi (403 Forbidden):** `user1` (Member) tự ý đi xóa `user2`: DELETE `/projects/1/members/3`.

---

## 5. Tasks (Công việc)

### 5.1 POST `/projects/{project_id}/tasks` (Tạo Task mới)
- [ ] **Case đúng (201 Created):** Dùng token của `admin@example.com` (Owner project 1), POST `/projects/1/tasks`:
  > *(Đăng nhập lấy token)*
  > ```json
  > {"email": "admin@example.com", "password": "admin123"}
  > ```
  ```json
  {
    "title": "Task mới tinh",
    "description": "Nội dung task",
    "priority": "MEDIUM",
    "status": "TODO"
  }
  ```
- [ ] **Case lỗi (403 Forbidden):** Dùng token của `user1@example.com` (Member project 1), cố tình POST tạo task.
  > *(Đăng nhập lấy token)*
  > ```json
  > {"email": "user1@example.com", "password": "user123"}
  > ```
  ```json
  {
    "title": "Task mới tinh",
    "description": "Nội dung task",
    "priority": "MEDIUM",
    "status": "TODO"
  }
  ```

### 5.2 GET `/projects/{project_id}/tasks` (Danh sách Task)
- [ ] **Case đúng (200 OK):** Lấy danh sách task cho Project 1. GET `/projects/1/tasks`.
- [ ] **Case đúng (200 OK) - Bộ lọc & Phân trang:** GET `/projects/1/tasks?task_status=IN_PROGRESS&priority=HIGH&limit=5`.

### 5.3 GET `/tasks/{task_id}` (Chi tiết Task)
- [ ] **Case đúng (200 OK):** GET `/tasks/1`.
- [ ] **Case lỗi (403 Forbidden):** `user3` (không thuộc project 1) GET `/tasks/1`.

### 5.4 PATCH `/tasks/{task_id}` (Cập nhật Task & Phân công)
- [ ] **Case đúng (200 OK):** Token `admin@example.com` (Owner), PATCH `/tasks/1` (Vừa sửa trạng thái vừa chuyển người thực hiện):
  > *(Đăng nhập lấy token)*
  > ```json
  > {"email": "admin@example.com", "password": "admin123"}
  > ```
  ```json
  {
    "status": "DONE",
    "priority": "LOW",
    "assignee_id": 2
  }
  ```
- [ ] **Case lỗi (400 Bad Request):** Phân công cho `assignee_id: 4` (user 4 chưa nằm trong Project 1).
  ```json
  {
    "assignee_id": 4
  }
  ```
- [ ] **Case lỗi (403 Forbidden):** Token `user1@example.com` (Member), PATCH `/tasks/1`.
  > *(Đăng nhập lấy token)*
  > ```json
  > {"email": "user1@example.com", "password": "user123"}
  > ```
  ```json
  {
    "status": "DONE"
  }
  ```

### 5.5 DELETE `/tasks/{task_id}` (Xóa Task)
- [ ] **Case đúng (200 OK):** Token `admin@example.com`, DELETE `/tasks/1`.
  > *(Đăng nhập lấy token)*
  > ```json
  > {"email": "admin@example.com", "password": "admin123"}
  > ```
- [ ] **Case lỗi (403 Forbidden):** Token `user1@example.com`, DELETE `/tasks/2`.
  > *(Đăng nhập lấy token)*
  > ```json
  > {"email": "user1@example.com", "password": "user123"}
  > ```
