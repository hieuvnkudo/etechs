from datetime import datetime, timezone
from typing import Optional
from sqlmodel import Field


class TimestampMixin:
    """Mixin để thêm timestamp fields cho models

    Cung cấp created_at và updated_at fields với automatic timezone handling.
    """

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Thời gian tạo record"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Thời gian cập nhật record lần cuối"
    )
