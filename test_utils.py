import pytest


@pytest.mark.parametrize(
    argnames=['pos', 'expected'],
    argvalues=[
        [-1, Exception],
        [0, 0],  # "| ABCD EFGH "
        [1, 0],  # " |ABCD EFGH "
        [2, 2],  # " A|BCD EFGH "
        [3, 2],  # " AB|CD EFGH "
        [4, 2],  # " ABC|D EFGH "
        [5, 2],  # " ABCD| EFGH "
        [6, 6],  # " ABCD |EFGH "
        [7, 7],  # " ABCD E|FGH "
        [8, 7],  # " ABCD EF|GH "
        [9, 7],  # " ABCD EFG|H "
        [10, 7],  # " ABCD EFGH| "
        [11, 11],  # " ABCD EFGH |"
        [12, Exception],
    ]
)
def test_chunk_leftmost(pos, expected):
    from utils import _chunk_leftmost as cl
    content = b" ABCD EFGH "
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            cl(content, pos)
    else:
        output = cl(content, pos)
        assert output == expected


@pytest.mark.parametrize(
    argnames=['pos', 'expected'],
    argvalues=[
        [-1, Exception],
        [0, 0],  # "| ABCD EFGH "
        [1, 4],  # " |ABCD EFGH "
        [2, 4],  # " A|BCD EFGH "
        [3, 4],  # " AB|CD EFGH "
        [4, 4],  # " ABC|D EFGH "
        [5, 5],  # " ABCD| EFGH "
        [6, 9],  # " ABCD |EFGH "
        [7, 9],  # " ABCD E|FGH "
        [8, 9],  # " ABCD EF|GH "
        [9, 9],  # " ABCD EFG|H "
        [10, 10],  # " ABCD EFGH| "
        [11, 11],  # " ABCD EFGH |"
        [12, Exception],
    ]
)
def test_chunk_rightmost(pos, expected):
    from utils import _chunk_rightmost as cr
    content = b" ABCD EFGH "
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            cr(content, pos)
    else:
        output = cr(content, pos)
        assert output == expected


@pytest.mark.parametrize(
    argnames=['npos', 'expected', 'capital'],
    argvalues=[
        [-1, Exception, True],
        [0, 1, True],  # "| |A@C  ^%G  "
        [1, 6, True],  # " |A|@C  ^%G  "
        [2, 6, True],  # " A|@|C  ^%G  "
        [3, 6, True],  # " A@|C|  ^%G  "
        [4, 6, True],  # " A@C| | ^%G  "
        [5, 6, True],  # " A@C | |^%G  "
        [6, 11, True],  # " A@C  |^|%G  "
        [7, 11, True],  # " A@C  ^|%|G  "
        [8, 11, True],  # " A@C  ^%|G|  "
        [9, 11, True],  # " A@C  ^%G| | "
        [10, 11, True],  # " A@C  ^%G | |"
        [11, Exception, True],

        # same as above, but capital is set to False
        [-1, Exception, False],
        [0, 1, False],  # "| |A@C  ^%G  "
        [1, 2, False],  # " |A|@C  ^%G  "
        [2, 3, False],  # " A|@|C  ^%G  "
        [3, 6, False],  # " A@|C|  ^%G  "
        [4, 6, False],  # " A@C| | ^%G  "
        [5, 6, False],  # " A@C | |^%G  "
        [6, 8, False],  # " A@C  |^|%G  "
        [7, 8, False],  # " A@C  ^|%|G  "
        [8, 11, False],  # " A@C  ^%|G|  "
        [9, 11, False],  # " A@C  ^%G| | "
        [10, 11, False],  # " A@C  ^%G | |"
        [11, Exception, False],
    ]
)
def test_vim_word(npos, expected, capital):
    from utils import vim_word
    content = b" A@C  ^%G  "

    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            vim_word(content, npos, capital=capital)
    else:
        output = vim_word(content, npos, capital=capital)
        assert output == expected


@pytest.mark.parametrize(
    argnames=['npos', 'expected', 'capital'],
    argvalues=[
        [-1, Exception, True],
        [0, 3, True],  # "| |A@C  ^%G  "
        [1, 3, True],  # " |A|@C  ^%G  "
        [2, 3, True],  # " A|@|C  ^%G  "
        [3, 8, True],  # " A@|C|  ^%G  "
        [4, 8, True],  # " A@C| | ^%G  "
        [5, 8, True],  # " A@C | |^%G  "
        [6, 8, True],  # " A@C  |^|%G  "
        [7, 8, True],  # " A@C  ^|%|G  "
        [8, 11, True],  # " A@C  ^%|G|  "
        [9, 11, True],  # " A@C  ^%G| | "
        [10, 11, True],  # " A@C  ^%G | |"
        [11, Exception, True],

        # same as above, but capital is set to False
        [-1, Exception, False],
        [0, 1, False],  # "| |A@C  ^%G  "
        [1, 2, False],  # " |A|@C  ^%G  "
        [2, 3, False],  # " A|@|C  ^%G  "
        [3, 7, False],  # " A@|C|  ^%G  "
        [4, 7, False],  # " A@C| | ^%G  "
        [5, 7, False],  # " A@C | |^%G  "
        [6, 7, False],  # " A@C  |^|%G  "
        [7, 8, False],  # " A@C  ^|%|G  "
        [8, 11, False],  # " A@C  ^%|G|  "
        [9, 11, False],  # " A@C  ^%G| | "
        [10, 11, False],  # " A@C  ^%G | |"
        [11, Exception, False],
    ]
)
def test_vim_word_end(npos, expected, capital):
    from utils import vim_word_end
    content = b" A@C  ^%G  "

    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            vim_word_end(content, npos, capital=capital)
    else:
        output = vim_word_end(content, npos, capital=capital)
        assert output == expected


@pytest.mark.parametrize(
    argnames=['npos', 'expected', 'capital'],
    argvalues=[
        [-1, Exception, True],
        [0, -1, True],  # "| |A@C  ^%G  "
        [1, -1, True],  # " |A|@C  ^%G  "
        [2, 1, True],  # " A|@|C  ^%G  "
        [3, 1, True],  # " A@|C|  ^%G  "
        [4, 1, True],  # " A@C| | ^%G  "
        [5, 1, True],  # " A@C | |^%G  "
        [6, 1, True],  # " A@C  |^|%G  "
        [7, 6, True],  # " A@C  ^|%|G  "
        [8, 6, True],  # " A@C  ^%|G|  "
        [9, 6, True],  # " A@C  ^%G| | "
        [10, 6, True],  # " A@C  ^%G | |"
        [11, Exception, True],

        # same as above, but capital is set to False
        [-1, Exception, False],
        [0, -1, False],  # "| |A@C  ^%G  "
        [1, -1, False],  # " |A|@C  ^%G  "
        [2, 1, False],  # " A|@|C  ^%G  "
        [3, 2, False],  # " A@|C|  ^%G  "
        [4, 3, False],  # " A@C| | ^%G  "
        [5, 3, False],  # " A@C | |^%G  "
        [6, 3, False],  # " A@C  |^|%G  "
        [7, 6, False],  # " A@C  ^|%|G  "
        [8, 6, False],  # " A@C  ^%|G|  "
        [9, 8, False],  # " A@C  ^%G| | "
        [10, 8, False],  # " A@C  ^%G | |"
        [11, Exception, False],
    ]
)
def test_vim_word_begin(npos, expected, capital):
    from utils import vim_word_begin
    content = b" A@C  ^%G  "

    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            vim_word_begin(content, npos, capital=capital)
    else:
        output = vim_word_begin(content, npos, capital=capital)
        assert output == expected


@pytest.mark.parametrize(
    argnames=["npos", "err"],
    argvalues=[
        [-1, True],
        [0, False],
        [1, False],
        [2, False],
    ]
)
def test_vim_line_begin(npos, err):
    from utils import vim_line_begin
    content = b"ABC"
    if err:
        with pytest.raises(Exception):
            vim_line_begin(content, npos, False)
    else:
        assert vim_line_begin(content, npos, False) == 0


@pytest.mark.parametrize(
    argnames=["npos", "err"],
    argvalues=[
        [-1, True],
        [0, False],
        [1, False],
        [2, False],
    ]
)
def test_vim_line_begin(npos, err):
    from utils import vim_line_end
    content = b"ABC"
    if err:
        with pytest.raises(Exception):
            vim_line_end(content, npos, False)
    else:
        assert vim_line_end(content, npos, False) == 2


@pytest.mark.parametrize(
    argnames=['npos', 'expected', 'capital'],
    argvalues=[
        # find forward
        [-1, Exception, False],
        [0, 1, False],  # "|A|BCABC"
        [1, 4, False],  # "A|B|CABC"
        [2, 4, False],  # "AB|C|ABC"
        [3, 4, False],  # "ABC|A|BC"
        [4, 6, False],  # "ABCA|B|C"
        [5, 6, False],  # "ABCAB|C|"
        [6, Exception, False],
        # find backward
        [-1, Exception, True],
        [0, -1, True],  # "|A|BCABC"
        [1, -1, True],  # "A|B|CABC"
        [2, 1, True],  # "AB|C|ABC"
        [3, 1, True],  # "ABC|A|BC"
        [4, 1, True],  # "ABCA|B|C"
        [5, 4, True],  # "ABCAB|C|"
        [6, Exception, True],
    ]
)
def test_vim_find(npos, expected, capital):
    from utils import vim_find
    content = b"ABCABC"
    needle = b"B"
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            vim_find(content, npos, needle, capital)
    else:
        assert vim_find(content, npos, needle, capital) == expected


@pytest.mark.parametrize(
    argnames=['npos', 'expected', 'capital'],
    argvalues=[
        # find forward
        [-1, Exception, False],
        [0, 0, False],  # "|A|BCABC"
        [1, 3, False],  # "A|B|CABC"
        [2, 3, False],  # "AB|C|ABC"
        [3, 3, False],  # "ABC|A|BC"
        [4, 6, False],  # "ABCA|B|C"
        [5, 6, False],  # "ABCAB|C|"
        [6, Exception, False],
        # find backward
        [-1, Exception, True],
        [0, -1, True],  # "|A|BCABC"
        [1, -1, True],  # "A|B|CABC"
        [2, 2, True],  # "AB|C|ABC"
        [3, 2, True],  # "ABC|A|BC"
        [4, 2, True],  # "ABCA|B|C"
        [5, 5, True],  # "ABCAB|C|"
        [6, Exception, True],
    ]
)
def test_vim_till(npos, expected, capital):
    from utils import vim_till
    content = b"ABCABC"
    needle = b"B"
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            vim_till(content, npos, needle, capital)
    else:
        assert vim_till(content, npos, needle, capital) == expected
