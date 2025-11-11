import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

# Use SQLite with async driver
#DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite+aiosqlite:///./test.db"

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True
)

# Async session
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()

# Dependency for FastAPI or other frameworks
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
