from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession


class SessionFactory:
    def __init__(self, db_url : str):
        self._engine = create_async_engine(url=db_url)
        self._session_maker = async_sessionmaker(bind=self._engine)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._engine.dispose()

    def __call__(self, *args, **kwargs) -> async_sessionmaker[AsyncSession]:
        return self._session_maker