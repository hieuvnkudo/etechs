from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel
from app.features.todos.model import TodoBase


class TodoCreate(TodoBase):
    """Schema để tạo todo mới"""
    pass


class TodoUpdate(SQLModel):
    """Schema để cập nhật todo"""
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None


class TodoPublic(TodoBase):
    """Schema để trả về todo cho client"""
    id: int
    created_at: datetime
    updated_at: datetime

