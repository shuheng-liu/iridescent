import os


class HistoryManager:
    def __init__(self, file, init_max_size=5000):
        self.file = file

        if file and os.path.exists(file) and os.path.isfile(file):
            with open(file) as f:
                self.history = [line[1:] for line in f.read().split('\n') if line.startswith(":")]
        else:
            self.history = []

        if len(self.history) > init_max_size:
            self.history = self.history[-init_max_size:]
        self.init_size = len(self.history)
        self.index = self.init_size - 1
        self._buffer = ""

    def _emit(self):
        if self.index == len(self.history):
            return self._buffer.encode()
        assert isinstance(self.history[self.index], str)
        return self.history[self.index].encode()

    def go_prev(self):
        self.index = (self.index - 1) % (len(self.history) + 1)
        return self._emit()

    def go_next(self):
        self.index = (self.index + 1) % (len(self.history) + 1)
        return self._emit()

    def ingest(self):
        if self._buffer and (len(self.history) == 0 or self._buffer != self.history[-1]):
            self.history.append(self._buffer)
        self.index = len(self.history)
        self.buffer(b"")

    def retrieve_buffer(self):
        self.index = len(self.history)
        return self._emit()

    def buffer(self, line: bytes):
        self._buffer = line.decode()

    def write_to_disk(self):
        if not self.file:
            return
        with open(self.file, "a") as f:
            f.writelines(":" + line + "\n" for line in self.history[self.init_size:])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.write_to_disk()
