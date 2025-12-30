import pytest
from httpx import AsyncClient
from app.features.profiles.schemas import ProfileCreate, ProfileUpdate


@pytest.mark.asyncio
async def test_create_profile_success(client: AsyncClient):
    """Test tạo profile mới thành công"""
    profile_data = {
        "username": "testuser",
        "bio": "Test bio",
        "avatar_url": "https://example.com/avatar.jpg",
        "birthdate": "1990-01-01",
        "user_id": "user123"
    }

    response = await client.post("/profiles/", json=profile_data)

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["bio"] == "Test bio"
    assert data["id"] is not None
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


@pytest.mark.asyncio
async def test_create_profile_validation_error(client: AsyncClient):
    """Test tạo profile với validation error"""
    profile_data = {
        "username": "ab"  # Quá ngắn
    }

    response = await client.post("/profiles/", json=profile_data)

    assert response.status_code == 422
    data = response.json()
    assert "error" in data


@pytest.mark.asyncio
async def test_create_profile_duplicate_username(client: AsyncClient):
    """Test tạo profile với username trùng"""
    # Tạo profile đầu tiên
    profile_data = {"username": "testuser"}
    await client.post("/profiles/", json=profile_data)

    # Thử tạo profile thứ hai với username trùng
    response = await client.post("/profiles/", json=profile_data)

    assert response.status_code == 409
    data = response.json()
    assert "error" in data
    assert "đã được sử dụng" in data["error"]["message"]


@pytest.mark.asyncio
async def test_get_profiles_empty(client: AsyncClient):
    """Test lấy danh sách profiles khi rỗng"""
    response = await client.get("/profiles/")

    assert response.status_code == 200
    data = response.json()
    assert data == []


@pytest.mark.asyncio
async def test_get_profiles_with_data(client: AsyncClient):
    """Test lấy danh sách profiles có dữ liệu"""
    # Tạo profiles
    await client.post("/profiles/", json={"username": "user1"})
    await client.post("/profiles/", json={"username": "user2"})

    response = await client.get("/profiles/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    usernames = [p["username"] for p in data]
    assert "user1" in usernames
    assert "user2" in usernames


@pytest.mark.asyncio
async def test_search_profiles_by_username(client: AsyncClient):
    """Test tìm kiếm profiles theo username"""
    # Tạo profiles
    await client.post("/profiles/", json={"username": "john_doe"})
    await client.post("/profiles/", json={"username": "jane_doe"})
    await client.post("/profiles/", json={"username": "bob_smith"})

    response = await client.get("/profiles/?username=doe")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    usernames = [p["username"] for p in data]
    assert "john_doe" in usernames
    assert "jane_doe" in usernames


@pytest.mark.asyncio
async def test_get_profiles_pagination(client: AsyncClient):
    """Test phân trang profiles"""
    # Tạo 3 profiles
    await client.post("/profiles/", json={"username": "user1"})
    await client.post("/profiles/", json={"username": "user2"})
    await client.post("/profiles/", json={"username": "user3"})

    # Test pagination
    response = await client.get("/profiles/?skip=1&limit=2")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_profile_by_id_success(client: AsyncClient):
    """Test lấy profile theo ID thành công"""
    # Tạo profile
    create_response = await client.post("/profiles/", json={"username": "testuser"})
    created = create_response.json()

    # Lấy theo ID
    response = await client.get(f"/profiles/{created['id']}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created["id"]
    assert data["username"] == "testuser"


@pytest.mark.asyncio
async def test_get_profile_by_id_not_found(client: AsyncClient):
    """Test lấy profile theo ID khi không tồn tại"""
    response = await client.get("/profiles/999")

    assert response.status_code == 404
    data = response.json()
    assert "error" in data


@pytest.mark.asyncio
async def test_get_profile_by_username_success(client: AsyncClient):
    """Test lấy profile theo username thành công"""
    # Tạo profile
    await client.post("/profiles/", json={"username": "testuser"})

    # Lấy theo username
    response = await client.get("/profiles/by-username/testuser")

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"


@pytest.mark.asyncio
async def test_get_profile_by_username_not_found(client: AsyncClient):
    """Test lấy profile theo username khi không tồn tại"""
    response = await client.get("/profiles/by-username/nonexistent")

    assert response.status_code == 404
    data = response.json()
    assert "error" in data


@pytest.mark.asyncio
async def test_update_profile_success(client: AsyncClient):
    """Test cập nhật profile thành công"""
    # Tạo profile
    create_response = await client.post("/profiles/", json={"username": "testuser"})
    created = create_response.json()

    # Cập nhật
    update_data = {"bio": "Updated bio"}
    response = await client.patch(f"/profiles/{created['id']}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["bio"] == "Updated bio"
    assert data["username"] == "testuser"


@pytest.mark.asyncio
async def test_update_profile_partial(client: AsyncClient):
    """Test cập nhật một phần profile"""
    # Tạo profile
    create_response = await client.post(
        "/profiles/",
        json={"username": "testuser", "bio": "Original bio"}
    )
    created = create_response.json()

    # Chỉ cập nhật bio
    update_data = {"bio": "New bio"}
    response = await client.patch(f"/profiles/{created['id']}", json=update_data)

    assert response.status_code == 200
    data = response.json()
    assert data["bio"] == "New bio"
    assert data["username"] == "testuser"  # Username không đổi


@pytest.mark.asyncio
async def test_update_profile_not_found(client: AsyncClient):
    """Test cập nhật profile khi không tồn tại"""
    update_data = {"bio": "Updated bio"}
    response = await client.patch("/profiles/999", json=update_data)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_profile_username_conflict(client: AsyncClient):
    """Test cập nhật profile với username đã tồn tại"""
    # Tạo 2 profiles
    await client.post("/profiles/", json={"username": "user1"})
    response2 = await client.post("/profiles/", json={"username": "user2"})
    profile2 = response2.json()

    # Cập nhật profile2 với username của profile1
    update_data = {"username": "user1"}
    response = await client.patch(f"/profiles/{profile2['id']}", json=update_data)

    assert response.status_code == 409
    data = response.json()
    assert "error" in data


@pytest.mark.asyncio
async def test_delete_profile_success(client: AsyncClient):
    """Test xóa profile thành công"""
    # Tạo profile
    create_response = await client.post("/profiles/", json={"username": "testuser"})
    created = create_response.json()

    # Xóa
    response = await client.delete(f"/profiles/{created['id']}")

    assert response.status_code == 204

    # Verify đã xóa
    get_response = await client.get(f"/profiles/{created['id']}")
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_profile_not_found(client: AsyncClient):
    """Test xóa profile khi không tồn tại"""
    response = await client.delete("/profiles/999")

    assert response.status_code == 404
