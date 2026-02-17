import json
import asyncio

from database.models import Video, VideoSnapshot, VideoDataPydantic
from core import DBDependency


async def load_videos() -> None:
    """Загружает данные из JSON файла в базу данных."""
    try:
        with open("database/videos.json", 'r', encoding='utf-8') as f:
            data = json.load(f)

        validated_data = VideoDataPydantic(**data)

        videos = []
        snapshots = []

        for video in validated_data.videos:
            videos.append(Video(**video.model_dump(exclude={'snapshots'})))
            snapshots.extend(
                VideoSnapshot(**snapshot.model_dump())
                for snapshot in video.snapshots
            )

        async with DBDependency().db_session() as session:
            session.add_all(videos + snapshots)
            await session.commit()
    except Exception as e:
        print(f"Ошибка: {e}")
    else:
        print(f"Загружено объектов: {len(videos)}")


if __name__ == "__main__":
    asyncio.run(load_videos())
