import os
import re
import bisect

DEFAULT_REJECT_REGEXES = (
    re.compile(r"h\s*", re.IGNORECASE),
    re.compile(r"halt\s*", re.IGNORECASE),
)


class HistoryManager:
    def __init__(self, file, init_max_size=5000, reject_regexes=DEFAULT_REJECT_REGEXES):
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
        self.reject_regexes = reject_regexes
        self.search_pattern = None
        self.search_matches = []  # list of (history_index, match) pairs
        self._skip_buffers = 0  # number of times to skip the .set_buffer() operations
        self._marks_lookup = {}  # mark -> history_index

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

    def _ingestible(self, buf):
        if not buf:
            return False
        for regex in self.reject_regexes:
            if regex.fullmatch(buf):
                return False
        return len(self.history) == 0 or buf != self.history[-1]

    def ingest(self):
        if self._ingestible(self._buffer):
            self.history.append(self._buffer)
            match = self.search_pattern and self.search_pattern.search(self._buffer)
            self.index = len(self.history)
            if match:
                self.search_matches.append((self.index - 1, match))
        self.set_buffer(b"")

    def start_search(self, pattern: str):
        self.search_pattern = re.compile(pattern)
        self.search_matches = []
        for i, history in enumerate(self.history):
            match = self.search_pattern.search(history)
            if match:
                self.search_matches.append((i, match))

    def search_next(self):
        if not self.search_matches:
            return None, None

        pos = bisect.bisect_left([key for key, match in self.search_matches], self.index + 1)
        self.index, match = self.search_matches[pos if pos < len(self.search_matches) else 0]
        return self._emit(), match

    def search_prev(self):
        if not self.search_matches:
            return None, None
        pos = bisect.bisect_left([key for key, match in self.search_matches], self.index) - 1
        # pos == -1 happen to be what we need (the last entry)
        self.index, match = self.search_matches[pos]
        return self._emit(), match

    def retrieve_buffer(self):
        self.index = len(self.history)
        return self._emit()

    def skip_buffers(self, n=1):
        self._skip_buffers = n

    def set_buffer(self, line: bytes):
        if self._skip_buffers > 0:
            self._skip_buffers -= 1
            return
        self._buffer = line.decode()

    def write_to_disk(self):
        if not self.file:
            return
        with open(self.file, "a") as f:
            f.writelines(":" + line + "\n" for line in self.history[self.init_size:])

    def set_mark(self, mark):
        self._marks_lookup[mark] = self.index

    def retrieve_mark(self, mark):
        if mark in self._marks_lookup:
            self.index = self._marks_lookup[mark]
        return self._emit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file and os.path.samefile(self.file, os.path.expanduser("~/.iris_history")):
            return

        self.write_to_disk()
