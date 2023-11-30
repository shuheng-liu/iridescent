#!/Users/shuliu/PycharmProjects/pexpect/venv/bin/python3
import os
import argparse
import sys

import pexpect as pe
from filters import DebugLogger, InputFilter, OutputFilter
from history import HistoryManager

parser = argparse.ArgumentParser()
parser.add_argument("instance", nargs='?', default=os.environ.get("IRIS_INSTANCE", None), type=str)
parser.add_argument("--input-path", "-i", type=str, help="location of input logs")
parser.add_argument("--output-path", "-o", type=str, help="location of output logs")
parser.add_argument("--debug-path", "-d", type=str, help="Location of debugging logs")
parser.add_argument("--history-path", "-H", type=str, help="Location of history files")


def fetch_credentials():
    return tuple(
        os.environ.get(k, None)
        for k in ["IRIS_USERNAME", "IRIS_PASSWORD"]
    )


if __name__ == "__main__":
    opt = parser.parse_args()
    if opt.instance is None:
        print(
            "Please specify instance name using\n"
            f"\t{sys.argv[0]} <instance>\n"
            "or set the $IRIS_INSTANCE environment variable."
        )
        sys.exit(1)

    username, password = fetch_credentials()
    if (not username or not password) and (opt.input_path or opt.output_path or opt.debug_path):
        yn = input(
            "Credentials are not specified in environment variables $IRIS_USERNAME and $IRIS_PASSWORD.\n"
            "Consider specifying those or turn off logging. Otherwise, your credentials might be logged.\n"
            "Proceed? (y/N) "
        )
        if not yn.lower().startswith("y"):
            print("Aborting due to security concerns.")
            sys.exit(0)

    with HistoryManager(opt.history_path) as hm:
        debug_logger = DebugLogger(opt.debug_path)
        input_filter = InputFilter(opt.input_path, dlogger=debug_logger, history_manager=hm)
        output_filter = OutputFilter(opt.output_path, dlogger=debug_logger)

        with pe.spawnu(f"/usr/local/bin/iris session {opt.instance}") as c:
            c.setecho(False)

            if username and password:
                c.expect("Username:")
                c.sendline(username)

                c.expect("Password:")
                c.send(f"{password}\r")

            print(r"You are inside IRIS using pexpect. The escape character is ^]")
            c.interact(
                input_filter=input_filter,
                output_filter=output_filter
            )
            c.kill(15)
            print("\n\nIRIS session terminated.")
