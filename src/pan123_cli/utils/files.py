"""Bounded file hashing and safe local publication primitives."""

from __future__ import annotations

import hashlib
import os
import re
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO

from pan123_cli.errors import Pan123Error

BLOCK_SIZE = 1024 * 1024
_MD5 = re.compile(r"^[0-9a-fA-F]{32}$")


@dataclass(frozen=True)
class FileSnapshot:
    size: int
    mtime_ns: int
    inode: int
    device: int


def snapshot_file(path: Path) -> FileSnapshot:
    try:
        value = path.stat()
    except OSError:
        raise Pan123Error(
            "LOCAL_IO", "Cannot read the local source file.", details={"path": str(path)}
        ) from None
    if not stat.S_ISREG(value.st_mode):
        raise Pan123Error("INVALID_INPUT", "The source must be a regular file.", exit_code=2)
    return FileSnapshot(value.st_size, value.st_mtime_ns, value.st_ino, value.st_dev)


def assert_source_unchanged(path: Path, original: FileSnapshot) -> None:
    if snapshot_file(path) != original:
        raise Pan123Error(
            "SOURCE_CHANGED", "The source file changed during the upload.", exit_code=7
        )


def hash_file(path: Path, algorithm: str = "md5") -> tuple[str, FileSnapshot]:
    original = snapshot_file(path)
    digest = hashlib.new(algorithm, usedforsecurity=False)
    try:
        with path.open("rb") as handle:
            opened = os.fstat(handle.fileno())
            if (opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns) != (
                original.device,
                original.inode,
                original.size,
                original.mtime_ns,
            ):
                raise Pan123Error(
                    "SOURCE_CHANGED", "The source file changed before hashing.", exit_code=7
                )
            while block := handle.read(BLOCK_SIZE):
                digest.update(block)
    except OSError:
        raise Pan123Error(
            "LOCAL_IO", "Cannot hash the local file.", details={"path": str(path)}
        ) from None
    assert_source_unchanged(path, original)
    return digest.hexdigest(), original


def valid_md5(value: object) -> bool:
    return isinstance(value, str) and _MD5.fullmatch(value) is not None


def safe_filename(name: object, *, upload: bool = False, windows: bool | None = None) -> str:
    if not isinstance(name, str) or not name.strip() or name in {".", ".."}:
        raise Pan123Error("INVALID_INPUT", "A safe nonempty filename is required.", exit_code=2)
    if any(ord(char) < 32 or 127 <= ord(char) < 160 for char in name):
        raise Pan123Error(
            "INVALID_INPUT", "A filename cannot contain control characters.", exit_code=2
        )
    if any(char in name for char in "/\\") or Path(name).is_absolute():
        raise Pan123Error(
            "INVALID_INPUT", "A filename must not contain a directory path.", exit_code=2
        )
    if upload and (len(name) >= 255 or any(char in name for char in '"/:*?|><')):
        raise Pan123Error(
            "INVALID_INPUT", "The remote filename violates the upload naming rules.", exit_code=2
        )
    if windows is None:
        windows = os.name == "nt"
    if windows:
        reserved = {"CON", "PRN", "AUX", "NUL", "CONIN$", "CONOUT$"}
        reserved.update(f"{prefix}{number}" for prefix in ("COM", "LPT") for number in range(1, 10))
        stem = name.split(".", 1)[0].upper()
        if name.endswith((" ", ".")) or stem in reserved or any(char in name for char in ':*?"<>|'):
            raise Pan123Error("INVALID_INPUT", "The filename is not valid on Windows.", exit_code=2)
    return name


def validate_target(path: Path, *, overwrite: bool) -> None:
    try:
        info = path.lstat()
    except FileNotFoundError:
        return
    except OSError:
        raise Pan123Error(
            "LOCAL_IO", "Cannot inspect the output path.", details={"path": str(path)}
        ) from None
    if not stat.S_ISREG(info.st_mode):
        raise Pan123Error(
            "LOCAL_IO",
            "Output must not be a symlink, directory, or special file.",
            details={"path": str(path)},
        )
    if not overwrite:
        raise Pan123Error(
            "LOCAL_IO",
            "The output file already exists; explicit overwrite is required.",
            details={"path": str(path)},
        )


def publish_file(part: Path, final: Path, *, overwrite: bool) -> None:
    validate_target(final, overwrite=overwrite)
    try:
        if overwrite:
            os.replace(part, final)
        else:
            os.link(part, final)
            # Publication has succeeded. A leftover second link is a cleanup
            # problem, not a failed transfer or a reason to delete the final.
            try:
                part.unlink()
            except OSError:
                pass
    except OSError:
        raise Pan123Error(
            "LOCAL_IO",
            "Cannot publish the verified file without changing another target.",
            details={"path": str(final), "part_path": str(part)},
        ) from None


def open_source(path: Path) -> BinaryIO:
    snapshot_file(path)
    try:
        return path.open("rb")
    except OSError:
        raise Pan123Error(
            "LOCAL_IO", "Cannot open the source file.", details={"path": str(path)}
        ) from None
