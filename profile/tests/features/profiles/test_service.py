import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.profiles.service import ProfileService
from app.features.profiles.schemas import ProfileCreate, ProfileUpdate
from app.core.exceptions import NotFoundError, ConflictError, APIValidationError


@pytest.mark.asyncio
async def test_create_profile_success(test_session: AsyncSession):
    """Test tạo profile thành công"""
    service = ProfileService(test_session)

    profile_data = ProfileCreate(
        username="testuser",
        bio="Test bio",
        avatar_url="https://example.com/avatar.jpg",
        birthdate="1990-01-01",
        user_id="user123"
    )

    result = await service.create_profile(profile_data)

    assert result.id is not None
    assert result.username == "testuser"
    assert result.bio == "Test bio"


@pytest.mark.asyncio
async def test_create_profile_invalid_username_too_short(test_session: AsyncSession):
    """Test tạo profile với username quá ngắn"""
    service = ProfileService(test_session)

    profile_data = ProfileCreate(username="ab")

    with pytest.raises(APIValidationError) as exc_info:
        await service.create_profile(profile_data)

    assert "Username phải từ 3 đến 50 ký tự" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_create_profile_invalid_username_too_long(test_session: AsyncSession):
    """Test tạo profile với username quá dài"""
    service = ProfileService(test_session)

    # Pydantic sẽ validate trước, nên test này cho Pydantic validation
    with pytest.raises(Exception) as exc_info:
        ProfileCreate(username="a" * 51)

    # Pydantic validation error
    assert "string_too_long" in str(exc_info.value) or "at most 50" in str(exc_info.value)


@pytest.mark.asyncio
async def test_create_profile_invalid_username_chars(test_session: AsyncSession):
    """Test tạo profile với username chứa ký tự không hợp lệ"""
    service = ProfileService(test_session)

    profile_data = ProfileCreate(username="user@name")

    with pytest.raises(APIValidationError) as exc_info:
        await service.create_profile(profile_data)

    assert "Username chỉ được chứa chữ cái, số" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_create_profile_duplicate_username(test_session: AsyncSession):
    """Test tạo profile với username trùng"""
    service = ProfileService(test_session)

    # Tạo profile đầu tiên
    profile_data1 = ProfileCreate(username="testuser")
    await service.create_profile(profile_data1)

    # Thử tạo profile thứ hai với username trùng
    profile_data2 = ProfileCreate(username="testuser")

    with pytest.raises(ConflictError) as exc_info:
        await service.create_profile(profile_data2)

    assert "đã được sử dụng" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_create_profile_invalid_birthdate_format(test_session: AsyncSession):
    """Test tạo profile với birthdate sai format"""
    service = ProfileService(test_session)

    profile_data = ProfileCreate(
        username="testuser",
        birthdate="01-01-1990"  # Sai format
    )

    with pytest.raises(APIValidationError) as exc_info:
        await service.create_profile(profile_data)

    assert "Birthdate phải ở định dạng YYYY-MM-DD" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_create_profile_future_birthdate(test_session: AsyncSession):
    """Test tạo profile với birthdate trong tương lai"""
    service = ProfileService(test_session)

    profile_data = ProfileCreate(
        username="testuser",
        birthdate="2099-01-01"
    )

    with pytest.raises(APIValidationError) as exc_info:
        await service.create_profile(profile_data)

    assert "không thể là ngày trong tương lai" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_create_profile_too_old_birthdate(test_session: AsyncSession):
    """Test tạo profile với birthdate quá cũ"""
    service = ProfileService(test_session)

    profile_data = ProfileCreate(
        username="testuser",
        birthdate="1800-01-01"
    )

    with pytest.raises(APIValidationError) as exc_info:
        await service.create_profile(profile_data)

    assert "không thể trước năm 1900" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_create_profile_invalid_avatar_url(test_session: AsyncSession):
    """Test tạo profile với avatar URL không hợp lệ"""
    service = ProfileService(test_session)

    profile_data = ProfileCreate(
        username="testuser",
        avatar_url="ftp://example.com/avatar.jpg"  # Không phải http/https
    )

    with pytest.raises(APIValidationError) as exc_info:
        await service.create_profile(profile_data)

    assert "phải bắt đầu với http:// hoặc https://" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_profile_by_id_success(test_session: AsyncSession):
    """Test lấy profile theo ID thành công"""
    service = ProfileService(test_session)

    # Tạo profile
    profile_data = ProfileCreate(username="testuser")
    created = await service.create_profile(profile_data)

    # Lấy theo ID
    result = await service.get_profile_by_id(created.id)

    assert result.id == created.id
    assert result.username == "testuser"


@pytest.mark.asyncio
async def test_get_profile_by_id_not_found(test_session: AsyncSession):
    """Test lấy profile theo ID khi không tồn tại"""
    service = ProfileService(test_session)

    with pytest.raises(NotFoundError) as exc_info:
        await service.get_profile_by_id(999)

    assert "not found" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_get_profile_by_username_success(test_session: AsyncSession):
    """Test lấy profile theo username thành công"""
    service = ProfileService(test_session)

    # Tạo profile
    profile_data = ProfileCreate(username="testuser")
    created = await service.create_profile(profile_data)

    # Lấy theo username
    result = await service.get_profile_by_username("testuser")

    assert result.id == created.id
    assert result.username == "testuser"


@pytest.mark.asyncio
async def test_get_profile_by_username_not_found(test_session: AsyncSession):
    """Test lấy profile theo username khi không tồn tại"""
    service = ProfileService(test_session)

    with pytest.raises(NotFoundError):
        await service.get_profile_by_username("nonexistent")


@pytest.mark.asyncio
async def test_search_profiles_no_filter(test_session: AsyncSession):
    """Test tìm kiếm profiles không có filter"""
    service = ProfileService(test_session)

    # Tạo profiles
    await service.create_profile(ProfileCreate(username="user1"))
    await service.create_profile(ProfileCreate(username="user2"))

    # Tìm kiếm không filter
    results = await service.search_profiles()

    assert len(results) == 2


@pytest.mark.asyncio
async def test_search_profiles_with_query(test_session: AsyncSession):
    """Test tìm kiếm profiles với username query"""
    service = ProfileService(test_session)

    # Tạo profiles
    await service.create_profile(ProfileCreate(username="john_doe"))
    await service.create_profile(ProfileCreate(username="jane_doe"))
    await service.create_profile(ProfileCreate(username="bob_smith"))

    # Tìm kiếm
    results = await service.search_profiles(username_query="doe")

    assert len(results) == 2
    usernames = [p.username for p in results]
    assert "john_doe" in usernames
    assert "jane_doe" in usernames


@pytest.mark.asyncio
async def test_update_profile_success(test_session: AsyncSession):
    """Test cập nhật profile thành công"""
    service = ProfileService(test_session)

    # Tạo profile
    created = await service.create_profile(
        ProfileCreate(username="testuser", bio="Original bio")
    )

    # Cập nhật
    update_data = ProfileUpdate(bio="Updated bio")
    result = await service.update_profile(created.id, update_data)

    assert result.bio == "Updated bio"


@pytest.mark.asyncio
async def test_update_profile_username_conflict(test_session: AsyncSession):
    """Test cập nhật profile với username đã tồn tại"""
    service = ProfileService(test_session)

    # Tạo 2 profiles
    profile1 = await service.create_profile(ProfileCreate(username="user1"))
    await service.create_profile(ProfileCreate(username="user2"))

    # Cập nhật profile1 với username của profile2
    update_data = ProfileUpdate(username="user2")

    with pytest.raises(ConflictError):
        await service.update_profile(profile1.id, update_data)


@pytest.mark.asyncio
async def test_update_profile_keep_same_username(test_session: AsyncSession):
    """Test cập nhật profile và giữ nguyên username"""
    service = ProfileService(test_session)

    # Tạo profile
    created = await service.create_profile(ProfileCreate(username="testuser"))

    # Cập nhật nhưng giữ username cũ
    update_data = ProfileUpdate(username="testuser", bio="New bio")
    result = await service.update_profile(created.id, update_data)

    assert result.username == "testuser"
    assert result.bio == "New bio"


@pytest.mark.asyncio
async def test_delete_profile_success(test_session: AsyncSession):
    """Test xóa profile thành công"""
    service = ProfileService(test_session)

    # Tạo profile
    created = await service.create_profile(ProfileCreate(username="testuser"))

    # Xóa
    await service.delete_profile(created.id)

    # Verify đã xóa
    with pytest.raises(NotFoundError):
        await service.get_profile_by_id(created.id)


@pytest.mark.asyncio
async def test_delete_profile_not_found(test_session: AsyncSession):
    """Test xóa profile khi không tồn tại"""
    service = ProfileService(test_session)

    with pytest.raises(NotFoundError):
        await service.delete_profile(999)
