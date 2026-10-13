import socket

import pytest

from pan123_cli.errors import Pan123Error
from pan123_cli.utils.urls import validate_external_url


@pytest.mark.parametrize(
    "url",
    [
        "http://cdn.example/file",
        "https://user:password@cdn.example/file",
        "https://127.0.0.1/a",
        "https://[::1]/a",
        "https://192.168.1.5/a",
        "https://169.254.169.254/a",
        "https://0.0.0.0/a",
        "https://localhost/a",
        "https://localhost./a",
        "https://[::ffff:127.0.0.1]/a",
        "https://cdn.example:bad/a",
        "https://cdn.example/a\nHeader: bad",
        "https://2130706433/a",
        "https://127.1/a",
        "https://0x7f000001/a",
        "https://cdn.example\\@127.0.0.1/a",
    ],
)
def test_unsafe_urls_are_rejected_without_network(url):
    with pytest.raises(Pan123Error):
        validate_external_url(url)


def test_https_signed_url_is_preserved_and_resolution_is_optional(monkeypatch):
    def unexpected(*args, **kwargs):
        raise AssertionError("DNS must not run in pure validation")

    monkeypatch.setattr(socket, "getaddrinfo", unexpected)
    assert (
        validate_external_url("https://cdn.example/file?sign=opaque")
        == "https://cdn.example/file?sign=opaque"
    )


def test_dns_validation_rejects_mixed_public_private_answers(monkeypatch):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs: [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 443)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.1", 443)),
        ],
    )
    with pytest.raises(Pan123Error):
        validate_external_url("https://cdn.example/file?secret=redact", resolve=True)


def test_dns_resolution_failures_are_safe_errors(monkeypatch):
    def failed(*args, **kwargs):
        raise socket.gaierror("secret internal resolver detail")

    monkeypatch.setattr(socket, "getaddrinfo", failed)
    with pytest.raises(Pan123Error) as caught:
        validate_external_url("https://cdn.example/file?signature=private", resolve=True)
    assert "private" not in str(caught.value)
    assert "internal resolver" not in str(caught.value)
