from .setup_keyboard import load_strokes, ESCAPE_SEQUENCE


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


class KEY:
    DELETE = b'\x7f'
    ESCAPE = b'\x1b'
    ENTER = b'\r'

    UP = b'\x1b[A'
    DOWN = b'\x1b[B'
    RIGHT = b'\x1b[C'
    LEFT = b'\x1b[D'


def _attempt_set_key(k, v):
    cls = globals()[k.split(".")[0]]
    old_v = getattr(cls, k.split(".")[1])
    if v != old_v:
        print(f"Overwriting {k} from {repr(old_v)} to {repr(v)}")
    setattr(cls, k.split(".")[1], v)


def set_keys():
    d = load_strokes()
    for k, v in d.items():
        _attempt_set_key(k, v)
