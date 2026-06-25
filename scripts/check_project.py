from __future__ import annotations

import subprocess
import sys


def run(command: list[str]) -> int:
    print("+", " ".join(command))
    return subprocess.call(command)


def main() -> int:
    steps = [
        [sys.executable, "-m", "pip", "install", "-e", ".[dev]"],
        ["ruff", "check", "."],
        ["pytest", "-q"],
        ["stock-brushup", "sample", "--output", "reports"],
    ]
    for step in steps:
        code = run(step)
        if code != 0:
            return code
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
