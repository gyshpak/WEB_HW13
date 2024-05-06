import asyncio

from datetime import date

import pytest
import pytest_asyncio

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from main import app
from src.database.models import Base, Contact
from src.database.db import get_db
from src.services.auth import auth_service

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)

test_contact1 = {
    "name": "test1_name",
    "email": "testemail1@ukr.net",
    "phone": "0674444441",
    "birthday": date(1975, 12, 12),
    "password": "12345678"
}

test_contact2 = {
    "name": "test2_name",
    "email": "testemail2@ukr.net",
    "phone": "0674444442",
    "birthday": date(2010, 12, 12),
    "password": "123456",
}

@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            hash_password = auth_service.get_password_hash(test_contact1["password"])
            current_contact = Contact(
                name=test_contact1["name"],
                email=test_contact1["email"],
                phone=test_contact1["phone"],
                birthday=test_contact1["birthday"],
                password=hash_password,
                confirmed=True,
            )
            session.add(current_contact)

            hash_password = auth_service.get_password_hash(test_contact2["password"])
            current_contact = Contact(
                name=test_contact2["name"],
                email=test_contact2["email"],
                phone=test_contact2["phone"],
                birthday=test_contact2["birthday"],
                password=hash_password,
                confirmed=True,
            )
            session.add(current_contact)
            await session.commit()

    asyncio.run(init_models())


@pytest.fixture(scope="module")
def client():
    # Dependency override

    async def override_get_db():
        session = TestingSessionLocal()
        try:
            yield session
        except Exception as err:
            print(err)
            await session.rollback()
        finally:
            await session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest_asyncio.fixture()
async def get_token():
    token = await auth_service.create_access_token(data={"sub": test_contact1["email"]})
    return token
