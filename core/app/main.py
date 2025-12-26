from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import create_db_and_tables
from .settings import settings
from .logging import setup_logging
from .middleware import logging_middleware
from .features.todo.router import router as todo_router

# Khởi tạo logging
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(
    debug=settings.debug,
    title=settings.app_name,
    lifespan=lifespan
)

# Đăng ký middleware
app.middleware("http")(logging_middleware)

# Đăng ký routers từ các features
app.include_router(todo_router)

@app.get("/")
async def read_root():
    return {"message": f"Welcome to {settings.app_name}!"}
