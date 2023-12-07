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

    @property
    def bvalue(self):
        return self.value.encode()

    def set(self):
        print(self.value, end="", flush=True)

    @staticmethod
    def reset():
        print(FgColor.RESET.value, end="", flush=True)


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

    @property
    def bvalue(self):
        return self.value.encode()

    def set(self):
        print(self.value, end="", flush=True)

    @staticmethod
    def reset():
        print(BgColor.RESET.value, end="", flush=True)


class TextStyle(Enum):
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    INVERSE = "\033[7m"

    @property
    def bvalue(self):
        return self.value.encode()

    def set(self):
        print(self.value, end="", flush=True)

    @staticmethod
    def reset():
        print(TextStyle.RESET.value, end="", flush=True)
