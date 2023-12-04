from enum import Enum
from abc import ABC, abstractmethod
from typing import List, Union, Tuple
from keys import LEFT as _LEFT, RIGHT as _RIGHT, DELETE as _DELETE
from utils import printable, whitespace, next_predicate, prev_predicate, get_chunk
from utils import vim_word, vim_word_begin, vim_word_end, vim_line_begin, vim_line_end
from clipboard import clipboard


class Op(Enum):
    LEFT = _LEFT
    RIGHT = _RIGHT
    DELETE = _DELETE


class SpecialOp(ABC):
    r"""Special Ops that controls the `editor_state_manager`"""

    def __init__(self, *args):
        self.args = args

    @abstractmethod
    def control(self, editor_state_manager, ops):
        pass


class SetInsert(SpecialOp):
    def control(self, editor_state_manager, ops):
        editor_state_manager.set_insert()


class SetReplace(SpecialOp):
    def control(self, editor_state_manager, ops):
        editor_state_manager.set_replace()


ActionOutput = Union[
    List[Union[Op, bytes]],
    Tuple[List[Union[Op, bytes]], List[SpecialOp]]
]


class ActionEnum(Enum):  # vim-like actions
    d = b"d"  # delete
    di = b"di"  # delete in-between
    dt = b"dt"  # delete till
    x = b"x"  # remove character
    c = b"c"  # change
    ci = b"ci"  # change in-between
    ct = b"ct"  # change till
    s = b"s"  # substitute character

    i = b"i"  # insert
    a = b"a"  # append
    I = b"I"  # insert at the beginning
    A = b"A"  # append at the end

    p = b"p"  # paste after
    P = b"P"  # paste before

    r = b"r"  # replace the character under cursor
    R = b"R"  # change vim to replace mode


class Action(ABC):
    NO_ARG = False

    def left(self, n):
        return [Op.LEFT] * n

    def right(self, n):
        return [Op.RIGHT] * n

    def delete(self, n):
        return [Op.DELETE] * n

    @abstractmethod
    def act(self, arg: bytes, line: bytes, ipos: int) -> ActionOutput:
        pass


class Delete(Action):
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

    def act(self, arg: bytes, line: bytes, npos: int) -> ActionOutput:
        assert 0 <= npos < len(line)

        # special case for "dd" and "cc"
        if arg.decode() == self.__class__.__name__.lower()[0]:
            return self.right(len(line) - npos) + self.delete(len(line))

        if arg not in self._VF_CAP_OFFSET_LOOKUP:
            return []

        vf, cap, offset = self._VF_CAP_OFFSET_LOOKUP[arg]
        count = vf(line, npos, cap) - npos + offset
        if count > 0:
            return self.right(count) + self.delete(count)
        else:
            return self.right(1) + self.delete(abs(count) + 1)


class DeleteInBetween(Delete):
    def act(self, arg: bytes, line: bytes, ipos: int) -> ActionOutput:
        if arg == b'w':
            # HACK: think twice before changing it
            return Delete.act(self, b"w", line, ipos) + Delete.act(self, b"b", line, ipos)

        pairs = [b'()', b'[]', b'{}', b'<>', b'``', b"''", b'""', b',,', b'  ']
        for pair in pairs:
            if arg in pair:
                l, r = pair
                break
        else:
            return []

        try:
            left = line.rindex(l, 0, ipos)
            right = line.index(r, ipos)
            return self.right(right - ipos) + self.delete(right - left - 1)
        except ValueError:
            return []


class DeleteTill(Delete):
    def act(self, arg: bytes, line: bytes, ipos: int) -> List[Op]:
        try:
            new_pos = line.index(arg, ipos)
            count = new_pos - ipos
            return self.right(count) + self.delete(count)
        except ValueError:
            return []


class DeleteOneChar(Action):
    NO_ARG = True

    def act(self, arg, line, ipos):
        assert arg is None
        return self.right(1) + self.delete(1)


def __convert_delete_to_change(D):
    assert "Delete" in D.__name__

    class C(D):
        def act(self, arg: bytes, line: bytes, ipos: int) -> ActionOutput:
            return D.act(self, arg, line, ipos), [SetInsert()]

    C.__name__ = D.__name__.replace("Delete", "Change")

    return C


class Insert(Action):
    NO_ARG = True

    def act(self, arg: bytes, line: bytes, ipos: int) -> ActionOutput:
        assert arg is None
        return [], [SetInsert()]


class InsertAtLineStart(Action):
    NO_ARG = True

    def act(self, arg: bytes, line: bytes, ipos: int) -> ActionOutput:
        assert arg is None
        return self.left(ipos), [SetInsert()]


class Append(Action):
    NO_ARG = True

    def act(self, arg: bytes, line: bytes, ipos: int) -> ActionOutput:
        assert arg is None
        return self.right(1), [SetInsert()]


class AppendAtLineEnd(Action):
    NO_ARG = True

    def act(self, arg: bytes, line: bytes, ipos: int) -> ActionOutput:
        assert arg is None
        return self.right(len(line) - ipos), [SetInsert()]


class PasteBefore(Action):
    NO_ARG = True

    def act(self, arg: bytes, line: bytes, ipos: int) -> ActionOutput:
        assert arg is None
        return [clipboard.paste()]


class PasteAfter(Action):
    NO_ARG = True

    def act(self, arg: bytes, line: bytes, ipos: int) -> ActionOutput:
        assert arg is None
        return [Op.RIGHT, clipboard.paste(), Op.LEFT]


class ReplaceCharacter(Action):
    def act(self, arg: bytes, line: bytes, ipos: int) -> ActionOutput:
        if arg not in printable or arg == "\n":
            return []

        return self.right(1) + self.delete(1) + [arg]


class EnterReplaceMode(Action):
    NO_ARG = True

    def act(self, arg: bytes, line: bytes, ipos: int) -> ActionOutput:
        assert arg is None
        return [], [SetReplace()]


__lookup = {
    ActionEnum.d: Delete,
    ActionEnum.di: DeleteInBetween,
    ActionEnum.dt: DeleteTill,
    ActionEnum.x: DeleteOneChar,
    ActionEnum.c: __convert_delete_to_change(Delete),
    ActionEnum.ci: __convert_delete_to_change(DeleteInBetween),
    ActionEnum.ct: __convert_delete_to_change(DeleteTill),
    ActionEnum.s: __convert_delete_to_change(DeleteOneChar),
    ActionEnum.i: Insert,
    ActionEnum.a: Append,
    ActionEnum.I: InsertAtLineStart,
    ActionEnum.A: AppendAtLineEnd,
    ActionEnum.p: PasteAfter,
    ActionEnum.P: PasteBefore,
    ActionEnum.r: ReplaceCharacter,
    ActionEnum.R: EnterReplaceMode,
}


def get_action(action: ActionEnum):
    return __lookup[action]
