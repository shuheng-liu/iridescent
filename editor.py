import time
from enum import Enum
from vim_actions import ActionEnum, get_action, Op


def _set_cursor_vertical():
    print("\x1B[5 q", end="", flush=True)


def _set_cursor_block():
    print("\x1B[2 q", end="", flush=True)


class EditorState(Enum):
    NORMAL = 'normal'
    INSERT = 'insert'


class EditorStateManger:
    def __init__(self, normal_timeout=1.0):
        self._state = EditorState.INSERT
        self._timeout = normal_timeout
        self._last_normal = None
        self._action_buffer = None

    def set_normal(self):  # set to normal mode
        self._state = EditorState.NORMAL
        self._last_normal = time.time()
        self._action_buffer = None
        _set_cursor_block()

    def set_insert(self):  # set to input mode
        self._state = EditorState.INSERT
        self._action_buffer = None
        _set_cursor_vertical()

    @property
    def state(self):
        if self._timeout is None:
            return self._state

        if self._state != EditorState.NORMAL:
            return self._state

        now = time.time()
        if now - self._last_normal > self._timeout:
            self.set_insert()

        return self._state

    def buffer(self, key, current_line, cursor_pos):
        if len(key) != 1:
            self._action_buffer = None
            return []

        if not self._action_buffer:
            try:
                self._action_buffer = ActionEnum(key)
                action = get_action(self._action_buffer)
                return self.post_process(action().act(None, current_line, cursor_pos)) if action.NO_ARG else []
            except ValueError:
                self._action_buffer = None
                return []

        try:
            action = ActionEnum(self._action_buffer.value + key)
            self._action_buffer = action
            return []
        except ValueError:
            action = get_action(self._action_buffer)()
            return self.post_process(action.act(key, current_line, cursor_pos))

    def post_process(self, action_output):
        if isinstance(action_output, tuple) and len(action_output) == 2 and isinstance(action_output[0], list):
            ops, sops = action_output
            for sop in sops:
                sop.control(self, ops)
        else:
            ops = action_output

        self._action_buffer = None
        return ops
