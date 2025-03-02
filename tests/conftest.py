from datetime import datetime

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.models import Base, Product, ProductReservation, Reservation, ReservationStatus

test_db_url = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def test_db_engine():
    engine = create_async_engine(test_db_url, echo=False)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def create_tables(test_db_engine):
    async with test_db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture(scope="session")
def session_factory(test_db_engine):
    return async_sessionmaker(
        bind=test_db_engine,
        class_=AsyncSession,
    )


@pytest_asyncio.fixture(scope="session")
async def populate_test_db(session_factory, create_tables):
    async with session_factory() as session:
        product = Product(name="Product 1", quantity=10, price=100)
        product_2 = Product(name="Product 2", quantity=5, price=50)
        reservation = Reservation(status=ReservationStatus.PENDING)
        product_reservation = ProductReservation(
            product=product,
            reservation=reservation,
            reservation_quantity=2,
            date=datetime(2025, 1, 1),
        )
        session.add_all([product, reservation, product_reservation, product_2])
        await session.commit()


@pytest_asyncio.fixture(scope="function")
async def test_db_session(session_factory, populate_test_db):
    async with session_factory() as session:
        yield session
        await session.rollback()
