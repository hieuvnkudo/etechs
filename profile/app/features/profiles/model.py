from typing import Optional
from sqlmodel import Field, SQLModel
from app.core.mixins import TimestampMixin


class ProfileBase(SQLModel):
    """Base model cho Profile với các fields chung"""
    username: str = Field(index=True, max_length=50, unique=True)
    bio: Optional[str] = Field(default=None, max_length=500)
    avatar_url: Optional[str] = Field(default=None, max_length=2048)
    birthdate: Optional[str] = None
    user_id: Optional[str] = Field(default=None, max_length=100)


class Profile(ProfileBase, TimestampMixin, table=True):
    """Database model cho Profile"""
    id: Optional[int] = Field(default=None, primary_key=True)
