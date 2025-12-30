import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.profiles.model import Profile
from app.features.profiles.repository import ProfileRepository


@pytest.mark.asyncio
async def test_create_profile(test_session: AsyncSession):
    """Test tạo profile mới"""
    repository = ProfileRepository(test_session)

    profile = Profile(
        username="testuser",
        bio="Test bio",
        avatar_url="https://example.com/avatar.jpg",
        birthdate="1990-01-01",
        user_id="user123"
    )

    result = await repository.create(profile)

    assert result.id is not None
    assert result.username == "testuser"
    assert result.bio == "Test bio"
    assert result.avatar_url == "https://example.com/avatar.jpg"
    assert result.birthdate == "1990-01-01"
    assert result.user_id == "user123"
    assert result.created_at is not None
    assert result.updated_at is not None


@pytest.mark.asyncio
async def test_get_by_id(test_session: AsyncSession):
    """Test lấy profile theo ID"""
    repository = ProfileRepository(test_session)

    # Tạo profile trước
    profile = Profile(username="testuser")
    created = await repository.create(profile)

    # Lấy theo ID
    result = await repository.get_by_id(created.id)

    assert result is not None
    assert result.id == created.id
    assert result.username == "testuser"


@pytest.mark.asyncio
async def test_get_by_id_not_found(test_session: AsyncSession):
    """Test lấy profile theo ID khi không tồn tại"""
    repository = ProfileRepository(test_session)

    result = await repository.get_by_id(999)

    assert result is None


@pytest.mark.asyncio
async def test_get_by_username(test_session: AsyncSession):
    """Test lấy profile theo username"""
    repository = ProfileRepository(test_session)

    # Tạo profile trước
    profile = Profile(username="testuser")
    created = await repository.create(profile)

    # Lấy theo username
    result = await repository.get_by_username("testuser")

    assert result is not None
    assert result.id == created.id
    assert result.username == "testuser"


@pytest.mark.asyncio
async def test_username_exists(test_session: AsyncSession):
    """Test kiểm tra username tồn tại"""
    repository = ProfileRepository(test_session)

    # Tạo profile trước
    profile = Profile(username="testuser")
    await repository.create(profile)

    # Check username tồn tại
    exists = await repository.username_exists("testuser")
    assert exists is True

    # Check username không tồn tại
    not_exists = await repository.username_exists("nonexistent")
    assert not_exists is False


@pytest.mark.asyncio
async def test_username_exists_with_exclude_id(test_session: AsyncSession):
    """Test kiểm tra username tồn tại với exclude_id"""
    repository = ProfileRepository(test_session)

    # Tạo profile trước
    profile = Profile(username="testuser")
    created = await repository.create(profile)

    # Check với exclude_id - nên trả về False (để cho phép giữ username cũ)
    exists = await repository.username_exists("testuser", exclude_id=created.id)
    assert exists is False

    # Check với exclude_id khác - nên trả về True
    exists = await repository.username_exists("testuser", exclude_id=999)
    assert exists is True


@pytest.mark.asyncio
async def test_search_by_username(test_session: AsyncSession):
    """Test tìm profile theo username (partial match)"""
    repository = ProfileRepository(test_session)

    # Tạo nhiều profiles
    await repository.create(Profile(username="john_doe"))
    await repository.create(Profile(username="jane_doe"))
    await repository.create(Profile(username="bob_smith"))

    # Tìm kiếm theo "doe"
    results = await repository.search_by_username("doe")

    assert len(results) == 2
    usernames = [p.username for p in results]
    assert "john_doe" in usernames
    assert "jane_doe" in usernames


@pytest.mark.asyncio
async def test_search_by_username_case_insensitive(test_session: AsyncSession):
    """Test tìm profile theo username không phân biệt hoa thường"""
    repository = ProfileRepository(test_session)

    # Tạo profile
    await repository.create(Profile(username="JohnDoe"))

    # Tìm kiếm với lowercase
    results = await repository.search_by_username("john")

    assert len(results) == 1
    assert results[0].username == "JohnDoe"


@pytest.mark.asyncio
async def test_get_all(test_session: AsyncSession):
    """Test lấy tất cả profiles với phân trang"""
    repository = ProfileRepository(test_session)

    # Tạo nhiều profiles
    await repository.create(Profile(username="user1"))
    await repository.create(Profile(username="user2"))
    await repository.create(Profile(username="user3"))

    # Lấy tất cả
    results = await repository.get_all()

    assert len(results) == 3

    # Test pagination
    results_paginated = await repository.get_all(skip=1, limit=2)
    assert len(results_paginated) == 2


@pytest.mark.asyncio
async def test_update_profile(test_session: AsyncSession):
    """Test cập nhật profile"""
    repository = ProfileRepository(test_session)

    # Tạo profile
    profile = Profile(username="testuser", bio="Original bio")
    created = await repository.create(profile)

    # Cập nhật
    created.bio = "Updated bio"
    result = await repository.update(created)

    assert result.bio == "Updated bio"
    assert result.updated_at >= created.updated_at


@pytest.mark.asyncio
async def test_delete_profile(test_session: AsyncSession):
    """Test xóa profile"""
    repository = ProfileRepository(test_session)

    # Tạo profile
    profile = Profile(username="testuser")
    created = await repository.create(profile)

    # Xóa
    await repository.delete(created)

    # Verify đã xóa
    result = await repository.get_by_id(created.id)
    assert result is None
