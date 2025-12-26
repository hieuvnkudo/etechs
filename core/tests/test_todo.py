import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_todo(client: AsyncClient):
    response = await client.post(
        "/todos/",
        json={"title": "Test Todo", "description": "Test Description"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["id"] is not None

@pytest.mark.asyncio
async def test_read_todos(client: AsyncClient):
    # Tạo một todo trước
    await client.post("/todos/", json={"title": "Todo 1"})
    
    response = await client.get("/todos/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["title"] == "Todo 1"

@pytest.mark.asyncio
async def test_read_todo(client: AsyncClient):
    # Tạo một todo
    create_res = await client.post("/todos/", json={"title": "Todo to read"})
    todo_id = create_res.json()["id"]
    
    response = await client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Todo to read"

@pytest.mark.asyncio
async def test_update_todo(client: AsyncClient):
    # Tạo một todo
    create_res = await client.post("/todos/", json={"title": "Old Title"})
    todo_id = create_res.json()["id"]
    
    response = await client.patch(f"/todos/{todo_id}", json={"title": "New Title"})
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"

@pytest.mark.asyncio
async def test_delete_todo(client: AsyncClient):
    # Tạo một todo
    create_res = await client.post("/todos/", json={"title": "To delete"})
    todo_id = create_res.json()["id"]
    
    response = await client.delete(f"/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json() == {"ok": True}
    
    # Kiểm tra lại xem đã xóa chưa
    get_res = await client.get(f"/todos/{todo_id}")
    assert get_res.status_code == 404

