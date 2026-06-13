from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class DatabaseManager:
    def __init__(self, url: str):
        self.engine = create_async_engine(url)
        self.session = sessionmaker(self.engine, class_=AsyncSession)

    async def get_session(self) -> AsyncSession:
        async with self.session() as session:
            yield session
