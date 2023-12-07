from .utils import nonwhitespace_printable, _chunk_rightmost, _chunk_leftmost
from .editor import EditorStateManger
from .input_handlers import *

HANDLER_CLASSES = [
    EscapeSequenceHandler,
    SwitchToNormalHandler,
    PrintableHandler,
    DeleteHandler,
    OptionDeleteHandler,
    HistoryNavigationHandler,
    SigBellHandler,
    LeftHandler,
    RightHandler,
    OptionLeftHandler,
    OptionRightHandler,
    LineEndHandler,
    VimNavigationHandler,
    VimEnterHandler,
    VimActionHandler,
    ReplaceModeHandler,
    DefaultHandler,
]


class DebugLogger:
    def __init__(self, file):
        self.file = file

    def log(self, *args, **kwargs):
        if not self.file:
            return
        with open(self.file, "a") as f:
            f.write("DEBUG: ")
            f.write("\n       ".join(repr(arg) for arg in args))
            for k, v in kwargs.items():
                f.write(k + ": " + repr(v) + "\n       ")
            f.write("\n")


class IOFilter(ABC):
    def __init__(self, file, dlogger) -> None:
        self.file = file
        self.dlogger = dlogger

    def debug(self, *args, **kwargs):
        if not self.dlogger:
            return
        self.dlogger.log(*args, **kwargs)

    @abstractmethod
    def __call__(self, key: bytes) -> bytes:
        pass


class InputFilter(IOFilter):
    def __init__(self, file=None, dlogger=None, history_manager=None):
        super().__init__(file=file, dlogger=dlogger)
        self.current_line = None
        self.cursor_pos = 0
        self.state_manager = EditorStateManger(filter_obj=self)
        self.history_manager = history_manager
        self.handlers = [H(self) for H in HANDLER_CLASSES]
        self.reset_line()

    @property
    def current_byte(self):
        if self.cursor_pos == 0:
            return b''
        return self.current_line[self.cursor_pos - 1]

    def reset_line(self):
        from .color_utils import FgColor, _set_fg_color
        _set_fg_color(FgColor.RED)
        self.current_line = b""
        self.cursor_pos = 0
        self.history_manager.ingest()
        return b"\r"

    @staticmethod
    def is_line_end(key):
        if key in [b"\r", b"\n", b"\r\n", SIG.INT]:  # for cross-platform compatibility
            return True
        return False

    @staticmethod
    def contains_printable(key):
        return any(k in nonwhitespace_printable for k in key)

    def debug(self, *args, **kwargs):
        if not self.dlogger:
            return
        self.dlogger.log(*args, **kwargs)

    def debug_cursor(self):
        repr = self.current_line[:self.cursor_pos] + b"|" + self.current_line[self.cursor_pos:]
        self.debug(repr.decode())

    def log_key(self, key, is_old=True):
        if not self.file:
            return
        if is_old:
            output = f"\nReceiving key stroke (length={len(key)}):    {repr(key)}\n"
        else:
            output = f"     SENDING   ----->(length={len(key)}):    {repr(key)}\n"
        with open(self.file, "a") as f:
            f.write(output)

    def log(self, msg):
        if not self.file:
            return
        with open(self.file, "a") as f:
            f.write(msg + "\n")

    def delete(self, by=1):
        self.current_line = self.current_line[:self.cursor_pos - by] + self.current_line[self.cursor_pos:]
        self.cursor_pos -= by
        if self.cursor_pos < 0:
            self.cursor_pos = 0
        return KEY.DELETE * by

    def delete_by_chunk(self):
        new_pos = _chunk_leftmost(self.current_line, self.cursor_pos)

        if new_pos > 0:
            new_pos -= 1

        self.current_line = self.current_line[:new_pos] + self.current_line[self.cursor_pos:]
        count = self.cursor_pos - new_pos
        self.cursor_pos = new_pos
        return KEY.DELETE * count

    def move_cursor_left(self, by=1):
        old_pos = self.cursor_pos
        self.cursor_pos = max(0, self.cursor_pos - by)
        return KEY.LEFT * (old_pos - self.cursor_pos)

    def move_cursor_left_by_chunk(self):
        new_pos = _chunk_leftmost(self.current_line, self.cursor_pos)
        if new_pos > 0:
            new_pos -= 1

        count = self.cursor_pos - new_pos
        self.move_cursor_left(count)
        return KEY.LEFT * count

    def move_cursor_right(self, by=1):
        output = b""
        if isinstance(by, bytes):
            self.current_line = self.current_line[:self.cursor_pos] + by + self.current_line[self.cursor_pos:]
            output = by
            by = len(by)
        old_pos = self.cursor_pos
        self.cursor_pos = min(len(self.current_line), self.cursor_pos + by)
        return output or KEY.RIGHT * (self.cursor_pos - old_pos)

    def move_cursor_right_by_chunk(self):
        new_pos = _chunk_rightmost(self.current_line, self.cursor_pos)
        if new_pos < len(self.current_line):
            new_pos += 1

        count = new_pos - self.cursor_pos
        self.move_cursor_right(count)
        return KEY.RIGHT * count

    def move_cursor_vim(self, vf, capital):
        assert self.state_manager.state == EditorState.NORMAL
        new_npos = vf(self.current_line, self.cursor_pos, capital)
        right = new_npos - self.cursor_pos
        if right > 0:
            return self.move_cursor_right(right)
        else:
            return self.move_cursor_left(-right)

    def __call__(self, key):
        if not isinstance(key, bytes):
            raise TypeError("InputFilter only accepts bytes as input")

        self.log_key(key, is_old=True)

        state = self.state_manager.state
        output = b''
        for handler in self.handlers:
            if handler.accepts_mode(state) and handler.accepts_key(key):
                self.log(f"Using handler: {handler.__class__.__name__}")
                output = handler.handle(key, state)
                break

        if self.state_manager.state == EditorState.NORMAL and self.cursor_pos == len(self.current_line):
            self.move_cursor_left()
            output += KEY.LEFT

        self.history_manager.set_buffer(self.current_line)

        self.log_key(output, is_old=False)
        self.debug_cursor()
        return output


class OutputFilter(IOFilter):
    def __init__(self, file, dlogger):
        super().__init__(file=file, dlogger=dlogger)

    def __call__(self, content):
        from .color_utils import TextStyle

        if self.file:
            with open(self.file, 'a') as f:
                f.write(repr(content) + "\n")

        if content.endswith(b">"):
            try:
                last_index = content.rindex(b"\r\n")
            except ValueError:
                return content
            if b"<" not in content[last_index:]:
                content = content[:last_index] + TextStyle.RESET.value.encode() + content[last_index:]

        return content
