from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.features.profiles.schemas import ProfileCreate, ProfileUpdate, ProfilePublic
from app.features.profiles.service import ProfileService

router = APIRouter(prefix="/profiles", tags=["profiles"])


def get_profile_service(session: AsyncSession = Depends(get_session)) -> ProfileService:
    """Dependency để inject ProfileService"""
    return ProfileService(session)


@router.post("/", response_model=ProfilePublic, status_code=201)
async def create_profile(
    profile_data: ProfileCreate,
    service: ProfileService = Depends(get_profile_service)
):
    """Tạo profile mới

    Validation:
    - Username: 3-50 chars, alphanumeric + underscore/dash, unique
    - Bio: max 500 chars
    - Avatar URL: phải là valid URL nếu provided
    - Birthdate: format YYYY-MM-DD, không phải future date
    """
    return await service.create_profile(profile_data)


@router.get("/", response_model=List[ProfilePublic])
async def get_profiles(
    skip: int = Query(0, ge=0, description="Số profiles để skip (pagination)"),
    limit: int = Query(100, ge=1, le=100, description="Số profiles tối đa trả về"),
    username: Optional[str] = Query(None, description="Tìm kiếm theo username (partial match)"),
    service: ProfileService = Depends(get_profile_service)
):
    """Lấy danh sách profiles với phân trang và tìm kiếm

    - Nếu không có filter: trả về tất cả profiles (mới nhất trước)
    - Nếu có username: tìm kiếm theo username (case-insensitive, partial match)
    """
    return await service.search_profiles(
        username_query=username,
        skip=skip,
        limit=limit
    )


@router.get("/{profile_id}", response_model=ProfilePublic)
async def get_profile(
    profile_id: int,
    service: ProfileService = Depends(get_profile_service)
):
    """Lấy thông tin chi tiết profile theo ID"""
    return await service.get_profile_by_id(profile_id)


@router.get("/by-username/{username}", response_model=ProfilePublic)
async def get_profile_by_username(
    username: str,
    service: ProfileService = Depends(get_profile_service)
):
    """Lấy profile theo username (exact match)"""
    return await service.get_profile_by_username(username)


@router.patch("/{profile_id}", response_model=ProfilePublic)
async def update_profile(
    profile_id: int,
    profile_data: ProfileUpdate,
    service: ProfileService = Depends(get_profile_service)
):
    """Cập nhật thông tin profile

    Chỉ cập nhật các fields được cung cấp (partial update)
    - Username: phải unique nếu thay đổi
    - Tất cả validations tương tự create
    """
    return await service.update_profile(profile_id, profile_data)


@router.delete("/{profile_id}", status_code=204)
async def delete_profile(
    profile_id: int,
    service: ProfileService = Depends(get_profile_service)
):
    """Xóa profile"""
    await service.delete_profile(profile_id)
    return None
