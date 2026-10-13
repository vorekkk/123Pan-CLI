"""Exact cursor pagination for cloud, OSS and transcode spaces."""

from __future__ import annotations

from typing import Any

from pan123_cli.errors import Pan123Error


def list_files(
    client: Any,
    *,
    parent_id: int | str = 0,
    limit: int = 100,
    cursor: int | str | None = None,
    search: str | None = None,
    all_pages: bool = False,
    include_trashed: bool = False,
    api_version: str = "v2",
    **extra: Any,
) -> dict[str, Any]:
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
        raise Pan123Error("INVALID_INPUT", "List limit must be between 1 and 100.", exit_code=2)
    business = extra.pop("business", "file")
    if business not in {"file", "image", "transcode", "transcode-source"}:
        raise Pan123Error("INVALID_INPUT", "Unknown listing business.", exit_code=2)
    if api_version not in {"v1", "v2"}:
        raise Pan123Error("INVALID_INPUT", "List API version must be v1 or v2.", exit_code=2)
    oss = business == "image"
    if oss:
        if parent_id == 0:
            parent_id = ""
        if not isinstance(parent_id, str):
            raise Pan123Error("INVALID_INPUT", "OSS directory IDs are strings.", exit_code=2)
    elif isinstance(parent_id, bool) or not isinstance(parent_id, int) or parent_id < 0:
        raise Pan123Error(
            "INVALID_INPUT", "Directory ID must be a nonnegative integer.", exit_code=2
        )
    if cursor is not None:
        if oss:
            valid_cursor = isinstance(cursor, str) and bool(cursor) and cursor != "-1"
        else:
            valid_cursor = type(cursor) is int and isinstance(cursor, int) and cursor >= 0
        if not valid_cursor:
            raise Pan123Error(
                "INVALID_INPUT", "The starting cursor has the wrong type.", exit_code=2
            )
    if api_version == "v1" and not oss:
        if all_pages or cursor is not None:
            raise Pan123Error(
                "INVALID_INPUT",
                "Legacy v1 listing supports one page, not v2 cursor traversal.",
                exit_code=2,
            )
        params: dict[str, Any] = {
            "parentFileId": parent_id,
            "limit": limit,
            "page": extra.get("page", 1),
            "orderBy": extra.get("order_by", "file_id"),
            "orderDirection": extra.get("order_direction", "asc"),
        }
        if search is not None:
            params["searchData"] = search
        if extra.get("trashed") is not None:
            params["trashed"] = extra["trashed"]
        data = client.request("GET", "/api/v1/file/list", params=params, retryable=True)
        if not isinstance(data, dict) or not isinstance(data.get("fileList"), list):
            raise Pan123Error("PROTOCOL_ERROR", "Legacy list returned invalid fileList.")
        return {
            "items": data["fileList"],
            "next_cursor": None,
            "pages_fetched": 1,
            "complete": False,
            "page": params["page"],
            "total": data.get("total"),
        }
    params = {"parentFileId": parent_id, "limit": limit}
    if search is not None:
        params["searchData"] = search
    if oss:
        params["type"] = 1
        for field, option in (("startTime", "start_time"), ("endTime", "end_time")):
            if extra.get(option) is not None:
                params[field] = extra[option]
    elif business == "transcode":
        params["businessType"] = 2
    elif business == "transcode-source":
        params["category"] = 2
    if not oss and extra.get("search_mode") is not None:
        params["searchMode"] = extra["search_mode"]
    terminal: int | str = "-1" if oss else -1
    seen: set[int | str] = {cursor} if cursor is not None else set()
    items: list[Any] = []
    pages = 0
    current = cursor
    last_success = cursor
    try:
        while pages < 10_000:
            request_params = dict(params)
            if current is not None:
                request_params["lastFileId"] = current
            data = client.request(
                "POST" if oss else "GET",
                "/api/v1/oss/file/list" if oss else "/api/v2/file/list",
                json=request_params if oss else None,
                params=None if oss else request_params,
                retryable=True,
            )
            if not isinstance(data, dict) or not isinstance(data.get("fileList"), list):
                raise Pan123Error("PROTOCOL_ERROR", "List response is missing a valid fileList.")
            next_cursor = data.get("lastFileId")
            valid_next = (
                (isinstance(next_cursor, str) and bool(next_cursor))
                if oss
                else (
                    type(next_cursor) is int and isinstance(next_cursor, int) and next_cursor >= -1
                )
            )
            if not valid_next:
                raise Pan123Error("PROTOCOL_ERROR", "List response has an invalid lastFileId.")
            assert isinstance(next_cursor, (int, str))
            for row in data["fileList"]:
                _validate_row(row, oss=oss, require_trashed=business in {"file", "transcode"})
                if include_trashed or row.get("trashed", 0) == 0:
                    items.append(row)
            pages += 1
            last_success = next_cursor
            if next_cursor == terminal or not all_pages:
                return {
                    "items": items,
                    "next_cursor": next_cursor,
                    "pages_fetched": pages,
                    "complete": next_cursor == terminal,
                }
            if next_cursor in seen:
                raise Pan123Error("PROTOCOL_ERROR", "List returned a repeated pagination cursor.")
            seen.add(next_cursor)
            current = next_cursor
        raise Pan123Error("PROTOCOL_ERROR", "List exceeded the local 10000-page safety limit.")
    except Pan123Error as error:
        error.details = {
            **(error.details or {}),
            "partial": bool(pages),
            "items": items,
            "pages_fetched": pages,
            "last_success_cursor": last_success,
            "failed_page_cursor": current,
        }
        raise


def _validate_row(row: Any, *, oss: bool, require_trashed: bool) -> None:
    if not isinstance(row, dict):
        raise Pan123Error("PROTOCOL_ERROR", "The list contains a non-object file record.")
    id_type = str if oss else int
    for key in ("fileId", "parentFileId"):
        value = row.get(key)
        if type(value) is not id_type or (key == "fileId" and not value):
            raise Pan123Error("PROTOCOL_ERROR", "A list record has an invalid file or parent ID.")
    for key in ("type", "size", "status"):
        if type(row.get(key)) is not int or row[key] < 0:
            raise Pan123Error("PROTOCOL_ERROR", f"A list record has an invalid {key}.")
    if (
        row["type"] not in {0, 1}
        or not isinstance(row.get("filename"), str)
        or not isinstance(row.get("etag"), str)
    ):
        raise Pan123Error("PROTOCOL_ERROR", "A list record has invalid file metadata.")
    if require_trashed or "trashed" in row:
        if type(row.get("trashed")) is not int or row["trashed"] not in {0, 1}:
            raise Pan123Error("PROTOCOL_ERROR", "A list record has an invalid trashed state.")
    if not oss and type(row.get("category")) is not int:
        raise Pan123Error("PROTOCOL_ERROR", "A list record has an invalid category.")
