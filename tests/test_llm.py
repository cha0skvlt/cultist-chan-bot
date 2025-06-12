from unittest import mock


import asyncio
from aiohttp import web
import aiohttp
import pytest

from cultist_chan_bot.llm import generate_reply


@pytest.mark.asyncio
async def test_generate_reply_returns_clean_response():
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

    with mock.patch('cultist_chan_bot.llm.llm._CFG') as cfg:
        cfg.LLM_URL = url
        result = await generate_reply('hello')
        async with aiohttp.ClientSession() as sess:
            second = await generate_reply('hi', session=sess)
    assert result == 'hi'
    assert second == 'hi'
    await runner.cleanup()


@pytest.mark.asyncio
async def test_llm_async():
    with mock.patch('aiohttp.ClientSession.post', side_effect=asyncio.TimeoutError):
        with pytest.raises(RuntimeError, match='timed out'):
            await generate_reply('x')

    from aiohttp import ClientConnectionError

    with mock.patch('aiohttp.ClientSession.post', side_effect=ClientConnectionError('bad')):
        with pytest.raises(RuntimeError, match='failed'):
            await generate_reply('x')
