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


SEARCH_FILE = "search-history.txt"
SEARCH_CONTENT = """
:a
:b
:aa
:aaa
:bbb
"""


@pytest.fixture
def search_file():
    with open(SEARCH_FILE, "w") as f:
        f.write(SEARCH_CONTENT)
    yield
    if os.path.exists(SEARCH_FILE):
        os.remove(SEARCH_FILE)


def test_history_search_next(search_file):
    with HistoryManager(SEARCH_FILE) as hm:
        hm.start_search("a+")

        hm.set_buffer(b"abcd")
        hm.ingest()

        line, match = hm.search_next()
        assert line == b"a"

        line, match = hm.search_next()
        assert line == b"aa"

        line, match = hm.search_next()
        assert line == b"aaa"

        line, match = hm.search_next()
        assert line == b"abcd"

        hm.set_buffer(b"abcdefg")
        hm.ingest()

        line, match = hm.search_prev()
        assert line == b"abcdefg"

        line, match = hm.search_next()
        assert line == b"a"

        line, match = hm.search_prev()
        assert line == b"abcdefg"

        hm.start_search("z")

        line, match = hm.search_next()
        assert line is None

        line, match = hm.search_prev()
        assert line is None
