"""Validation for temporary external HTTPS upload and download targets."""

from __future__ import annotations

import ipaddress
import re
import socket
from urllib.parse import urlsplit

from ..errors import Pan123Error


def _public_address(address: str) -> bool:
    try:
        parsed = ipaddress.ip_address(address)
    except ValueError:
        return False
    if isinstance(parsed, ipaddress.IPv6Address) and parsed.ipv4_mapped is not None:
        return parsed.ipv4_mapped.is_global
    return parsed.is_global


def validate_external_url(url: str, *, resolve: bool = False) -> str:
    """Reject unsafe URL syntax and optionally every nonpublic DNS answer."""
    error = Pan123Error(
        "protocol", "The external target must be a public HTTPS URL without embedded credentials."
    )
    if (
        not isinstance(url, str)
        or any(ord(character) <= 32 or ord(character) == 127 for character in url)
        or "\\" in url
    ):
        raise error
    try:
        parts = urlsplit(url)
        host = parts.hostname
        port = parts.port
        if (
            parts.scheme.lower() != "https"
            or not host
            or parts.username is not None
            or parts.password is not None
        ):
            raise error
        if "%" in host or (port is not None and not 1 <= port <= 65535):
            raise error
        hostname = host.rstrip(".").lower()
        if hostname == "localhost" or hostname.endswith((".localhost", ".local", ".internal")):
            raise error
        try:
            address = ipaddress.ip_address(hostname)
        except ValueError:
            if re.fullmatch(
                r"(?:0[xX][0-9a-fA-F]+|[0-9]+)(?:\.(?:0[xX][0-9a-fA-F]+|[0-9]+))*", hostname
            ):
                raise error from None
            hostname = hostname.encode("idna").decode("ascii")
            labels = hostname.split(".")
            if (
                len(labels) < 2
                or len(hostname) > 253
                or any(
                    not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", label)
                    for label in labels
                )
            ):
                raise error from None
        else:
            if not _public_address(str(address)):
                raise error
        if resolve:
            try:
                answers = socket.getaddrinfo(hostname, port or 443, type=socket.SOCK_STREAM)
            except OSError:
                raise Pan123Error(
                    "network", "The external target hostname could not be resolved."
                ) from None
            if not answers or any(not _public_address(str(answer[4][0])) for answer in answers):
                raise error
    except (ValueError, UnicodeError):
        raise error from None
    return url
