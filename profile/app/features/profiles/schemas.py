from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel
from app.features.profiles.model import ProfileBase


class ProfileCreate(ProfileBase):
    """Schema để tạo profile mới"""
    pass


class ProfileUpdate(SQLModel):
    """Schema để cập nhật profile (tất cả fields optional)"""
    username: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    birthdate: Optional[str] = None
    user_id: Optional[str] = None


class ProfilePublic(ProfileBase):
    """Schema để trả về profile cho client"""
    id: int
    created_at: datetime
    updated_at: datetime
