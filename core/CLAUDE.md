# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **FastAPI-based asynchronous API** built with Python 3.12, using **Clean Architecture** principles with a **feature-oriented modular design**. Each feature is self-contained with its own models, repository, service, and router layers.

## Tech Stack

- **Package Manager:** `uv` (fast alternative to pip/poetry)
- **Framework:** FastAPI 0.127+ with async/await throughout
- **ORM:** SQLModel (combines SQLAlchemy + Pydantic)
- **Databases:** PostgreSQL (production), SQLite (dev/testing)
- **Testing:** pytest with pytest-asyncio, httpx for integration tests
- **Logging:** structlog for structured logging

## Commands

```bash
# Setup
uv sync                              # Install dependencies

# Development
uv run fastapi dev app/main.py       # Hot-reload dev server

# Testing
uv run pytest                        # All tests
uv run pytest -v                     # Verbose output
uv run pytest tests/test_todo.py     # Single test file
uv run pytest --cov=app              # With coverage

# Production
uv run fastapi run app/main.py       # Production server
```

## Architecture

### Feature Module Structure

Each feature in `app/features/<feature_name>/` follows this layered architecture:

```
features/<feature_name>/
├── models.py       # SQLModel schemas & database models
├── repository.py   # Data access layer (database operations)
├── service.py      # Business logic layer
└── router.py       # API endpoints (FastAPI routes)
```

**Key principle:** Dependencies flow inward - Router depends on Service, Service depends on Repository. This enables easy testing and maintainability.

### Request Flow

1. **Router** (`router.py`): Receives HTTP request, validates via Pydantic models
2. **Service** (`service.py`): Implements business logic, calls repository
3. **Repository** (`repository.py`): Executes database queries with AsyncSession
4. **Response**: Flows back through layers with proper status codes

### Dependency Injection

Services and repositories are injected via FastAPI's dependency system:
```python
# In router.py
@router.post("/")
async def create_todo(
    todo: TodoCreate,
    session: AsyncSession = Depends(get_session),
    service: TodoService = Depends(todo_service)
):
    return await service.create(todo, session)
```

### Testing Strategy

- **SQLite in-memory** database for tests (configured in `tests/conftest.py`)
- **Dependency override** pattern replaces real database session with test session
- **Fixtures** provide reusable test setup (`session`, `client`)
- Tests use **httpx AsyncClient** with ASGI transport for real API calls

### Database Layer

- **AsyncSession** from `sqlmodel.ext.asyncio` for all database operations
- **Connection pooling** managed by SQLAlchemy engine
- **Lifespan context** in `app/main.py` creates tables on startup
- **No migrations** currently - tables are created via `SQLModel.metadata.create_all()`

### Adding New Features

1. Create directory: `app/features/<feature_name>/`
2. Define models in `models.py` (inherit from `SQLModel`)
3. Implement repository pattern in `repository.py`
4. Build service layer in `service.py`
5. Create router in `router.py` with proper dependency injection
6. Register router in `app/main.py`: `app.include_router(router)`
7. Write tests in `tests/test_<feature_name>.py`

### Configuration

- **Settings** in `app/settings.py` using Pydantic Settings
- **Environment variables** via `.env` file or system environment
- **Defaults** defined in settings class for local development
- Key settings: `DATABASE_URL`, `APP_NAME`, `DEBUG`

### Logging

- **structlog** configured in `app/logging.py`
- **JSON format** in production for centralized logging
- **Request middleware** (`app/middleware.py`) adds unique request IDs
- **Structured context** includes request_id, path, method, status

### Docker Support

- **Multi-stage build** in `Dockerfile` for optimized production images
- **Non-root user** for security
- **Hot-reload** via `compose.yml` for development
