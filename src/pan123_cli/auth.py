"""Official developer and OAuth authentication with protected local state."""

from __future__ import annotations

import hashlib
import hmac
import logging
import secrets
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlencode, urlsplit

import httpx
from filelock import FileLock, Timeout

from .cache import _private_directory, owner_uid, read_private_json, write_private_json
from .config import Settings
from .errors import Pan123Error, redact_sensitive

OFFICIAL_BASE = "https://open-api.123pan.com"
OAUTH_SCOPE = "user:base,file:all:read,file:all:write"
STATE_TTL_SECONDS = 600


class _SafeHTTPLog(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact_sensitive(record.getMessage())
        record.args = ()
        return True


_HTTP_LOG_FILTER = _SafeHTTPLog()


def _utc_date(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(UTC)


def _required(value: Any, description: str) -> str:
    if not isinstance(value, str) or not value.strip() or any(ord(char) < 32 for char in value):
        raise Pan123Error(
            "AUTH_REQUIRED",
            f"{description} is required. 请运行 pan123 setup 或设置 PAN123 环境变量。",
        )
    return value


class TokenManager:
    """Manage local tokens; construction, status and clear never require a network."""

    def __init__(self, settings: Settings, client: httpx.Client | None = None) -> None:
        self.settings = settings
        self._client = client
        self._owns_client = client is None

    @staticmethod
    def _path(settings: Settings) -> Path:
        return settings.cache_dir / f"token-{settings.fingerprint}.json"

    @contextmanager
    def _lock(self, path: Path) -> Iterator[None]:
        try:
            _private_directory(path.parent)
            uid = owner_uid()
            if uid is not None:
                if path.parent.stat().st_uid != uid:
                    raise Pan123Error(
                        "LOCAL_IO", "The cache directory is not owned by the current user."
                    )
                path.parent.chmod(0o700)
            lock_path = path.with_suffix(".lock")
            if lock_path.is_symlink():
                raise Pan123Error("LOCAL_IO", "The authentication lock cannot use a symbolic link.")
            with FileLock(lock_path, timeout=30, mode=0o600):
                yield
        except Timeout:
            raise Pan123Error(
                "TOKEN_UNAVAILABLE", "Timed out waiting for the local authentication lock."
            ) from None
        except OSError:
            raise Pan123Error(
                "LOCAL_IO", "Could not access the local authentication cache."
            ) from None

    @staticmethod
    def _raw_record(path: Path) -> dict[str, Any] | None:
        if not path.exists():
            return None
        if path.is_symlink():
            raise Pan123Error("LOCAL_IO", "The token cache cannot use a symbolic link.")
        try:
            record = read_private_json(path)
        except Pan123Error:
            return None
        return record if isinstance(record, dict) else None

    def _record(self, settings: Settings) -> dict[str, Any] | None:
        record = self._raw_record(self._path(settings))
        if (
            record is None
            or type(record.get("schema_version")) is not int
            or record.get("schema_version") != 1
            or record.get("auth_mode") != settings.auth_mode
            or record.get("credential_fingerprint") != settings.fingerprint
            or not isinstance(record.get("access_token"), str)
            or not record["access_token"].strip()
            or _utc_date(record.get("expires_at")) is None
            or record.get("refresh_status") in ("in_flight", "unknown")
        ):
            return None
        return record

    @staticmethod
    def _usable(record: Mapping[str, Any] | None, settings: Settings) -> bool:
        if record is None or record.get("access_invalid", False):
            return False
        expiry = _utc_date(record.get("expires_at"))
        return expiry is not None and expiry > datetime.now(UTC) + timedelta(
            seconds=settings.token_refresh_skew_seconds
        )

    def _status(self, settings: Settings) -> dict[str, Any]:
        record = self._record(settings)
        expiry = _utc_date(record.get("expires_at")) if record else None
        return {
            "auth_mode": settings.auth_mode,
            "cached": record is not None,
            "usable": self._usable(record, settings),
            "expires_at": expiry.isoformat() if expiry else None,
        }

    def status(self) -> dict[str, Any]:
        return self._status(self.settings)

    def clear(self) -> dict[str, Any]:
        path = self._path(self.settings)
        existed = path.exists()
        if existed:
            with self._lock(path):
                if path.is_symlink():
                    raise Pan123Error("LOCAL_IO", "The token cache cannot use a symbolic link.")
                path.unlink(missing_ok=True)
        return {"auth_mode": self.settings.auth_mode, "cleared": existed, "local_only": True}

    def invalidate(self, token: str | None = None) -> None:
        path = self._path(self.settings)
        if not path.exists():
            return
        with self._lock(path):
            record = self._raw_record(path)
            if token is None or (record is not None and record.get("access_token") == token):
                if self.settings.auth_mode == "oauth" and record is not None:
                    record["access_invalid"] = True
                    write_private_json(path, record)
                else:
                    path.unlink(missing_ok=True)

    def get_token(self) -> str:
        settings = self.settings
        if settings.auth_mode == "developer":
            _required(settings.client_id, "Developer client ID")
            _required(settings.client_secret, "Developer client secret")
        elif settings.auth_mode == "oauth":
            _required(settings.oauth_client_id, "OAuth application ID")
            _required(settings.oauth_client_secret, "OAuth application secret")
        else:
            raise Pan123Error("CONFIG_ERROR", "Unknown authentication mode.")
        record = self._record(settings)
        if self._usable(record, settings):
            assert record is not None
            return str(record["access_token"])
        if settings.auth_mode == "oauth":
            raise Pan123Error(
                "TOKEN_UNAVAILABLE", "No usable OAuth token. Run oauth exchange or oauth refresh."
            )
        with self._lock(self._path(settings)):
            record = self._record(settings)
            if self._usable(record, settings):
                assert record is not None
                return str(record["access_token"])
            payload = self._request(
                "/api/v1/access_token",
                json={"clientID": settings.client_id, "clientSecret": settings.client_secret},
                sensitive=(settings.client_secret or "",),
            )
            code = payload.get("code")
            if type(code) is not int:
                raise Pan123Error(
                    "PROTOCOL_ERROR", "The token response has no valid business status."
                )
            if code != 0:
                trace = payload.get("x-traceID")
                if isinstance(trace, str) and settings.client_secret:
                    trace = trace.replace(settings.client_secret, "[redacted]")
                raise Pan123Error(
                    "TOKEN_UNAVAILABLE",
                    "The official token endpoint rejected the credentials.",
                    http_status=200,
                    api_code=code,
                    trace_id=trace if isinstance(trace, str) else None,
                )
            data = payload.get("data")
            if not isinstance(data, dict):
                raise Pan123Error("PROTOCOL_ERROR", "The token response has no data object.")
            access_token = data.get("accessToken")
            expiry = _utc_date(data.get("expiredAt"))
            if not isinstance(access_token, str) or not access_token.strip() or expiry is None:
                raise Pan123Error(
                    "PROTOCOL_ERROR", "The token response has invalid token or expiration fields."
                )
            if expiry <= datetime.now(UTC) + timedelta(seconds=settings.token_refresh_skew_seconds):
                raise Pan123Error(
                    "TOKEN_UNAVAILABLE",
                    "The returned token expires before the configured refresh margin.",
                )
            record = self._base_record(settings, access_token, expiry)
            write_private_json(self._path(settings), record)
            return access_token

    def _request(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any = None,
        sensitive: tuple[str, ...] = (),
    ) -> dict[str, Any]:
        if self._client is None:
            self._client = httpx.Client(trust_env=False, follow_redirects=False)
        logging.getLogger("httpx").addFilter(_HTTP_LOG_FILTER)
        timeout = httpx.Timeout(self.settings.api_timeout, connect=10, pool=10)
        request = httpx.Request(
            "POST",
            OFFICIAL_BASE + path,
            params=params,
            json=json,
            headers={"Platform": "open_platform"},
            extensions={"timeout": timeout.as_dict()},
        )
        try:
            response = self._client.send(request, auth=None, follow_redirects=False)
        except httpx.HTTPError:
            raise Pan123Error(
                "TOKEN_UNAVAILABLE",
                "The authentication request failed; its result may be unknown. Do not replay a consumed OAuth credential.",
            ) from None
        if not 200 <= response.status_code < 300:
            code: int | str | None = None
            trace: str | None = None
            try:
                failed = response.json()
                if isinstance(failed, dict):
                    code = failed.get("code") if type(failed.get("code")) is int else None
                    trace = (
                        failed.get("x-traceID")
                        if isinstance(failed.get("x-traceID"), str)
                        else None
                    )
            except ValueError:
                pass
            if trace is not None:
                for secret in sensitive:
                    if secret:
                        trace = trace.replace(secret, "[redacted]")
            raise Pan123Error(
                "TOKEN_UNAVAILABLE",
                "The official authentication endpoint returned an HTTP error.",
                http_status=response.status_code,
                api_code=code,
                trace_id=trace,
            )
        try:
            payload = response.json()
        except (ValueError, UnicodeError):
            raise Pan123Error(
                "PROTOCOL_ERROR", "The official authentication endpoint returned invalid JSON."
            ) from None
        if not isinstance(payload, dict):
            raise Pan123Error(
                "PROTOCOL_ERROR", "The official authentication endpoint returned an invalid object."
            )
        return payload

    @staticmethod
    def _base_record(settings: Settings, access: str, expiry: datetime) -> dict[str, Any]:
        return {
            "schema_version": 1,
            "auth_mode": settings.auth_mode,
            "credential_fingerprint": settings.fingerprint,
            "access_token": access,
            "expires_at": expiry.isoformat(),
            "created_at": datetime.now(UTC).isoformat(),
        }

    def _oauth_settings(
        self,
        client_id: str | None = None,
        redirect_uri: str | None = None,
        client_secret: str | None = None,
    ) -> Settings:
        return replace(
            self.settings,
            auth_mode="oauth",
            oauth_client_id=client_id if client_id is not None else self.settings.oauth_client_id,
            oauth_redirect_uri=redirect_uri
            if redirect_uri is not None
            else self.settings.oauth_redirect_uri,
            oauth_client_secret=client_secret
            if client_secret is not None
            else self.settings.oauth_client_secret,
        )

    def _state_path(self, state: str) -> Path:
        digest = hashlib.sha256(state.encode("utf-8")).hexdigest()
        return self.settings.cache_dir / f"oauth-state-{digest}.json"

    def authorize_url(
        self,
        client_id: str | None = None,
        redirect_uri: str | None = None,
        state: str | None = None,
    ) -> dict[str, Any]:
        settings = self._oauth_settings(client_id, redirect_uri)
        application = _required(settings.oauth_client_id, "OAuth application ID")
        redirect = _required(settings.oauth_redirect_uri, "OAuth redirect URI")
        if not urlsplit(redirect).scheme:
            raise Pan123Error(
                "INVALID_ARGUMENT", "OAuth redirect URI must include its registered scheme."
            )
        selected_state = (
            secrets.token_urlsafe(32) if state is None else _required(state, "OAuth state")
        )
        path = self._state_path(selected_state)
        with self._lock(path):
            if path.exists():
                raise Pan123Error(
                    "INVALID_ARGUMENT", "This OAuth state already has a pending authorization."
                )
            now = datetime.now(UTC)
            expiry = now + timedelta(seconds=STATE_TTL_SECONDS)
            write_private_json(
                path,
                {
                    "schema_version": 1,
                    "auth_mode": "oauth",
                    "state": selected_state,
                    "client_id": application,
                    "redirect_uri": redirect,
                    "created_at": now.isoformat(),
                    "expires_at": expiry.isoformat(),
                },
            )
        query = urlencode(
            {
                "client_id": application,
                "redirect_uri": redirect,
                "scope": OAUTH_SCOPE,
                "state": selected_state,
            }
        )
        return {
            "auth_mode": "oauth",
            "url": f"https://yun.123pan.com/auth?{query}",
            "state": selected_state,
            "expires_at": expiry.isoformat(),
        }

    def exchange(
        self,
        code: str,
        state: str,
        client_id: str | None = None,
        redirect_uri: str | None = None,
        client_secret: str | None = None,
    ) -> dict[str, Any]:
        settings = self._oauth_settings(client_id, redirect_uri, client_secret)
        application = _required(settings.oauth_client_id, "OAuth application ID")
        secret = _required(settings.oauth_client_secret, "OAuth application secret")
        redirect = _required(settings.oauth_redirect_uri, "OAuth redirect URI")
        code = _required(code, "OAuth authorization code")
        state = _required(state, "OAuth state")
        path = self._state_path(state)
        if not path.exists():
            raise Pan123Error(
                "AUTH_REQUIRED", "OAuth state is missing, expired or already consumed."
            )
        with self._lock(self._path(settings)):
            with self._lock(path):
                record = self._raw_record(path)
                now = datetime.now(UTC)
                created = _utc_date(record.get("created_at")) if record else None
                expiry = _utc_date(record.get("expires_at")) if record else None
                if (
                    record is None
                    or type(record.get("schema_version")) is not int
                    or record.get("schema_version") != 1
                    or record.get("auth_mode") != "oauth"
                    or not isinstance(record.get("state"), str)
                    or not hmac.compare_digest(
                        record["state"].encode("utf-8"), state.encode("utf-8")
                    )
                    or record.get("client_id") != application
                    or record.get("redirect_uri") != redirect
                    or created is None
                    or expiry is None
                    or created > now
                    or expiry <= now
                    or now - created > timedelta(seconds=STATE_TTL_SECONDS)
                ):
                    raise Pan123Error(
                        "AUTH_REQUIRED",
                        "OAuth state does not match the application, callback or local validity period.",
                    )
                path.unlink()
            payload = self._request(
                "/api/v1/oauth2/access_token",
                params={
                    "client_id": application,
                    "client_secret": secret,
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": redirect,
                },
                sensitive=(secret, code),
            )
            record = self._oauth_record(payload, settings)
            write_private_json(self._path(settings), record)
        return self._status(settings)

    def _oauth_record(self, payload: Mapping[str, Any], settings: Settings) -> dict[str, Any]:
        if "code" in payload:
            raise Pan123Error(
                "TOKEN_UNAVAILABLE",
                "The OAuth endpoint rejected the authorization.",
                api_code=payload.get("code"),
                http_status=200,
            )
        access = payload.get("access_token")
        refresh = payload.get("refresh_token")
        duration = payload.get("expires_in")
        token_type = payload.get("token_type")
        scope = payload.get("scope")
        if (
            not isinstance(access, str)
            or not access.strip()
            or not isinstance(refresh, str)
            or not refresh.strip()
            or not isinstance(duration, (int, float))
            or isinstance(duration, bool)
            or duration <= settings.token_refresh_skew_seconds
            or not isinstance(token_type, str)
            or token_type.lower() != "bearer"
            or not isinstance(scope, str)
        ):
            raise Pan123Error(
                "PROTOCOL_ERROR", "The OAuth response has invalid token or expiration fields."
            )
        try:
            expiry = datetime.now(UTC) + timedelta(seconds=duration)
        except (ValueError, OverflowError):
            raise Pan123Error("PROTOCOL_ERROR", "The OAuth token expiration is invalid.") from None
        record = self._base_record(settings, access, expiry)
        record.update({"refresh_token": refresh, "token_type": "Bearer", "scope": scope})
        return record

    def refresh(
        self, refresh_token: str | None = None, client_secret: str | None = None
    ) -> dict[str, Any]:
        settings = self._oauth_settings(client_secret=client_secret)
        application = _required(settings.oauth_client_id, "OAuth application ID")
        secret = _required(settings.oauth_client_secret, "OAuth application secret")
        path = self._path(settings)
        observed = self._raw_record(path)
        with self._lock(path):
            latest = self._raw_record(path)
            if (
                refresh_token is None
                and latest
                and latest != observed
                and self._usable(self._record(settings), settings)
            ):
                return self._status(settings)
            selected = (
                refresh_token
                if refresh_token is not None
                else latest.get("refresh_token")
                if latest
                else None
            )
            selected = _required(selected, "A usable OAuth refresh token; run oauth exchange")
            digest = hashlib.sha256(selected.encode("utf-8")).hexdigest()
            if latest and latest.get("consumed_refresh_hash") == digest:
                raise Pan123Error(
                    "TOKEN_UNAVAILABLE",
                    "This refresh token has already been consumed. Authorize again.",
                )
            tombstone = {
                "schema_version": 1,
                "auth_mode": "oauth",
                "credential_fingerprint": settings.fingerprint,
                "refresh_status": "unknown",
                "consumed_refresh_hash": digest,
            }
            write_private_json(path, tombstone)
            payload = self._request(
                "/api/v1/oauth2/access_token",
                params={
                    "client_id": application,
                    "client_secret": secret,
                    "grant_type": "refresh_token",
                    "refresh_token": selected,
                },
                sensitive=(secret, selected),
            )
            record = self._oauth_record(payload, settings)
            record["consumed_refresh_hash"] = digest
            write_private_json(path, record)
        return self._status(settings)

    def close(self) -> None:
        if self._owns_client and self._client is not None:
            self._client.close()
            self._client = None
