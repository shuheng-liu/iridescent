import pytest


@pytest.fixture
def content():
    return b" ABCD EFGH "


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
def test_chunk_leftmost(pos, expected, content):
    from utils import _chunk_leftmost as cl
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
def test_chunk_rightmost(pos, expected, content):
    from utils import _chunk_rightmost as cr
    if isinstance(expected, type) and issubclass(expected, Exception):
        with pytest.raises(expected):
            cr(content, pos)
    else:
        output = cr(content, pos)
        assert output == expected
