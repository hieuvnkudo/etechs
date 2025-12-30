# FastAPI REST API

Ứng dụng FastAPI REST API với kiến trúc sạch (clean architecture), hỗ trợ async/await và các best practices hiện đại.

## Tính năng

- **FastAPI**: Framework web hiện đại với hiệu suất cao
- **Clean Architecture**: Phân tách rõ ràng giữa các lớp (Repository, Service, Router)
- **SQLModel**: Kết hợp SQLAlchemy và Pydantic cho ORM an toàn kiểu dữ liệu
- **Async/First**: Hỗ trợ đầy đủ async/await cho database operations
- **Type Safety**: Type hints và validation với Pydantic
- **Testing**: Hạ tầng test hoàn chỉnh với pytest
- **Docker**: Hỗ trợ deployment với Docker
- **Package Manager**: Sử dụng `uv` cho dependency management nhanh chóng

## Yêu cầu

- Python >= 3.12
- `uv` package manager

## Cài đặt

```bash
# Cài đặt tất cả dependencies (bao gồm dev dependencies)
uv sync

# Chỉ cài đặt production dependencies (dùng cho Docker)
uv sync --locked --no-install-project
```

## Chạy ứng dụng

```bash
# Development mode với auto-reload
uv run fastapi dev app/main.py

# Production server
uv run fastapi run app/main.py --host 0.0.0.0
```

API documentation sẽ available tại:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

```bash
# Chạy tất cả tests
uv run pytest

# Chạy với coverage report
uv run pytest --cov=app

# Chạy một test file cụ thể
uv run pytest tests/test_todos.py

# Chạy một test function cụ thể
uv run pytest tests/test_todos.py::test_create_todo

# Chạy với verbose output
uv run pytest -v
```

## Docker

```bash
# Build production image
docker build -t fastapi-app .

# Run container
docker run -p 8000:8000 fastapi-app
```

## Cấu trúc dự án

```
app/
├── core/              # Cross-cutting concerns
│   ├── config.py      # Cấu hình ứng dụng (Pydantic BaseSettings)
│   ├── database.py    # Kết nối DB và session management
│   ├── exceptions.py  # Custom exception handlers
│   ├── health.py      # Health check endpoints
│   └── logging.py     # Cấu hình logging
├── features/          # Feature-based modules (Domain layer)
│   └── todos/         # Mỗi feature là module tự chứa
│       ├── model.py       # SQLModel database models
│       ├── schemas.py     # Pydantic schemas (request/response)
│       ├── repository.py  # Data access layer
│       ├── service.py     # Business logic layer
│       └── router.py      # API endpoints
├── middleware/        # Request processing
│   ├── cors.py        # CORS configuration
│   └── request_id.py  # Request ID tracking
└── main.py           # FastAPI app instance & startup/shutdown
```

## Kiến trúc

### Layered Architecture Pattern

Dự án theo đuổi **clean architecture** với sự phân tách rõ ràng:

1. **Model**: Database entity (SQLModel)
2. **Schemas**: Pydantic models cho validation (`*Create`, `*Update`, response models)
3. **Repository**: Data access logic (CRUD operations với AsyncSession)
4. **Service**: Business logic layer (sử dụng repository, xử lý validation/errors)
5. **Router**: FastAPI routes/endpoints (dependency injection cho services)

### Dependency Injection

- Services nhận `AsyncSession` qua FastAPI's dependency injection
- Routers nhận services qua dependencies

### Database

- **ORM**: SQLModel (kết hợp SQLAlchemy + Pydantic)
- **Default**: SQLite với `aiosqlite` async driver
- **Config**: Thiết lập `database_url` trong `.env` hoặc qua environment variable
- Dễ dàng chuyển sang PostgreSQL/MySQL bằng cách thay đổi connection string

### Configuration

Settings được quản lý qua `app/core/config.py` sử dụng Pydantic BaseSettings:
- Tải từ file `.env`
- Default: `app_name`, `debug`, `database_url`
- Mở rộng class `Settings` để thêm configuration mới

## Environment Variables

Tạo file `.env` trong root directory:

```env
APP_NAME=FastAPI App
DEBUG=true
DATABASE_URL=sqlite+aiosqlite://./app.db
```

## Thêm Feature mới

1. Tạo directory dưới `app/features/<feature>/`
2. Tạo files: `model.py`, `schemas.py`, `repository.py`, `service.py`, `router.py`
3. Import model trong `main.py` cho SQLModel metadata registration
4. Register router trong `main.py` với `app.include_router()`

## License

MIT
