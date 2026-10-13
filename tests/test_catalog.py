"""Wire contract regressions independently sourced from bundled official pages."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from pan123_cli.catalog import ENDPOINTS, payload_for
from pan123_cli.errors import Pan123Error


def endpoint(*command):
    matches = [e for e in ENDPOINTS if e.command == command]
    assert len(matches) == 1, command
    return matches[0]


def test_all_72_official_routes_and_source_pages_are_covered():
    root = Path(__file__).parents[1] / "docs" / "api-source"
    expected = set()
    pages = set()
    for d in json.loads((root / "_manifest.json").read_text(encoding="utf-8"))["documents"]:
        text = (root / d["path"]).read_text(encoding="utf-8")
        for method, path in re.findall(
            r"API[：:].*?(GET|POST|PUT|DELETE).*?(/(?:api|upload)/[A-Za-z0-9_\\/\-]+)", text
        ):
            expected.add((method, path.replace("\\_", "_")))
            pages.add(d["path"])
    assert len(expected) == 72
    assert {(e.method, e.path) for e in ENDPOINTS if e.path.startswith("/")} == expected
    assert pages <= {p for e in ENDPOINTS for p in e.source_paths}
    assert len({e.command for e in ENDPOINTS}) == len(ENDPOINTS)


@pytest.mark.parametrize(
    "command,values,expected",
    [
        (("file", "info"), {"file_id": 7}, {"fileID": 7}),
        (("file", "download-url"), {"file_id": 7}, {"fileId": 7}),
        (
            ("file", "recover-to"),
            {"file_id": [7, 8], "parent_id": 0},
            {"fileIDs": [7, 8], "parentFileID": 0},
        ),
        (
            ("file", "rename"),
            {"file_id": 7, "name": "文档.txt"},
            {"fileId": 7, "fileName": "文档.txt"},
        ),
        (("file", "copy-progress"), {"task_id": 11}, {"taskId": 11}),
        (
            ("file", "move"),
            {"file_id": [7, 8], "parent_id": 0},
            {"fileIDs": [7, 8], "toParentFileID": 0},
        ),
        (
            ("share", "create"),
            {"name": "资料", "expire_days": 7, "file_id": [7, 8]},
            {"shareName": "资料", "shareExpire": 7, "fileIDList": "7,8"},
        ),
        (("directlink", "blacklist", "switch"), {"status": 2}, {"Status": 2}),
        (("directlink", "blacklist", "update"), {"ip": ["192.0.2.1"]}, {"IpList": ["192.0.2.1"]}),
        (
            ("image", "move"),
            {"file_id": ["oss-a"], "parent_id": "oss-dir"},
            {"fileIDs": ["oss-a"], "toParentFileID": "oss-dir"},
        ),
        (
            ("image", "source-copy"),
            {"file_id": ["123"], "parent_id": ""},
            {"fileIDs": ["123"], "toParentFileID": "", "sourceType": 1, "type": 1},
        ),
        (("transcode", "from-cloud"), {"file_id": [7, 8]}, [{"fileId": 7}, {"fileId": 8}]),
        (
            ("transcode", "delete"),
            {"file_id": 7, "trashed": 2},
            {"fileId": 7, "businessType": 2, "trashed": 2},
        ),
        (
            ("transcode", "segment-url"),
            {"file_id": 7, "resolution": "1080P", "type": 1},
            {"fileId": 7, "resolution": "1080P", "type": 1},
        ),
        (
            ("image", "upload-api", "create"),
            {"parent_id": "", "filename": "a.png", "etag": "a" * 32, "size": 1},
            {"parentFileID": "", "filename": "a.png", "etag": "a" * 32, "size": 1, "type": 1},
        ),
    ],
)
def test_exact_wire_shapes(command, values, expected):
    assert payload_for(endpoint(*command), values) == expected


def test_fixed_list_variants_do_not_leak_filters():
    assert payload_for(endpoint("transcode", "source-list"), {}) == {
        "parentFileId": 0,
        "limit": 100,
        "category": 2,
    }
    assert payload_for(endpoint("transcode", "folder-list"), {}) == {
        "parentFileId": 0,
        "limit": 100,
        "businessType": 2,
    }
    assert payload_for(endpoint("file", "list"), {}) == {"parentFileId": 0, "limit": 100}
    with pytest.raises(Pan123Error):
        payload_for(
            endpoint("transcode", "source-list"), {}, {"parentFileId": 0, "limit": 2, "category": 3}
        )


def test_special_parameter_locations_and_auth_are_exact():
    assert endpoint("file", "copy-progress").location == "json"
    assert endpoint("file", "copy-progress").method == "GET"
    assert endpoint("file", "safebox-unlock").location == "query"
    assert endpoint("directlink", "offline-logs").location == "query"
    assert endpoint("image", "info").location == "query"
    assert endpoint("file", "upload-api", "v2", "slice").location == "multipart"
    assert endpoint("file", "upload-api", "v2", "slice").special == "upload-slice"
    assert endpoint("transcode", "list").auth_mode == "oauth"
    assert endpoint("oauth", "exchange").location == "query"
    assert endpoint("oauth", "exchange").special == "oauth-exchange"
    assert endpoint("file", "upload-api", "v1", "put").special == "upload-put"
    assert not endpoint("file", "upload-api", "v1", "put").path.startswith("/")


@pytest.mark.parametrize(
    "command,data",
    [
        (("file", "recover-to"), {"fileIDs": [1], "parentFileID": 0, "extra": True}),
        (("file", "infos"), {"fileIDs": [1]}),
        (("transcode", "from-cloud"), [{"fileId": 1, "extra": 2}]),
        (("transcode", "from-cloud"), {"fileId": [1]}),
        (("transcode", "from-cloud"), [{"fileId": True}]),
        (("transcode", "from-cloud"), [{"fileId": 1.5}]),
        (("file", "rename-batch"), {"renameList": ["abc|name"]}),
        (("file", "rename-batch"), {"renameList": ["1|folder/name"]}),
        (("file", "rename-batch"), {"renameList": ["1|name", "1|other"]}),
        (("directlink", "blacklist", "update"), {"IpList": ["2001:db8::1"]}),
        (("directlink", "blacklist", "update"), {"IpList": ["192.0.2.0/24"]}),
        (("share", "create"), {"shareName": "a", "shareExpire": 2, "fileIDList": "1"}),
        (("share", "create"), {"shareName": "a", "shareExpire": 7, "fileIDList": [1]}),
        (("file", "trash"), {"fileIDs": [True]}),
        (("file", "trash"), {"fileIDs": [1.0]}),
        (("file", "trash"), {"fileIDs": []}),
        (("file", "trash"), {"fileIDs": list(range(1, 102))}),
        (("image", "move"), {"fileIDs": ["x"], "toParentFileID": ""}),
        (("transcode", "delete"), {"fileId": 1, "businessType": 1, "trashed": 1}),
        (("share", "payment", "create"), {"shareName": "a", "fileIDList": "1", "payAmount": 0}),
        (("transcode", "segment-url"), {"fileId": 1, "resolution": "1080P", "type": 2}),
        (
            ("transcode", "run"),
            {"fileId": 1, "codecName": "H.264", "videoTime": 10, "resolutions": "1080p"},
        ),
        (
            ("directlink", "traffic-logs"),
            {
                "pageNum": 1,
                "pageSize": 2,
                "startTime": "2026-10-14 10:00:00",
                "endTime": "2026-10-13 00:00:00",
            },
        ),
    ],
)
def test_invalid_requests_fail_before_http(command, data):
    with pytest.raises(Pan123Error):
        payload_for(endpoint(*command), {}, data)


def test_nested_input_preserved_and_limited():
    data = [{"fileId": 1}, {"fileId": 2}]
    assert payload_for(endpoint("transcode", "from-cloud"), {}, data) == data
    with pytest.raises(Pan123Error):
        payload_for(endpoint("transcode", "from-cloud"), {}, [{"fileId": i} for i in range(1, 102)])


def test_sensitive_inputs_have_no_argv_value_option():
    cases = [
        (("file", "safebox-unlock"), "password"),
        (("auth", "ensure"), "clientSecret"),
        (("oauth", "exchange"), "client_secret"),
        (("oauth", "exchange"), "code"),
        (("oauth", "refresh"), "refresh_token"),
        (("share", "create"), "sharePwd"),
        (("file", "upload-api", "v2", "slice"), "preuploadID"),
    ]
    for cmd, wire in cases:
        assert next(f for f in endpoint(*cmd).fields if f.wire == wire).flag is None


def test_request_file_exclusivity_and_casing():
    ep = endpoint("file", "info")
    assert payload_for(ep, {}, {"fileID": 7}) == {"fileID": 7}
    with pytest.raises(Pan123Error):
        payload_for(ep, {"file_id": 8}, {"fileID": 7})
    with pytest.raises(Pan123Error):
        payload_for(ep, {}, {"fileId": 7})


def test_optional_false_is_preserved_none_omitted():
    ep = endpoint("file", "upload-api", "v2", "create")
    base = {"parent_id": 0, "filename": "a", "etag": "a" * 32, "size": 1}
    assert "containDir" not in payload_for(ep, {**base, "contain_dir": None})
    assert payload_for(ep, {**base, "contain_dir": False})["containDir"] is False


def test_update_requires_change_and_omits_unselected_fields():
    ep = endpoint("share", "update")
    with pytest.raises(Pan123Error):
        payload_for(ep, {"share_id": [1]})
    assert payload_for(ep, {"share_id": [1], "traffic_switch": 2}) == {
        "shareIdList": [1],
        "trafficSwitch": 2,
    }


def test_extreme_video_time_is_reported_as_validation_error():
    with pytest.raises(Pan123Error):
        payload_for(
            endpoint("transcode", "run"),
            {},
            {"fileId": 1, "codecName": "H.264", "videoTime": 10**400, "resolutions": "1080P"},
        )
