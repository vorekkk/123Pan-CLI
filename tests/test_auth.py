import json
import logging
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import httpx
import pytest

from pan123_cli.auth import TokenManager
from pan123_cli.cache import read_private_json, write_private_json
from pan123_cli.config import Settings
from pan123_cli.errors import Pan123Error


def developer_settings(tmp_path, **kwargs):
    return Settings(
        client_id="developer-id",
        client_secret="developer-secret",
        cache_dir=tmp_path / "cache",
        **kwargs,
    )


def oauth_settings(tmp_path):
    return Settings(
        auth_mode="oauth",
        oauth_client_id="app-id",
        oauth_client_secret="app-secret",
        oauth_redirect_uri="demo://callback",
        cache_dir=tmp_path / "cache",
    )


def developer_response(token="developer-token", expiry=None):
    return {
        "code": 0,
        "message": "ok",
        "data": {
            "accessToken": token,
            "expiredAt": expiry or (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
        },
        "x-traceID": "trace",
    }


def oauth_response(token="oauth-token", refresh="refresh-new"):
    return {
        "access_token": token,
        "refresh_token": refresh,
        "expires_in": 7200,
        "scope": "user:base,file:all:read,file:all:write",
        "token_type": "Bearer",
    }


def token_path(settings):
    return settings.cache_dir / f"token-{settings.fingerprint}.json"


def test_status_and_clear_without_credentials_are_local_and_do_not_create_cache(tmp_path):
    settings = Settings(cache_dir=tmp_path / "missing")

    def unexpected(request):
        raise AssertionError("local commands must not request a token")

    manager = TokenManager(settings, httpx.Client(transport=httpx.MockTransport(unexpected)))
    assert manager.status()["usable"] is False
    manager.clear()
    assert not settings.cache_dir.exists()
    with pytest.raises(Pan123Error) as caught:
        manager.get_token()
    assert caught.value.exit_code == 3


def test_developer_request_is_official_json_and_does_not_inherit_auth(tmp_path):
    def respond(request):
        assert str(request.url) == "https://open-api.123pan.com/api/v1/access_token"
        assert request.method == "POST"
        assert "authorization" not in request.headers
        assert "cookie" not in request.headers
        assert request.headers["Platform"] == "open_platform"
        assert json.loads(request.content) == {
            "clientID": "developer-id",
            "clientSecret": "developer-secret",
        }
        return httpx.Response(200, json=developer_response())

    client = httpx.Client(
        transport=httpx.MockTransport(respond),
        headers={"Authorization": "Bearer inherited", "Cookie": "inherited-cookie"},
    )
    manager = TokenManager(developer_settings(tmp_path), client)
    assert manager.get_token() == "developer-token"
    assert manager.get_token() == "developer-token"
    status = manager.status()
    assert status["usable"] is True
    assert "developer-token" not in json.dumps(status)
    assert "developer-secret" not in json.dumps(status)


@pytest.mark.parametrize("expiry", ["2025-01-01T12:00:00", "invalid", "2000-01-01T00:00:00Z"])
def test_invalid_or_expired_token_responses_are_not_cached(tmp_path, expiry):
    settings = developer_settings(tmp_path)
    manager = TokenManager(
        settings,
        httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, json=developer_response(expiry=expiry))
            )
        ),
    )
    with pytest.raises(Pan123Error) as caught:
        manager.get_token()
    assert caught.value.exit_code in (3, 7)
    assert not token_path(settings).exists()


def test_invalid_cache_is_replaced_and_stale_invalidation_keeps_new_token(tmp_path):
    settings = developer_settings(tmp_path)
    write_private_json(
        token_path(settings),
        {
            "schema_version": 1,
            "auth_mode": "developer",
            "credential_fingerprint": settings.fingerprint,
            "access_token": "old",
            "expires_at": "2025-01-01T12:00:00",
        },
    )
    manager = TokenManager(
        settings,
        httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, json=developer_response("new"))
            )
        ),
    )
    assert manager.get_token() == "new"
    manager.invalidate("old")
    assert manager.get_token() == "new"
    manager.invalidate("new")
    assert manager.status()["usable"] is False


def test_concurrent_developer_managers_issue_one_token(tmp_path):
    settings = developer_settings(tmp_path)
    calls = []

    def respond(request):
        calls.append(request)
        time.sleep(0.1)
        return httpx.Response(200, json=developer_response())

    managers = [
        TokenManager(settings, httpx.Client(transport=httpx.MockTransport(respond)))
        for _ in range(2)
    ]
    barrier = threading.Barrier(2)

    def acquire(manager):
        barrier.wait()
        return manager.get_token()

    with ThreadPoolExecutor(max_workers=2) as pool:
        tokens = list(pool.map(acquire, managers))
    assert tokens == ["developer-token", "developer-token"]
    assert len(calls) == 1


def test_business_token_error_keeps_codes_but_redacts_secret_message(tmp_path):
    manager = TokenManager(
        developer_settings(tmp_path),
        httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(
                    200, json={"code": 401, "message": "developer-secret", "x-traceID": "trace"}
                )
            )
        ),
    )
    with pytest.raises(Pan123Error) as caught:
        manager.get_token()
    assert caught.value.api_code == 401
    assert caught.value.trace_id == "trace"
    assert "developer-secret" not in str(caught.value)


def test_oauth_exchange_uses_query_contract_and_consumes_bound_state(tmp_path):
    settings = oauth_settings(tmp_path)
    calls = []

    def respond(request):
        calls.append(request)
        query = dict(request.url.params)
        assert request.method == "POST"
        assert request.url.path == "/api/v1/oauth2/access_token"
        assert query == {
            "client_id": "app-id",
            "client_secret": "app-secret",
            "grant_type": "authorization_code",
            "code": "private-code",
            "redirect_uri": "demo://callback",
        }
        assert not request.content
        assert "authorization" not in request.headers
        return httpx.Response(200, json=oauth_response())

    manager = TokenManager(settings, httpx.Client(transport=httpx.MockTransport(respond)))
    authorization = manager.authorize_url(state="state-unique")
    query = parse_qs(urlsplit(authorization["url"]).query)
    assert query["state"] == ["state-unique"]
    assert query["scope"] == ["user:base,file:all:read,file:all:write"]
    result = manager.exchange("private-code", "state-unique")
    assert result["usable"] is True
    assert manager.get_token() == "oauth-token"
    assert "oauth-token" not in json.dumps(result)
    assert "refresh-new" not in json.dumps(result)
    with pytest.raises(Pan123Error):
        manager.exchange("private-code", "state-unique")
    assert len(calls) == 1


def test_oauth_state_rejects_duplicate_and_wrong_application_binding(tmp_path):
    manager = TokenManager(oauth_settings(tmp_path))
    manager.authorize_url(state="pending-state")
    with pytest.raises(Pan123Error):
        manager.authorize_url(state="pending-state")
    with pytest.raises(Pan123Error):
        manager.exchange("code", "pending-state", client_id="different-app")
    with pytest.raises(Pan123Error):
        manager.exchange("code", "pending-state", redirect_uri="demo://different")
    assert len(list(manager.settings.cache_dir.glob("oauth-state-*.json"))) == 1


def test_oauth_expired_state_is_rejected_before_network(tmp_path):
    def unexpected(request):
        raise AssertionError("expired state must not be exchanged")

    manager = TokenManager(
        oauth_settings(tmp_path), httpx.Client(transport=httpx.MockTransport(unexpected))
    )
    manager.authorize_url(state="expired-state")
    path = next(manager.settings.cache_dir.glob("oauth-state-*.json"))
    record = read_private_json(path)
    record["created_at"] = (datetime.now(UTC) - timedelta(minutes=11)).isoformat()
    record["expires_at"] = (datetime.now(UTC) - timedelta(minutes=1)).isoformat()
    write_private_json(path, record)
    with pytest.raises(Pan123Error):
        manager.exchange("code", "expired-state")


def test_oauth_refresh_rotates_pair_atomically_and_unknown_result_cannot_replay(tmp_path):
    settings = oauth_settings(tmp_path)
    requests = []

    def respond(request):
        requests.append(request)
        if request.url.params["grant_type"] == "authorization_code":
            return httpx.Response(200, json=oauth_response("first-access", "first-refresh"))
        assert request.url.params["refresh_token"] == "first-refresh"
        assert "redirect_uri" not in request.url.params
        raise httpx.ReadTimeout(
            "request https://open-api.123pan.com/token?client_secret=app-secret&refresh_token=first-refresh",
            request=request,
        )

    manager = TokenManager(settings, httpx.Client(transport=httpx.MockTransport(respond)))
    manager.authorize_url(state="state")
    manager.exchange("code", "state")
    with pytest.raises(Pan123Error) as caught:
        manager.refresh()
    assert "app-secret" not in str(caught.value)
    assert "first-refresh" not in str(caught.value)
    assert manager.status()["usable"] is False
    with pytest.raises(Pan123Error):
        manager.refresh()
    assert len(requests) == 2


def test_oauth_refresh_success_persists_new_access_and_refresh(tmp_path):
    settings = oauth_settings(tmp_path)

    def respond(request):
        grant = request.url.params["grant_type"]
        return httpx.Response(
            200,
            json=oauth_response("first", "refresh-first")
            if grant == "authorization_code"
            else oauth_response("second", "refresh-second"),
        )

    manager = TokenManager(settings, httpx.Client(transport=httpx.MockTransport(respond)))
    manager.authorize_url(state="state")
    manager.exchange("code", "state")
    manager.refresh()
    assert manager.get_token() == "second"
    record = read_private_json(token_path(settings))
    assert record["access_token"] == "second"
    assert record["refresh_token"] == "refresh-second"


def test_oauth_invalidation_retains_refresh_token_and_stale_invalidation_preserves_rotation(
    tmp_path,
):
    settings = oauth_settings(tmp_path)
    grants = []

    def respond(request):
        grants.append(dict(request.url.params))
        if request.url.params["grant_type"] == "authorization_code":
            return httpx.Response(200, json=oauth_response("first-access", "first-refresh"))
        assert request.url.params["refresh_token"] == "first-refresh"
        return httpx.Response(200, json=oauth_response("second-access", "second-refresh"))

    manager = TokenManager(settings, httpx.Client(transport=httpx.MockTransport(respond)))
    manager.authorize_url(state="invalidate-state")
    manager.exchange("code", "invalidate-state")
    manager.invalidate("first-access")
    assert read_private_json(token_path(settings))["refresh_token"] == "first-refresh"
    assert manager.status()["usable"] is False
    with pytest.raises(Pan123Error):
        manager.get_token()
    assert len(grants) == 1
    assert manager.refresh()["usable"] is True
    manager.invalidate("first-access")
    assert manager.get_token() == "second-access"
    assert read_private_json(token_path(settings))["refresh_token"] == "second-refresh"


@pytest.mark.parametrize("outcome", ["success", "unknown"])
def test_oauth_refresh_started_during_tombstone_coalesces_or_keeps_unknown_failure(
    tmp_path, monkeypatch, outcome
):
    settings = oauth_settings(tmp_path)
    write_private_json(
        token_path(settings),
        {
            "schema_version": 1,
            "auth_mode": "oauth",
            "credential_fingerprint": settings.fingerprint,
            "access_token": "first-access",
            "refresh_token": "first-refresh",
            "expires_at": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
            "token_type": "Bearer",
            "scope": "user:base,file:all:read,file:all:write",
        },
    )
    first_request_started = threading.Event()
    late_observer_read = threading.Event()
    release_first_request = threading.Event()
    refresh_requests = []

    def respond(request):
        refresh_requests.append(dict(request.url.params))
        first_request_started.set()
        assert release_first_request.wait(timeout=5)
        if outcome == "unknown":
            raise httpx.ReadTimeout("offline unknown response", request=request)
        return httpx.Response(200, json=oauth_response("second-access", "second-refresh"))

    first = TokenManager(settings, httpx.Client(transport=httpx.MockTransport(respond)))
    late = TokenManager(settings, httpx.Client(transport=httpx.MockTransport(respond)))
    original_read = late._raw_record

    def observe_record(path):
        record = original_read(path)
        if record and record.get("refresh_status") == "unknown":
            late_observer_read.set()
        return record

    monkeypatch.setattr(late, "_raw_record", observe_record)
    with ThreadPoolExecutor(max_workers=2) as pool:
        first_result = pool.submit(first.refresh)
        assert first_request_started.wait(timeout=5)
        late_result = pool.submit(late.refresh)
        try:
            assert late_observer_read.wait(timeout=5)
        finally:
            release_first_request.set()
        if outcome == "success":
            assert first_result.result(timeout=5)["usable"] is True
            assert late_result.result(timeout=5)["usable"] is True
        else:
            with pytest.raises(Pan123Error):
                first_result.result(timeout=5)
            with pytest.raises(Pan123Error):
                late_result.result(timeout=5)
            with pytest.raises(Pan123Error):
                late.refresh()
    assert len(refresh_requests) == 1
    if outcome == "success":
        assert late.get_token() == "second-access"
    else:
        assert late.status()["usable"] is False


def test_oauth_http_diagnostics_hide_query_credentials(tmp_path, caplog):
    manager = TokenManager(
        oauth_settings(tmp_path),
        httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, json=oauth_response())
            )
        ),
    )
    manager.authorize_url(state="log-state")
    with caplog.at_level(logging.INFO, logger="httpx"):
        manager.exchange("secret-auth-code", "log-state")
    assert "app-secret" not in caplog.text
    assert "secret-auth-code" not in caplog.text
    assert "access_token" in caplog.text


def test_explicit_unicode_state_can_be_consumed(tmp_path):
    manager = TokenManager(
        oauth_settings(tmp_path),
        httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, json=oauth_response())
            )
        ),
    )
    manager.authorize_url(state="状态-unique")
    assert manager.exchange("code", "状态-unique")["usable"] is True


def test_oauth_state_boolean_schema_is_rejected(tmp_path):
    def unexpected(request):
        raise AssertionError("boolean state schema must not be exchanged")

    manager = TokenManager(
        oauth_settings(tmp_path), httpx.Client(transport=httpx.MockTransport(unexpected))
    )
    manager.authorize_url(state="bad-schema-state")
    path = next(manager.settings.cache_dir.glob("oauth-state-*.json"))
    record = read_private_json(path)
    record["schema_version"] = True
    write_private_json(path, record)
    with pytest.raises(Pan123Error) as caught:
        manager.exchange("code", "bad-schema-state")
    assert caught.value.exit_code == 3


def test_oauth_pending_state_auth_mode_is_verified(tmp_path):
    def unexpected(request):
        raise AssertionError("wrong identity record must never be exchanged")

    manager = TokenManager(
        oauth_settings(tmp_path), httpx.Client(transport=httpx.MockTransport(unexpected))
    )
    manager.authorize_url(state="bad-mode-state")
    path = next(manager.settings.cache_dir.glob("oauth-state-*.json"))
    record = read_private_json(path)
    record["auth_mode"] = "developer"
    write_private_json(path, record)
    with pytest.raises(Pan123Error):
        manager.exchange("code", "bad-mode-state")


def test_developer_error_trace_is_redacted_against_known_credentials(tmp_path):
    manager = TokenManager(
        developer_settings(tmp_path),
        httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(
                    200, json={"code": 401, "message": "denied", "x-traceID": "developer-secret"}
                )
            )
        ),
    )
    with pytest.raises(Pan123Error) as caught:
        manager.get_token()
    assert "developer-secret" not in json.dumps(caught.value.as_dict())


def test_token_invalid_http_status_is_never_success(tmp_path):
    settings = developer_settings(tmp_path)
    manager = TokenManager(
        settings,
        httpx.Client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(503, json=developer_response())
            )
        ),
    )
    with pytest.raises(Pan123Error) as caught:
        manager.get_token()
    assert caught.value.http_status == 503
    assert not token_path(settings).exists()


def test_concurrent_oauth_refresh_reuses_pair_written_by_waiting_process(tmp_path):
    settings = oauth_settings(tmp_path)
    requests = []

    def respond(request):
        if request.url.params["grant_type"] == "authorization_code":
            return httpx.Response(200, json=oauth_response("first-access", "first-refresh"))
        requests.append(request)
        time.sleep(0.1)
        return httpx.Response(200, json=oauth_response("second-access", "second-refresh"))

    managers = [
        TokenManager(settings, httpx.Client(transport=httpx.MockTransport(respond)))
        for _ in range(2)
    ]
    managers[0].authorize_url(state="race-state")
    managers[0].exchange("code", "race-state")
    barrier = threading.Barrier(2)

    def refresh(manager):
        barrier.wait()
        return manager.refresh()

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(refresh, managers))
    assert all(result["usable"] for result in results)
    assert len(requests) == 1
    assert managers[0].get_token() == "second-access"


def test_cross_process_developer_lock_avoids_duplicate_issue(tmp_path):
    cache = tmp_path / "cache"
    issued = tmp_path / "issued.txt"
    child_source = """
import sys, time
from datetime import UTC, datetime, timedelta
from pathlib import Path
import httpx
from pan123_cli.auth import TokenManager
from pan123_cli.config import Settings
cache, issued = map(Path, sys.argv[1:])
def respond(request):
    with issued.open("a") as record:
        record.write("issued\\n")
    time.sleep(0.2)
    return httpx.Response(200, json={"code": 0, "data": {"accessToken": "shared-token", "expiredAt": (datetime.now(UTC) + timedelta(hours=1)).isoformat()}})
manager = TokenManager(Settings(client_id="id", client_secret="secret", cache_dir=cache), httpx.Client(transport=httpx.MockTransport(respond)))
print(manager.get_token())
"""
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / "src"))
    processes = [
        subprocess.Popen(
            [sys.executable, "-c", child_source, str(cache), str(issued)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=env,
        )
        for _ in range(2)
    ]
    for process in processes:
        stdout, stderr = process.communicate(timeout=15)
        assert process.returncode == 0, stderr
        assert stdout.strip() == "shared-token"
    assert issued.read_text().splitlines() == ["issued"]
