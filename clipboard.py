class _ClipBoard:
    def __init__(self):
        self._content = b""

    def clear(self):
        self._content = b""

    def copy(self, value):
        if isinstance(value, int):
            value = value.to_bytes(1, "big")
        assert isinstance(value, bytes), (value, type(value))
        self._content = value

    def paste(self):
        return self._content


clipboard = _ClipBoard()
