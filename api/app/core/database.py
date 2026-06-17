from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.engine import URL


class Base(DeclarativeBase):
    pass


def _create_engine():
    from app.core.config import get_settings
    s = get_settings()
    url = URL.create(
        drivername="postgresql+asyncpg",
        username=s.postgres_user,
        password=s.postgres_password,
        host=s.postgres_host,
        port=s.postgres_port,
        database=s.postgres_db,
    )
    return create_async_engine(url, echo=False, pool_pre_ping=True)


engine = _create_engine()

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise