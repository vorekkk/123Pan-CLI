import json
from importlib import import_module

import pytest


def main():
    try:
        return import_module("pan123_cli.cli").main
    except ModuleNotFoundError:
        pytest.fail("CLI runner is not implemented yet")


def test_help_needs_no_credentials_or_network(capsys, monkeypatch):
    monkeypatch.delenv("PAN123_CLIENT_ID", raising=False)
    monkeypatch.delenv("PAN123_CLIENT_SECRET", raising=False)
    assert main()(["--help"]) == 0
    assert "file" in capsys.readouterr().out


def test_json_argument_error_is_one_parseable_document(capsys):
    assert main()(["file", "info", "--file-id", "not-an-integer", "--json"]) == 2
    output = json.loads(capsys.readouterr().out)
    assert output["ok"] is False
    assert output["error"]["kind"] == "INVALID_ARGUMENT"


def test_root_alias_help(capsys):
    assert main()(["upload", "--help"]) == 0
    assert "--file" in capsys.readouterr().out


def test_alias_after_global_option_with_value(capsys):
    assert main()(["--env-file", "unused.env", "list", "--help"]) == 0
    assert "--parent-id" in capsys.readouterr().out


def test_credential_missing_returns_auth_code_in_json(capsys, monkeypatch, tmp_path):
    monkeypatch.delenv("PAN123_CLIENT_ID", raising=False)
    monkeypatch.delenv("PAN123_CLIENT_SECRET", raising=False)
    assert main()(["user", "info", "--cache-dir", str(tmp_path), "--json"]) == 3
    assert json.loads(capsys.readouterr().out)["ok"] is False


def test_multiple_stdin_consumers_rejected_before_credential_loading(capsys):
    assert main()(["oauth", "exchange", "--code-stdin", "--client-secret-stdin", "--json"]) == 2
    result = json.loads(capsys.readouterr().out)
    assert result["error"]["kind"] == "INVALID_ARGUMENT"


@pytest.mark.parametrize(
    "args, method, path, expected",
    [
        (["file", "info", "--file-id", "7"], "GET", "/api/v1/file/detail", {"fileID": 7}),
        (
            ["file", "copy-progress", "--task-id", "11"],
            "GET",
            "/api/v1/file/async/copy/process",
            {"taskId": 11},
        ),
        (
            ["directlink", "blacklist", "switch", "--status", "2", "--yes"],
            "POST",
            "/api/v1/developer/config/forbide-ip/switch",
            {"Status": 2},
        ),
        (
            ["transcode", "from-cloud", "--file-id", "7", "--file-id", "8"],
            "POST",
            "/api/v1/transcode/upload/from_cloud_disk",
            [{"fileId": 7}, {"fileId": 8}],
        ),
    ],
)
def test_real_parser_dispatches_exact_request(args, method, path, expected, capsys, monkeypatch):
    module = import_module("pan123_cli.cli")
    requests = []

    class Client:
        def __init__(self, settings):
            self.settings = settings

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def request(self, actual_method, actual_path, **kwargs):
            assert actual_method == method and actual_path == path
            payload = kwargs.get("json", kwargs.get("params"))
            requests.append(payload)
            return {"received": True}

    monkeypatch.setattr(module, "ApiClient", Client)
    assert module.main([*args, "--json"]) == 0
    assert requests == [expected]
    assert json.loads(capsys.readouterr().out)["data"] == {"received": True}


def test_zip_wait_never_reports_success_if_capacity_full(monkeypatch):
    module = import_module("pan123_cli.cli")
    catalog = import_module("pan123_cli.catalog")
    ep = next(e for e in catalog.ENDPOINTS if e.command == ("transcode", "all-download-urls"))
    from types import SimpleNamespace

    from pan123_cli.errors import Pan123Error

    client = SimpleNamespace(
        settings=SimpleNamespace(api_timeout=30),
        request=lambda *a, **k: {"isFull": True, "isDownloading": False, "downloadUrl": ""},
    )
    with pytest.raises(Pan123Error):
        module._wait_endpoint(client, ep, {"fileId": 7, "zipName": "archive"}, {})


def test_wait_boolean_status_cannot_be_integer(monkeypatch):
    from types import SimpleNamespace

    from pan123_cli.errors import Pan123Error

    module = import_module("pan123_cli.cli")
    ep = next(
        e
        for e in import_module("pan123_cli.catalog").ENDPOINTS
        if e.command == ("transcode", "resolutions")
    )
    client = SimpleNamespace(
        settings=SimpleNamespace(api_timeout=30), request=lambda *a, **k: {"IsGetResolution": 0}
    )
    with pytest.raises(Pan123Error):
        module._wait_endpoint(client, ep, {"fileId": 7}, {})


def test_all_catalog_commands_expose_offline_help(capsys):
    module = import_module("pan123_cli.cli")
    commands = [
        e.command
        for e in import_module("pan123_cli.catalog").ENDPOINTS
        if e.command != ("file", "list-v1")
    ]
    for command in commands:
        assert module.main([*command, "--help"]) == 0, command
        assert "usage:" in capsys.readouterr().out


def test_v2_rejects_v1_only_page_options_before_network(capsys):
    assert main()(["file", "list", "--page", "2", "--json"]) == 2
    assert json.loads(capsys.readouterr().out)["ok"] is False


def test_request_file_listing_extras_are_sent(capsys, monkeypatch, tmp_path):
    module = import_module("pan123_cli.cli")
    request = tmp_path / "list.json"
    request.write_text('{"parentFileId":0,"limit":5,"searchMode":1}')

    class Client:
        def __init__(self, settings):
            self.settings = settings

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def request(self, method, path, **kwargs):
            assert kwargs["params"] == {
                "parentFileId": 0,
                "limit": 5,
                "category": 2,
                "searchMode": 1,
            }
            return {"fileList": [], "lastFileId": -1}

    monkeypatch.setattr(module, "ApiClient", Client)
    assert module.main(["transcode", "source-list", "--request-file", str(request), "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["data"]["complete"] is True


def test_request_file_overwrite_needs_confirmation_before_network(capsys, tmp_path):
    request = tmp_path / "upload.json"
    request.write_text(
        json.dumps(
            {"parentFileID": 0, "filename": "test.bin", "etag": "a" * 32, "size": 1, "duplicate": 2}
        )
    )
    assert (
        main()(["file", "upload-api", "v2", "create", "--request-file", str(request), "--json"])
        == 2
    )
    assert json.loads(capsys.readouterr().out)["error"]["kind"] == "INVALID_ARGUMENT"


def test_oauth_mode_from_env_file_satisfies_endpoint_requirement(capsys, monkeypatch, tmp_path):
    module = import_module("pan123_cli.cli")
    env_file = tmp_path / "oauth.env"
    env_file.write_text(
        "PAN123_AUTH_MODE=oauth\nPAN123_OAUTH_CLIENT_ID=app\nPAN123_OAUTH_CLIENT_SECRET=secret\n"
    )
    monkeypatch.delenv("PAN123_AUTH_MODE", raising=False)

    class Client:
        def __init__(self, settings):
            assert settings.auth_mode == "oauth"

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def request(self, *args, **kwargs):
            return {"videos": []}

    monkeypatch.setattr(module, "ApiClient", Client)
    assert (
        module.main(["--env-file", str(env_file), "transcode", "list", "--file-id", "7", "--json"])
        == 0
    )
    assert json.loads(capsys.readouterr().out)["ok"]


def test_auth_request_file_is_not_silently_ignored(capsys):
    assert main()(["auth", "ensure", "--request-file", "ignored.json", "--json"]) == 2
    assert json.loads(capsys.readouterr().out)["error"]["kind"] == "INVALID_ARGUMENT"


def _run_cli(arguments, environment):
    import os
    import subprocess
    import sys
    from pathlib import Path

    source = Path(__file__).resolve().parents[1] / "src"
    return subprocess.run(
        [sys.executable, "-m", "pan123_cli", *arguments],
        capture_output=True,
        check=False,
        # Detach stdin so a runner console cannot turn the confirmation prompt
        # into an interactive wait.
        stdin=subprocess.DEVNULL,
        env={**os.environ, "PYTHONPATH": str(source), **environment},
    )


def test_legacy_windows_encoding_cannot_break_help_or_json_output(tmp_path):
    # Windows pipes default to the ANSI code page; Chinese help text and JSON
    # messages must still reach them as UTF-8 instead of failing the command.
    legacy = {"PYTHONIOENCODING": "cp1252"}
    helped = _run_cli(["--help"], legacy)
    assert helped.returncode == 0, helped.stderr
    assert "云盘" in helped.stdout.decode("utf-8")
    output = tmp_path / "out.bin"
    refused = _run_cli(
        [
            "file",
            "download",
            "--file-id",
            "1",
            "--output",
            str(output),
            "--overwrite",
            "--json",
        ],
        legacy,
    )
    # Windows reports a NUL stdin as a terminal, so the refusal wording differs
    # there; the invariants are the exit code, the CJK message and no local write.
    assert refused.returncode == 2
    error = json.loads(refused.stdout.decode("utf-8"))["error"]
    assert error["kind"] == "INVALID_ARGUMENT" and error["exit_code"] == 2
    assert error["message"] and not error["message"].isascii()
    assert not output.exists()
