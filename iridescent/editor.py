from enum import Enum
from .vim_actions import ActionEnum, get_action, _redo_stack


def _set_cursor_vertical():
    print("\x1B[5 q", end="", flush=True)


def _set_cursor_block():
    print("\x1B[2 q", end="", flush=True)


def _set_cursor_underline():
    print("\x1B[3 q", end="", flush=True)


class EditorState(Enum):
    NORMAL = 'normal'
    INSERT = 'insert'
    REPLACE = "replace"


class EditorStateManger:
    def __init__(self, filter_obj):
        self._state = EditorState.INSERT
        self._action_buffer = None
        self._arg_buffer = None
        self.filter_obj = filter_obj

    def _reset_buffers(self):
        self._action_buffer = b""
        self._arg_buffer = b""

    def set_normal(self):  # set to normal mode
        if self._state != EditorState.NORMAL:
            _redo_stack.clear()
        self._state = EditorState.NORMAL
        self._reset_buffers()
        _set_cursor_block()

    def set_insert(self):  # set to input mode
        self._state = EditorState.INSERT
        self._reset_buffers()
        _set_cursor_vertical()

    def set_replace(self):
        self._state = EditorState.REPLACE
        self._reset_buffers()
        _set_cursor_underline()

    @property
    def state(self):
        return self._state

    def normal_buffer(self, key, current_line, cursor_pos):
        # a list of operations/keystrokes
        # if the operation is not completed, return None
        if len(key) != 1:
            self._reset_buffers()
            return None

        if not self._action_buffer:
            try:
                self._action_buffer = ActionEnum(key)
            except ValueError:
                self._reset_buffers()
                return None

            action = get_action(self._action_buffer)
            return self.post_process(action().act(None, current_line, cursor_pos)) if action.N_ARGS == 0 else None

        # Variadic arguments
        action = get_action(self._action_buffer)
        if action.N_ARGS == -1:
            self._arg_buffer += key
            if key in action.VARIADIC_ARG_TERMINATORS:
                return self.post_process(action().act(self._arg_buffer, current_line, cursor_pos))
            return None

        try:
            action = ActionEnum(self._action_buffer.value + key)
            self._action_buffer = action
            return None
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

        self._reset_buffers()
        return ops
