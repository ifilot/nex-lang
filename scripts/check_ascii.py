import shutil
import subprocess
import sys
from pathlib import Path

TEXT_FILE_PATTERNS = (
    "*.md",
    "*.nex",
    "*.py",
    "*.toml",
    "*.yml",
    "*.yaml",
)

IGNORED_DIR_NAMES = {
    ".git",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
}
TEXT_FILE_SUFFIXES = {pattern.removeprefix("*") for pattern in TEXT_FILE_PATTERNS}


def iter_text_files(root: Path):
    for path in root.rglob("*"):
        if any(part in IGNORED_DIR_NAMES for part in path.parts):
            continue
        if path.is_file() and path.suffix in TEXT_FILE_SUFFIXES:
            yield path


def find_non_ascii_files_python(root: Path):
    non_ascii_files = []

    for path in sorted(iter_text_files(root)):
        try:
            path.read_text(encoding="ascii")
        except UnicodeDecodeError:
            non_ascii_files.append(path.relative_to(root))

    return non_ascii_files


def find_non_ascii_files_rg(root: Path, rg_executable: str):
    command = [
        rg_executable,
        "--files-with-matches",
        "-P",
        r"[^\x00-\x7F]",
    ]

    for pattern in TEXT_FILE_PATTERNS:
        command.extend(["--glob", pattern])

    for directory in sorted(IGNORED_DIR_NAMES):
        command.extend(["-g", f"!**/{directory}/**"])

    command.append(".")

    result = subprocess.run(
        command,
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode == 1:
        return []

    if result.returncode != 0:
        return None

    return sorted(Path(line) for line in result.stdout.splitlines() if line)


def find_non_ascii_files(root: Path):
    rg_executable = shutil.which("rg")
    if rg_executable is not None:
        non_ascii_files = find_non_ascii_files_rg(root, rg_executable)
        if non_ascii_files is not None:
            return non_ascii_files

    return find_non_ascii_files_python(root)


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    non_ascii_files = find_non_ascii_files(root)

    if non_ascii_files:
        print("Found non-ASCII text files:", file=sys.stderr)
        for path in non_ascii_files:
            print(path, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
