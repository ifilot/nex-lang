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


def iter_text_files(root: Path):
    for pattern in TEXT_FILE_PATTERNS:
        for path in root.rglob(pattern):
            if any(part in IGNORED_DIR_NAMES for part in path.parts):
                continue
            if path.is_file():
                yield path


def main() -> int:
    root = Path(__file__).resolve().parent.parent
    non_ascii_files = []

    for path in sorted(set(iter_text_files(root))):
        try:
            path.read_text(encoding="ascii")
        except UnicodeDecodeError:
            non_ascii_files.append(path.relative_to(root))

    if non_ascii_files:
        print("Found non-ASCII text files:", file=sys.stderr)
        for path in non_ascii_files:
            print(path, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
