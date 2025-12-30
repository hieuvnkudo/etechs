from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from app.features.profiles.model import Profile


class ProfileRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, profile: Profile) -> Profile:
        """Tạo profile mới"""
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def get_by_id(self, profile_id: int) -> Optional[Profile]:
        """Lấy profile theo ID"""
        return await self.session.get(Profile, profile_id)

    async def get_by_username(self, username: str) -> Optional[Profile]:
        """Lấy profile theo username (exact match)"""
        statement = select(Profile).where(Profile.username == username)
        result = await self.session.execute(statement)
        return result.scalars().first()

    async def username_exists(self, username: str, exclude_id: Optional[int] = None) -> bool:
        """Kiểm tra username đã tồn tại chưa

        Args:
            username: Username cần kiểm tra
            exclude_id: ID của profile hiện tại (dùng khi update)

        Returns:
            True nếu username đã tồn tại, False nếu chưa
        """
        statement = select(Profile).where(Profile.username == username)

        if exclude_id is not None:
            statement = statement.where(Profile.id != exclude_id)

        result = await self.session.execute(statement)
        return result.scalars().first() is not None

    async def search_by_username(
        self,
        username_query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Profile]:
        """Tìm profile theo username (partial match, case-insensitive)"""
        statement = select(Profile).where(
            Profile.username.ilike(f"%{username_query}%")
        )
        statement = statement.offset(skip).limit(limit).order_by(Profile.username)

        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Profile]:
        """Lấy tất cả profiles với phân trang"""
        statement = select(Profile)
        statement = statement.offset(skip).limit(limit).order_by(Profile.created_at.desc())

        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def update(self, profile: Profile) -> Profile:
        """Cập nhật profile"""
        profile.updated_at = datetime.now(timezone.utc)
        self.session.add(profile)
        await self.session.commit()
        await self.session.refresh(profile)
        return profile

    async def delete(self, profile: Profile) -> None:
        """Xóa profile"""
        await self.session.delete(profile)
        await self.session.commit()
