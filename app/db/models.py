from datetime import datetime
from enum import Enum
from typing import List

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class ReservationStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class Base(DeclarativeBase):
    pass


class ProductReservation(Base):
    __tablename__ = "products_reservations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reservation_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("reservations.id"), nullable=False
    )
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    reservation_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    reservation: Mapped["Reservation"] = relationship(lazy="selectin")
    product: Mapped["Product"] = relationship(lazy="selectin")

    __table_args__ = (
        UniqueConstraint("reservation_id", "product_id", name="uq_reservation_product"),
    )


class Reservation(Base):
    __tablename__ = "reservations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status: Mapped[ReservationStatus] = mapped_column(String, nullable=False)

    product_reservations: Mapped[List["ProductReservation"]] = relationship(
        back_populates="reservation", lazy="selectin"
    )


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    price: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer)

    product_reservations: Mapped[List["ProductReservation"]] = relationship(
        back_populates="product", lazy="selectin"
    )
