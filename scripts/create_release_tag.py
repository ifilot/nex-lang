import argparse
import subprocess
import sys
from pathlib import Path

import check_release_version


def run_git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


def create_annotated_tag(root: Path, tag: str, message: str) -> None:
    result = run_git(root, ["tag", "-a", tag, "-m", message])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a release tag only after release-version checks pass."
    )
    parser.add_argument(
        "--tag",
        help="Release tag to create. Defaults to v<package-version>.",
    )
    parser.add_argument(
        "--message",
        help="Annotated tag message. Defaults to 'Release <tag>'.",
    )
    parser.add_argument(
        "--repository-url",
        default=check_release_version.DEFAULT_REPOSITORY_URL,
        help="Base JSON API URL for the package index.",
    )
    parser.add_argument(
        "--skip-index-check",
        action="store_true",
        help="Skip the package-index availability check.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    root = Path(__file__).resolve().parent.parent
    project_name = check_release_version.read_project_name(root)
    version = check_release_version.read_package_version(root)
    tag = args.tag or f"v{version}"

    errors = check_release_version.check_tag_matches_version(tag, version)
    errors.extend(check_release_version.check_local_tag_available(root, tag))
    try:
        if not args.skip_index_check:
            errors.extend(
                check_release_version.check_repository_version_available(
                    args.repository_url,
                    project_name,
                    version,
                )
            )
    except RuntimeError as error:
        errors.append(str(error))

    if errors:
        print("Release tag was not created:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    message = args.message or f"Release {tag}"
    try:
        create_annotated_tag(root, tag, message)
    except RuntimeError as error:
        print(f"Release tag was not created: {error}", file=sys.stderr)
        return 1

    print(f"Created release tag {tag} for {project_name} {version}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
