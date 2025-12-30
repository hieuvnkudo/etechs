from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.todos.model import Todo
from app.features.todos.schemas import TodoCreate, TodoUpdate
from app.features.todos.repository import TodoRepository
from app.core.exceptions import NotFoundError


class TodoService:
    def __init__(self, session: AsyncSession):
        self.repository = TodoRepository(session)

    async def create_todo(self, todo_data: TodoCreate) -> Todo:
        todo = Todo(**todo_data.model_dump())
        return await self.repository.create(todo)

    async def get_todo_by_id(self, todo_id: int) -> Todo:
        todo = await self.repository.get_by_id(todo_id)
        if not todo:
            raise NotFoundError(resource="Todo", resource_id=todo_id)
        return todo

    async def get_all_todos(
        self,
        skip: int = 0,
        limit: int = 100,
        completed: Optional[bool] = None
    ) -> List[Todo]:
        return await self.repository.get_all(skip=skip, limit=limit, completed=completed)

    async def update_todo(self, todo_id: int, todo_data: TodoUpdate) -> Todo:
        todo = await self.get_todo_by_id(todo_id)
        
        update_data = todo_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(todo, field, value)
        
        return await self.repository.update(todo)

    async def delete_todo(self, todo_id: int) -> None:
        todo = await self.get_todo_by_id(todo_id)
        await self.repository.delete(todo)

