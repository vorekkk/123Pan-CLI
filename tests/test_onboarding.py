import json

import pytest

from pan123_cli.cli import build_parser, main
from pan123_cli.config import load_settings
from pan123_cli.errors import Pan123Error


def test_setup_and_skill_commands_parse():
    parser = build_parser()
    assert parser.parse_args(["setup"]).command == ("setup",)
    assert parser.parse_args(
        ["skill", "install", "--agent", "cursor", "--scope", "project"]
    ).command == ("skill", "install")


def test_private_credentials_are_defaults(tmp_path, monkeypatch):
    monkeypatch.setattr("pan123_cli.config.user_config_dir", lambda *a, **k: str(tmp_path))
    (tmp_path / "credentials.json").write_text(
        json.dumps({"schema_version": 1, "client_id": "saved", "client_secret": "saved-secret"})
    )
    (tmp_path / "credentials.json").chmod(0o600)
    assert load_settings({}, {}).client_secret == "saved-secret"
    config = tmp_path / "custom.json"
    config.write_text(json.dumps({"client_id": "custom"}))
    settings = load_settings({"config": str(config)}, {"PAN123_CLIENT_SECRET": "env-secret"})
    assert (settings.client_id, settings.client_secret) == ("custom", "env-secret")


def test_setup_failure_preserves_old_credentials(tmp_path, monkeypatch):
    from pan123_cli import onboarding

    monkeypatch.setattr("pan123_cli.config.user_config_dir", lambda *a, **k: str(tmp_path))
    old = {"schema_version": 1, "client_id": "old", "client_secret": "old-secret"}
    (tmp_path / "credentials.json").write_text(json.dumps(old))
    (tmp_path / "credentials.json").chmod(0o600)
    answers = iter(["new", "n"])
    monkeypatch.setattr("builtins.input", lambda *a: next(answers))
    monkeypatch.setattr(onboarding.getpass, "getpass", lambda *a: "new-secret")

    def fail(*a):
        raise Pan123Error("TOKEN_UNAVAILABLE", "failed")

    monkeypatch.setattr(onboarding, "verify_credentials", fail)
    with pytest.raises(Pan123Error):
        onboarding.setup({})
    assert json.loads((tmp_path / "credentials.json").read_text()) == old


def test_noninteractive_setup_and_json_do_not_prompt(monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda *a: pytest.fail("prompted"))
    assert main(["setup", "--json"]) == 2
    assert "pan123 setup" in capsys.readouterr().out


@pytest.mark.parametrize(
    "agent,folder", [("codex", ".agents"), ("claude", ".claude"), ("cursor", ".cursor")]
)
def test_skill_install_conflict_and_uninstall(tmp_path, monkeypatch, agent, folder):
    from pan123_cli.skills import manage

    monkeypatch.chdir(tmp_path)
    options = {"agent": [agent], "scope": "project"}
    result = manage("install", options)
    dest = tmp_path / folder / "skills" / "pan123-cli"
    assert dest.joinpath("SKILL.md").is_file()
    assert result["results"][0]["status"] == "installed"
    assert manage("install", options)["results"][0]["status"] == "unchanged"
    dest.joinpath("SKILL.md").write_text("user changes")
    with pytest.raises(Pan123Error):
        manage("install", options)
    with pytest.raises(Pan123Error):
        manage("uninstall", options)
    manage("install", {**options, "force": True})
    assert list(dest.parent.glob("pan123-cli.backup-*"))
    manage("uninstall", options)
    assert not dest.exists()


def test_skill_failure_does_not_block_business_command(monkeypatch):
    from pan123_cli.onboarding import prepare

    monkeypatch.setattr("pan123_cli.onboarding.interactive", lambda _: True)
    monkeypatch.setattr(
        "pan123_cli.onboarding.load_settings",
        lambda _: __import__("pan123_cli.config", fromlist=["Settings"]).Settings(
            client_id="id", client_secret="secret"
        ),
    )
    monkeypatch.setattr(
        "pan123_cli.skills.status",
        lambda _: (_ for _ in ()).throw(Pan123Error("FILE_CONFLICT", "unsafe path")),
    )
    assert prepare({"command": ("user", "info")}) is None


def test_custom_dest_does_not_depend_on_detected_agents(tmp_path, monkeypatch):
    from pan123_cli.skills import manage

    monkeypatch.setattr("pan123_cli.skills.detected_agents", lambda: ["codex", "claude"])
    assert (
        manage("install", {"dest": str(tmp_path / "custom")})["results"][0]["status"] == "installed"
    )


def test_setup_success_saves_validated_pair_without_secret_output(tmp_path, monkeypatch, capsys):
    from pan123_cli import onboarding

    monkeypatch.setattr("pan123_cli.config.user_config_dir", lambda *a, **k: str(tmp_path))
    monkeypatch.setattr("builtins.input", lambda: "test-id")
    monkeypatch.setattr(onboarding.getpass, "getpass", lambda *a: "hidden-test-secret")
    seen = []
    monkeypatch.setattr(
        onboarding,
        "verify_credentials",
        lambda settings: seen.append((settings.client_id, settings.client_secret)),
    )
    result = onboarding.setup({})
    assert seen == [("test-id", "hidden-test-secret")]
    assert load_settings({}, {}).client_id == "test-id"
    assert result["configured"]
    assert "hidden-test-secret" not in str(result) + capsys.readouterr().out


def test_setup_blank_input_cancels_without_writing(tmp_path, monkeypatch):
    from pan123_cli import onboarding

    monkeypatch.setattr("pan123_cli.config.user_config_dir", lambda *a, **k: str(tmp_path))
    monkeypatch.setattr("builtins.input", lambda: "")
    with pytest.raises(Pan123Error, match="取消"):
        onboarding.setup({})
    assert not (tmp_path / "credentials.json").exists()


@pytest.mark.parametrize(
    "mode,client_id,secret,expected",
    [
        ("developer", None, None, True),
        ("developer", "partial", None, True),
        ("developer", "id", "secret", False),
        ("oauth", None, None, False),
    ],
)
def test_first_run_only_configures_missing_developer_credentials(
    tmp_path, monkeypatch, mode, client_id, secret, expected
):
    from pan123_cli import onboarding
    from pan123_cli.config import Settings

    monkeypatch.setattr("pan123_cli.config.user_config_dir", lambda *a, **k: str(tmp_path))
    monkeypatch.setattr(onboarding, "interactive", lambda _: True)
    monkeypatch.setattr(
        onboarding,
        "load_settings",
        lambda _: Settings(auth_mode=mode, client_id=client_id, client_secret=secret),
    )
    calls = []
    monkeypatch.setattr(onboarding, "setup", lambda _: calls.append("setup"))
    monkeypatch.setattr("pan123_cli.skills.status", lambda _: "managed")
    onboarding.prepare({"command": ("user", "info")})
    assert bool(calls) is expected


def test_help_version_never_initialize(monkeypatch):
    monkeypatch.setattr("pan123_cli.onboarding.prepare", lambda _: pytest.fail("initialized"))
    assert main(["--help"]) == 0
    assert main(["--version"]) == 0


def test_windows_private_writer_restricts_acl_before_replace(tmp_path, monkeypatch):
    from pan123_cli import cache

    calls = []
    monkeypatch.setattr(cache, "restrict_windows_acl", lambda path: calls.append(path.read_bytes()))
    cache.write_private_json(tmp_path / "private.json", {"secret": "protected"})
    assert calls and b"protected" in calls[0]


def test_bare_interactive_invocation_starts_setup(monkeypatch, capsys):
    from pan123_cli import onboarding

    monkeypatch.setattr(onboarding, "interactive", lambda _: True)
    seen = []
    monkeypatch.setattr(
        onboarding, "prepare", lambda opts: seen.append(opts["command"]) or {"configured": True}
    )
    assert main([]) == 0
    assert seen == [("setup",)]


def test_oauth_command_never_requests_developer_credentials(tmp_path, monkeypatch):
    from pan123_cli import onboarding
    from pan123_cli.config import Settings

    monkeypatch.setattr("pan123_cli.config.user_config_dir", lambda *a, **k: str(tmp_path))
    monkeypatch.setattr(onboarding, "interactive", lambda _: True)
    monkeypatch.setattr(onboarding, "load_settings", lambda _: Settings())
    monkeypatch.setattr(onboarding, "setup", lambda _: pytest.fail("developer setup for OAuth"))
    monkeypatch.setattr("pan123_cli.skills.status", lambda _: "managed")
    onboarding.prepare({"command": ("oauth", "authorize-url")})
