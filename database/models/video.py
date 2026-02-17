from datetime import datetime

from sqlalchemy import String, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Базовый класс моделей."""
    pass


class VideoBaseModel(Base):
    """Абстрактная модель с общими полями."""
    __abstract__ = True

    views_count: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0)
    likes_count: Mapped[int] = mapped_column(default=0)
    comments_count: Mapped[int] = mapped_column(default=0)
    reports_count: Mapped[int] = mapped_column(default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)


class Video(VideoBaseModel):
    """Итоговая статистика по каждому видео."""

    __tablename__ = 'videos'

    id: Mapped[str] = mapped_column(primary_key=True)
    creator_id: Mapped[str] = mapped_column(index=True)
    video_created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)

    snapshots: Mapped[list["VideoSnapshot"]] = relationship(
        back_populates="video",
        cascade="all, delete-orphan"
    )


class VideoSnapshot(VideoBaseModel):
    """Почасовые «снапшоты» статистики по каждому видео."""

    __tablename__ = 'video_snapshots'

    id: Mapped[str] = mapped_column(primary_key=True)
    video_id: Mapped[str] = mapped_column(
        String,
        ForeignKey('videos.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )

    delta_views_count: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0)
    delta_likes_count: Mapped[int] = mapped_column(default=0)
    delta_comments_count: Mapped[int] = mapped_column(default=0)
    delta_reports_count: Mapped[int] = mapped_column(default=0)

    video: Mapped["Video"] = relationship(back_populates="snapshots")
