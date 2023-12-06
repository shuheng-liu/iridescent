import warnings
from enum import Enum
from abc import ABC, abstractmethod
from string import ascii_lowercase, ascii_uppercase
from typing import List, Union, Tuple
from keys import LEFT as _LEFT, RIGHT as _RIGHT, DELETE as _DELETE, CTRL
from utils import printable
from utils import vim_word, vim_word_begin, vim_word_end, vim_word_boundary, vim_line_begin, vim_line_end
from utils import vim_find, vim_till
from clipboard import clipboard

ascii_lowercase = ascii_lowercase.encode()
ascii_uppercase = ascii_uppercase.encode()

# Used internally to control whether searching forward (with /) or backward (with ?)
_search_forward = True
# Used by the @register_action decorator to store the mapping from ActionEnum to Action
_action_lookup = {}
# Last action and argument, to be used by the repeat (dot) command
_last_action_arg = None
# redo and undo stacks, used by the repeat and undo/redo commands
_redo_stack, _undo_stack = [], []


class Op(Enum):
    LEFT = _LEFT
    RIGHT = _RIGHT
    DELETE = _DELETE


class SpecialOp(ABC):
    r"""Special Ops that controls the `editor_state_manager`. Side effects of commands should subclass this."""

    def __init__(self, *args):
        self.args = args

    @abstractmethod
    def control(self, editor_state_manager, ops):
        pass


class SetInsertOp(SpecialOp):
    def control(self, editor_state_manager, ops):
        editor_state_manager.set_insert()


class SetReplaceOp(SpecialOp):
    def control(self, editor_state_manager, ops):
        editor_state_manager.set_replace()


class StartHistorySearchOp(SpecialOp):
    def __init__(self, forward, pattern):
        super().__init__(forward, pattern)

    def control(self, editor_state_manager, ops):
        hm = editor_state_manager.filter_obj.history_manager
        forward, pattern = self.args

        global _search_forward
        _search_forward = forward

        hm.start_search(pattern)


class NavigateHistoryOp(SpecialOp):
    def __init__(self, forward):
        super().__init__(forward)

    def control(self, editor_state_manager, ops):
        hm = editor_state_manager.filter_obj.history_manager
        line, match = hm.search_next() if self.args[0] else hm.search_prev()
        hm.skip_buffers()

        if not line:  # if the match_pattern is not found, don't delete anything
            ops.clear()
        else:
            ops.append(line)


class SetHistoryMarkOp(SpecialOp):
    def __init__(self, mark):
        super().__init__(mark)

    def control(self, editor_state_manager, ops):
        mark, = self.args
        hm = editor_state_manager.filter_obj.history_manager
        hm.skip_buffers()
        hm.set_mark(mark)


class RetrieveHistoryMarkOp(SpecialOp):
    def __init__(self, mark):
        super().__init__(mark)

    def control(self, editor_state_manager, ops):
        mark, = self.args
        hm = editor_state_manager.filter_obj.history_manager
        line = hm.retrieve_mark(mark)

        hm.skip_buffers()
        if line:
            ops.append(line)


class ClipboardCopyOp(SpecialOp):
    def __init__(self, content):
        super().__init__(content)

    def control(self, editor_state_manager, ops):
        content, = self.args
        if content:
            clipboard.copy(content)


ActionOutput = Union[
    List[Union[Op, bytes]],
    Tuple[List[Union[Op, bytes]], List[SpecialOp]]
]


class ActionEnum(Enum):  # vim-like actions
    f = b"f"  # find
    t = b"t"  # till
    F = b"F"  # find (backwards)
    T = b"T"  # till (backwards)

    d = b"d"  # delete
    di = b"di"  # delete in-between
    dt = b"dt"  # delete till
    dT = b"dT"  # delete till (backwards)
    df = b"df"  # delete find
    dF = b"dF"  # delete find (backwards)
    x = b"x"  # remove character

    c = b"c"  # change
    ci = b"ci"  # change in-between
    ct = b"ct"  # change till
    cT = b"cT"  # change till (backwards)
    cf = b"cf"  # change find
    cF = b"cF"  # change find (backwards)
    s = b"s"  # substitute character

    y = b"y"  # yank
    yi = b"yi"  # yank in-between
    yt = b"yt"  # yank till
    yT = b"yT"  # yank till (backwards)
    yf = b"yf"  # yank find
    yF = b"yF"  # yank find (backwards)

    i = b"i"  # insert
    a = b"a"  # append
    I = b"I"  # insert at the beginning
    A = b"A"  # append at the end

    p = b"p"  # paste after
    P = b"P"  # paste before

    r = b"r"  # replace the character under cursor
    R = b"R"  # change vim to replace mode

    tilde = b"~"  # switch casing
    slash = b"/"  # start history search (forward)
    qmark = b"?"  # start history search (backward)
    n = b"n"  # search next history match
    N = b"N"  # search prev history match

    dot = b"."  # repeat last change
    u = b"u"  # undo
    ctrl_r = CTRL.R  # redo

    m = b"m"  # set mark
    backtick = b"`"  # retrieve mark


def register_action(action: ActionEnum, transform_cls=None):
    if transform_cls is None:
        transform_cls = lambda x: x

    def wrapper(cls):
        _action_lookup[action] = transform_cls(cls)
        return cls

    return wrapper


def __convert_delete_to_change(D):
    assert "Delete" in D.__name__

    class C(D):
        def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
            ops, sops = D.on_act(self, arg, line, pos)
            return ops, sops + [SetInsertOp()]

    C.__name__ = D.__name__.replace("Delete", "Change")

    return C


def __convert_delete_to_yank(D):
    assert "Delete" in D.__name__

    class Y(D):
        def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
            return [], D.on_act(self, arg, line, pos)[1]

    Y.__name__ = D.__name__.replace("Delete", "Yank")

    return Y


class Action(ABC):
    N_ARGS = ...
    VARIADIC_ARG_TERMINATORS = ...
    REPEATABLE = True  # controls whether this action can be repeated with the dot command
    UNDOABLE = True  # controls whether this action can be undone
    PRESERVE_REDO_STACK = False  # controls whether this action clears the redo stack

    def left(self, n):
        return [Op.LEFT] * n

    def right(self, n):
        return [Op.RIGHT] * n

    def delete(self, n):
        return [Op.DELETE] * n

    def act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        if self.REPEATABLE:
            global _last_action_arg
            _last_action_arg = (self.__class__, arg)
        if self.UNDOABLE:
            if (not _undo_stack) or _undo_stack[-1] != (line, pos):
                _undo_stack.append((line, pos))
        if not self.PRESERVE_REDO_STACK:
            _redo_stack.clear()
        return self.on_act(arg, line, pos)

    @abstractmethod
    def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        pass

    def delete_line(self, line: bytes, pos: int):
        return self.right(len(line) - pos) + self.delete(len(line))

    def swap(self, line, pos, new_line, new_pos):
        return self.delete_line(line, pos) + [new_line] + self.left(len(new_line) - new_pos)


@register_action(ActionEnum.f)
class Find(Action):
    N_ARGS = 1

    def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        new = vim_find(line, pos, arg, capital=False)
        if not 0 <= new < len(line):
            return []
        return self.right(new - pos)


@register_action(ActionEnum.t)
class Till(Action):
    N_ARGS = 1

    def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        new = vim_till(line, pos, arg, capital=False)
        if not 0 <= new < len(line):
            return []
        return self.right(new - pos)


@register_action(ActionEnum.F)
class FindBackwards(Action):
    N_ARGS = 1

    def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        new = vim_find(line, pos, arg, capital=True)
        if not 0 <= new < len(line):
            return []
        return self.left(pos - new)


@register_action(ActionEnum.T)
class TillBackwards(Action):
    N_ARGS = 1

    def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        new = vim_till(line, pos, arg, capital=True)
        if not 0 <= new < len(line):
            return []
        return self.left(pos - new)


@register_action(ActionEnum.y, transform_cls=__convert_delete_to_yank)
@register_action(ActionEnum.c, transform_cls=__convert_delete_to_change)
@register_action(ActionEnum.d)
class Delete(Action):
    N_ARGS = 1
    _VF_CAP_OFFSET_LOOKUP = {
        b"b": (vim_word_begin, False, 0),
        b"B": (vim_word_begin, True, 0),
        b"w": (vim_word, False, 0),
        b"W": (vim_word, True, 0),
        b"e": (vim_word_end, False, 1),
        b"E": (vim_word_end, True, 1),
        b"$": (vim_line_end, False, 1),
        b"0": (vim_line_begin, False, 0),
    }

    def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        assert 0 <= pos < len(line)

        # special case for "dd", "cc", and "yy"
        if arg.decode() == self.__class__.__name__.lower()[0]:
            return self.delete_line(line, pos), [ClipboardCopyOp(line)]

        if arg not in self._VF_CAP_OFFSET_LOOKUP:
            return [], []

        vf, cap, offset = self._VF_CAP_OFFSET_LOOKUP[arg]
        new = vf(line, pos, cap) + offset
        count = min(max(0, new), len(line)) - pos
        if count > 0:
            return self.right(count) + self.delete(count), [ClipboardCopyOp(line[pos: pos + count])]
        else:
            return self.delete(abs(count)), [ClipboardCopyOp(line[pos - abs(count): pos])]


@register_action(ActionEnum.yi, transform_cls=__convert_delete_to_yank)
@register_action(ActionEnum.ci, transform_cls=__convert_delete_to_change)
@register_action(ActionEnum.di)
class DeleteInBetween(Delete):
    N_ARGS = 1

    def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        if arg == b'w' or arg == b'W':
            begin, end = vim_word_boundary(line, pos, capital=(arg == b'W'))
            return self.right(end - pos + 1) + self.delete(end - begin + 1), [ClipboardCopyOp(line[begin: end + 1])]

        pairs = [b'()', b'[]', b'{}', b'<>', b'``', b"''", b'""', b',,', b'  ']
        for pair in pairs:
            if arg in pair:
                l, r = pair
                break
        else:
            return [], []

        try:
            left = line.rindex(l, 0, pos + 1)
            right = line.index(r, pos)
            return self.right(right - pos) + self.delete(right - left - 1), [ClipboardCopyOp(line[left + 1: right])]
        except ValueError:
            return [], []


@register_action(ActionEnum.yt, transform_cls=__convert_delete_to_yank)
@register_action(ActionEnum.ct, transform_cls=__convert_delete_to_change)
@register_action(ActionEnum.dt)
class DeleteTill(Delete):
    N_ARGS = 1

    def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        new_pos = vim_till(line, pos, arg, False)
        if not 0 <= new_pos < len(line):
            return [], []
        count = new_pos - pos + 1
        return self.right(count) + self.delete(count), [ClipboardCopyOp(line[pos: new_pos + 1])]


@register_action(ActionEnum.yT, transform_cls=__convert_delete_to_yank)
@register_action(ActionEnum.cT, transform_cls=__convert_delete_to_change)
@register_action(ActionEnum.dT)
class DeleteTillBackwards(Delete):
    N_ARGS = 1

    def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        new_pos = vim_till(line, pos, arg, True)
        if not 0 <= new_pos < len(line):
            return [], []
        count = pos - new_pos + 1
        return self.right(1) + self.delete(count), [ClipboardCopyOp(line[new_pos: pos + 1])]


@register_action(ActionEnum.yf, transform_cls=__convert_delete_to_yank)
@register_action(ActionEnum.cf, transform_cls=__convert_delete_to_change)
@register_action(ActionEnum.df)
class DeleteFind(Delete):
    N_ARGS = 1

    def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        new_pos = vim_find(line, pos, arg, False)
        if not 0 <= new_pos < len(line):
            return [], []
        count = new_pos - pos + 1
        return self.right(count) + self.delete(count), [ClipboardCopyOp(line[pos: new_pos + 1])]


@register_action(ActionEnum.yF, transform_cls=__convert_delete_to_yank)
@register_action(ActionEnum.cF, transform_cls=__convert_delete_to_change)
@register_action(ActionEnum.dF)
class DeleteFindBackwards(Delete):
    N_ARGS = 1

    def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        new_pos = vim_find(line, pos, arg, True)
        if not 0 <= new_pos < len(line):
            return [], []
        count = pos - new_pos + 1
        return self.right(1) + self.delete(count), [ClipboardCopyOp(line[new_pos: pos + 1])]


@register_action(ActionEnum.s, transform_cls=__convert_delete_to_change)
@register_action(ActionEnum.x)
class DeleteOneChar(Action):
    N_ARGS = 0

    def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        assert arg is None
        return self.right(1) + self.delete(1), [ClipboardCopyOp(line[pos: pos + 1])]


@register_action(ActionEnum.i)
class Insert(Action):
    N_ARGS = 0

    def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        assert arg is None
        return [], [SetInsertOp()]


@register_action(ActionEnum.I)
class InsertAtLineStart(Action):
    N_ARGS = 0

    def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        assert arg is None
        return self.left(pos), [SetInsertOp()]


@register_action(ActionEnum.a)
class Append(Action):
    N_ARGS = 0

    def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        assert arg is None
        return self.right(1), [SetInsertOp()]


@register_action(ActionEnum.A)
class AppendAtLineEnd(Action):
    N_ARGS = 0

    def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        assert arg is None
        return self.right(len(line) - pos), [SetInsertOp()]


@register_action(ActionEnum.P)
class PasteBefore(Action):
    N_ARGS = 0

    def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        assert arg is None
        return [clipboard.paste()]


@register_action(ActionEnum.p)
class PasteAfter(Action):
    N_ARGS = 0

    def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        assert arg is None
        return [Op.RIGHT, clipboard.paste(), Op.LEFT]


@register_action(ActionEnum.r)
class ReplaceCharacter(Action):
    N_ARGS = 1

    def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        if arg not in printable or arg == "\n":
            return []

        return self.right(1) + self.delete(1) + [arg]


@register_action(ActionEnum.R)
class EnterReplaceMode(Action):
    N_ARGS = 0

    def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        assert arg is None
        return [], [SetReplaceOp()]


@register_action(ActionEnum.tilde)
class SwitchCasing(Action):
    N_ARGS = 0
    CASE_MAP = {
        k: v
        for k, v in zip(
            ascii_lowercase + ascii_uppercase,
            ascii_uppercase + ascii_lowercase,
        )
    }

    def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        assert arg is None
        ch = line[pos]
        if ch not in self.CASE_MAP:
            return []
        return self.right(1) + self.delete(1) + [self.CASE_MAP[ch]]


class StartSearchAbstract(Action):
    N_ARGS = -1
    VARIADIC_ARG_TERMINATORS = [b"\r"]
    IS_FORWARD = ...

    def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        assert arg.endswith(b"\r") and isinstance(self.IS_FORWARD, bool)
        pattern = arg[:-1].decode()
        ops = self.delete_line(line, pos)
        special_ops = [
            StartHistorySearchOp(self.IS_FORWARD, pattern),
            NavigateHistoryOp(self.IS_FORWARD)
        ]
        return ops, special_ops


@register_action(ActionEnum.slash)
class StartSearchForward(StartSearchAbstract):
    IS_FORWARD = True


@register_action(ActionEnum.qmark)
class StartSearchBackward(StartSearchAbstract):
    IS_FORWARD = False


class SearchNavigate(Action):
    N_ARGS = 0
    SEARCH_FORWARD = ...

    def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        assert arg is None and isinstance(self.SEARCH_FORWARD, bool)
        ops = self.delete_line(line, pos)
        global _search_forward
        return ops, [NavigateHistoryOp(not self.SEARCH_FORWARD ^ _search_forward)]


@register_action(ActionEnum.n)
class SearchNext(SearchNavigate):
    SEARCH_FORWARD = True


@register_action(ActionEnum.N)
class SearchPrev(SearchNavigate):
    SEARCH_FORWARD = False


@register_action(ActionEnum.dot)
class SingleRepeat(Action):
    N_ARGS = 0
    REPEATABLE = False  # SingleRepeat itself cannot be repeated

    def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        assert arg is None
        global _last_action_arg
        if _last_action_arg is None:
            return []
        action, arg = _last_action_arg
        return action().act(arg, line, pos)


@register_action(ActionEnum.u)
class Undo(Action):
    N_ARGS = 0
    REPEATABLE = False
    UNDOABLE = False
    PRESERVE_REDO_STACK = True

    def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        assert arg is None
        if not _undo_stack:
            return []
        if (not _redo_stack) or _redo_stack[-1] != (line, pos):
            _redo_stack.append((line, pos))
        return self.swap(line, pos, *_undo_stack.pop())


@register_action(ActionEnum.ctrl_r)
class Redo(Action):
    N_ARGS = 0
    REPEATABLE = False
    PRESERVE_REDO_STACK = True

    def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        assert arg is None
        if not _redo_stack:
            return []
        return self.swap(line, pos, *_redo_stack.pop())


@register_action(ActionEnum.m)
class SetMark(Action):
    N_ARGS = 1

    def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        if arg not in ascii_lowercase + ascii_uppercase:
            return []
        return [], [SetHistoryMarkOp(arg)]


@register_action(ActionEnum.backtick)
class RetrieveMark(Action):
    N_ARGS = 1

    def on_act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        if arg not in ascii_lowercase + ascii_uppercase:
            return []
        return self.delete_line(line, pos), [RetrieveHistoryMarkOp(arg)]


def get_action(action: ActionEnum):
    return _action_lookup[action]


# import-time checks
for action in ActionEnum:
    if action not in _action_lookup:
        warnings.warn(f"Action `{action.name}` is not implemented")
        continue

    cls = _action_lookup[action]
    assert isinstance(cls.N_ARGS, int), f"{cls.__name__}.N_ARGS must be an integer, got {cls.N_ARGS}"
    if cls.N_ARGS == -1:
        error_msg = (f"{cls.__name__}.VARIADIC_ARG_TERMINATORS must be a list of bytes when N_ARGS=-1, "
                     f"got {cls.VARIADIC_ARG_TERMINATORS}")
        assert isinstance(cls.VARIADIC_ARG_TERMINATORS, list), error_msg
        for term in cls.VARIADIC_ARG_TERMINATORS:
            assert isinstance(term, bytes), error_msg
    else:
        assert cls.VARIADIC_ARG_TERMINATORS is ...
