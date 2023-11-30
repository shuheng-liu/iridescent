import pytest
import os
from history import HistoryManager

FILENAME = "history_file.txt"
INIT_CONTENT = ":aaa\n:bbb\n:ccc\n"


@pytest.fixture
def history_file():
    with open(FILENAME, "w") as f:
        f.write(INIT_CONTENT)
    yield
    if os.path.exists(FILENAME):
        os.remove(FILENAME)


def test_history_manager(history_file):
    with HistoryManager(FILENAME, 2) as hm:
        assert hm.retrieve_buffer() == b""

        hm.set_buffer(b"d")
        assert hm.retrieve_buffer() == b"d"

        hm.set_buffer(b"dd")
        assert hm.retrieve_buffer() == b"dd"

        assert hm.go_prev() == b"ccc"
        assert hm.go_next() == b"dd"
        assert hm.go_prev() == b"ccc"
        assert hm.go_prev() == b"bbb"
        assert hm.go_prev() == b"dd"

        hm.ingest()
        assert hm.retrieve_buffer() == b""

    with open(FILENAME) as f:
        content = f.read()
        assert content == INIT_CONTENT + ":dd\n"
