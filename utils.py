from string import ascii_letters, digits, punctuation, whitespace
from enum import Enum

whitespace = b" \n\t"
ascii_letters = ascii_letters.encode('utf-8')
digits = digits.encode('utf-8')
punctuation = punctuation.encode('utf-8')
printable = ascii_letters + digits + punctuation + whitespace

_word_components = ascii_letters + digits + b"_"

nonwhitespace_printable = ascii_letters + digits + punctuation

CHUNK_TYPES = (
    whitespace,
    ascii_letters + digits,  # alphanumeric
    punctuation
)


def get_chunk(ch, chunk_types=CHUNK_TYPES):
    return next((chunk for chunk in chunk_types if ch in chunk), None)


def _chunk_leftmost(content, pos):
    r"""Return the leftmost position of the current chunk.
    The current char is defined as the char to the left of the cursor.
    """
    assert 0 <= pos <= len(content), f"Invalid cursor position {pos} for string of length {len(content)}"
    if len(content) == 0 or pos == 0:
        return 0
    curr_char = content[pos - 1]
    chunk = next((chk for chk in CHUNK_TYPES if curr_char in chk), None)
    if chunk is None:
        return pos
    while pos >= 0:
        pos -= 1
        if pos < 0 or content[pos - 1] not in chunk:
            break
    return pos + 1


def _chunk_rightmost(content, pos):
    r"""Return the rightmost position of the current chunk.
    The current char is defined as the char to the right of the cursor.
    """
    assert 0 <= pos <= len(content), f"Invalid cursor position {pos} for string of length {len(content)}"
    if len(content) == 0 or pos == len(content):
        return len(content)
    curr_char = content[pos]
    chunk = next((chk for chk in CHUNK_TYPES if curr_char in chk), None)
    if chunk is None:
        return pos
    while pos < len(content):
        pos += 1
        if pos >= len(content) or content[pos] not in chunk:
            break
    return pos - 1


def next_predicate(content, pos, predicate):
    while pos < len(content):
        pos += 1
        if pos == len(content):
            return -1
        if predicate(content[pos]):
            return pos


def prev_predicate(content, pos, predicate):
    while pos >= 0:
        pos -= 1
        if pos < 0:
            return -1
        if predicate(content[pos]):
            return pos


class _ByteGroup(Enum):
    NONWHITESPACE = -1
    WHITESPACE = 0
    ALPHANUMERIC = 1
    PUNCTUATION = 2


def _get_group(byte, capital):
    if capital:
        return _ByteGroup.WHITESPACE if byte in b' \t' else _ByteGroup.NONWHITESPACE
    if byte in whitespace:
        return _ByteGroup.WHITESPACE
    elif byte in _word_components:
        return _ByteGroup.ALPHANUMERIC
    elif byte in punctuation:
        return _ByteGroup.PUNCTUATION
    raise ValueError("Invalid byte: " + repr(byte))


def vim_word(content, npos, capital=False):  # emulate "w"/"W" in vim
    r"""Return the beginning of the next word if there is one. Otherwise, return len(content)."""
    assert 0 <= npos < len(content)
    grp = _get_group(content[npos], capital)
    while True:
        npos += 1
        if npos == len(content):
            return len(content)

        newgrp = _get_group(content[npos], capital)
        if grp != newgrp and newgrp is not _ByteGroup.WHITESPACE:
            return npos
        grp = newgrp


def vim_word_end(content, npos, capital=False):  # emulate "e"/"E" in vim
    r"""Return the next end-of-word. If none found, return len(content)."""
    assert 0 <= npos < len(content)
    grp = _get_group(content[npos], capital)
    is_group_end = npos == len(content) - 1 or _get_group(content[npos + 1], capital) != grp

    # ensure we are inside the word of interest, not in a whitespace, or an end-of-word already,
    if grp is _ByteGroup.WHITESPACE or is_group_end:
        npos = vim_word(content, npos, capital)
        if npos == len(content):
            return len(content)
        grp = _get_group(content[npos], capital)

    while True:
        npos += 1
        if npos == len(content):
            return npos - 1
        newgrp = _get_group(content[npos], capital)
        if grp != newgrp:
            return npos - 1
        grp = newgrp


def vim_word_begin(content, npos, capital=False):  # emulate "b"/"B" in vim
    r"""Return the previous begin-of-word. If none found, return -1."""
    assert 0 <= npos < len(content)
    grp = _get_group(content[npos], capital)
    is_group_begin = (npos == 0) or _get_group(content[npos - 1], capital) != grp

    # ensure we are inside the word of interest, not in a whitespace, or an begin-of-word already,
    while grp is _ByteGroup.WHITESPACE or is_group_begin:
        npos -= 1
        is_group_begin = False
        if npos < 0:
            return -1
        grp = _get_group(content[npos], capital)

    while True:
        npos -= 1
        if npos < 0:
            return 0
        newgrp = _get_group(content[npos], capital)
        if grp != newgrp:
            return npos + 1
        grp = newgrp
