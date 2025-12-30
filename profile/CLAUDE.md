# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **FastAPI REST API** application implementing a clean architecture pattern with async/await support. The project demonstrates modern Python best practices using `uv` as the package manager, SQLModel for type-safe database operations, and a layered architecture separating concerns.

## Development Commands

### Package Management
```bash
# Install all dependencies
uv sync

# Install only production dependencies (used in Dockerfile)
uv sync --locked --no-install-project
```

### Development Server
```bash
# Run with auto-reload
uv run fastapi dev app/main.py

# Run production server
uv run fastapi run app/main.py --host 0.0.0.0
```

### Testing
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app

# Run specific test file
uv run pytest tests/test_todos.py

# Run specific test function
uv run pytest tests/test_todos.py::test_create_todo
```

### Docker
```bash
# Build production image
docker build -t fastapi-app .

# Run container
docker run -p 8000:8000 fastapi-app
```

## Architecture

### Layered Architecture Pattern

The project follows a **clean architecture** with clear separation of concerns:

```
app/
├── core/              # Cross-cutting concerns
│   ├── config.py      # Application settings (Pydantic BaseSettings)
│   ├── database.py    # DB connection & session management
│   ├── exceptions.py  # Custom exception handlers
│   ├── health.py      # Health check endpoints
│   └── logging.py     # Logging configuration
├── features/          # Feature-based modules (Domain layer)
│   └── todos/         # Each feature is self-contained
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

### Key Architectural Patterns

1. **Feature-Based Organization**: Each feature (e.g., `todos`) is a self-contained module with:
   - **Model**: Database entity (SQLModel)
   - **Schemas**: Pydantic models for validation (`*Create`, `*Update`, response models)
   - **Repository**: Data access logic (CRUD operations with AsyncSession)
   - **Service**: Business logic layer (uses repository, handles validation/errors)
   - **Router**: FastAPI routes/endpoints (dependency injection for services)

2. **Dependency Injection**: Services receive `AsyncSession` through FastAPI's dependency injection. Routers receive services through dependencies.

3. **Async/First**: All database operations use async patterns with `aiosqlite` (easily swappable to PostgreSQL/MySQL).

4. **Exception Handling**: Centralized custom exceptions in `core/exceptions.py` with dedicated handlers in `main.py` (line 52-54).

5. **Lifespan Management**: Database connections and logging setup in `lifespan` context manager (main.py:25-36).

### Adding a New Feature

When creating a new feature, follow the existing pattern:

1. Create directory under `app/features/<feature>/`
2. Create files: `model.py`, `schemas.py`, `repository.py`, `service.py`, `router.py`
3. Import model in `main.py` for SQLModel metadata registration
4. Register router in `main.py` with `app.include_router()`

### Database

- **ORM**: SQLModel (combines SQLAlchemy + Pydantic)
- **Default**: SQLite with `aiosqlite` async driver
- **Config**: Set `database_url` in `.env` or via environment variable
- **Migration**: Manual schema creation in `lifespan` startup via `create_db_and_tables()`

### Testing Infrastructure

Tests use **in-memory SQLite** with fixtures in `tests/conftest.py`:

- `test_engine`: Creates in-memory database and tables
- `test_session`: Provides AsyncSession for tests
- `override_get_session`: Overrides FastAPI's `get_session` dependency
- `client`: httpx AsyncClient with ASGI transport for testing endpoints

Important: Always import model classes (`from app.features.todos.model import Todo`) in test files or conftest to ensure SQLModel metadata registration.

### Configuration

Settings managed via `app/core/config.py` using Pydantic BaseSettings:
- Loads from `.env` file
- Default: `app_name`, `debug`, `database_url`
- Extend the `Settings` class to add new configuration

### Middleware

- **Request ID**: Automatic request ID generation for tracing
- **CORS**: Configured in `middleware/cors.py`

### API Documentation

Auto-generated Swagger UI available at `/docs` when server is running.

## Important Notes

- **Language**: Code comments and strings use Vietnamese. Maintain this convention when modifying existing code.
- **Python Version**: Requires Python >=3.12
- **Dependency Management**: Uses `uv.lock` for reproducible builds
- **Production Deployment**: Dockerfile uses multi-stage build without uv in final image (runs with `fastapi run`)
