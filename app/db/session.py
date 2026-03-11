from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings


engine = create_async_engine(
    str(settings.DATABASE_URL),

    # debugging
    echo=False,

    # When using Supabase "Transaction pooler" (PgBouncer pool_mode=transaction),
    # disable SQLAlchemy pooling and let PgBouncer do pooling.
    poolclass=NullPool,

    # Fix PgBouncer prepared statement issue
    connect_args={
        # asyncpg option
        "statement_cache_size": 0,
        # SQLAlchemy asyncpg dialect option (kept for compatibility across versions)
        "prepared_statement_cache_size": 0,
    }
    
)
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@asynccontextmanager
async def get_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

