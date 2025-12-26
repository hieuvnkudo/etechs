# E-Techs Core API

Dự án Backend hiệu năng cao được xây dựng với **FastAPI** và **SQLModel**, tập trung vào tính module hóa và khả năng mở rộng.

## 🚀 Công nghệ sử dụng

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) - Hiện đại, nhanh chóng.
- **ORM/ODM:** [SQLModel](https://sqlmodel.tiangolo.com/) - Kết hợp sức mạnh của SQLAlchemy và Pydantic.
- **Package Manager:** [uv](https://github.com/astral-sh/uv) - Cực nhanh, thay thế hoàn hảo cho pip/poetry.
- **Database:** Hỗ trợ PostgreSQL (Production) và SQLite (Development/Testing).
- **Asynchronous:** Sử dụng `asyncio`, `asyncpg` và `aiosqlite` để tối ưu I/O.
- **Logging:** [structlog](https://www.structlog.org/) cho structured logging.
- **Testing:** [pytest](https://docs.pytest.org/) kết hợp `httpx` cho Integration Testing.

## 📂 Cấu trúc thư mục

```text
core/
├── app/
│   ├── features/          # Các module chức năng theo từng feature
│   │   └── todo/          # Ví dụ: Feature Quản lý công việc
│   │       ├── models.py      # Định nghĩa Database Models & API Schemas
│   │       ├── repository.py  # Thao tác trực tiếp với Database
│   │       ├── service.py     # Xử lý logic nghiệp vụ
│   │       └── router.py      # Định nghĩa các API endpoints
│   ├── database.py        # Cấu hình Database & Session management
│   ├── main.py            # Khởi tạo ứng dụng & Đăng ký routes
│   ├── settings.py        # Quản lý biến môi trường (Pydantic Settings)
│   ├── logging.py         # Cấu hình logging hệ thống
│   └── middleware.py      # Các middleware (Logging, Auth, v.v.)
├── tests/                 # Hệ thống kiểm thử tự động
│   ├── conftest.py        # Cấu hình chung cho pytest (fixtures, mock DB)
│   ├── test_main.py       # Kiểm tra các endpoint hệ thống
│   └── test_todo.py       # Kiểm tra logic của feature Todo
├── pyproject.toml         # Quản lý dependencies và cấu hình tool
└── README.md
```

## 🛠 Cài đặt & Setup

### 1. Yêu cầu hệ thống
- Đã cài đặt [uv](https://github.com/astral-sh/uv).

### 2. Cài đặt môi trường
```bash
# Clone và di chuyển vào thư mục core
cd etechs/core

# Cài đặt dependencies và tạo virtual environment
uv sync
```

### 3. Biến môi trường
Mặc định hệ thống sử dụng các giá trị trong `app/settings.py`. Bạn có thể tạo file `.env` để ghi đè:
```env
APP_NAME="E-Techs API"
DEBUG=true
DATABASE_URL="postgresql+asyncpg://user:password@localhost/dbname"
```

## 🏃 Chạy ứng dụng

Chạy server ở chế độ phát triển (Hot Reload):
```bash
uv run fastapi dev app/main.py
```

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## 🧪 Kiểm thử (Testing)

Dự án đã được cấu hình sẵn để chạy test với **SQLite in-memory**, không làm ảnh hưởng đến database thật.

Chạy tất cả các bài test:
```bash
uv run pytest
```

Chạy với báo cáo chi tiết:
```bash
uv run pytest -v
```

## 📝 Quy trình thêm Feature mới

1. Tạo thư mục mới trong `app/features/<feature_name>`.
2. Định nghĩa Model kế thừa `SQLModel` trong `models.py`.
3. Implement `Repository` để quản lý truy vấn.
4. Xây dựng `Service` để xử lý logic.
5. Đăng ký `Router` vào `app/main.py`.
6. **Quan trọng:** Viết test tương ứng trong thư mục `tests/`.
