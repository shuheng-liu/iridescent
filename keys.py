class OPTION:
    LEFT = b'\x1bb'
    RIGHT = b'\x1bf'
    UP = b'\x1b[1;9A'
    DOWN = b'\x1b[1;9B'
    DELETE = b'\x1b\x7f'


class SIG:
    INT = b'\x03'
    BELL = b'\x07'


class CTRL:
    R = b'\x12'


DELETE = b'\x7f'
ESCAPE = b'\x1b'
ENTER = b'\r'

UP = b'\x1b[A'
DOWN = b'\x1b[B'
RIGHT = b'\x1b[C'
LEFT = b'\x1b[D'

ESCAPE_SEQUENCE = b'\x1d'
