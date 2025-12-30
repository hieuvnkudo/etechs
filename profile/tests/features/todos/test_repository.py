import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.todos.model import Todo
from app.features.todos.repository import TodoRepository


@pytest.mark.asyncio
async def test_create_todo(test_session: AsyncSession):
    """Test tạo todo mới"""
    repository = TodoRepository(test_session)
    
    todo_data = Todo(
        title="Test Todo",
        description="Test description",
        completed=False
    )
    
    created_todo = await repository.create(todo_data)
    
    assert created_todo.id is not None
    assert created_todo.title == "Test Todo"
    assert created_todo.description == "Test description"
    assert created_todo.completed is False
    assert created_todo.created_at is not None
    assert created_todo.updated_at is not None


@pytest.mark.asyncio
async def test_get_by_id(test_session: AsyncSession):
    """Test lấy todo theo ID"""
    repository = TodoRepository(test_session)
    
    # Tạo todo
    todo = Todo(title="Test Todo", description="Test")
    created_todo = await repository.create(todo)
    
    # Lấy todo theo ID
    found_todo = await repository.get_by_id(created_todo.id)
    
    assert found_todo is not None
    assert found_todo.id == created_todo.id
    assert found_todo.title == "Test Todo"
    
    # Test với ID không tồn tại
    not_found = await repository.get_by_id(999)
    assert not_found is None


@pytest.mark.asyncio
async def test_get_all(test_session: AsyncSession):
    """Test lấy tất cả todos"""
    repository = TodoRepository(test_session)
    
    # Tạo nhiều todos
    todo1 = Todo(title="Todo 1", completed=False)
    todo2 = Todo(title="Todo 2", completed=True)
    todo3 = Todo(title="Todo 3", completed=False)
    
    await repository.create(todo1)
    await repository.create(todo2)
    await repository.create(todo3)
    
    # Lấy tất cả
    all_todos = await repository.get_all()
    assert len(all_todos) == 3
    
    # Lấy với filter completed=True
    completed_todos = await repository.get_all(completed=True)
    assert len(completed_todos) == 1
    assert completed_todos[0].completed is True
    
    # Lấy với filter completed=False
    incomplete_todos = await repository.get_all(completed=False)
    assert len(incomplete_todos) == 2
    assert all(not todo.completed for todo in incomplete_todos)
    
    # Test pagination
    paginated = await repository.get_all(skip=1, limit=1)
    assert len(paginated) == 1


@pytest.mark.asyncio
async def test_update_todo(test_session: AsyncSession):
    """Test cập nhật todo"""
    import time
    repository = TodoRepository(test_session)
    
    # Tạo todo
    todo = Todo(title="Original Title", description="Original", completed=False)
    created_todo = await repository.create(todo)
    
    original_updated_at = created_todo.updated_at
    
    # Đợi một chút để đảm bảo updated_at khác nhau
    time.sleep(0.01)
    
    # Cập nhật
    created_todo.title = "Updated Title"
    created_todo.description = "Updated Description"
    created_todo.completed = True
    
    updated_todo = await repository.update(created_todo)
    
    assert updated_todo.title == "Updated Title"
    assert updated_todo.description == "Updated Description"
    assert updated_todo.completed is True
    assert updated_todo.updated_at >= original_updated_at


@pytest.mark.asyncio
async def test_delete_todo(test_session: AsyncSession):
    """Test xóa todo"""
    repository = TodoRepository(test_session)
    
    # Tạo todo
    todo = Todo(title="To Delete", description="Will be deleted")
    created_todo = await repository.create(todo)
    todo_id = created_todo.id
    
    # Xóa
    await repository.delete(created_todo)
    
    # Verify đã xóa
    deleted_todo = await repository.get_by_id(todo_id)
    assert deleted_todo is None

