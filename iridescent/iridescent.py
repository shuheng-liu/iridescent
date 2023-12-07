import pexpect as pe
from .filters import DebugLogger, InputFilter, OutputFilter
from .history import HistoryManager
from .cursor import CursorManager
from .cli import opt, username, password
from .setup_keyboard import detect_keys, key_config_file, ESCAPE_SEQUENCE
from .keys import set_keys


def main():
    with HistoryManager(opt.history_path) as hm, CursorManager():
        debug_logger = DebugLogger(opt.debug_path)
        input_filter = InputFilter(opt.input_path, dlogger=debug_logger, history_manager=hm)
        output_filter = OutputFilter(opt.output_path, dlogger=debug_logger)

        if not key_config_file.exists():
            print("Keyboard layout not found. Detecting keyboard layout...")
            detect_keys()

        print("Loading keyboard layout from", key_config_file)
        print("If you want to change the keyboard layout, delete this file and restart iridescent")
        set_keys()

        with pe.spawnu(f"iris terminal {opt.instance}") as c:
            c.setecho(False)

            if username and password:
                c.expect("Username:")
                c.sendline(username)

                c.expect("Password:")
                c.send(f"{password}\r")

            print(r"You are communicating with IRIS via pexpect. The escape character is ^]")
            c.interact(
                escape_character=ESCAPE_SEQUENCE.decode(),
                input_filter=input_filter,
                output_filter=output_filter
            )


if __name__ == "__main__":
    main()
