"""HTTP boundary for official API, upload servers and credential-free downloads."""

from __future__ import annotations

import ipaddress
import random
import re
import socket
import time
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any
from urllib.parse import unquote

import httpx

from .errors import Pan123Error
from .utils.urls import validate_external_url

if TYPE_CHECKING:
    from .config import Settings

BASE_URL = "https://open-api.123pan.com"


class ApiClient:
    def __init__(
        self,
        settings: Settings,
        token_manager: Any = None,
        http_client: httpx.Client | None = None,
        transfer_client: httpx.Client | None = None,
    ):
        self.settings = settings
        if token_manager is None:
            from .auth import TokenManager

            token_manager = TokenManager(settings)
        self.tokens = token_manager
        self.http = http_client or httpx.Client(
            timeout=httpx.Timeout(settings.api_timeout, connect=10, pool=10),
            follow_redirects=False,
        )
        self.transfer = transfer_client or httpx.Client(
            timeout=httpx.Timeout(settings.transfer_timeout, connect=10, pool=10),
            follow_redirects=False,
            trust_env=False,
        )
        # Injected transports are trusted test/library dependencies. The CLI always pins DNS.
        self._pin_targets = transfer_client is None

    def _safe_message(self, message: Any, token: str = "") -> str:
        result = str(message)
        for secret in (
            token,
            getattr(self.settings, "client_secret", ""),
            getattr(self.settings, "oauth_client_secret", ""),
        ):
            if secret:
                result = result.replace(secret, "[redacted]")
        result = re.sub(r"https?://[^\s]+", "[URL redacted]", result)
        return result[:1000]

    def _decode(self, response: httpx.Response, token: str = "") -> Any:
        status = response.status_code
        try:
            payload = response.json()
        except ValueError as exc:
            if not response.is_success:
                raise Pan123Error(
                    "UPSTREAM_ERROR", "官方接口返回 HTTP 错误", http_status=status
                ) from exc
            raise Pan123Error("PROTOCOL_ERROR", "官方接口没有返回有效 JSON") from exc
        if not isinstance(payload, dict) or type(payload.get("code")) is not int:
            raise Pan123Error("PROTOCOL_ERROR", "官方接口响应缺少有效业务状态码")
        code = payload["code"]
        if not response.is_success or code != 0:
            kind = "AUTH_REQUIRED" if status == 401 or code == 401 else "UPSTREAM_ERROR"
            raise Pan123Error(
                kind,
                self._safe_message(payload.get("message", "官方请求失败"), token),
                http_status=status,
                api_code=code,
                trace_id=payload.get("x-traceID") or response.headers.get("x-traceID"),
                retryable=status in {429, 502, 503, 504} or code == 429,
            )
        if "data" not in payload:
            raise Pan123Error("PROTOCOL_ERROR", "官方接口响应缺少 data")
        return payload["data"]

    def request(
        self,
        method: str,
        path: str,
        *,
        params: Any = None,
        json: Any = None,
        retryable: bool = False,
        authenticated: bool = True,
        timeout: float | None = None,
    ) -> Any:
        decoded = unquote(unquote(path))
        if (
            not path.startswith("/")
            or path.startswith("//")
            or ".." in decoded.split("/")
            or any(c in path for c in "?#\r\n")
        ):
            raise Pan123Error("INVALID_ARGUMENT", "只能调用固定官方域名的 API 路径")
        reauthenticated = False
        retries = 0
        deadline = time.monotonic() + timeout if timeout is not None else None
        while True:
            remaining = None if deadline is None else deadline - time.monotonic()
            if remaining is not None and remaining <= 0:
                raise Pan123Error("WAIT_TIMEOUT", "请求的总等待时限已到")
            token = self.tokens.get_token() if authenticated else ""
            headers = {"Platform": "open_platform"}
            if authenticated:
                headers["Authorization"] = "Bearer " + token
            kwargs: dict[str, Any] = {
                "params": params,
                "headers": headers,
                "follow_redirects": False,
            }
            if json is not None:
                kwargs["json"] = json
            if remaining is not None:
                kwargs["timeout"] = remaining
            response = None
            try:
                response = self.http.request(method, BASE_URL + path, **kwargs)
                return self._decode(response, token)
            except httpx.HTTPError as exc:
                error = Pan123Error(
                    "NETWORK_ERROR", "无法连接官方接口，或请求等待超时", retryable=True
                )
                error.__cause__ = exc
            except Pan123Error as exc:
                error = exc
            if error.kind == "AUTH_REQUIRED" and authenticated:
                self.tokens.invalidate(token)
                if (
                    retryable
                    and not reauthenticated
                    and getattr(self.settings, "auth_mode", "developer") != "oauth"
                ):
                    reauthenticated = True
                    continue
            if retryable and error.retryable and retries < self.settings.read_max_retries:
                delay = min(8, 0.5 * (2**retries)) + random.uniform(0, 0.1)
                if response is not None:
                    try:
                        retry_after = float(response.headers.get("Retry-After", ""))
                        if 0 <= retry_after <= 60:
                            delay = retry_after
                    except ValueError:
                        pass
                if deadline is not None:
                    delay = min(delay, max(0, deadline - time.monotonic()))
                time.sleep(delay)
                retries += 1
                continue
            raise error

    def _external_request(self, method: str, url: str, **kwargs: Any) -> httpx.Request:
        validate_external_url(url)
        original = httpx.URL(url)
        target = original
        extensions: dict[str, Any] = {}
        host = original.host
        headers = dict(kwargs.pop("headers", {}))
        if self._pin_targets:
            try:
                addresses = socket.getaddrinfo(host, original.port or 443, type=socket.SOCK_STREAM)
                ips = list(dict.fromkeys(item[4][0] for item in addresses))
            except OSError as exc:
                raise Pan123Error("NETWORK_ERROR", "无法解析官方返回的传输地址") from exc
            fake_ip_network = ipaddress.ip_network("198.18.0.0/15")

            def acceptable(ip):
                address = ipaddress.ip_address(ip)
                return address.is_global or (
                    getattr(self.settings, "allow_fake_ip", False) and address in fake_ip_network
                )

            if not ips or any(not acceptable(ip) for ip in ips):
                raise Pan123Error("INVALID_ARGUMENT", "传输地址指向非公网网络")
            target = original.copy_with(host=ips[0])
            host_header = f"[{host}]" if ":" in host else host
            if original.port not in (None, 443):
                host_header += f":{original.port}"
            headers["Host"] = host_header
            extensions["sni_hostname"] = host
        request = self.transfer.build_request(
            method, target, headers=headers, extensions=extensions, **kwargs
        )
        # Credentials are added only by upload_slice after this boundary.
        for field in ("authorization", "platform", "cookie", "stoken"):
            request.headers.pop(field, None)
        return request

    def upload_slice(self, server: str, *, data: Any, files: Any) -> Any:
        validate_external_url(server)
        origin = httpx.URL(server)
        if origin.path not in ("", "/") or origin.query or origin.fragment:
            raise Pan123Error("INVALID_ARGUMENT", "上传服务器必须是官方返回的 HTTPS origin")
        token = self.tokens.get_token()
        request = self._external_request(
            "POST", server.rstrip("/") + "/upload/v2/file/slice", data=data, files=files
        )
        request.headers["Authorization"] = "Bearer " + token
        request.headers["Platform"] = "open_platform"
        try:
            response = self.transfer.send(request, follow_redirects=False)
            return self._decode(response, token)
        except httpx.HTTPError as exc:
            raise Pan123Error(
                "NETWORK_ERROR", "分片请求失败；远程接收结果未知，未自动重发"
            ) from exc

    def post_external(self, url: str, *, data: Any, files: Any) -> Any:
        """Official V2 single-upload transport, with the same authenticated boundary."""
        token = self.tokens.get_token()
        request = self._external_request("POST", url, data=data, files=files)
        request.headers["Authorization"] = "Bearer " + token
        request.headers["Platform"] = "open_platform"
        try:
            return self._decode(self.transfer.send(request, follow_redirects=False), token)
        except httpx.HTTPError as exc:
            raise Pan123Error("NETWORK_ERROR", "单步上传请求失败，远程结果未知") from exc

    def upload_single(self, server: str, *, data: Any, files: Any) -> Any:
        validate_external_url(server)
        origin = httpx.URL(server)
        if origin.path not in ("", "/") or origin.query or origin.fragment:
            raise Pan123Error("INVALID_ARGUMENT", "上传服务器必须是官方返回的 HTTPS origin")
        return self.post_external(
            server.rstrip("/") + "/upload/v2/file/single/create", data=data, files=files
        )

    def put_external(self, url: str, fileobj: Any) -> None:
        headers = {"Content-Type": "application/octet-stream"}
        position = fileobj.tell()
        fileobj.seek(0, 2)
        headers["Content-Length"] = str(fileobj.tell() - position)
        fileobj.seek(position)

        def chunks():
            while chunk := fileobj.read(1024 * 1024):
                yield chunk

        request = self._external_request("PUT", url, headers=headers, content=chunks())
        try:
            response = self.transfer.send(request, follow_redirects=False)
        except httpx.HTTPError as exc:
            raise Pan123Error("NETWORK_ERROR", "分片 PUT 请求失败，远程结果未知") from exc
        if not response.is_success:
            raise Pan123Error("UPSTREAM_ERROR", "分片 PUT 被拒绝", http_status=response.status_code)

    @contextmanager
    def stream_download(self, url: str):
        current = url
        response = None
        try:
            for _ in range(6):
                request = self._external_request(
                    "GET", current, headers={"Accept-Encoding": "identity"}
                )
                response = self.transfer.send(request, stream=True, follow_redirects=False)
                if response.status_code in {301, 302, 303, 307, 308}:
                    location = response.headers.get("Location")
                    response.close()
                    if not location:
                        raise Pan123Error("PROTOCOL_ERROR", "下载重定向缺少 Location")
                    current = str(httpx.URL(current).join(location))
                    continue
                if not response.is_success:
                    raise Pan123Error(
                        "UPSTREAM_ERROR", "下载地址请求失败", http_status=response.status_code
                    )
                yield response
                return
            raise Pan123Error("PROTOCOL_ERROR", "下载重定向超过 5 次")
        except httpx.HTTPError as exc:
            raise Pan123Error("NETWORK_ERROR", "下载连接中断或等待超时") from exc
        finally:
            if response is not None:
                response.close()

    def close(self):
        self.http.close()
        self.transfer.close()
        close = getattr(self.tokens, "close", None)
        if close:
            close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
