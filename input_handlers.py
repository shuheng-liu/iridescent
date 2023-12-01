from abc import ABC, abstractmethod
from editor import EditorState
from keys import DELETE, UP, DOWN, LEFT, RIGHT, ESCAPE, ENTER, OPTION, SIG, ESCAPE_SEQUENCE
from vim_actions import Op
from clipboard import clipboard
from utils import printable


class AbstractKeyStrokeHandler(ABC):
    def __init__(self, filter_obj):
        self.filter_obj = filter_obj

    @abstractmethod
    def accepts_mode(self, mode):
        pass

    @abstractmethod
    def accepts_key(self, key):
        pass

    @abstractmethod
    def handle(self, key, mode):
        pass


class EscapeSequenceHandler(AbstractKeyStrokeHandler):
    def accepts_mode(self, mode):
        return True

    def accepts_key(self, key):
        return key == ESCAPE_SEQUENCE

    def handle(self, key, mode):
        return key


class SwitchToNormalHandler(AbstractKeyStrokeHandler):
    def accepts_mode(self, mode):
        return True

    def accepts_key(self, key):
        return key == ESCAPE

    def handle(self, key, mode):
        self.filter_obj.state_manager.set_normal()
        if self.filter_obj.cursor_pos == len(self.filter_obj.current_line):
            self.filter_obj.move_cursor_left()
            return LEFT

        return b''


class InputModeHandler(AbstractKeyStrokeHandler):
    def accepts_mode(self, mode):
        return mode == EditorState.INSERT


class PrintableHandler(InputModeHandler):
    def accepts_key(self, key):
        return key.decode().isprintable() and key not in b'\r\n'

    def handle(self, key, mode):
        self.filter_obj.move_cursor_right(key)
        return key


class DeleteHandler(AbstractKeyStrokeHandler):
    def accepts_mode(self, mode):
        return mode in [EditorState.INSERT, EditorState.REPLACE]

    def accepts_key(self, key):
        return key == DELETE

    def handle(self, key, mode):
        return self.filter_obj.delete()


class OptionDeleteHandler(InputModeHandler):
    def accepts_key(self, key):
        return key == OPTION.DELETE

    def handle(self, key, mode):
        return self.filter_obj.delete_by_chunk()


class HistoryNavigationHandler(AbstractKeyStrokeHandler):
    def accepts_mode(self, mode):
        return mode in [EditorState.INSERT, EditorState.NORMAL, EditorState.REPLACE]

    def accepts_key(self, key):
        return key in [UP, DOWN]

    def _set_history(self, new):
        line = self.filter_obj.current_line
        pos = self.filter_obj.cursor_pos
        # self.filter_obj.debug(line=line, pos=pos)
        self.filter_obj.current_line = new
        self.filter_obj.cursor_pos = len(new)
        return RIGHT * (len(line) - pos) + DELETE * len(line) + new

    def handle(self, key, mode):
        if key == UP:
            buffer = self.filter_obj.history_manager.go_prev()
        elif key == DOWN:
            buffer = self.filter_obj.history_manager.go_next()
        return self._set_history(buffer)


class SigBellHandler(InputModeHandler):
    def accepts_key(self, key):
        return key == SIG.BELL

    def handle(self, key, mode):
        return b''


class LeftHandler(AbstractKeyStrokeHandler):
    def accepts_mode(self, mode):
        return mode in [EditorState.INSERT, EditorState.NORMAL, EditorState.REPLACE]

    def accepts_key(self, key):
        return key == LEFT

    def handle(self, key, mode):
        return self.filter_obj.move_cursor_left()


class RightHandler(AbstractKeyStrokeHandler):
    def accepts_mode(self, mode):
        return mode in [EditorState.INSERT, EditorState.NORMAL, EditorState.REPLACE]

    def accepts_key(self, key):
        return key == RIGHT

    def handle(self, key, mode):
        return self.filter_obj.move_cursor_right()


class OptionLeftHandler(InputModeHandler):
    def accepts_key(self, key):
        return key == OPTION.LEFT

    def handle(self, key, mode):
        return self.filter_obj.move_cursor_left_by_chunk()


class OptionRightHandler(InputModeHandler):
    def accepts_key(self, key):
        return key == OPTION.RIGHT

    def handle(self, key, mode):
        return self.filter_obj.move_cursor_right_by_chunk()


class LineEndHandler(InputModeHandler):
    def accepts_key(self, key):
        return self.filter_obj.is_line_end(key)

    def handle(self, key, mode):
        self.filter_obj.reset_line()
        return ENTER


class DefaultHandler(AbstractKeyStrokeHandler):
    def accepts_mode(self, mode):
        return True

    def accepts_key(self, key):
        # This should be at the last in the list of handlers
        # as it will accept all keys and handle the unhandled keys
        return True

    def handle(self, key, mode):
        self.filter_obj.debug(f"Unhandled key : {key}, mode: {mode}")
        return b""


class NormalModeHandler(AbstractKeyStrokeHandler):
    def accepts_mode(self, mode):
        return mode == EditorState.NORMAL


class VimActionHandler(NormalModeHandler):
    def accepts_key(self, key):
        return key.decode().isprintable()

    def handle(self, key, mode):
        ops = self.filter_obj.state_manager.normal_buffer(
            key,
            self.filter_obj.current_line,
            self.filter_obj.cursor_pos,
        )
        output = b""
        cleared = False
        for op in ops:
            if op == Op.LEFT:
                self.filter_obj.move_cursor_left()
                output += LEFT
            elif op == Op.RIGHT:
                self.filter_obj.move_cursor_right()
                output += RIGHT
            elif op == Op.DELETE:
                if not cleared:
                    clipboard.clear()
                    cleared = True
                clipboard.prepend(self.filter_obj.current_byte)
                self.filter_obj.delete()
                output += DELETE
            elif isinstance(op, bytes) and op.decode().isprintable():
                self.filter_obj.move_cursor_right(op)
                output += op

        return output


class VimEnterHandler(NormalModeHandler, LineEndHandler):
    def accepts_mode(self, mode):
        return NormalModeHandler.accepts_mode(self, mode)


class VimNavigationHandler(NormalModeHandler, HistoryNavigationHandler):
    def accepts_mode(self, mode):
        return NormalModeHandler.accepts_mode(self, mode)

    def accepts_key(self, key):
        if self.filter_obj.state_manager._action_buffer is not None:
            return False
        return key in [
            UP, DOWN,
            LEFT, RIGHT,
            b"j", b"k",
            b"h", b"l",
            b"b", b"w",
            b"0", b"$",
            b"G",
        ]

    def handle(self, key, mode):
        if key in [UP, b"k"]:
            buffer = self.filter_obj.history_manager.go_prev()
            return HistoryNavigationHandler._set_history(self, buffer)
        elif key in [DOWN, b"j"]:
            buffer = self.filter_obj.history_manager.go_next()
            return HistoryNavigationHandler._set_history(self, buffer)
        elif key == b"G":
            buffer = self.filter_obj.history_manager.retrieve_buffer()
            return HistoryNavigationHandler._set_history(self, buffer)
        elif key in [LEFT, b"h"]:
            self.filter_obj.move_cursor_left()
            return LEFT
        elif key in [RIGHT, b"l"]:
            return self.filter_obj.move_cursor_right()
        elif key == b"0":
            count = self.filter_obj.cursor_pos
            self.filter_obj.move_cursor_left(count)
            return count * LEFT
        elif key == b"$":
            count = len(self.filter_obj.current_line) - self.filter_obj.cursor_pos
            self.filter_obj.move_cursor_right(count)
            return count * RIGHT
        elif key == b"b":
            return self.filter_obj.move_cursor_left_by_chunk()
        elif key == b"w":
            return self.filter_obj.move_cursor_right_by_chunk()

        return b""


class ReplaceModeHandler(AbstractKeyStrokeHandler):
    def accepts_mode(self, mode):
        return mode == EditorState.REPLACE

    def accepts_key(self, key):
        return key in printable or key == b"\r"

    def handle(self, key, mode):
        if key in b"\r\n":
            return self.filter_obj.reset_line()

        if self.filter_obj.cursor_pos == len(self.filter_obj.current_line):
            return self.filter_obj.move_cursor_right(key)

        return (
                self.filter_obj.move_cursor_right()
                + self.filter_obj.delete()
                + self.filter_obj.move_cursor_right(key)
        )
