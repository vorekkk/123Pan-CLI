"""Official normal/paid share cursor and secret-output behavior."""

from __future__ import annotations

import copy

import pytest

from pan123_cli.errors import Pan123Error
from pan123_cli.services.sharing import list_shares


class RecordingClient:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    def request(self, method, path, **kwargs):
        self.calls.append((method, path, kwargs))
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        return response


def test_single_page_normal_shares_preserves_stats_but_redacts_password_everywhere():
    raw = {
        "lastShareId": 20,
        "shareList": [
            {
                "shareId": 10,
                "shareKey": "key",
                "shareName": "资料",
                "sharePwd": "1234",
                "trafficLimit": 100,
                "downloadCount": 3,
                "extra": {"sharePwd": "secret", "nested": [{"sharePwd": "more"}]},
            }
        ],
    }
    original = copy.deepcopy(raw)
    client = RecordingClient([raw])
    result = list_shares(client, {"limit": 10, "lastShareId": 0})
    assert client.calls == [
        (
            "GET",
            "/api/v1/share/list",
            {"params": {"limit": 10, "lastShareId": 0}, "retryable": True},
        )
    ]
    assert result == {
        "items": [
            {
                "shareId": 10,
                "shareKey": "key",
                "shareName": "资料",
                "sharePwd": "[redacted]",
                "trafficLimit": 100,
                "downloadCount": 3,
                "extra": {"sharePwd": "[redacted]", "nested": [{"sharePwd": "[redacted]"}]},
            }
        ],
        "next_cursor": 20,
        "pages_fetched": 1,
        "complete": False,
    }
    assert raw == original


def test_paid_shares_empty_page_does_not_end_before_terminal_cursor():
    client = RecordingClient(
        [
            {"lastShareId": 5, "shareList": []},
            {
                "lastShareId": -1,
                "shareList": [{"shareId": 6, "payAmount": 1, "amount": 3, "orderCnt": 3}],
            },
        ]
    )
    result = list_shares(client, {"limit": 100}, paid=True, all_pages=True)
    assert result == {
        "items": [{"shareId": 6, "payAmount": 1, "amount": 3, "orderCnt": 3}],
        "next_cursor": -1,
        "pages_fetched": 2,
        "complete": True,
    }
    assert [call[1] for call in client.calls] == ["/api/v1/share/payment/list"] * 2
    assert client.calls[1][2]["params"] == {"limit": 100, "lastShareId": 5}


def test_start_cursor_passed_exactly_and_input_unchanged():
    payload = {"limit": 2, "lastShareId": 15}
    client = RecordingClient([{"lastShareId": -1, "shareList": []}])
    assert list_shares(client, payload)["complete"] is True
    assert client.calls[0][2]["params"] == payload
    assert payload == {"limit": 2, "lastShareId": 15}


def test_repeated_cursor_is_bounded_and_partial_rows_are_safe():
    client = RecordingClient(
        [
            {"lastShareId": 5, "shareList": [{"shareId": 1, "sharePwd": "hidden"}]},
            {"lastShareId": 5, "shareList": [{"shareId": 2, "sharePwd": "also-hidden"}]},
        ]
    )
    with pytest.raises(Pan123Error) as caught:
        list_shares(client, {"limit": 2}, all_pages=True)
    assert len(client.calls) == 2
    assert caught.value.kind == "PROTOCOL_ERROR"
    assert caught.value.details["pages_fetched"] == 2
    assert caught.value.details["last_success_cursor"] == 5
    assert [row["sharePwd"] for row in caught.value.details["items"]] == ["[redacted]"] * 2


def test_failure_after_page_preserves_cursor_rows_and_underlying_error():
    error = Pan123Error("UPSTREAM_ERROR", "failed", api_code=429, details={"sharePwd": "hidden"})
    client = RecordingClient(
        [{"lastShareId": 8, "shareList": [{"shareId": 1, "sharePwd": "hidden"}]}, error]
    )
    with pytest.raises(Pan123Error) as caught:
        list_shares(client, {"limit": 2}, all_pages=True)
    assert caught.value is error
    assert error.api_code == 429
    assert error.details == {
        "sharePwd": "[redacted]",
        "partial": True,
        "items": [{"shareId": 1, "sharePwd": "[redacted]"}],
        "pages_fetched": 1,
        "last_success_cursor": 8,
        "failed_page_cursor": 8,
    }


@pytest.mark.parametrize(
    "response",
    [
        None,
        [],
        {},
        {"lastShareId": -1},
        {"lastShareId": -1, "shareList": None},
        {"lastShareId": True, "shareList": []},
        {"lastShareId": "-1", "shareList": []},
        {"lastShareId": -2, "shareList": []},
        {"lastShareId": -1, "shareList": [None]},
        {"lastShareId": -1, "shareList": [{"shareId": True}]},
        {"lastShareId": -1, "shareList": [{"shareId": "1"}]},
        {"lastShareId": -1, "shareList": [{"shareId": 0}]},
    ],
)
def test_malformed_share_responses_do_not_silently_succeed(response):
    client = RecordingClient([response])
    with pytest.raises(Pan123Error) as caught:
        list_shares(client, {"limit": 1})
    assert caught.value.kind == "PROTOCOL_ERROR"


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"limit": True},
        {"limit": 0},
        {"limit": 101},
        {"limit": 1.5},
        {"limit": 1, "lastShareId": True},
        {"limit": 1, "lastShareId": -1},
        {"limit": 1, "lastShareId": "2"},
        {"limit": 1, "unknown": 2},
    ],
)
def test_invalid_share_request_is_rejected_before_any_http(payload):
    client = RecordingClient([])
    with pytest.raises(Pan123Error):
        list_shares(client, payload)
    assert client.calls == []


def test_success_redaction_preserves_nonsecret_source_strings():
    client = RecordingClient(
        [
            {
                "lastShareId": -1,
                "shareList": [
                    {
                        "shareId": 1,
                        "shareName": "https://example.com/?label=report",
                        "shareKey": "safe-key",
                        "sharePwd": "secret",
                    }
                ],
            }
        ]
    )
    item = list_shares(client, {"limit": 1})["items"][0]
    assert item["shareName"] == "https://example.com/?label=report"
    assert item["shareKey"] == "safe-key"
    assert item["sharePwd"] == "[redacted]"
