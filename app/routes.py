from typing import Annotated

from asyncpg.exceptions import LockNotAvailableError
from fastapi import APIRouter, Depends
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.crud import (
    add_product_reservation,
    add_reservation,
    get_product,
    get_product_reservation,
    get_reservation,
)
from app.db.models import ReservationStatus
from app.dependencies import get_db_session
from app.utils.dto import ReservationDTO, ReservationResponse
from app.utils.exceptions import (
    NotEnoughProductsException,
    ProductIsReservedException,
    ProductNotFoundException,
    ReservationClosedException,
    ReservationIsLockedException,
    ReservationNotFoundException,
)
from app.utils.logging import logger

reservation_router = APIRouter(prefix="/reservation", tags=["reservation"])


@reservation_router.post("/make", response_model=ReservationResponse)
async def make_reservation(
    reservation_dto: ReservationDTO, session: Annotated[AsyncSession, Depends(get_db_session)]
) -> ReservationResponse:
    """
    Creates a new reservation or updates an existing one for a given product and quantity.
    \f
    Args:
        reservation_dto (ReservationDTO): The reservation details, including the reservation ID,
            product ID, and quantity.
        session (AsyncSession): The database session to use for the operation.

    Returns:
        ReservationResponse: A response object containing the status, message, and reservation ID.

    Raises:
        ProductNotFoundException: If the specified product does not exist.
        ReservationClosedException: If the reservation is not in the pending state.
        ProductIsReservedException: If the product is already reserved with the same quantity.
        NotEnoughProductsException: If the requested quantity exceeds the
            available product quantity.
        ReservationIsLockedException: If the reservation is locked due to a database error.
    """
    try:
        async with session.begin():
            product = await get_product(reservation_dto.product_id, session, True)
            if not product:
                logger.error(f"Product with id {reservation_dto.product_id} not found")
                raise ProductNotFoundException(reservation_dto.reservation_id)

            reservation = await get_reservation(reservation_dto.reservation_id, session, True)
            if not reservation:
                logger.info(
                    f"Reservation with id {reservation_dto.reservation_id} not found, "
                    "adding new one."
                )
                reservation = await add_reservation(reservation_dto.reservation_id, session)

            elif reservation.status != ReservationStatus.PENDING:
                logger.info(f"Reservation with id {reservation_dto.reservation_id} is not pending")
                raise ReservationClosedException(reservation_dto.reservation_id)

            product_in_reservation = await get_product_reservation(
                reservation_dto.reservation_id, reservation_dto.product_id, session, True
            )

            change = 0
            if product_in_reservation:
                logger.info(
                    f"Product {reservation_dto.product_id} is reserved for reservation {reservation_dto.reservation_id}. "  # noqa
                    f"Checking if it's reservation amount change"
                )

                if product_in_reservation.reservation_quantity == reservation_dto.quantity:
                    logger.error(
                        f"Product with id {reservation_dto.product_id} is already reserved for "
                        f"reservation id {reservation_dto.reservation_id} with the same quantity"
                    )
                    raise ProductIsReservedException(reservation_dto.reservation_id)
                else:
                    logger.info(
                        f"Changing amount of product id {reservation_dto.product_id} "
                        f"in reservation id {reservation_dto.reservation_id}"
                    )
                    change = product_in_reservation.reservation_quantity - reservation_dto.quantity
            else:
                product_in_reservation = await add_product_reservation(
                    reservation_dto.reservation_id,
                    reservation_dto.product_id,
                    reservation_dto.quantity,
                    reservation_dto.timestamp,
                    session,
                )
                change = -reservation_dto.quantity

            if product.quantity + change < 0:
                logger.error(
                    f"Not enough products for reservation."
                    f"Change: {change}, quantity of product {product.quantity}:"
                )
                raise NotEnoughProductsException(reservation_dto.reservation_id)
            else:
                product.quantity += change
                product_in_reservation.reservation_quantity = reservation_dto.quantity
                product_in_reservation.date = reservation_dto.timestamp
                await session.flush()
                await session.commit()
                logger.info(
                    f"Reservation was created/updated successfully. "
                    f"Product: {product.id} Quantity Change: {change}"  # noqa
                )

            return ReservationResponse(
                status="success",
                message="Reservation created/updated",
                reservation_id=reservation_dto.reservation_id,
            )

    except DBAPIError as db_err:
        # Check if the error is due to a lock not being available
        orig_exception = db_err.orig
        if isinstance(orig_exception, LockNotAvailableError) or isinstance(
            orig_exception.__cause__,  # type: ignore
            LockNotAvailableError,
        ):
            raise ReservationIsLockedException(reservation_dto.reservation_id)
        else:
            raise db_err


@reservation_router.get("/status/{reservation_id}", response_model=ReservationResponse)
async def check_reservation_status(
    reservation_id: int, session: Annotated[AsyncSession, Depends(get_db_session)]
):
    """
    Retrieves the status of a reservation by the given reservation ID.
    \f

    Args:
        reservation_id (int): The ID of the reservation to check.
        session (AsyncSession): The database session to use for the operation.

    Returns:
        ReservationResponse: A response object containing the status of the reservation.

    Raises:
        ReservationNotFoundException: If the reservation with the given ID is not found.
    """

    reservation = await get_reservation(reservation_id, session, False)
    if not reservation:
        raise ReservationNotFoundException(reservation_id)

    return ReservationResponse(
        status="success",
        message=f"Reservation status: {reservation.status}",
        reservation_id=reservation_id,
    )


@reservation_router.put("/confirm/{reservation_id}", response_model=ReservationResponse)
async def confirm_reservation(
    reservation_id: int, session: Annotated[AsyncSession, Depends(get_db_session)]
):
    """
    Confirms a reservation with the given reservation ID.
    \f

    Args:
        reservation_id (int): The ID of the reservation to close.
        session (AsyncSession): The database session to use for the operation.

    Raises:
        ReservationNotFoundException: If the reservation with the given ID is not found.
        ReservationClosedException: If the reservation is not in the pending status.

    Returns:
        ReservationResponse: A response object containing the status of the closed reservation.
    """
    reservation = await get_reservation(reservation_id, session, True)
    if not reservation:
        raise ReservationNotFoundException(reservation_id)
    if reservation.status != ReservationStatus.PENDING:
        raise ReservationClosedException(reservation_id)

    reservation.status = ReservationStatus.CONFIRMED
    await session.flush()
    await session.commit()
    return ReservationResponse(
        status="success",
        message="Reservation confirmed",
        reservation_id=reservation_id,
    )
