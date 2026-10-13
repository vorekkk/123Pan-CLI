"""Behavioral pagination fixtures copied from the public list contracts."""

from types import SimpleNamespace

import pytest


class PageClient:
    def __init__(self, pages):
        self.pages = iter(pages)
        self.requests = []
        self.settings = SimpleNamespace(cache_dir=None)

    def request(self, method, path, *, params=None, json=None, **kwargs):
        self.requests.append((method, path, params, json))
        return next(self.pages)


def item(file_id, trashed=0):
    return {
        "fileId": file_id,
        "filename": f"file-{file_id}",
        "type": 0,
        "size": 3,
        "etag": "900150983cd24fb0d6963f7d28e17f72",
        "status": 0,
        "parentFileId": 0,
        "category": 0,
        "trashed": trashed,
    }


def test_list_continues_after_a_page_filtered_to_empty():
    from pan123_cli.services.listing import list_files

    client = PageClient(
        [
            {"lastFileId": 17, "fileList": [item(17, 1)]},
            {"lastFileId": -1, "fileList": [item(19)]},
        ]
    )
    result = list_files(client, all_pages=True, search="季度报告")
    assert [row["fileId"] for row in result["items"]] == [19]
    assert result["complete"] is True
    assert result["pages_fetched"] == 2
    assert "lastFileId" not in client.requests[0][2]
    assert client.requests[1][2]["lastFileId"] == 17
    assert client.requests[0][2]["searchData"] == "季度报告"


def test_list_single_page_preserves_cursor_and_trashed_option():
    from pan123_cli.services.listing import list_files

    client = PageClient([{"lastFileId": 23, "fileList": [item(23, 1)]}])
    result = list_files(client, include_trashed=True)
    assert len(result["items"]) == 1
    assert result["next_cursor"] == 23
    assert result["complete"] is False


def test_list_repeated_cursor_reports_partial_items_instead_of_success():
    from pan123_cli.errors import Pan123Error
    from pan123_cli.services.listing import list_files

    client = PageClient(
        [
            {"lastFileId": 17, "fileList": [item(11)]},
            {"lastFileId": 17, "fileList": [item(12)]},
        ]
    )
    with pytest.raises(Pan123Error) as caught:
        list_files(client, all_pages=True)
    assert caught.value.details["partial"] is True
    assert caught.value.details["pages_fetched"] == 2


def test_image_list_uses_string_cursor_and_post_json():
    from pan123_cli.services.listing import list_files

    first = dict(item("oss-1"), parentFileId="")
    second = dict(item("oss-2"), parentFileId="")
    client = PageClient(
        [
            {"lastFileId": "oss-1", "fileList": [first]},
            {"lastFileId": "-1", "fileList": [second]},
        ]
    )
    result = list_files(client, parent_id="", business="image", all_pages=True)
    assert len(result["items"]) == 2
    assert client.requests[0][0:2] == ("POST", "/api/v1/oss/file/list")
    assert client.requests[1][3]["lastFileId"] == "oss-1"
    assert client.requests[0][3]["type"] == 1


def test_list_does_not_accept_boolean_or_missing_file_metadata():
    from pan123_cli.errors import Pan123Error
    from pan123_cli.services.listing import list_files

    malformed = item(True)
    malformed.pop("size")
    with pytest.raises(Pan123Error) as caught:
        list_files(PageClient([{"lastFileId": -1, "fileList": [malformed]}]))
    assert caught.value.exit_code == 7


def test_v1_list_sends_page_sort_and_bool_trashed_without_cursor():
    from pan123_cli.services.listing import list_files

    row = dict(item(17), fileID=17)
    client = PageClient([{"fileList": [row], "total": 1}])
    result = list_files(
        client, api_version="v1", page=2, order_by="size", order_direction="desc", trashed=True
    )
    assert result["items"] == [row]
    assert client.requests[0][2] == {
        "parentFileId": 0,
        "limit": 100,
        "page": 2,
        "orderBy": "size",
        "orderDirection": "desc",
        "trashed": True,
    }
