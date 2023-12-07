import os
import sys
import argparse


def _fetch_credentials():
    return tuple(
        os.environ.get(k, None)
        for k in ["IRIS_USERNAME", "IRIS_PASSWORD"]
    )


default_history = os.path.expanduser("~/.iris_history")

_parser = argparse.ArgumentParser()
_parser.add_argument("instance", nargs='?', default=os.environ.get("IRIS_INSTANCE", None), type=str)
_parser.add_argument("--log-path", "-l", type=str, help="Location of input and output logs")
_parser.add_argument("--debug-path", "-d", type=str, help="Location of debugging outputs")
_parser.add_argument("--history-path", "-H", type=str, default=default_history,
                     help="Location of history file. Defaults to ~/.iris_history")
opt = _parser.parse_args()

if opt.instance is None:
    print(
        "Please specify instance name using\n"
        f"\t{sys.argv[0]} <instance>\n"
        "or set the $IRIS_INSTANCE environment variable."
    )
    sys.exit(1)

username, password = _fetch_credentials()
if (not username or not password) and (opt.log_path or opt.debug_path):
    yn = input(
        "Credentials are not specified in environment variables $IRIS_USERNAME and $IRIS_PASSWORD.\n"
        "Consider specifying those or turn off logging. Otherwise, your credentials might be logged.\n"
        "Ignore the warning and proceed? (y/N) "
    )
    if not yn.lower().startswith("y"):
        print("Aborting due to security concerns.")
        sys.exit(0)
