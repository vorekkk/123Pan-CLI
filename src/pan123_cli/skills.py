"""Portable, conflict-aware installation of the bundled Agent Skill."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import tempfile
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from . import __version__
from .errors import Pan123Error

NAME = "pan123-cli"
MARKER = ".pan123-skill.json"
AGENTS = ("codex", "claude", "cursor")


def source_directory() -> Path:
    bundled = Path(__file__).parent / "skill_data"
    return bundled if bundled.is_dir() else Path(__file__).resolve().parents[2] / "skills" / NAME


def detected_agents() -> list[str]:
    home = Path.home()
    return [
        agent
        for agent in AGENTS
        if (home / (".codex" if agent == "codex" else "." + agent)).is_dir()
        or (agent == "codex" and os.environ.get("CODEX_HOME"))
    ]


def destination(agent: str, scope: str, dest: str | None = None) -> Path:
    if dest:
        return Path(dest).expanduser().absolute()
    if scope == "project":
        root = Path.cwd() / (".agents" if agent == "codex" else "." + agent)
    else:
        root = (
            Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).expanduser()
            if agent == "codex"
            else Path.home() / ("." + agent)
        )
    return root / "skills" / NAME


def hashes(root: Path) -> dict[str, str]:
    result = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise Pan123Error("FILE_CONFLICT", "Skill 目录包含符号链接，拒绝修改。")
        if path.is_file() and path.name != MARKER:
            result[path.relative_to(root).as_posix()] = hashlib.sha256(
                path.read_bytes()
            ).hexdigest()
    return result


def safe_path(path: Path) -> None:
    if any(part.is_symlink() for part in (path, *path.parents)):
        raise Pan123Error("FILE_CONFLICT", "Skill 安装路径不能使用符号链接。")


def status(path: Path) -> str:
    safe_path(path)
    if not path.exists():
        return "missing"
    try:
        record = json.loads((path / MARKER).read_text(encoding="utf-8"))
        if (
            record.get("name") == NAME
            and record.get("schema_version") == 1
            and record.get("files") == hashes(path)
        ):
            return "managed"
    except (OSError, ValueError, AttributeError):
        pass
    return "conflict"


@contextmanager
def install_lock(path: Path) -> Iterator[None]:
    lock = path.parent / ("." + path.name + ".install-lock")
    try:
        lock.mkdir()
    except FileExistsError:
        raise Pan123Error(
            "FILE_CONFLICT", "另一个 Skill 安装正在进行；确认无安装进程后清理 " + str(lock)
        ) from None
    try:
        yield
    finally:
        lock.rmdir()


def manage(action: str, options: dict[str, Any]) -> dict[str, Any]:
    agents = options.get("agent") or (
        ["codex"] if options.get("dest") else detected_agents() or ["codex"]
    )
    if options.get("dest") and len(set(agents)) > 1:
        raise Pan123Error("INVALID_ARGUMENT", "--dest 不能与多个 --agent 一起使用。")
    results = []
    for agent in dict.fromkeys(agents):
        path = destination(agent, options.get("scope", "user"), options.get("dest"))
        safe_path(path)
        if action == "status":
            results.append({"agent": agent, "path": str(path), "status": status(path)})
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        with install_lock(path):
            state = status(path)
            force = options.get("force", False)
            if state == "conflict" and not force:
                raise Pan123Error(
                    "FILE_CONFLICT", "Skill 已存在且不是未修改的托管版本；使用 --force 备份后继续。"
                )
            if (
                action == "install"
                and state == "managed"
                and hashes(path) == hashes(source_directory())
            ):
                results.append({"agent": agent, "path": str(path), "status": "unchanged"})
                continue
            backup = None
            temporary = None
            try:
                if action == "install":
                    temporary = Path(
                        tempfile.mkdtemp(prefix="." + path.name + "-", dir=path.parent)
                    )
                    shutil.copytree(source_directory(), temporary, dirs_exist_ok=True)
                    (temporary / MARKER).write_text(
                        json.dumps(
                            {
                                "schema_version": 1,
                                "name": NAME,
                                "version": __version__,
                                "files": hashes(temporary),
                            },
                            ensure_ascii=False,
                        ),
                        encoding="utf-8",
                    )
                if path.exists():
                    backup = path.with_name(path.name + ".backup-" + uuid.uuid4().hex)
                    path.rename(backup)
                if temporary is not None:
                    temporary.rename(path)
                    temporary = None
                if backup is not None and not force:
                    shutil.rmtree(backup)
                    backup = None
            except OSError:
                if backup is not None and not path.exists():
                    backup.rename(path)
                raise Pan123Error("LOCAL_IO", "Skill 安装失败；请检查目录权限。") from None
            finally:
                if temporary is not None:
                    shutil.rmtree(temporary, ignore_errors=True)
            result = {
                "agent": agent,
                "path": str(path),
                "status": "installed" if action == "install" else "uninstalled",
            }
            if backup is not None:
                result["backup"] = str(backup)
            results.append(result)
    return {"results": results}
