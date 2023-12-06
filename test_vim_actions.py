import pytest
from vim_actions import Op


@pytest.mark.parametrize(
    argnames=['arg', 'pos', 'exp_right', 'exp_delete', 'exp_clipboard'],
    argvalues=[
        # text object = 'w'
        (b'w', 0, 1, 1, "I"),  # "|I'm p.name !"
        (b'w', 1, 1, 1, "'"),  # "I|'m p.name !"
        (b'w', 2, 2, 2, "m "),  # "I'|m p.name !"
        (b'w', 3, 1, 1, " "),  # "I'm| p.name !"
        (b'w', 4, 1, 1, "p"),  # "I'm |p.name !"
        (b'w', 5, 1, 1, "."),  # "I'm p|.name !"
        (b'w', 6, 5, 5, "name "),  # "I'm p.|name !"
        (b'w', 7, 4, 4, "ame "),  # "I'm p.n|ame !"
        (b'w', 8, 3, 3, "me "),  # "I'm p.na|me !"
        (b'w', 9, 2, 2, "e "),  # "I'm p.nam|e !"
        (b'w', 10, 1, 1, " "),  # "I'm p.name| !"
        (b'w', 11, 1, 1, "!"),  # "I'm p.name |!"

        # same as above, but text object = 'W'
        (b'W', 0, 4, 4, "I'm "),  # "|I'm p.name !"
        (b'W', 1, 3, 3, "'m "),  # "I|'m p.name !"
        (b'W', 2, 2, 2, "m "),  # "I'|m p.name !"
        (b'W', 3, 1, 1, " "),  # "I'm| p.name !"
        (b'W', 4, 7, 7, "p.name "),  # "I'm |p.name !"
        (b'W', 5, 6, 6, ".name "),  # "I'm p|.name !"
        (b'W', 6, 5, 5, "name "),  # "I'm p.|name !"
        (b'W', 7, 4, 4, "ame "),  # "I'm p.n|ame !"
        (b'W', 8, 3, 3, "me "),  # "I'm p.na|me !"
        (b'W', 9, 2, 2, "e "),  # "I'm p.nam|e !"
        (b'W', 10, 1, 1, " "),  # "I'm p.name| !"
        (b'W', 11, 1, 1, "!"),  # "I'm p.name |!"

        # same as above, but text object = 'e'
        (b'e', 0, 2, 2, "I'"),  # "|I'm p.name !"
        (b'e', 1, 2, 2, "'m"),  # "I|'m p.name !"
        (b'e', 2, 3, 3, "m p"),  # "I'|m p.name !"
        (b'e', 3, 2, 2, " p"),  # "I'm| p.name !"
        (b'e', 4, 2, 2, "p."),  # "I'm |p.name !"
        (b'e', 5, 5, 5, ".name"),  # "I'm p|.name !"
        (b'e', 6, 4, 4, "name"),  # "I'm p.|name !"
        (b'e', 7, 3, 3, "ame"),  # "I'm p.n|ame !"
        (b'e', 8, 2, 2, "me"),  # "I'm p.na|me !"
        (b'e', 9, 3, 3, "e !"),  # "I'm p.nam|e !"
        (b'e', 10, 2, 2, " !"),  # "I'm p.name| !"
        (b'e', 11, 1, 1, "!"),  # "I'm p.name |!"

        # same as above, but text object = 'E'
        (b'E', 0, 3, 3, "I'm"),  # "|I'm p.name !"
        (b'E', 1, 2, 2, "'m"),  # "I|'m p.name !"
        (b'E', 2, 8, 8, "m p.name"),  # "I'|m p.name !"
        (b'E', 3, 7, 7, " p.name"),  # "I'm| p.name !"
        (b'E', 4, 6, 6, "p.name"),  # "I'm |p.name !"
        (b'E', 5, 5, 5, ".name"),  # "I'm p|.name !"
        (b'E', 6, 4, 4, "name"),  # "I'm p.|name !"
        (b'E', 7, 3, 3, "ame"),  # "I'm p.n|ame !"
        (b'E', 8, 2, 2, "me"),  # "I'm p.na|me !"
        (b'E', 9, 3, 3, "e !"),  # "I'm p.nam|e !"
        (b'E', 10, 2, 2, " !"),  # "I'm p.name| !"
        (b'E', 11, 1, 1, "!"),  # "I'm p.name |!"

        # same as above, but text object = '$'
        (b'$', 0, 12, 12, "I'm p.name !"),  # "|I'm p.name !"
        (b'$', 1, 11, 11, "'m p.name !"),  # "I|'m p.name !"
        (b'$', 2, 10, 10, "m p.name !"),  # "I'|m p.name !"
        (b'$', 3, 9, 9, " p.name !"),  # "I'm| p.name !"
        (b'$', 4, 8, 8, "p.name !"),  # "I'm |p.name !"
        (b'$', 5, 7, 7, ".name !"),  # "I'm p|.name !"
        (b'$', 6, 6, 6, "name !"),  # "I'm p.|name !"
        (b'$', 7, 5, 5, "ame !"),  # "I'm p.n|ame !"
        (b'$', 8, 4, 4, "me !"),  # "I'm p.na|me !"
        (b'$', 9, 3, 3, "e !"),  # "I'm p.nam|e !"
        (b'$', 10, 2, 2, " !"),  # "I'm p.name| !"
        (b'$', 11, 1, 1, "!"),  # "I'm p.name |!"

        # same as above, but text object = 'b'
        (b'b', 0, 0, 0, ""),  # "|I'm p.name !"
        (b'b', 1, 0, 1, "I"),  # "I|'m p.name !"
        (b'b', 2, 0, 1, "'"),  # "I'|m p.name !"
        (b'b', 3, 0, 1, "m"),  # "I'm| p.name !"
        (b'b', 4, 0, 2, "m "),  # "I'm |p.name !"
        (b'b', 5, 0, 1, "p"),  # "I'm p|.name !"
        (b'b', 6, 0, 1, "."),  # "I'm p.|name !"
        (b'b', 7, 0, 1, "n"),  # "I'm p.n|ame !"
        (b'b', 8, 0, 2, "na"),  # "I'm p.na|me !"
        (b'b', 9, 0, 3, "nam"),  # "I'm p.nam|e !"
        (b'b', 10, 0, 4, "name"),  # "I'm p.name| !"
        (b'b', 11, 0, 5, "name "),  # "I'm p.name |!"

        # same as above, but text object = 'B'
        (b'B', 0, 0, 0, ""),  # "|I'm p.name !"
        (b'B', 1, 0, 1, "I"),  # "I|'m p.name !"
        (b'B', 2, 0, 2, "I'"),  # "I'|m p.name !"
        (b'B', 3, 0, 3, "I'm"),  # "I'm| p.name !"
        (b'B', 4, 0, 4, "I'm "),  # "I'm |p.name !"
        (b'B', 5, 0, 1, "p"),  # "I'm p|.name !"
        (b'B', 6, 0, 2, "p."),  # "I'm p.|name !"
        (b'B', 7, 0, 3, "p.n"),  # "I'm p.n|ame !"
        (b'B', 8, 0, 4, "p.na"),  # "I'm p.na|me !"
        (b'B', 9, 0, 5, "p.nam"),  # "I'm p.nam|e !"
        (b'B', 10, 0, 6, "p.name"),  # "I'm p.name| !"
        (b'B', 11, 0, 7, "p.name "),  # "I'm p.name |!"

        # same as above, but text object = '0'
        (b'0', 0, 0, 0, ""),  # "|I'm p.name !"
        (b'0', 1, 0, 1, "I"),  # "I|'m p.name !"
        (b'0', 2, 0, 2, "I'"),  # "I'|m p.name !"
        (b'0', 3, 0, 3, "I'm"),  # "I'm| p.name !"
        (b'0', 4, 0, 4, "I'm "),  # "I'm |p.name !"
        (b'0', 5, 0, 5, "I'm p"),  # "I'm p|.name !"
        (b'0', 6, 0, 6, "I'm p."),  # "I'm p.|name !"
        (b'0', 7, 0, 7, "I'm p.n"),  # "I'm p.n|ame !"
        (b'0', 8, 0, 8, "I'm p.na"),  # "I'm p.na|me !"
        (b'0', 9, 0, 9, "I'm p.nam"),  # "I'm p.nam|e !"
        (b'0', 10, 0, 10, "I'm p.name"),  # "I'm p.name| !"
        (b'0', 11, 0, 11, "I'm p.name "),  # "I'm p.name |!"

        # same as above, but text object = 'd'
        (b'd', 0, 12, 12, "I'm p.name !"),  # "|I'm p.name !"
        (b'd', 1, 11, 12, "I'm p.name !"),  # "I|'m p.name !"
        (b'd', 2, 10, 12, "I'm p.name !"),  # "I'|m p.name !"
        (b'd', 3, 9, 12, "I'm p.name !"),  # "I'm| p.name !"
        (b'd', 4, 8, 12, "I'm p.name !"),  # "I'm |p.name !"
        (b'd', 5, 7, 12, "I'm p.name !"),  # "I'm p|.name !"
        (b'd', 6, 6, 12, "I'm p.name !"),  # "I'm p.|name !"
        (b'd', 7, 5, 12, "I'm p.name !"),  # "I'm p.n|ame !"
        (b'd', 8, 4, 12, "I'm p.name !"),  # "I'm p.na|me !"
        (b'd', 9, 3, 12, "I'm p.name !"),  # "I'm p.nam|e !"
        (b'd', 10, 2, 12, "I'm p.name !"),  # "I'm p.name| !"
        (b'd', 11, 1, 12, "I'm p.name !"),  # "I'm p.name |!"
    ]
)
def test_delete(arg, pos, exp_right, exp_delete, exp_clipboard):
    from vim_actions import Delete
    line = b"I'm p.name !"
    action = Delete()
    output, (clp,) = action.act(arg, line, pos)
    assert output == [Op.RIGHT] * exp_right + [Op.DELETE] * exp_delete
    assert clp.args == (exp_clipboard.encode(),)


@pytest.mark.parametrize(
    argnames=['arg', 'pos', 'exp_right', 'exp_delete', 'exp_clipboard'],
    argvalues=[
        # text object = '('
        (b'(', 0, 4, 3, "hey"),  # '|(hey)'
        (b'(', 1, 3, 3, "hey"),  # '(|hey)'
        (b'(', 2, 2, 3, "hey"),  # '(h|ey)'
        (b'(', 3, 1, 3, "hey"),  # '(he|y)'
        (b'(', 4, 0, 3, "hey"),  # '(hey|)'

        # same as above, except text object = ')'
        (b')', 0, 4, 3, "hey"),  # '|(hey)'
        (b')', 1, 3, 3, "hey"),  # '(|hey)'
        (b')', 2, 2, 3, "hey"),  # '(h|ey)'
        (b')', 3, 1, 3, "hey"),  # '(he|y)'
        (b')', 4, 0, 3, "hey"),  # '(hey|)'

        # same as above, except text object = 'w'
        (b'w', 0, 1, 1, "("),  # '|(hey)'
        (b'w', 1, 3, 3, "hey"),  # '(|hey)'
        (b'w', 2, 2, 3, "hey"),  # '(h|ey)'
        (b'w', 3, 1, 3, "hey"),  # '(he|y)'
        (b'w', 4, 1, 1, ")"),  # '(hey|)'

        # same as above, except text object = 'W'
        (b'W', 0, 5, 5, "(hey)"),  # '|(hey)'
        (b'W', 1, 4, 5, "(hey)"),  # '(|hey)'
        (b'W', 2, 3, 5, "(hey)"),  # '(h|ey)'
        (b'W', 3, 2, 5, "(hey)"),  # '(he|y)'
        (b'W', 4, 1, 5, "(hey)"),  # '(hey|)'

        # same as above, except text object is nonexistent, should always fail
        (b'[', 0, 0, 0, None),  # '|(hey)'
        (b'{', 1, 0, 0, None),  # '(|hey)'
        (b'.', 2, 0, 0, None),  # '(h|ey)'
        (b'`', 3, 0, 0, None),  # '(he|y)'
        (b' ', 4, 0, 0, None),  # '(hey|)'

        # unsupported text object
        (b'\r', 2, 0, 0, None),  # '(h|ey)'
    ]
)
def test_delete_in_between(arg, pos, exp_right, exp_delete, exp_clipboard):
    from vim_actions import DeleteInBetween
    line = b"(hey)"
    action = DeleteInBetween()
    output, side_effects = action.act(arg, line, pos)
    assert output == exp_right * [Op.RIGHT] + exp_delete * [Op.DELETE]
    if exp_clipboard is None:
        assert side_effects == []
    else:
        clp, = side_effects
        assert clp.args == (exp_clipboard.encode(),)


@pytest.mark.parametrize(
    argnames=['arg', 'pos', 'exp_count', 'exp_clipboard'],
    argvalues=[
        [b"A", 0, 0, None],  # "|ABCDBCD"
        [b"Z", 0, 0, None],  # "|ABCDBCD"
        [b"B", 0, 1, "A"],  # "|ABCDBCD"
        [b"C", 0, 2, "AB"],  # "|ABCDBCD"
        [b"D", 0, 3, "ABC"],  # "|ABCDBCD"

        [b"A", 2, 0, None],  # "AB|CDBCD"
        [b"Z", 2, 0, None],  # "AB|CDBCD"
        [b"B", 2, 2, "CD"],  # "AB|CDBCD"
        [b"C", 2, 3, "CDB"],  # "AB|CDBCD"
        [b"D", 2, 1, "C"],  # "AB|CDBCD"

        [b"A", 6, 0, None],  # "ABCDBC|D"
        [b"Z", 6, 0, None],  # "ABCDBC|D"
        [b"B", 6, 0, None],  # "ABCDBC|D"
        [b"C", 6, 0, None],  # "ABCDBC|D"
        [b"D", 6, 0, None],  # "ABCDBC|D"
    ]
)
def test_delete_till(arg, pos, exp_count, exp_clipboard):
    from vim_actions import DeleteTill
    line = b"ABCDBCD"
    action = DeleteTill()
    output, side_effects = action.act(arg, line, pos)
    assert output == [Op.RIGHT] * exp_count + [Op.DELETE] * exp_count
    if exp_clipboard is None:
        assert side_effects == []
    else:
        clp, = side_effects
        assert clp.args == (exp_clipboard.encode(),)
