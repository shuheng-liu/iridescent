import pexpect as pe
from .filters import DebugLogger, IOFilter
from .history import HistoryManager
from .cursor import CursorManager
from .cli import opt, username, password
from .keyboard import detect_keys, key_config_file, ESCAPE_SEQUENCE
from .keys import set_keys


def main():
    with HistoryManager(opt.history_path) as hm, CursorManager():
        if not key_config_file.exists():
            print("Keyboard layout not found. Detecting keyboard layout...")
            detect_keys()

        print("Loading keyboard layout from", key_config_file)
        print("If you want to change the keyboard layout, delete this file and restart iridescent")
        set_keys()

        debug_logger = DebugLogger(opt.debug_path)
        io_filter = IOFilter(opt.log_path, debug_logger, history_manager=hm)

        with pe.spawnu(f"iris terminal {opt.instance}") as c:

            try:
                import signal, fcntl, struct, termios, sys
                # See .interact() docs at https://pexpect.readthedocs.io/en/stable/api/pexpect.html#spawn-class

                def sigwinch_passthrough(sig, data):
                    s = struct.pack("HHHH", 0, 0, 0, 0)
                    a = struct.unpack('hhhh', fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, s))
                    if not c.closed:
                        c.setwinsize(a[0], a[1])

                signal.signal(signal.SIGWINCH, sigwinch_passthrough)
            except ModuleNotFoundError:
                pass

            c.setecho(False)

            if username and password:
                c.expect("Username:")
                c.sendline(username)

                c.expect("Password:")
                c.send(f"{password}\r")

            print(r"You are communicating with IRIS via pexpect. The escape character is ^]")
            c.interact(
                escape_character=ESCAPE_SEQUENCE.decode(),
                input_filter=io_filter.filter_input,
                output_filter=io_filter.filter_output
            )


if __name__ == "__main__":
    main()
