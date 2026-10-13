import json
import math
import os

import pytest

from pan123_cli.cache import read_private_json, write_private_json
from pan123_cli.config import Settings, load_settings
from pan123_cli.errors import Pan123Error


def test_config_precedence_and_explicit_env_file(tmp_path):
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"schema_version": 1, "client_id": "file-id", "api_timeout": 12}))
    env_file = tmp_path / "chosen.env"
    env_file.write_text(
        "PAN123_CLIENT_ID=env-file-id\nPAN123_API_TIMEOUT=15\nOTHER_SECRET=ignore\n"
    )
    settings = load_settings(
        {
            "config": config,
            "env_file": env_file,
            "api_timeout": 20,
            "cache_dir": tmp_path / "cache",
        },
        environ={"PAN123_CLIENT_ID": "process-id", "PAN123_CLIENT_SECRET": "secret"},
    )
    assert settings.client_id == "process-id"
    assert settings.client_secret == "secret"
    assert settings.api_timeout == 20
    assert not settings.cache_dir.exists()
    assert "secret" not in repr(settings)


def test_config_does_not_implicitly_read_dotenv_or_create_directories(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".env").write_text(
        "PAN123_CLIENT_ID=accidental-id\nPAN123_CLIENT_SECRET=accidental-secret\n"
    )
    cache = tmp_path / "not-created"
    settings = load_settings({"cache_dir": cache}, environ={})
    assert not settings.client_id
    assert not settings.client_secret
    assert not cache.exists()


@pytest.mark.parametrize("source", ["process", "explicit-file"])
def test_developer_credential_aliases_are_loaded_from_each_environment_source(tmp_path, source):
    aliases = {"CLIENT_ID": "alias-id", "CLIENT_SECRET": "alias-secret"}
    options = {"cache_dir": tmp_path / "cache"}
    environ = aliases if source == "process" else {}
    if source == "explicit-file":
        env_file = tmp_path / "chosen.env"
        env_file.write_text("CLIENT_ID=alias-id\nCLIENT_SECRET=alias-secret\n")
        options["env_file"] = env_file
    settings = load_settings(options, environ=environ)
    assert settings.client_id == "alias-id"
    assert settings.client_secret == "alias-secret"
    assert "alias-secret" not in repr(settings)
    assert not settings.cache_dir.exists()


@pytest.mark.parametrize("source", ["process", "explicit-file"])
def test_canonical_names_take_priority_over_aliases_within_each_source(tmp_path, source):
    values = {
        "CLIENT_ID": "alias-id",
        "CLIENT_SECRET": "alias-secret",
        "PAN123_CLIENT_ID": "canonical-id",
        "PAN123_CLIENT_SECRET": "canonical-secret",
    }
    options = {"cache_dir": tmp_path / "cache"}
    environ = values if source == "process" else {}
    if source == "explicit-file":
        env_file = tmp_path / "chosen.env"
        env_file.write_text("\n".join(f"{key}={value}" for key, value in values.items()))
        options["env_file"] = env_file
    settings = load_settings(options, environ=environ)
    assert settings.client_id == "canonical-id"
    assert settings.client_secret == "canonical-secret"


@pytest.mark.parametrize("source", ["process", "explicit-file"])
def test_empty_canonical_credential_does_not_fall_back_to_valid_alias(tmp_path, source):
    values = {"CLIENT_ID": "alias-id", "CLIENT_SECRET": "alias-secret", "PAN123_CLIENT_SECRET": ""}
    options = {"cache_dir": tmp_path / "cache"}
    environ = values if source == "process" else {}
    if source == "explicit-file":
        env_file = tmp_path / "chosen.env"
        env_file.write_text("\n".join(f"{key}={value}" for key, value in values.items()))
        options["env_file"] = env_file
    with pytest.raises(Pan123Error) as caught:
        load_settings(options, environ=environ)
    assert caught.value.exit_code == 2


def test_process_alias_overrides_file_canonical_but_options_override_process_alias(tmp_path):
    env_file = tmp_path / "chosen.env"
    env_file.write_text("PAN123_CLIENT_ID=file-id\nPAN123_CLIENT_SECRET=file-secret\n")
    settings = load_settings(
        {"env_file": env_file, "client_id": "option-id", "cache_dir": tmp_path / "cache"},
        environ={"CLIENT_ID": "process-id", "CLIENT_SECRET": "process-secret"},
    )
    assert settings.client_id == "option-id"
    assert settings.client_secret == "process-secret"


def test_fake_ip_setting_defaults_to_rejection(tmp_path):
    settings = load_settings({"cache_dir": tmp_path / "cache"}, environ={})
    assert settings.allow_fake_ip is False


@pytest.mark.parametrize(
    "value,want", [("true", True), ("false", False), ("1", True), ("0", False)]
)
def test_fake_ip_setting_accepts_only_declared_environment_boolean_forms(tmp_path, value, want):
    settings = load_settings(
        {"cache_dir": tmp_path / "cache"}, environ={"PAN123_ALLOW_FAKE_IP": value}
    )
    assert settings.allow_fake_ip is want


def test_fake_ip_setting_json_environment_and_option_precedence(tmp_path):
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"schema_version": 1, "allow_fake_ip": True}))
    options = {"config": config, "cache_dir": tmp_path / "cache"}
    assert load_settings(options, environ={}).allow_fake_ip is True
    assert load_settings(options, environ={"PAN123_ALLOW_FAKE_IP": "false"}).allow_fake_ip is False
    assert (
        load_settings(
            {**options, "allow_fake_ip": True}, environ={"PAN123_ALLOW_FAKE_IP": "false"}
        ).allow_fake_ip
        is True
    )
    assert (
        load_settings(
            {**options, "allow_fake_ip": False}, environ={"PAN123_ALLOW_FAKE_IP": "true"}
        ).allow_fake_ip
        is False
    )


def test_fake_ip_setting_can_be_enabled_only_by_explicit_env_file(tmp_path):
    env_file = tmp_path / "selected.env"
    env_file.write_text("PAN123_ALLOW_FAKE_IP=true\n")
    settings = load_settings({"env_file": env_file, "cache_dir": tmp_path / "cache"}, environ={})
    assert settings.allow_fake_ip is True


@pytest.mark.parametrize("value", ["yes", "no", "", "2", "maybe", "true trailing"])
def test_fake_ip_setting_rejects_invalid_environment_values(tmp_path, value):
    with pytest.raises(Pan123Error) as caught:
        load_settings({"cache_dir": tmp_path / "cache"}, environ={"PAN123_ALLOW_FAKE_IP": value})
    assert caught.value.exit_code == 2
    assert not (tmp_path / "cache").exists()


@pytest.mark.parametrize("value", [1, 0, None, [], {}])
def test_fake_ip_setting_json_requires_a_boolean(tmp_path, value):
    config = tmp_path / "config.json"
    config.write_text(json.dumps({"allow_fake_ip": value}))
    with pytest.raises(Pan123Error) as caught:
        load_settings({"config": config, "cache_dir": tmp_path / "cache"}, environ={})
    assert caught.value.exit_code == 2


@pytest.mark.parametrize(
    "data",
    [
        {"unknown": 1},
        {"client_secret": "secret"},
        {"oauth_client_secret": "secret"},
        {"schema_version": 2},
    ],
)
def test_config_rejects_unknown_schema_and_secret_storage(tmp_path, data):
    path = tmp_path / "config.json"
    path.write_text(json.dumps(data))
    with pytest.raises(Pan123Error) as caught:
        load_settings({"config": path}, environ={})
    assert caught.value.exit_code == 2
    assert "secret" not in json.dumps(caught.value.as_dict())


@pytest.mark.parametrize(
    "overrides",
    [
        {"api_timeout": 0},
        {"api_timeout": math.nan},
        {"transfer_timeout": math.inf},
        {"read_max_retries": -1},
        {"read_max_retries": True},
        {"token_refresh_skew_seconds": "1.5"},
        {"auth_mode": "gateway"},
        {"client_id": ""},
        {"client_secret": "   "},
    ],
)
def test_invalid_settings_fail_without_cache_side_effects(tmp_path, overrides):
    with pytest.raises(Pan123Error) as caught:
        load_settings({"cache_dir": tmp_path / "cache", **overrides}, environ={})
    assert caught.value.exit_code == 2
    assert not (tmp_path / "cache").exists()


def test_missing_explicit_files_fail_but_missing_default_config_is_allowed(tmp_path):
    with pytest.raises(Pan123Error):
        load_settings({"config": tmp_path / "missing.json"}, environ={})
    with pytest.raises(Pan123Error):
        load_settings({"env_file": tmp_path / "missing.env"}, environ={})


def test_fingerprint_separates_accounts_secrets_and_auth_modes(tmp_path):
    first = Settings(client_id="same", client_secret="one", cache_dir=tmp_path)
    changed = Settings(client_id="same", client_secret="two", cache_dir=tmp_path)
    oauth = Settings(
        auth_mode="oauth", oauth_client_id="same", oauth_client_secret="one", cache_dir=tmp_path
    )
    assert len(first.fingerprint) == 64
    assert len({first.fingerprint, changed.fingerprint, oauth.fingerprint}) == 3
    assert "one" not in first.fingerprint


def test_private_json_atomic_write_and_private_mode(tmp_path):
    path = tmp_path / "private" / "token.json"
    write_private_json(path, {"access_token": "first"})
    write_private_json(path, {"access_token": "second"})
    assert read_private_json(path) == {"access_token": "second"}
    assert not list(path.parent.glob("*.tmp"))
    if os.name == "posix":
        assert path.stat().st_mode & 0o777 == 0o600
        assert path.parent.stat().st_mode & 0o777 == 0o700


def test_private_json_refuses_symlinks_and_preserves_other_file(tmp_path):
    victim = tmp_path / "victim.json"
    victim.write_text('{"safe": true}')
    link = tmp_path / "link.json"
    link.symlink_to(victim)
    with pytest.raises(Pan123Error):
        write_private_json(link, {"safe": False})
    with pytest.raises(Pan123Error):
        read_private_json(link)
    assert json.loads(victim.read_text()) == {"safe": True}


def test_error_redacts_nested_credentials_and_signed_urls():
    error = Pan123Error(
        "auth",
        "Failed https://open-api.123pan.com/token?client_secret=topsecret&code=privatecode Bearer tokenvalue",
        details={
            "refresh_token": "private-refresh",
            "nested": {"downloadUrl": "https://cdn.example/file?sign=signed-value"},
        },
    )
    output = json.dumps(error.as_dict()) + str(error)
    for sensitive in ("topsecret", "privatecode", "tokenvalue", "private-refresh", "signed-value"):
        assert sensitive not in output
    assert error.exit_code == 3
