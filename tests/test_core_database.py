from unittest import mock
import importlib
import pytest


@pytest.mark.asyncio
async def test_database_pool():
    from cultist_chan_bot.core import database
    importlib.reload(database)

    settings = type(
        'S',
        (),
        {
            'POSTGRES_HOST': 'h',
            'POSTGRES_USER': 'u',
            'POSTGRES_PASS': 'p',
            'POSTGRES_NAME': 'n',
        },
    )()

    pool = mock.AsyncMock()
    with mock.patch('asyncpg.create_pool', new=mock.AsyncMock(return_value=pool)) as create:
        result = await database.create_pool(settings)
    assert result is pool
    assert database.get_pool() is pool

    pool.close = mock.AsyncMock()
    await database.close_pool()
    pool.close.assert_awaited_once()
    create.assert_awaited_once_with(
        host='h', user='u', password='p', database='n'
    )

