import asyncio
from datetime import datetime

import pytest
from asyncpg.exceptions import LockNotAvailableError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.db.crud import (
    add_product_reservation,
    add_reservation,
    get_product,
    get_product_reservation,
    get_reservation,
)
from app.db.models import ReservationStatus


@pytest.mark.asyncio
async def test_get_product_exists(test_db_session):
    product = await get_product(product_id=1, session=test_db_session, lock=False)
    assert product is not None
    assert product.id == 1
    assert product.name == "Product 1"
    assert product.quantity == 10
    assert product.price == 100


@pytest.mark.asyncio
async def test_get_product_not_exists(test_db_session):
    product = await get_product(product_id=999, session=test_db_session, lock=False)
    assert product is None


@pytest.mark.asyncio
async def test_get_reservation_exists(test_db_session):
    reservation = await get_reservation(reservation_id=1, session=test_db_session, lock=False)
    assert reservation is not None
    assert reservation.id == 1
    assert reservation.status == ReservationStatus.PENDING


@pytest.mark.asyncio
async def test_get_reservation_not_exists(test_db_session):
    reservation = await get_reservation(reservation_id=999, session=test_db_session, lock=False)
    assert reservation is None


@pytest.mark.asyncio
async def test_get_product_reservation_exists(test_db_session):
    product_reservation = await get_product_reservation(
        reservation_id=1, product_id=1, session=test_db_session, lock=False
    )
    assert product_reservation is not None
    assert product_reservation.reservation_id == 1
    assert product_reservation.product_id == 1
    assert product_reservation.reservation_quantity == 2
    assert product_reservation.date == datetime(2025, 1, 1)


@pytest.mark.asyncio
async def test_get_product_reservation_not_exists(test_db_session):
    product_reservation = await get_product_reservation(
        reservation_id=999, product_id=999, session=test_db_session, lock=False
    )
    assert product_reservation is None


@pytest.mark.asyncio
async def test_add_reservation(test_db_session):
    new_reservation_id = 2
    reservation = await add_reservation(reservation_id=new_reservation_id, session=test_db_session)

    assert reservation is not None
    assert reservation.id == new_reservation_id
    assert reservation.status == ReservationStatus.PENDING

    check_reservation = await get_reservation(
        reservation_id=new_reservation_id, session=test_db_session, lock=False
    )
    assert check_reservation is not None
    assert check_reservation.id == new_reservation_id


@pytest.mark.asyncio
async def test_add_existing_product_reservation(test_db_session):
    with pytest.raises(Exception):
        await add_product_reservation(
            reservation_id=1,
            product_id=1,
            quantity=3,
            date=datetime(2025, 2, 1),
            session=test_db_session,
        )


@pytest.mark.asyncio
async def test_add_new_product_reservation(test_db_session):
    new_product_reservation = await add_product_reservation(
        reservation_id=1,
        product_id=2,
        quantity=3,
        date=datetime(2025, 2, 1),
        session=test_db_session,
    )

    assert new_product_reservation is not None
    assert new_product_reservation.reservation_id == 1
    assert new_product_reservation.product_id == 2


@pytest.mark.skip("Not working with sqlite")
@pytest.mark.asyncio(scope="session")
async def test_concurrent_locking(test_db_engine):
    async def locking_get_product(
        product_id: int, db_engine: AsyncEngine, lock_time: float
    ) -> None:
        async with AsyncSession(db_engine) as session:
            async with session.begin():
                await get_product(product_id=product_id, session=session, lock=True)
                await asyncio.sleep(lock_time)

    task_1 = asyncio.create_task(locking_get_product(1, test_db_engine, 2))

    await asyncio.sleep(0.5)

    task_2 = asyncio.create_task(locking_get_product(1, test_db_engine, 0))

    results = await asyncio.gather(
        task_1,
        task_2,
        return_exceptions=True,
    )

    assert not isinstance(results[0], Exception)

    assert isinstance(results[1].orig.__cause__, LockNotAvailableError)  # type: ignore
