"""Atomic JSON persistence for local credentials and capability records."""

from __future__ import annotations

import json
import os
import stat
import tempfile
from pathlib import Path
from typing import Any, BinaryIO

from .errors import Pan123Error


def owner_uid() -> int | None:
    """Return this process's user ID, or None where the platform has none.

    ``os.getuid`` only exists on POSIX platforms, so both the check and its
    callers guard on this value instead of on ``os.name``. The indirection also
    keeps platform-specific stubs (mypy running on Windows) type-checkable.
    """
    getuid = getattr(os, "getuid", None)
    return int(getuid()) if getuid is not None else None


def set_private_file_mode(handle: BinaryIO) -> None:
    """Restrict an open file to its owner where the platform supports it."""
    fchmod = getattr(os, "fchmod", None)
    if fchmod is not None:
        fchmod(handle.fileno(), 0o600)


def _private_directory(path: Path) -> None:
    if path.is_symlink():
        raise Pan123Error("io", "Private storage cannot use a symbolic link.")
    if not path.exists():
        _private_directory(path.parent)
        try:
            path.mkdir(mode=0o700)
        except FileExistsError:
            pass
    if not path.is_dir() or path.is_symlink():
        raise Pan123Error("io", "Private storage must be a directory.")


def write_private_json(path: Path, data: Any) -> None:
    """Write a 0600 sibling temporary file and replace the destination atomically."""
    path = Path(path)
    temporary: Path | None = None
    try:
        if path.is_symlink():
            raise Pan123Error("io", "Private storage cannot use a symbolic link.")
        _private_directory(path.parent)
        if path.exists():
            uid = owner_uid()
            if not path.is_file() or (uid is not None and path.stat().st_uid != uid):
                raise Pan123Error(
                    "io", "The private storage file is not owned by the current user."
                )
        encoded = json.dumps(data, ensure_ascii=False, allow_nan=False).encode("utf-8")
        fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
        temporary = Path(name)
        with os.fdopen(fd, "wb") as handle:
            set_private_file_mode(handle)
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        if path.is_symlink():
            raise Pan123Error("io", "Private storage cannot use a symbolic link.")
        os.replace(temporary, path)
        temporary = None
        if os.name == "posix":
            directory_fd = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
    except Pan123Error:
        raise
    except (OSError, ValueError, TypeError, UnicodeError):
        raise Pan123Error("io", "Could not write private local storage.") from None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def read_private_json(path: Path) -> Any:
    """Read a regular current-user file without following a destination symlink."""
    path = Path(path)
    try:
        if path.is_symlink() or path.parent.is_symlink():
            raise Pan123Error("io", "Private storage cannot use a symbolic link.")
        fd = os.open(path, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0))
        with os.fdopen(fd, "r", encoding="utf-8") as handle:
            information = os.fstat(handle.fileno())
            if not stat.S_ISREG(information.st_mode):
                raise Pan123Error("io", "Private storage must be a regular file.")
            if os.name == "posix":
                uid = owner_uid()
                if uid is not None and information.st_uid != uid:
                    raise Pan123Error("io", "Private storage is not owned by the current user.")
                if information.st_mode & 0o077:
                    raise Pan123Error(
                        "io",
                        "Private storage permissions must restrict access to the current user.",
                    )
            return json.load(handle)
    except Pan123Error:
        raise
    except (OSError, ValueError, UnicodeError):
        raise Pan123Error("io", "Could not read private local storage.") from None
