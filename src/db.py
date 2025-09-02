import os
from typing import AsyncGenerator
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker

DB_DSN = os.getenv("DB_DSN", "postgresql+asyncpg://ecad:ecadpw@db:5432/ecad")

engine: AsyncEngine = create_async_engine(DB_DSN, future=True, echo=False)
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

GUARD_TOUCH_SQLS = [
    """
    CREATE OR REPLACE FUNCTION parts_guard_and_touch()
    RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      IF TG_OP='UPDATE' AND NEW.name IS DISTINCT FROM OLD.name THEN
        RAISE EXCEPTION 'parts.name is immutable once assigned';
      END IF;
      NEW.updated_at := now();
      RETURN NEW;
    END $$;
    """,
    "DROP TRIGGER IF EXISTS trg_parts_guard_touch ON parts;",
    """
    CREATE TRIGGER trg_parts_guard_touch
    BEFORE UPDATE ON parts
    FOR EACH ROW EXECUTE FUNCTION parts_guard_and_touch();
    """
]

async def init_db(install_triggers: bool = True) -> None:
    # import models to register metadata
    from src.definitions.parts import Category, Part  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        if install_triggers:
            for s in GUARD_TOUCH_SQLS:
                await conn.exec_driver_sql(s)
