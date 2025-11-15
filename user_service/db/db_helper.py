from asyncio import current_task
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
    AsyncSession,
)
from core.config import settings


class DatabaseHelper:
    def __init__(self, url: str, echo: bool = False):
        # 1. Создаем engine внутри класса
        self.engine = create_async_engine(
            url=url,
            echo=echo,
        )
        
        # 2. Создаем фабрику сессий внутри класса
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    # 3. Метод для получения сессии (Dependency)
    # Он заменяет функцию get_db_session, которую мы обсуждали раньше
    async def session_dependency(self):
        async with self.session_factory() as session:
            yield session
            await session.close()

    # 4. Метод для Scoped Session (опционально, для продвинутых кейсов)
    def get_scoped_session(self):
        session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task,
        )
        return session

db_helper = DatabaseHelper(
    url=settings.DATABASE_URL,
    echo=settings.DB_ECHO,
)