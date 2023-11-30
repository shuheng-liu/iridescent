import os
import sys
import argparse


def _fetch_credentials():
    return tuple(
        os.environ.get(k, None)
        for k in ["IRIS_USERNAME", "IRIS_PASSWORD"]
    )


_parser = argparse.ArgumentParser()
_parser.add_argument("instance", nargs='?', default=os.environ.get("IRIS_INSTANCE", None), type=str)
_parser.add_argument("--input-path", "-i", type=str, help="location of input logs")
_parser.add_argument("--output-path", "-o", type=str, help="location of output logs")
_parser.add_argument("--debug-path", "-d", type=str, help="Location of debugging logs")
_parser.add_argument("--history-path", "-H", type=str, help="Location of history files")
opt = _parser.parse_args()

if opt.instance is None:
    print(
        "Please specify instance name using\n"
        f"\t{sys.argv[0]} <instance>\n"
        "or set the $IRIS_INSTANCE environment variable."
    )
    sys.exit(1)

username, password = _fetch_credentials()
if (not username or not password) and (opt.input_path or opt.output_path or opt.debug_path):
    yn = input(
        "Credentials are not specified in environment variables $IRIS_USERNAME and $IRIS_PASSWORD.\n"
        "Consider specifying those or turn off logging. Otherwise, your credentials might be logged.\n"
        "Proceed? (y/N) "
    )
    if not yn.lower().startswith("y"):
        print("Aborting due to security concerns.")
        sys.exit(0)
