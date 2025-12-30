import pytest
from httpx import AsyncClient
from app.features.todos.model import Todo


@pytest.mark.asyncio
async def test_create_todo(client: AsyncClient):
    """Test API tạo todo"""
    response = await client.post(
        "/todos/",
        json={
            "title": "API Test Todo",
            "description": "API description",
            "completed": False
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "API Test Todo"
    assert data["description"] == "API description"
    assert data["completed"] is False
    assert data["id"] is not None
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_todo_minimal(client: AsyncClient):
    """Test API tạo todo với dữ liệu tối thiểu"""
    response = await client.post(
        "/todos/",
        json={"title": "Minimal Todo"}
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Minimal Todo"
    assert data["description"] is None
    assert data["completed"] is False


@pytest.mark.asyncio
async def test_create_todo_invalid(client: AsyncClient):
    """Test API tạo todo với dữ liệu không hợp lệ"""
    # Thiếu title
    response = await client.post("/todos/", json={})
    assert response.status_code == 422
    
    # Title quá dài
    response = await client.post(
        "/todos/",
        json={"title": "a" * 201}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_todos_empty(client: AsyncClient):
    """Test API lấy danh sách todos khi rỗng"""
    response = await client.get("/todos/")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


@pytest.mark.asyncio
async def test_get_todos_with_data(client: AsyncClient, test_session):
    """Test API lấy danh sách todos có dữ liệu"""
    # Tạo todos trực tiếp trong database
    todo1 = Todo(title="Todo 1", completed=False)
    todo2 = Todo(title="Todo 2", completed=True)
    todo3 = Todo(title="Todo 3", completed=False)
    
    test_session.add(todo1)
    test_session.add(todo2)
    test_session.add(todo3)
    await test_session.commit()
    
    # Lấy tất cả
    response = await client.get("/todos/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    
    # Lấy với filter completed=True
    response = await client.get("/todos/?completed=true")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["completed"] is True
    
    # Lấy với filter completed=False
    response = await client.get("/todos/?completed=false")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert all(not item["completed"] for item in data)
    
    # Test pagination
    response = await client.get("/todos/?skip=1&limit=1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


@pytest.mark.asyncio
async def test_get_todo_by_id(client: AsyncClient, test_session):
    """Test API lấy todo theo ID"""
    # Tạo todo
    todo = Todo(title="Get Test Todo", description="Test")
    test_session.add(todo)
    await test_session.commit()
    await test_session.refresh(todo)
    
    # Lấy todo
    response = await client.get(f"/todos/{todo.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo.id
    assert data["title"] == "Get Test Todo"
    assert data["description"] == "Test"


@pytest.mark.asyncio
async def test_get_todo_not_found(client: AsyncClient):
    """Test API lấy todo không tồn tại"""
    response = await client.get("/todos/999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_todo(client: AsyncClient, test_session):
    """Test API cập nhật todo"""
    # Tạo todo
    todo = Todo(title="Original", description="Original desc", completed=False)
    test_session.add(todo)
    await test_session.commit()
    await test_session.refresh(todo)
    
    # Cập nhật
    response = await client.patch(
        f"/todos/{todo.id}",
        json={
            "title": "Updated",
            "description": "Updated desc",
            "completed": True
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated"
    assert data["description"] == "Updated desc"
    assert data["completed"] is True
    assert data["id"] == todo.id


@pytest.mark.asyncio
async def test_update_todo_partial(client: AsyncClient, test_session):
    """Test API cập nhật một phần todo"""
    # Tạo todo
    todo = Todo(title="Original", description="Original desc", completed=False)
    test_session.add(todo)
    await test_session.commit()
    await test_session.refresh(todo)
    
    # Chỉ cập nhật title
    response = await client.patch(
        f"/todos/{todo.id}",
        json={"title": "Updated Title"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Original desc"  # Không đổi
    assert data["completed"] is False  # Không đổi


@pytest.mark.asyncio
async def test_update_todo_not_found(client: AsyncClient):
    """Test API cập nhật todo không tồn tại"""
    response = await client.patch(
        "/todos/999",
        json={"title": "Updated"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_todo(client: AsyncClient, test_session):
    """Test API xóa todo"""
    # Tạo todo
    todo = Todo(title="To Delete")
    test_session.add(todo)
    await test_session.commit()
    await test_session.refresh(todo)
    todo_id = todo.id
    
    # Xóa
    response = await client.delete(f"/todos/{todo_id}")
    assert response.status_code == 204
    
    # Verify đã xóa
    response = await client.get(f"/todos/{todo_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_todo_not_found(client: AsyncClient):
    """Test API xóa todo không tồn tại"""
    response = await client.delete("/todos/999")
    assert response.status_code == 404

