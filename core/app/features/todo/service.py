from .repository import TodoRepository
from .models import Todo, TodoCreate, TodoUpdate
from typing import List, Optional
import structlog

logger = structlog.get_logger()

class TodoService:
    def __init__(self, repository: TodoRepository):
        self.repository = repository

    async def create_todo(self, todo_data: TodoCreate) -> Todo:
        todo = await self.repository.create(todo_data)
        logger.info("todo_created", todo_id=todo.id)
        return todo

    async def get_todos(self) -> List[Todo]:
        return await self.repository.get_all()

    async def get_todo(self, todo_id: int) -> Optional[Todo]:
        todo = await self.repository.get_by_id(todo_id)
        if not todo:
            logger.warning("todo_not_found", todo_id=todo_id)
        return todo

    async def update_todo(self, todo_id: int, todo_data: TodoUpdate) -> Optional[Todo]:
        db_todo = await self.repository.get_by_id(todo_id)
        if not db_todo:
            logger.warning("todo_not_found_for_update", todo_id=todo_id)
            return None
        
        updated_todo = await self.repository.update(db_todo, todo_data)
        logger.info("todo_updated", todo_id=todo_id)
        return updated_todo

    async def delete_todo(self, todo_id: int) -> bool:
        db_todo = await self.repository.get_by_id(todo_id)
        if not db_todo:
            logger.warning("todo_not_found_for_deletion", todo_id=todo_id)
            return False
        
        await self.repository.delete(db_todo)
        logger.info("todo_deleted", todo_id=todo_id)
        return True

