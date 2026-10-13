"""Explicit configuration loading without credential or filesystem side effects."""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from dotenv import dotenv_values
from platformdirs import user_cache_dir, user_config_dir

from .errors import Pan123Error

APP_NAME = "123pan-cli"
_ENV_KEYS = {
    "client_id": "PAN123_CLIENT_ID",
    "client_secret": "PAN123_CLIENT_SECRET",
    "auth_mode": "PAN123_AUTH_MODE",
    "oauth_client_id": "PAN123_OAUTH_CLIENT_ID",
    "oauth_client_secret": "PAN123_OAUTH_CLIENT_SECRET",
    "oauth_redirect_uri": "PAN123_OAUTH_REDIRECT_URI",
    "cache_dir": "PAN123_CACHE_DIR",
    "api_timeout": "PAN123_API_TIMEOUT",
    "transfer_timeout": "PAN123_TRANSFER_TIMEOUT",
    "token_refresh_skew_seconds": "PAN123_TOKEN_REFRESH_SKEW_SECONDS",
    "read_max_retries": "PAN123_READ_MAX_RETRIES",
    "allow_fake_ip": "PAN123_ALLOW_FAKE_IP",
}
_ENV_ALIASES = {"client_id": "CLIENT_ID", "client_secret": "CLIENT_SECRET"}


@dataclass(frozen=True)
class Settings:
    client_id: str | None = None
    client_secret: str | None = field(default=None, repr=False)
    auth_mode: str = "developer"
    oauth_client_id: str | None = None
    oauth_client_secret: str | None = field(default=None, repr=False)
    oauth_redirect_uri: str | None = None
    cache_dir: Path = field(default_factory=lambda: Path(user_cache_dir(APP_NAME, appauthor=False)))
    api_timeout: float = 30
    transfer_timeout: float = 120
    token_refresh_skew_seconds: int = 300
    read_max_retries: int = 3
    allow_fake_ip: bool = False

    @property
    def fingerprint(self) -> str:
        if self.auth_mode == "oauth":
            components = ("oauth", self.oauth_client_id or "", self.oauth_client_secret or "")
        else:
            components = ("developer", self.client_id or "", self.client_secret or "")
        return hashlib.sha256("\0".join(components).encode("utf-8")).hexdigest()


def _fail(message: str) -> Pan123Error:
    return Pan123Error("config", message)


def _load_json(path: Path, *, required: bool) -> dict[str, Any]:
    if not path.exists():
        if required:
            raise _fail("The selected configuration file does not exist.")
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError):
        raise _fail("The configuration file must be readable UTF-8 JSON.") from None
    allowed = set(_ENV_KEYS) - {"client_secret", "oauth_client_secret"}
    if not isinstance(data, dict) or set(data) - allowed - {"schema_version"}:
        raise _fail("The configuration contains unsupported fields.")
    version = data.pop("schema_version", 1)
    if type(version) is not int or version != 1:
        raise _fail("The configuration schema version is unsupported.")
    return data


def _positive_number(value: Any, name: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError, OverflowError):
        raise _fail(f"{name} must be a finite positive number.") from None
    if isinstance(value, bool) or not math.isfinite(number) or number <= 0:
        raise _fail(f"{name} must be a finite positive number.")
    return number


def _nonnegative_integer(value: Any, name: str) -> int:
    if isinstance(value, str) and re.fullmatch(r"\d+", value):
        value = int(value)
    if type(value) is not int or value < 0:
        raise _fail(f"{name} must be a nonnegative integer.")
    return value


def _environment_value(key: str, value: Any) -> Any:
    if key != "allow_fake_ip":
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in ("true", "1"):
            return True
        if normalized in ("false", "0"):
            return False
    raise _fail("PAN123_ALLOW_FAKE_IP must be true, false, 1 or 0.")


def load_settings(
    overrides: Mapping[str, Any], environ: Mapping[str, str] | None = None
) -> Settings:
    """Merge settings; developer credentials also accept CLIENT_ID/CLIENT_SECRET.

    PAN123_ names win over aliases within each environment source. Process
    environment still wins over the explicit env-file, regardless of naming.
    """
    env = os.environ if environ is None else environ
    normalized = dict(overrides)
    if normalized.get("timeout") is not None:
        normalized["api_timeout"] = normalized["timeout"]
    selected_config = (
        normalized.get("config") or normalized.get("config_file") or env.get("PAN123_CONFIG_FILE")
    )
    config_path = (
        Path(selected_config).expanduser()
        if selected_config
        else Path(user_config_dir(APP_NAME, appauthor=False)) / "config.json"
    )
    values = _load_json(config_path, required=selected_config is not None)
    selected_env = normalized.get("env_file")
    if selected_env is not None:
        env_path = Path(selected_env).expanduser()
        if not env_path.is_file():
            raise _fail("The selected environment file does not exist.")
        try:
            file_values = dotenv_values(env_path, interpolate=False)
        except (OSError, ValueError, UnicodeError):
            raise _fail("The environment file could not be read.") from None
        for key, env_key in _ENV_KEYS.items():
            if env_key in file_values:
                values[key] = _environment_value(key, file_values[env_key])
            elif key in _ENV_ALIASES and _ENV_ALIASES[key] in file_values:
                values[key] = file_values[_ENV_ALIASES[key]]
    for key, env_key in _ENV_KEYS.items():
        if env_key in env:
            values[key] = _environment_value(key, env[env_key])
        elif key in _ENV_ALIASES and _ENV_ALIASES[key] in env:
            values[key] = env[_ENV_ALIASES[key]]
        if normalized.get(key) is not None:
            values[key] = normalized[key]
    for key in (
        "client_id",
        "client_secret",
        "oauth_client_id",
        "oauth_client_secret",
        "oauth_redirect_uri",
    ):
        if key in values:
            value = values[key]
            if not isinstance(value, str) or not value.strip() or "\0" in value:
                raise _fail("Configured credentials and callback values must be nonempty strings.")
    if values.get("auth_mode", "developer") not in ("developer", "oauth"):
        raise _fail("auth_mode must be developer or oauth.")
    if "allow_fake_ip" in values and type(values["allow_fake_ip"]) is not bool:
        raise _fail("allow_fake_ip must be a boolean.")
    for key in ("api_timeout", "transfer_timeout"):
        if key in values:
            values[key] = _positive_number(values[key], key)
    for key in ("token_refresh_skew_seconds", "read_max_retries"):
        if key in values:
            values[key] = _nonnegative_integer(values[key], key)
    if "cache_dir" in values:
        try:
            cache_value = values["cache_dir"]
            if not isinstance(cache_value, (str, Path)) or not str(cache_value).strip():
                raise ValueError
            cache_path = Path(cache_value).expanduser().absolute()
            if cache_path.is_symlink() or (cache_path.exists() and not cache_path.is_dir()):
                raise ValueError
            if (
                os.name == "posix"
                and cache_path.exists()
                and cache_path.stat().st_uid != os.getuid()
            ):
                raise ValueError
            parent = cache_path
            while not parent.exists() and parent != parent.parent:
                parent = parent.parent
            if not os.access(parent, os.W_OK):
                raise ValueError
            values["cache_dir"] = cache_path
        except (OSError, ValueError):
            raise _fail(
                "cache_dir must be a writable directory belonging to the current user."
            ) from None
    return Settings(**values)
