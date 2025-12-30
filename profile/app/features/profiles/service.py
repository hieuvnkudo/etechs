import re
from datetime import datetime, date
from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.features.profiles.model import Profile
from app.features.profiles.schemas import ProfileCreate, ProfileUpdate
from app.features.profiles.repository import ProfileRepository
from app.core.exceptions import NotFoundError, ConflictError, APIValidationError


class ProfileService:
    def __init__(self, session: AsyncSession):
        self.repository = ProfileRepository(session)

    def _validate_username(self, username: str) -> None:
        """Validate username format

        Rules:
        - Length: 3-50 characters
        - Pattern: only alphanumeric, underscore, dash
        """
        if not (3 <= len(username) <= 50):
            raise APIValidationError(
                f"Username phải từ 3 đến 50 ký tự (hiện tại: {len(username)})"
            )

        if not re.match(r'^[a-zA-Z0-9_-]+$', username):
            raise APIValidationError(
                "Username chỉ được chứa chữ cái, số, dấu gạch dưới (_) và dấu gạch ngang (-)"
            )

    def _validate_birthdate(self, birthdate_str: Optional[str]) -> Optional[date]:
        """Validate và parse birthdate string"""
        if birthdate_str is None:
            return None

        try:
            birthdate = datetime.strptime(birthdate_str, "%Y-%m-%d").date()
        except ValueError:
            raise APIValidationError(
                f"Birthdate phải ở định dạng YYYY-MM-DD (nhận: {birthdate_str})"
            )

        # Check không phải future date
        if birthdate > date.today():
            raise APIValidationError(
                "Birthdate không thể là ngày trong tương lai"
            )

        # Check không quá xa xưa (trước 1900)
        if birthdate < date(1900, 1, 1):
            raise APIValidationError(
                "Birthdate không thể trước năm 1900"
            )

        return birthdate

    def _validate_avatar_url(self, avatar_url: Optional[str]) -> None:
        """Validate avatar URL format (basic validation)"""
        if avatar_url is None:
            return

        # Basic URL validation - check protocol
        if not (avatar_url.startswith("http://") or avatar_url.startswith("https://")):
            raise APIValidationError(
                "Avatar URL phải bắt đầu với http:// hoặc https://"
            )

    async def create_profile(self, profile_data: ProfileCreate) -> Profile:
        """Tạo profile mới với validation đầy đủ"""
        # Validate username format
        self._validate_username(profile_data.username)

        # Validate birthdate
        self._validate_birthdate(profile_data.birthdate)

        # Validate avatar URL
        self._validate_avatar_url(profile_data.avatar_url)

        # Check username uniqueness
        if await self.repository.username_exists(profile_data.username):
            raise ConflictError(
                f"Username '{profile_data.username}' đã được sử dụng"
            )

        # Create profile
        profile = Profile(
            username=profile_data.username,
            bio=profile_data.bio,
            avatar_url=profile_data.avatar_url,
            birthdate=profile_data.birthdate,
            user_id=profile_data.user_id
        )

        try:
            return await self.repository.create(profile)
        except IntegrityError:
            # Fallback check trong case có race condition
            raise ConflictError(
                f"Username '{profile_data.username}' đã được sử dụng"
            )

    async def get_profile_by_id(self, profile_id: int) -> Profile:
        """Lấy profile theo ID"""
        profile = await self.repository.get_by_id(profile_id)
        if not profile:
            raise NotFoundError(resource="Profile", resource_id=profile_id)
        return profile

    async def get_profile_by_username(self, username: str) -> Profile:
        """Lấy profile theo username (exact match)"""
        profile = await self.repository.get_by_username(username)
        if not profile:
            raise NotFoundError(resource="Profile", resource_id=username)
        return profile

    async def search_profiles(
        self,
        username_query: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Profile]:
        """Tìm profiles với filter và phân trang"""
        if username_query:
            return await self.repository.search_by_username(
                username_query=username_query,
                skip=skip,
                limit=limit
            )
        else:
            return await self.repository.get_all(skip=skip, limit=limit)

    async def update_profile(
        self,
        profile_id: int,
        profile_data: ProfileUpdate
    ) -> Profile:
        """Cập nhật profile với validation"""
        profile = await self.get_profile_by_id(profile_id)

        update_data = profile_data.model_dump(exclude_unset=True)

        # Validate username nếu được update
        if "username" in update_data:
            new_username = update_data["username"]
            self._validate_username(new_username)

            # Check username uniqueness (exclude current profile)
            if await self.repository.username_exists(new_username, exclude_id=profile_id):
                raise ConflictError(
                    f"Username '{new_username}' đã được sử dụng"
                )

        # Validate birthdate nếu được update
        if "birthdate" in update_data:
            birthdate_str = update_data["birthdate"]
            self._validate_birthdate(birthdate_str)

        # Validate avatar_url nếu được update
        if "avatar_url" in update_data:
            avatar_url = update_data["avatar_url"]
            self._validate_avatar_url(avatar_url)

        # Apply updates
        for field, value in update_data.items():
            setattr(profile, field, value)

        return await self.repository.update(profile)

    async def delete_profile(self, profile_id: int) -> None:
        """Xóa profile"""
        profile = await self.get_profile_by_id(profile_id)
        await self.repository.delete(profile)
