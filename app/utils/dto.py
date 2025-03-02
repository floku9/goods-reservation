from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field


class ReservationDTO(BaseModel):
    reservation_id: Annotated[int, Field(gt=0, description="Reservation ID must be greater than 0")]
    product_id: Annotated[int, Field(gt=0, description="Product ID must be greater than 0")]
    quantity: Annotated[int, Field(gt=0, description="Quantity must be greater than 0")]
    timestamp: Annotated[datetime, Field(gt=datetime(1970, 1, 1))]


class ReservationResponse(BaseModel):
    status: str
    message: str
    reservation_id: int
