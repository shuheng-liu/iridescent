import warnings
from enum import Enum


class FgColor(Enum):
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    RESET = "\033[0m"


class BgColor(Enum):
    BLACK = "\033[40m"
    RED = "\033[41m"
    GREEN = "\033[42m"
    YELLOW = "\033[43m"
    BLUE = "\033[44m"
    MAGENTA = "\033[45m"
    CYAN = "\033[46m"
    WHITE = "\033[47m"
    RESET = "\033[0m"


class TextStyle(Enum):
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    INVERSE = "\033[7m"


def _set_fg_color(color: FgColor):
    if not color:
        return
    assert isinstance(color, FgColor)
    print(color.value, end="", flush=True)


def _set_bg_color(color: BgColor):
    if not color:
        return
    assert isinstance(color, BgColor)
    print(color.value, end="", flush=True)


def _set_style(style: TextStyle):
    if not style:
        return
    assert isinstance(style, TextStyle)
    print(style.value, end="", flush=True)


def _reset_color_style():
    print("\033[0m", end="", flush=True)


class ColorManager:
    def __init__(self, input_fg=None, input_bg=None, output_fg=None, output_bg=None):
        self.input_fg = input_fg
        self.input_bg = input_bg
        self.output_fg = output_fg
        self.output_bg = output_bg

        self.is_input = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _reset_color_style()

    def trigger_input(self):
        self.is_input = True

    def trigger_output(self):
        self.is_input = False

    def set_input_color(self):
        if self.is_input is True:
            _set_fg_color(self.input_fg)
            _set_bg_color(self.input_bg)

    def set_output_color(self):
        if self.is_input is False:
            _set_fg_color(self.output_fg)
            _set_bg_color(self.output_bg)

    def reset(self):
        _reset_color_style()
