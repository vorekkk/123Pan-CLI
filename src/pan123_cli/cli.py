"""Command parser and dispatch for the official 123Pan API."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from . import __version__
from .client import ApiClient
from .config import load_settings
from .errors import Pan123Error
from .output import emit, progress_callback


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise Pan123Error("INVALID_ARGUMENT", message, exit_code=2)


def boolean(value: str) -> bool:
    if value.lower() in {"true", "1"}:
        return True
    if value.lower() in {"false", "0"}:
        return False
    raise argparse.ArgumentTypeError("expected true or false")


def _positive(value: str) -> float:
    try:
        result = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError("expected a positive number") from None
    if not math.isfinite(result) or result <= 0:
        raise argparse.ArgumentTypeError("expected a finite positive number")
    return result


def _global(parser):
    # Suppressed defaults preserve options given at a parent parser level.
    options: list[tuple[str, dict[str, Any]]] = [
        ("--json", {"action": "store_true"}),
        ("--verbose", {"action": "store_true"}),
        ("--no-progress", {"action": "store_true"}),
        ("--allow-fake-ip", {"action": "store_true"}),
        ("--yes", {"action": "store_true"}),
        ("--config", {}),
        ("--env-file", {}),
        ("--cache-dir", {}),
        ("--auth-mode", {"choices": ["developer", "oauth"]}),
        ("--timeout", {"type": _positive}),
        ("--transfer-timeout", {"type": _positive}),
    ]
    for flag, kwargs in options:
        parser.add_argument(flag, default=argparse.SUPPRESS, **kwargs)


def build_parser():
    from .catalog import ENDPOINTS

    root = Parser(prog="pan123", description="123 云盘官方 OpenAPI 命令行工具", allow_abbrev=False)
    _global(root)
    root.add_argument("--version", action="version", version=f"pan123 {__version__}")
    parsers: dict[tuple[str, ...], Parser] = {(): root}
    subparsers: dict[tuple[str, ...], Any] = {}

    def node(command):
        current: tuple[str, ...] = ()
        for word in command:
            if current not in subparsers:
                subparsers[current] = parsers[current].add_subparsers(required=True)
            child = (*current, word)
            if child not in parsers:
                parsers[child] = subparsers[current].add_parser(word, allow_abbrev=False)
                _global(parsers[child])
            current = child
        return parsers[current]

    def add_if(parser, flag, **kwargs):
        if flag not in parser._option_string_actions:
            parser.add_argument(flag, default=argparse.SUPPRESS, **kwargs)

    for endpoint in ENDPOINTS:
        if endpoint.command == ("file", "list-v1"):
            continue
        parser = node(endpoint.command)
        parser.set_defaults(endpoint=endpoint, command=endpoint.command)
        if endpoint.command[0] not in {"auth", "oauth"}:
            parser.add_argument(
                "--request-file",
                default=argparse.SUPPRESS,
                help="UTF-8 JSON 请求文件；- 表示 stdin",
            )
        for field in endpoint.fields:
            if field.flag is None:
                continue
            kwargs: dict[str, Any] = {"help": field.help or field.wire}
            if field.kind in {"int", "ints"}:
                kwargs["type"] = int
            elif field.kind == "float":
                kwargs["type"] = float
            elif field.kind == "bool":
                kwargs["type"] = boolean
            elif field.kind == "json":
                kwargs["type"] = json.loads
            if field.kind in {"ints", "strs"}:
                kwargs["action"] = "append"
            if field.choices is not None:
                kwargs["choices"] = field.choices
            add_if(parser, "--" + field.flag, **kwargs)
        if endpoint.wait:
            add_if(parser, "--wait", action="store_true")
            add_if(parser, "--wait-timeout", type=_positive)
        if endpoint.command[:2] in {("file", "upload-api"), ("image", "upload-api")}:
            for flag in [
                "--session-file",
                "--session-out",
                "--url-out",
                "--domains-out",
                "--domains-file",
                "--upload-url-file",
                "--slice",
                "--slice-file",
                "--file",
            ]:
                add_if(parser, flag)
            add_if(parser, "--upload-url-stdin", action="store_true")
        if endpoint.command[0] in {"auth", "oauth"}:
            for flag in ["--client-id", "--redirect-uri", "--state"]:
                add_if(parser, flag)
            for flag in ["--client-secret-stdin", "--code-stdin", "--refresh-token-stdin"]:
                add_if(parser, flag, action="store_true")
        for field in endpoint.fields:
            if field.wire == "password":
                add_if(parser, "--password-stdin", action="store_true")
            if field.wire == "sharePwd":
                parser.add_argument(
                    "--share-password-stdin",
                    "--share-pwd-stdin",
                    dest="share_password_stdin",
                    action="store_true",
                    default=argparse.SUPPRESS,
                )

    for command in [("auth", "status"), ("auth", "clear"), ("oauth", "authorize-url")]:
        parser = node(command)
        parser.set_defaults(command=command, handler=" ".join(command))
        if command[0] == "oauth":
            for flag in ["--client-id", "--redirect-uri", "--state"]:
                add_if(parser, flag)

    list_parser = parsers[("file", "list")]
    add_if(list_parser, "--api-version", choices=["v1", "v2"])
    for field in next(e for e in ENDPOINTS if e.command == ("file", "list-v1")).fields:
        if field.flag:
            kwargs = (
                {"type": int}
                if field.kind == "int"
                else {"type": boolean}
                if field.kind == "bool"
                else {}
            )
            add_if(list_parser, "--" + field.flag, **kwargs)
    for command in [
        ("file", "list"),
        ("image", "list"),
        ("transcode", "source-list"),
        ("transcode", "folder-list"),
    ]:
        for flag in ["--all", "--include-trashed"]:
            add_if(parsers[command], flag, action="store_true")
    for share_command in [("share", "list"), ("share", "payment", "list")]:
        add_if(parsers[share_command], "--all", action="store_true")

    for command in [("file", "upload"), ("image", "upload"), ("transcode", "upload")]:
        parser = node(command)
        parser.set_defaults(command=command, handler="upload")
        parser.add_argument("--file", required=True)
        parser.add_argument(
            "--parent-id", type=str if command[0] == "image" else int, default=argparse.SUPPRESS
        )
        parser.add_argument("--name")
        parser.add_argument(
            "--duplicate", choices=["error", "keep-both", "overwrite"], default="error"
        )
        parser.add_argument("--api-version", choices=["v1", "v2"], default="v2")
        parser.add_argument("--complete-timeout", type=_positive, default=300)
    parser = node(("file", "download"))
    parser.set_defaults(command=("file", "download"), handler="download")
    parser.add_argument("--file-id", type=int, required=True)
    parser.add_argument("--output")
    parser.add_argument("--overwrite", action="store_true")
    node(("setup",)).set_defaults(command=("setup",))
    for action in ("install", "status", "uninstall"):
        parser = node(("skill", action))
        parser.set_defaults(command=("skill", action))
        parser.add_argument("--agent", action="append", choices=["codex", "claude", "cursor"])
        parser.add_argument("--scope", choices=["user", "project"], default="user")
        parser.add_argument("--dest", help="完整 Skill 目标目录（包含 pan123-cli 文件夹）")
        parser.add_argument("--force", action="store_true", help="备份已存在内容后更新或卸载")
    return root


def _read_json(path: str) -> Any:
    try:
        return json.loads(
            sys.stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
        )
    except (OSError, ValueError, UnicodeError) as exc:
        raise Pan123Error("INVALID_ARGUMENT", "请求文件必须是有效 UTF-8 JSON", exit_code=2) from exc


def _use_utf8_streams() -> None:
    """Write UTF-8 even when the platform default is a legacy code page.

    Windows pipes default to the ANSI code page, where printing Chinese help or
    a JSON filename raises UnicodeEncodeError (a ValueError) and turns a
    successful command into exit code 2. Consoles and test capture streams keep
    working because reconfiguration is best effort.
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            continue


def _confirm(options, command, required=False):
    if not required or options.get("yes"):
        return
    if not sys.stdin.isatty():
        raise Pan123Error("INVALID_ARGUMENT", "此变更命令在脚本中需要 --yes", exit_code=2)
    print(f"执行 {' '.join(command)}？输入 yes 确认: ", file=sys.stderr, end="", flush=True)
    if sys.stdin.readline().strip() != "yes":
        raise Pan123Error("INVALID_ARGUMENT", "操作未确认", exit_code=2)


def _wait_endpoint(client, endpoint, payload, options):
    from .catalog import ENDPOINTS

    state = endpoint.wait or {}
    target_command = state.get("command")
    if target_command:
        # Creation APIs return a task ID, then the progress schema owns its states.
        result = _single_request(client, endpoint, payload)
        target = next(e for e in ENDPOINTS if e.command == tuple(target_command))
        if not isinstance(result, dict):
            raise Pan123Error("PROTOCOL_ERROR", "任务创建没有返回有效任务 ID")
        task_id = result.get("taskId", result.get("taskID"))
        task_field = next((f for f in target.fields if f.wire.lower() == "taskid"), None)
        if task_id is None or task_field is None:
            raise Pan123Error("PROTOCOL_ERROR", "任务创建没有返回有效任务 ID")
        return _wait_endpoint(client, target, {task_field.wire: task_id}, options)
    deadline = time.monotonic() + options.get("wait_timeout", 300)
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise Pan123Error("WAIT_TIMEOUT", "等待异步任务完成超时", details=payload)
        result = _single_request(
            client, endpoint, payload, timeout=min(client.settings.api_timeout, remaining)
        )
        if not isinstance(result, dict):
            raise Pan123Error("PROTOCOL_ERROR", "异步任务查询未返回对象")
        if endpoint.special == "transcode-zip":
            if result.get("isFull") is True:
                raise Pan123Error("UPSTREAM_ERROR", "转码打包容量已满", details=result)
            if type(result.get("isFull")) is not bool:
                raise Pan123Error("PROTOCOL_ERROR", "转码打包响应缺少有效容量状态")
        current = result.get(state.get("field", "status"))
        defined = (*state.get("pending", ()), *state.get("success", ()), *state.get("failure", ()))
        if defined and not any(type(current) is type(value) for value in defined):
            raise Pan123Error("PROTOCOL_ERROR", "异步任务状态类型无效", details=result)
        if current in state.get("failure", []):
            raise Pan123Error("UPSTREAM_ERROR", "异步任务失败", details=result)
        if current in state.get("success", []):
            if endpoint.special == "transcode-zip" and not result.get("downloadUrl"):
                raise Pan123Error("PROTOCOL_ERROR", "转码打包未返回可用下载地址")
            for key in ("failCount", "failedCount", "failNum"):
                if result.get(key, 0):
                    raise Pan123Error(
                        "UPSTREAM_ERROR", "异步任务结束，但包含失败条目", details=result
                    )
            return result
        if current not in state.get("pending", []):
            raise Pan123Error("PROTOCOL_ERROR", "异步任务返回未定义状态", details=result)
        time.sleep(min(state.get("interval", 2), max(0, deadline - time.monotonic())))


def _single_request(client, endpoint, payload, timeout=None):
    return client.request(
        endpoint.method,
        endpoint.path,
        **({"params": payload} if endpoint.location == "query" else {"json": payload}),
        retryable=endpoint.read_only,
        timeout=timeout,
    )


def execute(options: Mapping[str, Any]) -> Any:
    from .auth import TokenManager
    from .catalog import ENDPOINTS, payload_for

    values = dict(options)
    command = tuple(values["command"])
    endpoint = values.get("endpoint")
    selectors = [key for key, value in values.items() if key.endswith("_stdin") and value]
    if values.get("request_file") == "-":
        selectors.append("request_file")
    if len(selectors) > 1:
        raise Pan123Error("INVALID_ARGUMENT", "一个命令只能有一个 stdin 输入消费者", exit_code=2)
    if command[0] == "oauth":
        values["auth_mode"] = "oauth"
    if command == ("file", "list") and values.get("api_version") == "v1":
        endpoint = next(e for e in ENDPOINTS if e.command == ("file", "list-v1"))
    elif command == ("file", "list") and any(
        key in values for key in ("page", "order_by", "order_direction", "trashed")
    ):
        raise Pan123Error(
            "INVALID_ARGUMENT", "page/order/trashed 参数仅适用于 --api-version v1", exit_code=2
        )
    if values.get("client_secret_stdin"):
        secret = sys.stdin.read().strip()
        values["oauth_client_secret" if command[0] == "oauth" else "client_secret"] = secret
    if command[0] == "oauth" and values.get("client_id"):
        values["oauth_client_id"] = values["client_id"]
    settings = load_settings(values)
    if (
        endpoint is not None
        and endpoint.auth_mode
        and command[0] != "auth"
        and settings.auth_mode != endpoint.auth_mode
    ):
        raise Pan123Error(
            "AUTH_REQUIRED", f"此接口要求 --auth-mode {endpoint.auth_mode}", exit_code=3
        )
    if command[0] in {"auth", "oauth"}:
        auth = TokenManager(settings)
        try:
            if command == ("auth", "status"):
                return auth.status()
            if command == ("auth", "clear"):
                return auth.clear()
            if command == ("auth", "ensure"):
                auth.get_token()
                return auth.status()
            if command == ("oauth", "authorize-url"):
                return auth.authorize_url(
                    values.get("client_id"), values.get("redirect_uri"), values.get("state")
                )
            if command == ("oauth", "exchange"):
                code = (
                    sys.stdin.read().strip()
                    if values.get("code_stdin")
                    else os.getenv("PAN123_OAUTH_CODE", "")
                )
                return auth.exchange(
                    code,
                    values.get("state", ""),
                    values.get("client_id"),
                    values.get("redirect_uri"),
                )
            if command == ("oauth", "refresh"):
                refresh = sys.stdin.read().strip() if values.get("refresh_token_stdin") else None
                return auth.refresh(refresh)
        finally:
            auth.close()

    request_data = _read_json(values["request_file"]) if values.get("request_file") else None
    payload = None
    if endpoint is not None:
        for field in endpoint.fields:
            if field.wire == "password" and request_data is None:
                values["password"] = (
                    sys.stdin.read().strip()
                    if values.get("password_stdin")
                    else os.getenv("PAN123_SAFEBOX_PASSWORD")
                )
            elif field.wire == "sharePwd" and request_data is None:
                value = (
                    sys.stdin.read().strip()
                    if values.get("share_password_stdin")
                    else os.getenv("PAN123_SHARE_PASSWORD", os.getenv("PAN123_SHARE_PWD"))
                )
                if value is not None:
                    values["sharePwd"] = value
        # Protected session capability parameters are loaded by transfer service.
        if command[:2] not in {("file", "upload-api"), ("image", "upload-api")}:
            payload = payload_for(endpoint, values, request_data)
        else:
            payload = request_data if request_data is not None else values
    _confirm(
        values,
        command,
        bool(endpoint and endpoint.confirmation)
        or values.get("overwrite", False)
        or values.get("duplicate") in {"overwrite", 2}
        or (isinstance(request_data, dict) and request_data.get("duplicate") == 2),
    )

    with (
        ApiClient(settings) as client,
        progress_callback(not values.get("json") and not values.get("no_progress")) as progress,
    ):
        if values.get("handler") == "upload":
            from .services.uploading import upload_file

            business = (
                "image"
                if command[0] == "image"
                else "transcode"
                if command[0] == "transcode"
                else "file"
            )
            parent = values.get("parent_id", "" if business == "image" else 0)
            if business == "transcode" and "parent_id" not in values:
                folder = client.request(
                    "POST", "/api/v1/transcode/folder/info", json={}, retryable=True
                )
                if not isinstance(folder, dict) or type(folder.get("fileID")) is not int:
                    raise Pan123Error("PROTOCOL_ERROR", "转码空间未返回有效目录 ID")
                parent = folder["fileID"]
            return upload_file(
                client,
                Path(values["file"]),
                parent_id=parent,
                name=values.get("name"),
                duplicate=values["duplicate"],
                api_version=values["api_version"],
                business=business,
                complete_timeout=values["complete_timeout"],
                progress=progress,
            )
        if values.get("handler") == "download":
            from .services.downloading import download_file

            return download_file(
                client,
                values["file_id"],
                Path(values["output"]) if values.get("output") else None,
                overwrite=values["overwrite"],
                progress=progress,
            )
        if command[:2] in {("file", "upload-api"), ("image", "upload-api")}:
            from .services.uploading import dispatch_upload

            return dispatch_upload(client, command, payload or {}, values)
        if command in {
            ("file", "list"),
            ("image", "list"),
            ("transcode", "source-list"),
            ("transcode", "folder-list"),
        }:
            from .services.listing import list_files

            assert isinstance(payload, dict)
            business = {
                "image": "image",
                "transcode": "transcode-source" if command[1] == "source-list" else "transcode",
            }.get(command[0], "file")
            return list_files(
                client,
                parent_id=payload.get("parentFileId", 0),
                limit=payload.get("limit", 100),
                cursor=payload.get("lastFileId"),
                search=payload.get("searchData"),
                all_pages=values.get("all", False),
                include_trashed=values.get("include_trashed", False),
                api_version=values.get("api_version", "v2"),
                business=business,
                **{
                    option: payload[wire]
                    for wire, option in {
                        "page": "page",
                        "orderBy": "order_by",
                        "orderDirection": "order_direction",
                        "trashed": "trashed",
                        "searchMode": "search_mode",
                        "startTime": "start_time",
                        "endTime": "end_time",
                    }.items()
                    if wire in payload
                },
            )
        if endpoint is None:
            raise Pan123Error("INVALID_ARGUMENT", "请选择一个有效命令", exit_code=2)
        if endpoint.special == "share-list":
            from .services.sharing import list_shares

            assert isinstance(payload, dict)
            return list_shares(
                client, payload, paid="payment" in command, all_pages=values.get("all", False)
            )
        if values.get("wait"):
            return _wait_endpoint(client, endpoint, payload, values)
        return _single_request(client, endpoint, payload)


def main(argv: Sequence[str] | None = None) -> int:
    _use_utf8_streams()
    args = list(sys.argv[1:] if argv is None else argv)
    json_mode = "--json" in args
    command: tuple[str, ...] = ()
    global_value_flags = {
        "--config",
        "--env-file",
        "--cache-dir",
        "--auth-mode",
        "--timeout",
        "--transfer-timeout",
    }
    index = 0
    while index < len(args):
        arg = args[index]
        if arg in global_value_flags:
            index += 2
        elif arg.startswith("-"):
            index += 1
        else:
            if arg in {"list", "upload", "download"}:
                args.insert(index, "file")
            break
    try:
        from .onboarding import interactive, prepare

        if not args and interactive({}):
            settings = load_settings({})
            args = (
                ["setup"]
                if settings.auth_mode == "developer"
                and (not settings.client_id or not settings.client_secret)
                else ["--help"]
            )
        parser = build_parser()
        options = vars(parser.parse_args(args))
        command = tuple(options["command"])
        local_result = prepare(options)
        data = local_result if local_result is not None else execute(options)
        emit(
            {"ok": True, "schema_version": 1, "command": " ".join(command), "data": data},
            json_mode=json_mode,
        )
        return 0
    except SystemExit as exc:
        return int(exc.code or 0)
    except Pan123Error as exc:
        emit(
            {
                "ok": False,
                "schema_version": 1,
                "command": " ".join(command),
                "error": exc.as_dict(),
            },
            json_mode=json_mode,
        )
        return exc.exit_code
    except KeyboardInterrupt:
        error = Pan123Error("INTERRUPTED", "操作已中断", exit_code=130)
        emit(
            {
                "ok": False,
                "schema_version": 1,
                "command": " ".join(command),
                "error": error.as_dict(),
            },
            json_mode=json_mode,
        )
        return 130
    except (OSError, ValueError) as exc:
        error = Pan123Error(
            "LOCAL_IO" if isinstance(exc, OSError) else "INVALID_ARGUMENT",
            "本地文件操作失败" if isinstance(exc, OSError) else "输入数据无效",
            exit_code=5 if isinstance(exc, OSError) else 2,
        )
        emit(
            {
                "ok": False,
                "schema_version": 1,
                "command": " ".join(command),
                "error": error.as_dict(),
            },
            json_mode=json_mode,
        )
        return error.exit_code
