from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from .models import Todo, TodoCreate, TodoUpdate
from typing import List, Optional

class TodoRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, todo_data: TodoCreate) -> Todo:
        db_todo = Todo.model_validate(todo_data)
        self.session.add(db_todo)
        await self.session.commit()
        await self.session.refresh(db_todo)
        return db_todo

    async def get_all(self) -> List[Todo]:
        result = await self.session.execute(select(Todo))
        return result.scalars().all()

    async def get_by_id(self, todo_id: int) -> Optional[Todo]:
        return await self.session.get(Todo, todo_id)

    async def update(self, db_todo: Todo, todo_data: TodoUpdate) -> Todo:
        update_data = todo_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_todo, key, value)
        
        self.session.add(db_todo)
        await self.session.commit()
        await self.session.refresh(db_todo)
        return db_todo

    async def delete(self, db_todo: Todo) -> None:
        await self.session.delete(db_todo)
        await self.session.commit()

