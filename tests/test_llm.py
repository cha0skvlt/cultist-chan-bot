from unittest import mock


import asyncio
from aiohttp import web
import pytest

from cultist_chan_bot.llm import query_llm


@pytest.mark.asyncio
async def test_query_llm_returns_clean_response():
    async def handler(request: web.Request) -> web.Response:
        return web.json_response({'response': ' hi '})

    app = web.Application()
    app.router.add_post('/', handler)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', 0)
    await site.start()
    port = site._server.sockets[0].getsockname()[1]
    url = f'http://127.0.0.1:{port}/'

    with mock.patch('cultist_chan_bot.llm._CFG') as cfg:
        cfg.LLM_URL = url
        result = await query_llm('hello')
    assert result == 'hi'
    await runner.cleanup()


@pytest.mark.asyncio
async def test_llm_async():
    with mock.patch('aiohttp.ClientSession.post', side_effect=asyncio.TimeoutError):
        with pytest.raises(RuntimeError, match='timed out'):
            await query_llm('x')

    from aiohttp import ClientConnectionError

    with mock.patch('aiohttp.ClientSession.post', side_effect=ClientConnectionError('bad')):
        with pytest.raises(RuntimeError, match='failed'):
            await query_llm('x')
