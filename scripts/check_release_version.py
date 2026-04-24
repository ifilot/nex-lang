import argparse
import ast
import json
import subprocess
import sys
import tomllib
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

DEFAULT_REPOSITORY_URL = "https://pypi.org/pypi"
REQUEST_TIMEOUT_SECONDS = 10


def read_project_name(root: Path) -> str:
    pyproject_path = root / "pyproject.toml"
    pyproject = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    return pyproject["project"]["name"]


def read_package_version(root: Path) -> str:
    init_path = root / "nex" / "__init__.py"
    module = ast.parse(init_path.read_text(encoding="utf-8"), filename=str(init_path))

    for statement in module.body:
        if not isinstance(statement, ast.Assign):
            continue
        for target in statement.targets:
            if isinstance(target, ast.Name) and target.id == "__version__":
                value = ast.literal_eval(statement.value)
                if isinstance(value, str):
                    return value

    raise ValueError(f"Could not find string __version__ in {init_path}")


def normalize_repository_url(repository_url: str) -> str:
    return repository_url.rstrip("/")


def build_version_url(repository_url: str, project_name: str, version: str) -> str:
    safe_project = urllib.parse.quote(project_name, safe="")
    safe_version = urllib.parse.quote(version, safe="")
    return (
        f"{normalize_repository_url(repository_url)}/{safe_project}/{safe_version}/json"
    )


def fetch_version_status(repository_url: str, project_name: str, version: str) -> int:
    request = urllib.request.Request(
        build_version_url(repository_url, project_name, version),
        headers={"Accept": "application/json"},
    )

    try:
        with urllib.request.urlopen(
            request, timeout=REQUEST_TIMEOUT_SECONDS
        ) as response:
            response.read()
            return response.status
    except urllib.error.HTTPError as error:
        return error.code
    except urllib.error.URLError as error:
        raise RuntimeError(
            f"Could not check {project_name} {version} at {repository_url}: {error.reason}"
        ) from error


def version_exists(repository_url: str, project_name: str, version: str) -> bool:
    status = fetch_version_status(repository_url, project_name, version)

    if status == 200:
        return True
    if status == 404:
        return False

    raise RuntimeError(
        f"Could not check {project_name} {version} at {repository_url}: HTTP {status}"
    )


def check_tag_matches_version(tag: str | None, version: str) -> list[str]:
    if tag is None:
        return []

    expected_tag = f"v{version}"
    if tag == expected_tag:
        return []

    return [f"Release tag must be {expected_tag}, got {tag}."]


def local_tag_exists(root: Path, tag: str) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"refs/tags/{tag}"],
        cwd=root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return result.returncode == 0


def check_local_tag_available(root: Path, tag: str | None) -> list[str]:
    if tag is None or not local_tag_exists(root, tag):
        return []

    return [f"Local Git tag {tag} already exists."]


def check_repository_version_available(
    repository_url: str,
    project_name: str,
    version: str,
) -> list[str]:
    if not version_exists(repository_url, project_name, version):
        return []

    return [
        f"{project_name} {version} already exists at {normalize_repository_url(repository_url)}."
    ]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate that the release tag and PyPI version are publishable."
    )
    parser.add_argument(
        "--tag",
        help="Git tag to compare with the package version, for example v0.3.0.",
    )
    parser.add_argument(
        "--repository-url",
        default=DEFAULT_REPOSITORY_URL,
        help="Base JSON API URL for the package index.",
    )
    parser.add_argument(
        "--skip-index-check",
        action="store_true",
        help="Only validate local release metadata.",
    )
    parser.add_argument(
        "--check-local-tag",
        action="store_true",
        help="Also fail when the requested tag already exists locally.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    root = Path(__file__).resolve().parent.parent
    project_name = read_project_name(root)
    version = read_package_version(root)

    errors = check_tag_matches_version(args.tag, version)
    if args.check_local_tag:
        errors.extend(check_local_tag_available(root, args.tag))
    try:
        if not args.skip_index_check:
            errors.extend(
                check_repository_version_available(
                    args.repository_url, project_name, version
                )
            )
    except RuntimeError as error:
        errors.append(str(error))

    if errors:
        print("Release version check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "project": project_name,
                "version": version,
                "tag": args.tag,
                "repository_url": normalize_repository_url(args.repository_url),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
