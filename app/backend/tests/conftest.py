import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from database import get_db
from models.base import Base
from models.user import User
from app import app
from auth.security import hash_password
from config import settings

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)

async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session
        await session.commit()

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(autouse=True)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # 2. Seed the admin user from settings
    async with TestingSessionLocal() as session:
        admin_email = getattr(settings, "admin_email", "admin@example.com")
        admin_password = getattr(settings, "admin_password", "adminpassword")
        admin_username = getattr(settings, "admin_username", "admin")
        
        admin_user = User(
            email=admin_email,
            username=admin_username,
            password_hash=hash_password(admin_password),
            is_admin=True
        )
        session.add(admin_user)
        await session.commit()
        
    yield
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def admin_headers_factory(client):
    """Provides headers for the seeded admin user."""
    async def _get_admin_headers():
        admin_email = getattr(settings, "admin_email", "admin@example.com")
        admin_password = getattr(settings, "admin_password", "adminpassword")
        
        resp = await client.post("/auth/login", json={"email": admin_email, "password": admin_password})
        token = resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return _get_admin_headers
    
@pytest_asyncio.fixture
async def auth_headers_factory(client, admin_headers_factory):
    """Uses the admin endpoint to create a standard test user, then logs in as them."""
    async def _get_headers(email="test@example.com"):
        admin_headers = await admin_headers_factory()
        
        # Create standard user via admin endpoint
        await client.post(
            "/admin/users", 
            headers=admin_headers, 
            json={"email": email, "password": "supersecretpassword"}
        )
        
        # Log in as the standard user
        resp = await client.post(
            "/auth/login", 
            json={"email": email, "password": "supersecretpassword"}
        )
        token = resp.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return _get_headers