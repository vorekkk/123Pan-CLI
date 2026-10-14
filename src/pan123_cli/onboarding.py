"""Interactive first-run setup; never prompts in machine-readable workflows."""

from __future__ import annotations

import getpass
import sys
import tempfile
from dataclasses import replace
from pathlib import Path
from typing import Any

from .auth import TokenManager
from .cache import read_private_json, write_private_json
from .config import credentials_path, load_settings
from .errors import Pan123Error
from .skills import AGENTS, detected_agents, manage


def interactive(options: dict[str, Any]) -> bool:
    return (
        not options.get("json")
        and not any(key.endswith("_stdin") and value for key, value in options.items())
        and options.get("request_file") != "-"
        and sys.stdin.isatty()
        and sys.stdout.isatty()
        and sys.stderr.isatty()
    )


def verify_credentials(settings) -> None:
    # A fresh isolated cache forces a real token request and leaves old auth state intact.
    with tempfile.TemporaryDirectory(prefix="pan123-setup-") as cache:
        manager = TokenManager(replace(settings, cache_dir=Path(cache)))
        try:
            manager.get_token()
        finally:
            manager.close()


def ask(prompt: str) -> str:
    print(prompt, end="", file=sys.stderr, flush=True)
    try:
        return input().strip()
    except EOFError:
        raise Pan123Error("INTERRUPTED", "配置已取消。") from None


def setup(options: dict[str, Any]) -> dict[str, Any]:
    settings = load_settings(options)
    while True:
        client_id = ask("PAN123_CLIENT_ID（空输入取消）: ")
        if not client_id:
            raise Pan123Error("INTERRUPTED", "配置已取消。")
        try:
            secret = getpass.getpass("PAN123_CLIENT_SECRET（隐藏输入）: ")
        except EOFError:
            raise Pan123Error("INTERRUPTED", "配置已取消。") from None
        if not secret.strip():
            raise Pan123Error("INTERRUPTED", "配置已取消。")
        candidate = replace(
            settings, auth_mode="developer", client_id=client_id, client_secret=secret
        )
        try:
            verify_credentials(candidate)
        except Pan123Error:
            print("鉴权验证失败，请检查凭据、网络和开发者权限。", file=sys.stderr)
            if ask("重试？[y/N]: ").lower() != "y":
                raise Pan123Error("TOKEN_UNAVAILABLE", "验证失败，旧配置未更改。") from None
            continue
        write_private_json(
            credentials_path(),
            {"schema_version": 1, "client_id": client_id, "client_secret": secret},
        )
        return {"configured": True, "credentials_path": str(credentials_path())}


def install_prompt() -> dict[str, Any]:
    detected = detected_agents()
    if len(detected) == 1:
        agents = detected
    else:
        defaults = ",".join(detected) if detected else "codex"
        selected = ask(f"Skill 目标 codex,claude,cursor（逗号多选；默认 {defaults}）: ") or defaults
        agents = list(dict.fromkeys([item.strip() for item in selected.split(",")]))
        if any(agent not in AGENTS for agent in agents):
            raise Pan123Error("INVALID_ARGUMENT", "未知 Skill 目标；可运行 pan123 skill install。")
    result = manage("install", {"agent": agents})
    write_private_json(
        credentials_path().with_name("onboarding.json"),
        {"schema_version": 1, "skill_agents": agents},
    )
    return result


def prepare(options: dict[str, Any]) -> dict[str, Any] | None:
    command = tuple(options["command"])
    if command[0] == "skill":
        return manage(command[1], options)
    if command == ("setup",):
        if not interactive(options):
            raise Pan123Error(
                "CONFIG_ERROR", "请在交互终端运行 pan123 setup；自动化任务请设置环境变量。"
            )
        result = setup(options)
        try:
            result["skill"] = install_prompt()
        except (Pan123Error, OSError):
            print("Skill 安装未完成，请运行 pan123 skill install。", file=sys.stderr)
        return result
    settings = load_settings(options)
    if interactive(options):
        if (
            settings.auth_mode == "developer"
            and command[0] != "oauth"
            and (not settings.client_id or not settings.client_secret)
            and command not in {("auth", "clear"), ("auth", "status")}
        ):
            setup(options)
        # Installer's manifest is the first-run marker; user conflicts remain untouched.
        from .skills import destination, status

        agents = detected_agents() or ["codex"]
        try:
            state_path = credentials_path().with_name("onboarding.json")
            if state_path.exists():
                state = read_private_json(state_path)
                if isinstance(state, dict) and isinstance(state.get("skill_agents"), list):
                    agents = [agent for agent in state["skill_agents"] if agent in AGENTS] or agents
            if any(status(destination(agent, "user")) == "missing" for agent in agents):
                install_prompt()
        except (Pan123Error, OSError):
            print("Skill 安装未完成，请运行 pan123 skill install。", file=sys.stderr)
    return None
