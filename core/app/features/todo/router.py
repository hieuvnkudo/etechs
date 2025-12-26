from fastapi import APIRouter, Depends, HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from app.database import get_session
from .models import Todo, TodoCreate, TodoUpdate
from .repository import TodoRepository
from .service import TodoService

router = APIRouter(prefix="/todos", tags=["todos"])

async def get_todo_service(session: AsyncSession = Depends(get_session)) -> TodoService:
    repository = TodoRepository(session)
    return TodoService(repository)

@router.post("/", response_model=Todo)
async def create_todo(
    todo_data: TodoCreate, 
    service: TodoService = Depends(get_todo_service)
):
    return await service.create_todo(todo_data)

@router.get("/", response_model=List[Todo])
async def read_todos(service: TodoService = Depends(get_todo_service)):
    return await service.get_todos()

@router.get("/{todo_id}", response_model=Todo)
async def read_todo(
    todo_id: int, 
    service: TodoService = Depends(get_todo_service)
):
    todo = await service.get_todo(todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@router.patch("/{todo_id}", response_model=Todo)
async def update_todo(
    todo_id: int, 
    todo_data: TodoUpdate, 
    service: TodoService = Depends(get_todo_service)
):
    updated_todo = await service.update_todo(todo_id, todo_data)
    if not updated_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated_todo

@router.delete("/{todo_id}")
async def delete_todo(
    todo_id: int, 
    service: TodoService = Depends(get_todo_service)
):
    success = await service.delete_todo(todo_id)
    if not success:
        raise HTTPException(status_code=404, detail="Todo not found")
    return {"ok": True}

