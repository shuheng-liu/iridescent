from enum import Enum
from abc import ABC, abstractmethod
from string import ascii_lowercase, ascii_uppercase
from typing import List, Union, Tuple
from keys import LEFT as _LEFT, RIGHT as _RIGHT, DELETE as _DELETE
from utils import printable
from utils import vim_word, vim_word_begin, vim_word_end, vim_word_boundary, vim_line_begin, vim_line_end
from utils import vim_find, vim_till
from clipboard import clipboard

ascii_lowercase = ascii_lowercase.encode()
ascii_uppercase = ascii_uppercase.encode()


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


class Action(ABC):
    NO_ARG = False

    def left(self, n):
        return [Op.LEFT] * n

    def right(self, n):
        return [Op.RIGHT] * n

    def delete(self, n):
        return [Op.DELETE] * n

    @abstractmethod
    def act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        pass


class Find(Action):
    def act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        new = vim_find(line, pos, arg, capital=False)
        if not 0 <= new < len(line):
            return []
        return self.right(new - pos)


class Till(Action):
    def act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        new = vim_till(line, pos, arg, capital=False)
        if not 0 <= new < len(line):
            return []
        return self.right(new - pos)


class FindBackwards(Action):
    def act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        new = vim_find(line, pos, arg, capital=True)
        if not 0 <= new < len(line):
            return []
        return self.left(pos - new)


class TillBackwards(Action):
    def act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        new = vim_till(line, pos, arg, capital=True)
        if not 0 <= new < len(line):
            return []
        return self.left(pos - new)


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

    def act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        assert 0 <= pos < len(line)

        # special case for "dd" and "cc"
        if arg.decode() == self.__class__.__name__.lower()[0]:
            return self.right(len(line) - pos) + self.delete(len(line))

        if arg not in self._VF_CAP_OFFSET_LOOKUP:
            return []

        vf, cap, offset = self._VF_CAP_OFFSET_LOOKUP[arg]
        new = vf(line, pos, cap) + offset
        count = min(max(0, new), len(line)) - pos
        if count > 0:
            return self.right(count) + self.delete(count)
        else:
            return self.delete(abs(count))


class DeleteInBetween(Delete):
    def act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        if arg == b'w' or arg == b'W':
            begin, end = vim_word_boundary(line, pos, capital=(arg == b'W'))
            return self.right(end - pos + 1) + self.delete(end - begin + 1)

        pairs = [b'()', b'[]', b'{}', b'<>', b'``', b"''", b'""', b',,', b'  ']
        for pair in pairs:
            if arg in pair:
                l, r = pair
                break
        else:
            return []

        try:
            left = line.rindex(l, 0, pos+1)
            right = line.index(r, pos)
            return self.right(right - pos) + self.delete(right - left - 1)
        except ValueError:
            return []


class DeleteTill(Delete):
    def act(self, arg: bytes, line: bytes, pos: int) -> List[Op]:
        new_pos = vim_till(line, pos, arg, False)
        if not 0 <= new_pos < len(line):
            return []
        count = new_pos - pos + 1
        return self.right(count) + self.delete(count)


class DeleteTillBackwards(Delete):
    def act(self, arg: bytes, line: bytes, pos: int) -> List[Op]:
        new_pos = vim_till(line, pos, arg, True)
        if not 0 <= new_pos < len(line):
            return []
        count = pos - new_pos + 1
        return self.right(1) + self.delete(count)


class DeleteFind(Delete):
    def act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        new_pos = vim_find(line, pos, arg, False)
        if not 0 <= new_pos < len(line):
            return []
        count = new_pos - pos + 1
        return self.right(count) + self.delete(count)


class DeleteFindBackwards(Delete):
    def act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        new_pos = vim_find(line, pos, arg, True)
        if not 0 <= new_pos < len(line):
            return []
        count = pos - new_pos + 1
        return self.right(1) + self.delete(count)


class DeleteOneChar(Action):
    NO_ARG = True

    def act(self, arg, line, pos):
        assert arg is None
        return self.right(1) + self.delete(1)


def __convert_delete_to_change(D):
    assert "Delete" in D.__name__

    class C(D):
        def act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
            return D.act(self, arg, line, pos), [SetInsert()]

    C.__name__ = D.__name__.replace("Delete", "Change")

    return C


def __convert_delete_to_yank(D):
    assert "Delete" in D.__name__

    class Y(D):
        def act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
            # print("yanking")
            actions = D.act(self, arg, line, pos)
            # print(actions)

            for n_rights, op in enumerate(actions):
                if op != Op.RIGHT:
                    break
            else:
                n_rights = len(actions)

            for n_deletes, op in enumerate(actions[n_rights:]):
                if op != Op.DELETE:
                    break
            else:
                n_deletes = len(actions) - n_rights

            right = pos + n_rights
            left = right - n_deletes
            if left != right:
                clipboard.copy(line[left: right])

            return []

    Y.__name__ = D.__name__.replace("Delete", "Yank")

    return Y


class Insert(Action):
    NO_ARG = True

    def act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        assert arg is None
        return [], [SetInsert()]


class InsertAtLineStart(Action):
    NO_ARG = True

    def act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        assert arg is None
        return self.left(pos), [SetInsert()]


class Append(Action):
    NO_ARG = True

    def act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        assert arg is None
        return self.right(1), [SetInsert()]


class AppendAtLineEnd(Action):
    NO_ARG = True

    def act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        assert arg is None
        return self.right(len(line) - pos), [SetInsert()]


class PasteBefore(Action):
    NO_ARG = True

    def act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        assert arg is None
        return [clipboard.paste()]


class PasteAfter(Action):
    NO_ARG = True

    def act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        assert arg is None
        return [Op.RIGHT, clipboard.paste(), Op.LEFT]


class ReplaceCharacter(Action):
    def act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        if arg not in printable or arg == "\n":
            return []

        return self.right(1) + self.delete(1) + [arg]


class EnterReplaceMode(Action):
    NO_ARG = True

    def act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        assert arg is None
        return [], [SetReplace()]


class SwitchCasing(Action):
    NO_ARG = True
    CASE_MAP = {k: v for k, v in zip(ascii_lowercase + ascii_uppercase, ascii_uppercase + ascii_lowercase)}

    def act(self, arg: bytes, line: bytes, pos: int) -> ActionOutput:
        assert arg is None
        ch = line[pos]
        if ch not in self.CASE_MAP:
            return []
        return self.right(1) + self.delete(1) + [self.CASE_MAP[ch]]


__lookup = {
    ActionEnum.f: Find,
    ActionEnum.t: Till,
    ActionEnum.F: FindBackwards,
    ActionEnum.T: TillBackwards,

    ActionEnum.d: Delete,
    ActionEnum.di: DeleteInBetween,
    ActionEnum.dt: DeleteTill,
    ActionEnum.dT: DeleteTillBackwards,
    ActionEnum.df: DeleteFind,
    ActionEnum.dF: DeleteFindBackwards,
    ActionEnum.x: DeleteOneChar,

    ActionEnum.c: __convert_delete_to_change(Delete),
    ActionEnum.ci: __convert_delete_to_change(DeleteInBetween),
    ActionEnum.ct: __convert_delete_to_change(DeleteTill),
    ActionEnum.cT: __convert_delete_to_change(DeleteTillBackwards),
    ActionEnum.cf: __convert_delete_to_change(DeleteFind),
    ActionEnum.cF: __convert_delete_to_change(DeleteFindBackwards),
    ActionEnum.s: __convert_delete_to_change(DeleteOneChar),

    ActionEnum.y: __convert_delete_to_yank(Delete),
    ActionEnum.yi: __convert_delete_to_yank(DeleteInBetween),
    ActionEnum.yt: __convert_delete_to_yank(DeleteTill),
    ActionEnum.yT: __convert_delete_to_yank(DeleteTillBackwards),
    ActionEnum.yf: __convert_delete_to_yank(DeleteFind),
    ActionEnum.yF: __convert_delete_to_yank(DeleteFindBackwards),

    ActionEnum.i: Insert,
    ActionEnum.a: Append,
    ActionEnum.I: InsertAtLineStart,
    ActionEnum.A: AppendAtLineEnd,
    ActionEnum.p: PasteAfter,
    ActionEnum.P: PasteBefore,
    ActionEnum.r: ReplaceCharacter,
    ActionEnum.R: EnterReplaceMode,
    ActionEnum.tilde: SwitchCasing,
}


def get_action(action: ActionEnum):
    return __lookup[action]
