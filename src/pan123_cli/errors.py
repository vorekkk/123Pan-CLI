"""Stable, safely printable application errors."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any
from urllib.parse import urlsplit, urlunsplit

_EXIT_CODES = {
    "argument": 2,
    "validation": 2,
    "config": 2,
    "configuration": 2,
    "confirmation": 2,
    "auth": 3,
    "authentication": 3,
    "network": 4,
    "http": 4,
    "api": 4,
    "business": 4,
    "io": 5,
    "file": 5,
    "conflict": 5,
    "timeout": 6,
    "protocol": 7,
    "integrity": 7,
    "INVALID_ARGUMENT": 2,
    "CONFIG_ERROR": 2,
    "AUTH_REQUIRED": 3,
    "TOKEN_UNAVAILABLE": 3,
    "NETWORK_ERROR": 4,
    "UPSTREAM_ERROR": 4,
    "LOCAL_IO": 5,
    "FILE_CONFLICT": 5,
    "WAIT_TIMEOUT": 6,
    "PROTOCOL_ERROR": 7,
    "VERIFY_FAILED": 7,
    "SOURCE_CHANGED": 7,
    "INTERRUPTED": 130,
    "interrupted": 130,
}
_SENSITIVE_KEYS = re.compile(
    r"secret|authorization|cookie|token|password|passwd|code$|sharepwd|"
    r"preupload|presigned|downloadurl|signature",
    re.IGNORECASE,
)
_URL = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)
_ASSIGNMENT = re.compile(
    r"((?:client[_-]?secret|access[_-]?token|refresh[_-]?token|password|"
    r"sharepwd|preuploadid|authorization|code)\s*[=:]\s*)[^\s&,;]+",
    re.IGNORECASE,
)


def redact_sensitive(value: Any) -> Any:
    """Remove credential fields and URL capability queries from diagnostics."""
    if isinstance(value, Mapping):
        return {
            str(key): "[redacted]" if _SENSITIVE_KEYS.search(str(key)) else redact_sensitive(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [redact_sensitive(item) for item in value]
    if not isinstance(value, str):
        return value

    def clean_url(match: re.Match[str]) -> str:
        try:
            parts = urlsplit(match.group())
            host = parts.hostname or "[redacted]"
            if ":" in host:
                host = f"[{host}]"
            port = parts.port
            if port is not None:
                host = f"{host}:{port}"
            return urlunsplit((parts.scheme, host, parts.path, "", ""))
        except ValueError:
            return "[redacted URL]"

    result = _URL.sub(clean_url, value)
    result = re.sub(r"\bBearer\s+[^\s,;]+", "Bearer [redacted]", result, flags=re.IGNORECASE)
    return _ASSIGNMENT.sub(r"\1[redacted]", result)


class Pan123Error(Exception):
    """An error with an exit status and optional upstream diagnostic fields."""

    def __init__(
        self,
        kind: str,
        message: str,
        *,
        exit_code: int | None = None,
        http_status: int | None = None,
        api_code: int | str | None = None,
        trace_id: str | None = None,
        retryable: bool = False,
        details: Any = None,
    ) -> None:
        self.kind = kind
        self.message = str(redact_sensitive(message))
        self.exit_code = exit_code if exit_code is not None else _EXIT_CODES.get(kind, 1)
        self.http_status = http_status
        self.api_code = api_code
        self.trace_id = redact_sensitive(trace_id)
        self.retryable = retryable
        self.details = redact_sensitive(details)
        super().__init__(self.message)

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "kind": self.kind,
            "message": self.message,
            "exit_code": self.exit_code,
            "retryable": self.retryable,
        }
        for field in ("http_status", "api_code", "trace_id", "details"):
            value = getattr(self, field)
            if value is not None:
                result[field] = value
        return result
