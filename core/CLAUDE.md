# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

High-performance FastAPI backend with SQLModel ORM, following a strict feature-based architecture. The project uses **uv** as package manager and follows a **Repository-Service-Router** pattern for each feature.

**Tech Stack:** FastAPI + SQLModel + SQLAlchemy (async) + uv + pytest + structlog

**Language:** Code & commits in English. Explanations in Vietnamese when needed.

## Development Commands

```bash
# Install dependencies
uv sync

# Run development server (hot reload)
uv run fastapi dev app/main.py

# Run tests
uv run pytest                  # All tests
uv run pytest -v              # Verbose output
uv run pytest tests/test_todo.py  # Single test file

# Linting (if ruff is configured)
uv run ruff check . --fix
```

**API Documentation:** `http://localhost:8000/docs` (Swagger UI)

## Architecture

### Feature-Based Structure

Each feature follows a **4-layer architecture** in `app/features/<feature>/`:

```
app/features/todo/
├── models.py       # SQLModel table + Pydantic schemas (Create/Update)
├── repository.py   # Database CRUD operations (AsyncSession)
├── service.py      # Business logic + logging
└── router.py       # FastAPI routes + dependency injection
```

**Dependency Flow:** Router → Service → Repository → Database

**Key Pattern:**
- `models.py`: Defines `<Model>`, `<Model>Create`, `<Model>Update`
- `repository.py`: Wraps AsyncSession, implements `create()`, `get_all()`, `get_by_id()`, `update()`, `delete()`
- `service.py`: Orchestrates repository calls, adds business logic and structured logging
- `router.py`: FastAPI endpoints with `Depends()` for dependency injection

### Database & Async

- **Session Management:** `app/database.py` provides `get_session()` dependency
- **Engine:** Created from `settings.database_url` (supports PostgreSQL + SQLite)
- **Testing:** Uses `sqlite+aiosqlite:///:memory:` with fixture overrides in `tests/conftest.py`
- **Table Creation:** `create_db_and_tables()` in lifespan context (`app/main.py`)

**Important:** When adding new models, import them in `app/database.py:create_db_and_tables()` to ensure tables are created.

### Settings & Configuration

- **File:** `app/settings.py` - Pydantic Settings with `.env` support
- **Defaults:** `app_name="Food Delivery API"`, `database_url="sqlite+aiosqlite:///database.db"`, `debug=True`
- **Override:** Create `.env` file to change values

### Logging

- **Library:** `structlog` with contextvars for request-scoped logging
- **Middleware:** `app/middleware.py` binds `request_id`, `method`, `path` to context
- **Service Layer:** Use `logger.info()`, `logger.warning()` with structured fields

### Testing Architecture

**Test Database:** SQLite in-memory, isolated per test session

**Fixtures (`tests/conftest.py`):**
- `session` - AsyncSession with auto-create/drop tables
- `client` - httpx AsyncClient with `get_session` override
- `event_loop` - AsyncIO event loop management
- `close_engine` - Engine disposal after all tests

**Test Pattern:**
1. Use `client` fixture for API tests
2. Use `session` fixture for direct DB tests
3. All tests are async - use `async def test_*()`

## Adding a New Feature

1. **Create directory:** `app/features/<feature>/`
2. **Define models** in `models.py` (Table + Create/Update schemas)
3. **Implement repository** with CRUD methods
4. **Implement service** with business logic and logging
5. **Create router** with FastAPI endpoints and dependency injection
6. **Register router** in `app/main.py` (add import + `app.include_router()`)
7. **Import model** in `app/database.py:create_db_and_tables()`
8. **Write tests** in `tests/test_<feature>.py`

## Critical Implementation Details

### Dependency Injection Pattern

```python
# router.py
async def get_feature_service(session: AsyncSession = Depends(get_session)) -> FeatureService:
    repository = FeatureRepository(session)
    return FeatureService(repository)

@router.post("/")
async def create(data: FeatureCreate, service: FeatureService = Depends(get_feature_service)):
    return await service.create(data)
```

### Repository Update Pattern

Always use `model_dump(exclude_unset=True)` for partial updates:

```python
def update(self, db_obj: Model, update_data: ModelUpdate) -> Model:
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(db_obj, key, value)
    self.session.add(db_obj)
    await self.session.commit()
    await self.session.refresh(db_obj)
    return db_obj
```

### Async Session Management

- Never manually close sessions - use `async with` context or let fixtures handle it
- Always `await session.commit()` after mutations
- Always `await session.refresh(db_obj)` after commit to get DB-generated values

## TDD Workflow

1. **RED:** Write failing test in `tests/test_<feature>.py`
2. **GREEN:** Implement minimal feature code to pass
3. **REFACTOR:** Improve design while keeping tests green

**Target:** 90%+ test coverage for new code
