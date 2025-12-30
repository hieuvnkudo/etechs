from typing import Optional
from sqlmodel import Field, SQLModel
from app.core.mixins import TimestampMixin


class TodoBase(SQLModel):
    """Base model cho Todo với các fields chung"""
    title: str = Field(index=True, max_length=200)
    description: Optional[str] = None
    completed: bool = Field(default=False, index=True)


class Todo(TodoBase, TimestampMixin, table=True):
    """Database model cho Todo"""
    id: Optional[int] = Field(default=None, primary_key=True)

