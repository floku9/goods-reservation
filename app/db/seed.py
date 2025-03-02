import asyncio
from datetime import datetime

from sqlalchemy import select

from app.db.models import Product, ProductReservation, Reservation
from app.db.setup import async_session_factory


async def seed_data():
    """
    Creates initial data if it doesn't exist id DB.
    NB! Use only if db already created with alembic
    """
    async with async_session_factory() as session:
        result = await session.execute(select(Product).limit(1))
        product = result.scalars().first()

        if product is not None:
            print("Data already exists. No seeding required.")
            return

        print("Seeding initial data...")

        products = [
            Product(name="Product 1", price=100, quantity=10),
            Product(name="Product 2", price=200, quantity=5),
            Product(name="Product 3", price=300, quantity=15),
        ]
        reservation = Reservation(status="pending")
        products_reservation = ProductReservation(
            reservation=reservation,
            product=products[0],
            reservation_quantity=1,
            date=datetime.now(),
        )

        session.add_all([*products, reservation, products_reservation])
        await session.commit()
        print("Seeding completed.")


async def main():
    await seed_data()


if __name__ == "__main__":
    asyncio.run(main())
