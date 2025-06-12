from unittest import mock
import numpy as np
import importlib
import faiss


def test_memory_embedding_store_and_retrieve(tmp_path):
    import cultist_chan_bot.memory as mem
    importlib.reload(mem)
    mem._INDEX_PATH = tmp_path / 'idx'
    mem._DATA_PATH = mem._INDEX_PATH.with_suffix('.json')
    mem._INDEX = faiss.IndexFlatIP(2)
    mem._DATA = []
    mem._EMBED_DIM = 2
    with mock.patch('cultist_chan_bot.memory._embed') as embed:
        embed.side_effect = [
            np.array([[1.0, 0.0]], dtype='float32'),
            np.array([[0.0, 1.0]], dtype='float32'),
            np.array([[1.0, 0.0]], dtype='float32'),
        ]
        mem.save_interaction(1, 'hello', 'world')
        mem.save_interaction(1, 'bye', 'now')
        ctx = mem.retrieve_context(1, k=1, query='hello again')
    assert ctx == [{'message': 'hello', 'reply': 'world'}]


def test_memory_persistence(tmp_path):
    path = tmp_path / 'mem.idx'
    with mock.patch('cultist_chan_bot.config.load_config') as loader:
        loader.return_value = type('S', (), {'MEMORY_PATH': str(path)})()
        mem = importlib.reload(__import__('cultist_chan_bot.memory', fromlist=['']))
    vec = np.ones((1, mem._EMBED_DIM), dtype='float32')
    with mock.patch('cultist_chan_bot.memory._embed', return_value=vec):
        mem.save_interaction(2, 'hi', 'there')
    with mock.patch('cultist_chan_bot.config.load_config') as loader:
        loader.return_value = type('S', (), {'MEMORY_PATH': str(path)})()
        mem = importlib.reload(__import__('cultist_chan_bot.memory', fromlist=['']))
    with mock.patch('cultist_chan_bot.memory._embed', return_value=vec):
        ctx = mem.retrieve_context(2, k=1, query='hi')
    assert ctx == [{'message': 'hi', 'reply': 'there'}]
