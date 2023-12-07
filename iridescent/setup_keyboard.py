import os
import json
import pexpect as pe
from pathlib import Path

_strokes = {}
_enter = ""
ESCAPE_SEQUENCE = b'\x1d'

key_config_file = Path(os.path.expanduser("~")) / ".iridescent" / "strokes.json"


class InputInterceptor:
    def __init__(self, target):
        self.target = target

    def __call__(self, b):
        _strokes[self.target] = b
        return ESCAPE_SEQUENCE


def _detect(name, description):
    print("Input this key (combination):\n", description)
    with pe.spawnu("/bin/sh") as c:
        c.setecho(False)
        c.interact(
            escape_character=ESCAPE_SEQUENCE,
            input_filter=InputInterceptor(name),
            output_filter=lambda b: b"",
        )
    print("Recorded stroke:", _strokes[name])


def write_strokes():
    key_config_file.parent.mkdir(parents=True, exist_ok=True)

    with open(key_config_file, "w") as f:
        json.dump({key: value.decode() for key, value in _strokes.items()}, f)


def load_strokes():
    if not key_config_file.exists():
        return
    with open(key_config_file) as f:
        d = json.load(f)
    return {key: value.encode() for key, value in d.items()}


def detect_keys():
    key_descriptions = [
        ("OPTION.LEFT", "<Meta><Left>, e.g., <Alt><Left> on windows or <Option><Left> on mac"),
        ("OPTION.RIGHT", "<Meta><Right>, e.g., <Alt><Right> on windows or <Option><Right> on mac"),
        ("OPTION.UP", "<Meta><Up>, e.g., <Alt><Up> on windows or <Option><Up> on mac"),
        ("OPTION.DOWN", "<Meta><Down>, e.g., <Alt><Down> on windows or <Option><Down> on mac"),
        ("OPTION.DELETE", "<Meta><DELETE>, e.g., <Alt><DELETE> on windows or <Option><DELETE> on mac"),

        ("SIG.INT", "<Ctrl>c"),
        ("SIG.BELL", "<Ctrl>g"),
        ("CTRL.R", "<Ctrl>r"),

        ("KEY.DELETE", "<BACKSPACE> on windows or <DELETE> on mac"),
        ("KEY.ESCAPE", "ESC"),
        ("KEY.ENTER", "ENTER"),

        ("KEY.UP", "<Up>"),
        ("KEY.DOWN", "<Down>"),
        ("KEY.LEFT", "<Left>"),
        ("KEY.RIGHT", "<Right>"),
    ]

    for k, desc in key_descriptions:
        _detect(k, desc)

    write_strokes()
