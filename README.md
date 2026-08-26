# FastAPI Project & Task Management API

Một hệ thống quản lý dự án và công việc (Task Management) được xây dựng bằng **FastAPI** và **SQLAlchemy**. Dự án cung cấp các API RESTful để quản lý người dùng, dự án, thành viên dự án và các công việc (tasks) bên trong dự án đó.

## 🚀 Tính năng nổi bật

- **Xác thực và Phân quyền (Authentication & Authorization):**
  - Đăng ký, Đăng nhập (với mã hóa mật khẩu bcrypt).
  - Cấp phát và làm mới Access Token / Refresh Token (JWT).
  - Phân quyền theo vai trò trong dự án (OWNER, MEMBER).

- **Quản lý Dự án (Project Management):**
  - Tạo, cập nhật, lấy danh sách dự án.
  - Xóa mềm (Soft delete) dự án để bảo toàn dữ liệu.
  - Quản lý thành viên (Thêm/Xóa thành viên, lấy danh sách thành viên).

- **Quản lý Công việc (Task Management):**
  - Tạo task mới trong một dự án.
  - Lấy danh sách task hỗ trợ: phân trang (limit, offset), lọc (trạng thái, độ ưu tiên, người được giao, tên task) và sắp xếp.

## 🛠 Tech Stack

- **Framework:** FastAPI
- **Database ORM:** SQLAlchemy
- **Database Driver:** PyMySQL (Dùng cho MySQL)
- **Data Validation & Settings:** Pydantic & Pydantic-Settings
- **Security:** PyJWT, Passlib (Bcrypt)

## 📁 Cấu trúc thư mục

```text
├── app/
│   ├── core/           # Cấu hình chung, security, exceptions, response schema
│   ├── db/             # Kết nối database
│   ├── dependencies/   # Các dependencies của FastAPI (xác thực, phân quyền)
│   ├── models/         # SQLAlchemy Models (User, Project, Task,...)
│   ├── routers/        # Định nghĩa các API endpoints (Controllers)
│   ├── schemas/        # Pydantic models cho Request / Response validation
│   └── services/       # Xử lý logic nghiệp vụ (Business logic)
├── tests/              # Các bài test (Unit/Integration tests)
├── .env.example        # File mẫu cấu hình biến môi trường
├── requirements.txt    # Danh sách các thư viện phụ thuộc
├── seed_data.py        # Script tạo dữ liệu mẫu
└── README.md           # Tài liệu hướng dẫn
```

## ⚙️ Hướng dẫn cài đặt và chạy dự án

### 1. Yêu cầu hệ thống
- **Python** 3.10 trở lên.
- **MySQL** Server (Hoặc công cụ giả lập như XAMPP/Docker).

### 2. Cài đặt

Bước 1: Clone dự án và tạo môi trường ảo (Virtual Environment)
```bash
# Tạo môi trường ảo
python -m venv .venv

# Kích hoạt môi trường ảo
# Trên Windows:
.venv\Scripts\activate
# Trên Linux/macOS:
source .venv/bin/activate
```

Bước 2: Cài đặt các thư viện cần thiết
```bash
pip install -r requirements.txt
```

### 3. Cấu hình biến môi trường

Tạo một file `.env` ở thư mục gốc của dự án (có thể copy từ `.env.example` nếu có) và cấu hình các biến môi trường sau:

```env
DATABASE_URL=mysql+pymysql://<username>:<password>@<host>:<port>/<database_name>
SECRET_KEY=your_super_secret_key_here
ACCESS_EXPIRES_TIME=15    # Thời gian hết hạn Access Token (phút)
REFRESH_EXPIRES_TIME=7    # Thời gian hết hạn Refresh Token (ngày)
```
*Lưu ý: Bạn cần tạo sẵn một database trống trên MySQL trước khi chạy dự án.*

### 4. Tạo dữ liệu mẫu (Tùy chọn)

Bạn có thể chạy script seed data để tạo nhanh một số dữ liệu mẫu (Users, Projects, Tasks) phục vụ cho quá trình test:
```bash
python seed_data.py
```
*(Script này cũng sẽ tự động khởi tạo các bảng trong database nếu chúng chưa tồn tại).*

### 5. Chạy ứng dụng

Khởi động server bằng Uvicorn:
```bash
uvicorn app.main:app --reload
```
Server sẽ chạy mặc định tại: `http://127.0.0.1:8000`

### 6. Xem tài liệu API (Swagger UI)

FastAPI tự động tạo tài liệu API tương tác. Sau khi chạy server, hãy truy cập:
- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

Tại đây bạn có thể xem mô tả chi tiết của từng endpoint và trực tiếp gọi thử API.
