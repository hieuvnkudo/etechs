import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.features.todos.model import Todo
from app.features.todos.schemas import TodoCreate, TodoUpdate
from app.features.todos.service import TodoService


@pytest.mark.asyncio
async def test_create_todo(test_session: AsyncSession):
    """Test service tạo todo"""
    service = TodoService(test_session)
    
    todo_data = TodoCreate(
        title="Service Test Todo",
        description="Service description",
        completed=False
    )
    
    created_todo = await service.create_todo(todo_data)
    
    assert created_todo.id is not None
    assert created_todo.title == "Service Test Todo"
    assert created_todo.description == "Service description"
    assert created_todo.completed is False


@pytest.mark.asyncio
async def test_get_todo_by_id_success(test_session: AsyncSession):
    """Test service lấy todo thành công"""
    service = TodoService(test_session)
    
    # Tạo todo trước
    todo_data = TodoCreate(title="Test Todo")
    created_todo = await service.create_todo(todo_data)
    
    # Lấy todo
    found_todo = await service.get_todo_by_id(created_todo.id)
    
    assert found_todo.id == created_todo.id
    assert found_todo.title == "Test Todo"


@pytest.mark.asyncio
async def test_get_todo_by_id_not_found(test_session: AsyncSession):
    """Test service lấy todo không tồn tại"""
    service = TodoService(test_session)
    
    with pytest.raises(HTTPException) as exc_info:
        await service.get_todo_by_id(999)
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_get_all_todos(test_session: AsyncSession):
    """Test service lấy tất cả todos"""
    service = TodoService(test_session)
    
    # Tạo nhiều todos
    await service.create_todo(TodoCreate(title="Todo 1", completed=False))
    await service.create_todo(TodoCreate(title="Todo 2", completed=True))
    await service.create_todo(TodoCreate(title="Todo 3", completed=False))
    
    # Lấy tất cả
    all_todos = await service.get_all_todos()
    assert len(all_todos) == 3
    
    # Lấy với filter
    completed_todos = await service.get_all_todos(completed=True)
    assert len(completed_todos) == 1
    
    incomplete_todos = await service.get_all_todos(completed=False)
    assert len(incomplete_todos) == 2
    
    # Test pagination
    paginated = await service.get_all_todos(skip=1, limit=1)
    assert len(paginated) == 1


@pytest.mark.asyncio
async def test_update_todo_success(test_session: AsyncSession):
    """Test service cập nhật todo thành công"""
    service = TodoService(test_session)
    
    # Tạo todo
    created_todo = await service.create_todo(TodoCreate(title="Original", completed=False))
    
    # Cập nhật
    update_data = TodoUpdate(
        title="Updated",
        description="New description",
        completed=True
    )
    
    updated_todo = await service.update_todo(created_todo.id, update_data)
    
    assert updated_todo.title == "Updated"
    assert updated_todo.description == "New description"
    assert updated_todo.completed is True


@pytest.mark.asyncio
async def test_update_todo_partial(test_session: AsyncSession):
    """Test service cập nhật một phần todo"""
    service = TodoService(test_session)
    
    # Tạo todo
    created_todo = await service.create_todo(
        TodoCreate(title="Original", description="Original desc", completed=False)
    )
    
    # Chỉ cập nhật title
    update_data = TodoUpdate(title="Updated Title")
    updated_todo = await service.update_todo(created_todo.id, update_data)
    
    assert updated_todo.title == "Updated Title"
    assert updated_todo.description == "Original desc"  # Không đổi
    assert updated_todo.completed is False  # Không đổi


@pytest.mark.asyncio
async def test_update_todo_not_found(test_session: AsyncSession):
    """Test service cập nhật todo không tồn tại"""
    service = TodoService(test_session)
    
    update_data = TodoUpdate(title="Updated")
    
    with pytest.raises(HTTPException) as exc_info:
        await service.update_todo(999, update_data)
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_todo_success(test_session: AsyncSession):
    """Test service xóa todo thành công"""
    service = TodoService(test_session)
    
    # Tạo todo
    created_todo = await service.create_todo(TodoCreate(title="To Delete"))
    todo_id = created_todo.id
    
    # Xóa
    await service.delete_todo(todo_id)
    
    # Verify đã xóa
    with pytest.raises(HTTPException) as exc_info:
        await service.get_todo_by_id(todo_id)
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_todo_not_found(test_session: AsyncSession):
    """Test service xóa todo không tồn tại"""
    service = TodoService(test_session)
    
    with pytest.raises(HTTPException) as exc_info:
        await service.delete_todo(999)
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

