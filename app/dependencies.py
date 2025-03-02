from app.db.setup import async_session_factory


async def get_db_session():
    async with async_session_factory() as session:
        yield session
