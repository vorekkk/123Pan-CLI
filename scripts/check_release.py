"""Validate the built distributions and metadata before publishing to PyPI.

Run after ``python -m build``. Checks the release tag against the project
version and inspects both artifacts without contacting any index, so it is safe
to run offline and in a pull request.
"""

from __future__ import annotations

import argparse
import re
import tarfile
import tomllib
import zipfile
from email.parser import Parser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ISSUE_URL = "https://github.com/vorekkk/123Pan-CLI/issues"
REQUIRED_METADATA = (
    "Metadata-Version",
    "Name",
    "Version",
    "Summary",
    # setuptools emits Author-email for [project.authors] entries.
    "Author-email",
    "Requires-Python",
    "Description-Content-Type",
    "Project-URL",
    "Classifier",
    "License-Expression",
)
FORBIDDEN_PREFIXES = ("tests/", "docs/", ".github/", "scripts/")
# The wheel is an installed runtime artifact and must never carry credentials or
# a template; the sdist is a source archive and may carry the empty template.
FORBIDDEN_ENV_NAMES = (".env",)
PACKAGE_FILES = (
    "pan123_cli/__init__.py",
    "pan123_cli/__main__.py",
    "pan123_cli/auth.py",
    "pan123_cli/cache.py",
    "pan123_cli/catalog.py",
    "pan123_cli/cli.py",
    "pan123_cli/client.py",
    "pan123_cli/config.py",
    "pan123_cli/errors.py",
    "pan123_cli/output.py",
    "pan123_cli/services/downloading.py",
    "pan123_cli/services/listing.py",
    "pan123_cli/services/sharing.py",
    "pan123_cli/services/uploading.py",
    "pan123_cli/utils/files.py",
    "pan123_cli/utils/urls.py",
)
VERSION = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+(?:[abc][0-9]+|\.post[0-9]+|\.dev[0-9]+)?")


def fail(message: str) -> None:
    raise SystemExit(f"release check failed: {message}\nReport this at {ISSUE_URL}")


def project_metadata() -> dict:
    try:
        with (ROOT / "pyproject.toml").open("rb") as handle:
            return tomllib.load(handle)["project"]
    except (OSError, KeyError, tomllib.TOMLDecodeError) as error:
        fail(f"cannot read [project] from pyproject.toml ({error})")


def check_tag(project: dict, tag: str | None) -> str:
    version = str(project["version"])
    if not VERSION.fullmatch(version):
        fail(f"version {version!r} is not a simple release version")
    if tag and tag not in {version, f"v{version}"}:
        fail(f"tag {tag!r} does not match the project version {version!r}")
    return version


def select_distributions(directory: Path, name: str, version: str) -> tuple[Path, Path]:
    wheels = sorted(directory.glob("*.whl"))
    archives = sorted(directory.glob("*.tar.gz"))
    if len(wheels) != 1 or len(archives) != 1:
        fail(f"expected exactly one wheel and one sdist in {directory}")
    wheel, archive = wheels[0], archives[0]
    for path in (wheel, archive):
        expected = f"{name.replace('-', '_')}-{version}"
        if not path.name.startswith(expected):
            fail(f"{path.name} does not match {name} {version}")
    return wheel, archive


def check_wheel(wheel: Path, name: str, version: str) -> None:
    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
        for entry in names:
            if entry.startswith(FORBIDDEN_PREFIXES) or Path(entry).name.startswith(".env"):
                fail(f"{wheel.name} ships development file {entry}")
        missing = [entry for entry in PACKAGE_FILES if entry not in names]
        if missing:
            fail(f"{wheel.name} is missing {', '.join(missing)}")
        if not wheel.name.endswith("py3-none-any.whl"):
            fail(f"{wheel.name} must stay a universal py3-none-any wheel")
        metadata_name = next(
            (entry for entry in names if entry.endswith(".dist-info/METADATA")), None
        )
        entry_points = next(
            (entry for entry in names if entry.endswith(".dist-info/entry_points.txt")), None
        )
        licences = [entry for entry in names if ".dist-info/licenses/" in entry]
        if metadata_name is None or entry_points is None or not licences:
            fail(f"{wheel.name} has no METADATA, entry_points.txt or bundled LICENSE")
        metadata = Parser().parsestr(archive.read(metadata_name).decode("utf-8"))
        for field in REQUIRED_METADATA:
            if not metadata.get_all(field):
                fail(f"{wheel.name} metadata has no {field}")
        if metadata["Name"] != name or metadata["Version"] != version:
            fail(f"{wheel.name} metadata is {metadata['Name']} {metadata['Version']}")
        if len(metadata.get_payload().strip()) < 200:
            fail(f"{wheel.name} has an empty or truncated long description")
        scripts = archive.read(entry_points).decode("utf-8")
        if "pan123 = pan123_cli.cli:main" not in scripts:
            fail(f"{wheel.name} does not expose the pan123 console script")
        print(f"wheel ok: {wheel.name} ({len(names)} entries, console script present)")


def check_sdist(archive_path: Path, name: str, version: str) -> None:
    prefix = f"{name.replace('-', '_')}-{version}/"
    with tarfile.open(archive_path) as archive:
        names = archive.getnames()
        required = ("LICENSE", "README.md", "pyproject.toml", "src/pan123_cli/cli.py")
        missing = [entry for entry in required if f"{prefix}{entry}" not in names]
        if missing:
            fail(f"{archive_path.name} is missing {', '.join(missing)}")
        leaked = [
            entry for entry in names if Path(entry).name in FORBIDDEN_ENV_NAMES or "/.git/" in entry
        ]
        if leaked:
            fail(f"{archive_path.name} ships {', '.join(leaked)}")
        print(f"sdist ok: {archive_path.name} ({len(names)} entries, LICENSE included)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", help="release tag to cross-check, for example v0.1.0")
    parser.add_argument("--dist", default="dist", help="directory holding the built artifacts")
    arguments = parser.parse_args()

    project = project_metadata()
    name = str(project["name"])
    version = check_tag(project, arguments.tag)
    wheel, archive = select_distributions(ROOT / arguments.dist, name, version)
    check_wheel(wheel, name, version)
    check_sdist(archive, name, version)
    print(
        f"release ready: {name} {version} (tag {'v' + version if arguments.tag else 'unchecked'})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
