from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.features.todos.schemas import TodoCreate, TodoUpdate, TodoPublic
from app.features.todos.service import TodoService

router = APIRouter(prefix="/todos", tags=["todos"])


def get_todo_service(session: AsyncSession = Depends(get_session)) -> TodoService:
    return TodoService(session)


@router.post("/", response_model=TodoPublic, status_code=201)
async def create_todo(
    todo_data: TodoCreate,
    service: TodoService = Depends(get_todo_service)
):
    """Tạo một todo mới"""
    return await service.create_todo(todo_data)


@router.get("/", response_model=List[TodoPublic])
async def get_todos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    completed: Optional[bool] = Query(None),
    service: TodoService = Depends(get_todo_service)
):
    """Lấy danh sách todos với phân trang và filter"""
    return await service.get_all_todos(skip=skip, limit=limit, completed=completed)


@router.get("/{todo_id}", response_model=TodoPublic)
async def get_todo(
    todo_id: int,
    service: TodoService = Depends(get_todo_service)
):
    """Lấy thông tin một todo theo ID"""
    return await service.get_todo_by_id(todo_id)


@router.patch("/{todo_id}", response_model=TodoPublic)
async def update_todo(
    todo_id: int,
    todo_data: TodoUpdate,
    service: TodoService = Depends(get_todo_service)
):
    """Cập nhật thông tin một todo"""
    return await service.update_todo(todo_id, todo_data)


@router.delete("/{todo_id}", status_code=204)
async def delete_todo(
    todo_id: int,
    service: TodoService = Depends(get_todo_service)
):
    """Xóa một todo"""
    await service.delete_todo(todo_id)
    return None

