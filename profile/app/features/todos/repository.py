from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.features.todos.model import Todo


class TodoRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, todo: Todo) -> Todo:
        self.session.add(todo)
        await self.session.commit()
        await self.session.refresh(todo)
        return todo

    async def get_by_id(self, todo_id: int) -> Optional[Todo]:
        result = await self.session.get(Todo, todo_id)
        return result

    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        completed: Optional[bool] = None
    ) -> List[Todo]:
        statement = select(Todo)
        
        if completed is not None:
            statement = statement.where(Todo.completed == completed)
        
        statement = statement.offset(skip).limit(limit).order_by(Todo.created_at.desc())
        
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def update(self, todo: Todo) -> Todo:
        from datetime import datetime, timezone
        todo.updated_at = datetime.now(timezone.utc)
        self.session.add(todo)
        await self.session.commit()
        await self.session.refresh(todo)
        return todo

    async def delete(self, todo: Todo) -> None:
        await self.session.delete(todo)
        await self.session.commit()

