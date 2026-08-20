#backend/database.py

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from constants import DATABASE_URL

engine = create_async_engine(DATABASE_URL)

SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
            await db.commit()
        except:
            await db.rollback()
            raise