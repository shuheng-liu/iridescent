from string import ascii_letters, digits, punctuation, whitespace, printable

whitespace = whitespace.encode('utf-8')
ascii_letters = ascii_letters.encode('utf-8')
digits = digits.encode('utf-8')
punctuation = punctuation.encode('utf-8')

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
