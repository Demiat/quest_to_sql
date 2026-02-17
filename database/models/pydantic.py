from pydantic import BaseModel
from datetime import datetime


class BaseVideoPydantic(BaseModel):
    """Общие поля для таблиц видео."""

    id: str
    views_count: int
    likes_count: int
    comments_count: int
    reports_count: int


class VideoSnapshotPydantic(BaseVideoPydantic):
    video_id: str
    reports_count: int
    delta_views_count: int
    delta_likes_count: int
    delta_comments_count: int
    delta_reports_count: int
    created_at: datetime
    updated_at: datetime


class VideoPydantic(BaseVideoPydantic):
    creator_id: str
    video_created_at: datetime
    created_at: datetime
    updated_at: datetime
    snapshots: list[VideoSnapshotPydantic]


class VideoDataPydantic(BaseModel):
    """Схема для JSON структуры с ключом videos."""
    videos: list[VideoPydantic]
