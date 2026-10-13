from importlib import import_module
from types import SimpleNamespace

import httpx
import pytest

from pan123_cli.errors import Pan123Error


class Tokens:
    def __init__(self):
        self.invalidated = []
        self.calls = 0

    def get_token(self):
        self.calls += 1
        return "official-access-token" if not self.invalidated else "new-access-token"

    def invalidate(self, token=None):
        self.invalidated.append(token)

    def close(self):
        pass


def make_client(handler, transfer_handler=None):
    try:
        module = import_module("pan123_cli.client")
    except ModuleNotFoundError:
        pytest.fail("Official API client is not implemented yet")
    settings = SimpleNamespace(
        api_timeout=30,
        transfer_timeout=120,
        read_max_retries=0,
        client_secret="hidden-secret",
        oauth_client_secret="hidden-oauth-secret",
    )
    api = httpx.Client(transport=httpx.MockTransport(handler))
    transfer = httpx.Client(transport=httpx.MockTransport(transfer_handler or handler))
    return module.ApiClient(settings, Tokens(), api, transfer)


def test_business_error_inside_http_200_is_a_failure():
    client = make_client(
        lambda r: httpx.Response(
            200, json={"code": 5113, "message": "quota", "data": None, "x-traceID": "trace"}
        )
    )
    with pytest.raises(Pan123Error) as captured:
        client.request("GET", "/api/v1/file/download_info", params={"fileId": 42})
    assert captured.value.api_code == 5113
    assert captured.value.trace_id == "trace"
    client.close()


def test_control_request_uses_official_domain_and_exact_get_body():
    def handler(request):
        assert request.url.host == "open-api.123pan.com"
        assert request.headers["Authorization"] == "Bearer official-access-token"
        assert request.headers["Platform"] == "open_platform"
        assert "stoken" not in request.headers
        assert request.method == "GET"
        assert request.content == b'{"taskId":"copy-task"}'
        return httpx.Response(200, json={"code": 0, "message": "ok", "data": {"status": 2}})

    client = make_client(handler)
    assert client.request(
        "GET", "/api/v1/file/async/copy/process", json={"taskId": "copy-task"}
    ) == {"status": 2}
    client.close()


def test_http_error_cannot_succeed_even_with_zero_business_code():
    client = make_client(
        lambda r: httpx.Response(503, json={"code": 0, "message": "ok", "data": {}})
    )
    with pytest.raises(Pan123Error) as captured:
        client.request("GET", "/api/v1/user/info")
    assert captured.value.http_status == 503
    client.close()


def test_mutation_auth_failure_is_not_replayed():
    requests = []

    def handler(request):
        requests.append(request)
        return httpx.Response(401, json={"code": 401, "message": "expired", "data": None})

    client = make_client(handler)
    with pytest.raises(Pan123Error):
        client.request("POST", "/upload/v2/file/create", json={"filename": "test"})
    assert len(requests) == 1
    client.close()


def test_read_auth_failure_reauthenticates_at_most_once():
    requests = []

    def handler(request):
        requests.append(request)
        if len(requests) == 1:
            return httpx.Response(200, json={"code": 401, "message": "expired", "data": None})
        assert request.headers["Authorization"] == "Bearer new-access-token"
        return httpx.Response(200, json={"code": 0, "data": {"uid": 1}})

    client = make_client(handler)
    assert client.request("GET", "/api/v1/user/info", retryable=True) == {"uid": 1}
    assert len(requests) == 2
    client.close()


@pytest.mark.parametrize("http_status", [200, 401])
@pytest.mark.parametrize("retryable", [False, True])
def test_oauth_401_preserves_refresh_and_requires_explicit_refresh(
    tmp_path, http_status, retryable
):
    from datetime import UTC, datetime, timedelta

    from pan123_cli.auth import TokenManager
    from pan123_cli.cache import read_private_json, write_private_json
    from pan123_cli.client import ApiClient
    from pan123_cli.config import Settings

    settings = Settings(
        auth_mode="oauth",
        oauth_client_id="app-id",
        oauth_client_secret="app-secret",
        cache_dir=tmp_path,
    )
    path = tmp_path / f"token-{settings.fingerprint}.json"
    write_private_json(
        path,
        {
            "schema_version": 1,
            "auth_mode": "oauth",
            "credential_fingerprint": settings.fingerprint,
            "access_token": "offline-access",
            "refresh_token": "offline-refresh",
            "expires_at": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
            "token_type": "Bearer",
            "scope": "user:base,file:all:read,file:all:write",
        },
    )
    api_requests = []
    refresh_requests = []

    def reject(request):
        api_requests.append(request)
        return httpx.Response(http_status, json={"code": 401, "message": "expired", "data": None})

    def refresh(request):
        refresh_requests.append(request)
        assert request.url.params["grant_type"] == "refresh_token"
        assert request.url.params["refresh_token"] == "offline-refresh"
        return httpx.Response(
            200,
            json={
                "access_token": "rotated-access",
                "refresh_token": "rotated-refresh",
                "expires_in": 7200,
                "token_type": "Bearer",
                "scope": "user:base,file:all:read,file:all:write",
            },
        )

    manager = TokenManager(settings, httpx.Client(transport=httpx.MockTransport(refresh)))
    api_http = httpx.Client(transport=httpx.MockTransport(reject))
    client = ApiClient(settings, manager, api_http, api_http)
    with pytest.raises(Pan123Error) as caught:
        client.request("GET", "/api/v1/user/info", retryable=retryable)
    assert caught.value.kind == "AUTH_REQUIRED"
    assert caught.value.api_code == 401
    assert len(api_requests) == 1
    assert refresh_requests == []
    assert read_private_json(path)["refresh_token"] == "offline-refresh"
    assert manager.status()["usable"] is False
    assert manager.refresh()["usable"] is True
    assert manager.get_token() == "rotated-access"
    client.close()


def test_api_cannot_be_redirected_to_user_supplied_host():
    client = make_client(lambda r: pytest.fail("Request must not be sent"))
    with pytest.raises(Pan123Error):
        client.request("GET", "https://evil.example/api/v1/user/info")
    client.close()


def test_download_redirects_do_not_send_api_credentials():
    def handler(request):
        assert "authorization" not in request.headers
        assert "platform" not in request.headers
        assert "cookie" not in request.headers
        if request.url.host == "first.example":
            return httpx.Response(302, headers={"Location": "https://second.example/data"})
        return httpx.Response(200, content=b"file-bytes")

    client = make_client(lambda r: pytest.fail("Not an API request"), handler)
    with client.stream_download("https://first.example/data") as response:
        assert response.read() == b"file-bytes"
    client.close()


def test_bad_json_is_protocol_failure():
    client = make_client(lambda r: httpx.Response(200, content=b"not-json"))
    with pytest.raises(Pan123Error) as captured:
        client.request("GET", "/api/v1/user/info")
    assert captured.value.kind == "PROTOCOL_ERROR"
    client.close()


def test_single_upload_posts_to_official_returned_server_with_multipart():
    from io import BytesIO

    def handler(request):
        assert request.method == "POST"
        assert str(request.url) == "https://upload.example/upload/v2/file/single/create"
        assert request.headers["Authorization"] == "Bearer official-access-token"
        assert "multipart/form-data; boundary=" in request.headers["Content-Type"]
        assert b"actual-bytes" in request.content
        return httpx.Response(200, json={"code": 0, "data": {"completed": True, "fileID": 42}})

    client = make_client(lambda r: pytest.fail("Not an API request"), handler)
    assert client.upload_single(
        "https://upload.example",
        data={"parentFileID": "0"},
        files={"file": ("test.bin", BytesIO(b"actual-bytes"))},
    ) == {"completed": True, "fileID": 42}
    client.close()


def test_poll_timeout_is_a_total_request_budget_including_retries(monkeypatch):
    timestamps = [0.0]

    def handler(request):
        timestamps[0] += 0.7
        return httpx.Response(503, json={"code": 503, "data": None})

    client = make_client(handler)
    client.settings.read_max_retries = 3
    module = import_module("pan123_cli.client")
    monkeypatch.setattr(module.time, "monotonic", lambda: timestamps[0])
    monkeypatch.setattr(
        module.time, "sleep", lambda delay: timestamps.__setitem__(0, timestamps[0] + delay)
    )
    with pytest.raises(Pan123Error):
        client.request("GET", "/api/v1/user/info", retryable=True, timeout=1)
    assert timestamps[0] <= 1
    client.close()


def test_fake_ip_network_requires_explicit_setting_and_preserves_tls_hostname(monkeypatch):
    module = import_module("pan123_cli.client")
    monkeypatch.setattr(
        module.socket, "getaddrinfo", lambda *a, **k: [(2, 1, 6, "", ("198.18.1.109", 443))]
    )
    client = make_client(lambda r: httpx.Response(200, content=b"verified-bytes"))
    client._pin_targets = True
    with pytest.raises(Pan123Error):
        client._external_request("GET", "https://openapi-upload.123242.com/path")
    client.settings.allow_fake_ip = True
    request = client._external_request("GET", "https://openapi-upload.123242.com/path")
    assert request.url.host == "198.18.1.109"
    assert request.headers["Host"] == "openapi-upload.123242.com"
    assert request.extensions["sni_hostname"] == "openapi-upload.123242.com"
    assert "authorization" not in request.headers
    with pytest.raises(Pan123Error):
        client._external_request("GET", "https://198.18.1.109/path")
    client.close()
