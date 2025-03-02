from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from app.db.models import Product, ProductReservation, Reservation, ReservationStatus


async def get_product(
    product_id: int, session: AsyncSession, lock: bool = True
) -> Optional[Product]:
    stmt = select(Product).where(Product.id == product_id)
    if lock:
        stmt = stmt.with_for_update(nowait=True)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_reservation(
    reservation_id: int, session: AsyncSession, lock: bool = True
) -> Optional[Reservation]:
    stmt = select(Reservation).where(Reservation.id == reservation_id)
    if lock:
        stmt = stmt.with_for_update(nowait=True)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_product_reservation(
    reservation_id: int, product_id: int, session: AsyncSession, lock: bool = True
) -> Optional[ProductReservation]:
    stmt = select(ProductReservation).where(
        ProductReservation.reservation_id == reservation_id,
        ProductReservation.product_id == product_id,
    )
    if lock:
        stmt = stmt.with_for_update(nowait=True)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def add_reservation(reservation_id: int, session: AsyncSession) -> Reservation:
    reservation = Reservation(id=reservation_id, status=ReservationStatus.PENDING)
    session.add(reservation)
    await session.flush()
    return reservation


async def add_product_reservation(
    reservation_id: int, product_id: int, quantity: int, date: datetime, session: AsyncSession
) -> ProductReservation:
    product_reservation = ProductReservation(
        reservation_id=reservation_id,
        product_id=product_id,
        reservation_quantity=quantity,
        date=date,
    )
    session.add(product_reservation)
    await session.flush()
    return product_reservation
