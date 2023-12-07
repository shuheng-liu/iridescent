import pexpect as pe
from .filters import DebugLogger, InputFilter, OutputFilter
from .history import HistoryManager
from .cursor import CursorManager
from .cli import opt, username, password


def main():
    with HistoryManager(opt.history_path) as hm, CursorManager():
        debug_logger = DebugLogger(opt.debug_path)
        input_filter = InputFilter(opt.input_path, dlogger=debug_logger, history_manager=hm)
        output_filter = OutputFilter(opt.output_path, dlogger=debug_logger)

        with pe.spawnu(f"iris terminal {opt.instance}") as c:
            c.setecho(False)

            if username and password:
                c.expect("Username:")
                c.sendline(username)

                c.expect("Password:")
                c.send(f"{password}\r")

            print(r"You are communicating with IRIS via pexpect. The escape character is ^]")
            c.interact(
                input_filter=input_filter,
                output_filter=output_filter
            )


if __name__ == "__main__":
    main()
