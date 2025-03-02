# Custom exception class accepting ReservationResponse
from app.utils.dto import ReservationResponse


class ReservationException(Exception):
    def __init__(self, status_code: int, response: ReservationResponse):
        self.status_code = status_code
        self.response = response


class ProductNotFoundException(ReservationException):
    def __init__(self, reservation_id: int):
        super().__init__(
            404,
            ReservationResponse(
                status="error",
                message="Product not found",
                reservation_id=reservation_id,
            ),
        )


class ProductIsReservedException(ReservationException):
    def __init__(self, reservation_id: int):
        super().__init__(
            409,
            ReservationResponse(
                status="error",
                message="This product is already reserved",
                reservation_id=reservation_id,
            ),
        )


class ReservationClosedException(ReservationException):
    def __init__(self, reservation_id: int):
        super().__init__(
            409,
            ReservationResponse(
                status="error",
                message="Reservation is closed or confirmed",
                reservation_id=reservation_id,
            ),
        )


class NotEnoughProductsException(ReservationException):
    def __init__(self, reservation_id: int):
        super().__init__(
            422,
            ReservationResponse(
                status="error",
                message="Not enough products available",
                reservation_id=reservation_id,
            ),
        )


class ReservationIsLockedException(ReservationException):
    def __init__(self, reservation_id: int):
        super().__init__(
            423,
            ReservationResponse(
                status="error",
                message="Reservation is locked by another transaction",
                reservation_id=reservation_id,
            ),
        )


class ReservationNotFoundException(ReservationException):
    def __init__(self, reservation_id: int):
        super().__init__(
            404,
            ReservationResponse(
                status="error",
                message="Reservation not found",
                reservation_id=reservation_id,
            ),
        )
