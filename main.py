from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ccworkflow.app.bootstrap import read_startup_options, start_app


def main() -> None:
    start_app(**read_startup_options())


if __name__ == "__main__":
    main()
