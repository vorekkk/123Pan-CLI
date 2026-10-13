"""Normal and paid share listings with exact numeric cursors and safe output."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pan123_cli.errors import Pan123Error, redact_sensitive


def _share_output(value: Any) -> Any:
    """Mask extraction passwords recursively without rewriting ordinary values."""
    if isinstance(value, Mapping):
        return {
            key: "[redacted]"
            if str(key).replace("_", "").casefold() == "sharepwd"
            else _share_output(item)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [_share_output(item) for item in value]
    return value


def list_shares(
    client: Any,
    payload: Mapping[str, Any],
    *,
    paid: bool = False,
    all_pages: bool = False,
) -> dict[str, Any]:
    """Traverse lastShareId until -1; an empty page alone is never terminal.

    Both documented routes return ``shareList`` and ``lastShareId``. Their row
    fields differ (payment amount/revenue/order count versus extraction password)
    and remain intact except credential values are redacted before any output,
    including partial rows attached to a later error.
    """
    if not isinstance(payload, Mapping) or set(payload) - {"limit", "lastShareId"}:
        raise Pan123Error("validation", "分享列表请求包含未知参数", exit_code=2)
    limit = payload.get("limit")
    cursor = payload.get("lastShareId", 0)
    if type(limit) is not int or not 1 <= limit <= 100:
        raise Pan123Error("validation", "分享列表 limit 必须为 1 到 100 的整数", exit_code=2)
    if type(cursor) is not int or cursor < 0:
        raise Pan123Error("validation", "分享列表起始 lastShareId 必须为非负整数", exit_code=2)
    if type(paid) is not bool or type(all_pages) is not bool:
        raise Pan123Error("validation", "分享列表选项必须为布尔值", exit_code=2)
    path = "/api/v1/share/payment/list" if paid else "/api/v1/share/list"
    seen = {cursor}
    items: list[dict[str, Any]] = []
    pages = 0
    last_success = cursor
    current = cursor
    try:
        while pages < 10_000:
            data = client.request(
                "GET", path, params={"limit": limit, "lastShareId": current}, retryable=True
            )
            if not isinstance(data, dict) or not isinstance(data.get("shareList"), list):
                raise Pan123Error("PROTOCOL_ERROR", "分享列表响应缺少有效 shareList")
            next_cursor = data.get("lastShareId")
            if type(next_cursor) is not int or next_cursor < -1:
                raise Pan123Error("PROTOCOL_ERROR", "分享列表响应缺少有效 lastShareId")
            safe_page = []
            for row in data["shareList"]:
                if (
                    not isinstance(row, dict)
                    or type(row.get("shareId")) is not int
                    or row["shareId"] <= 0
                ):
                    raise Pan123Error("PROTOCOL_ERROR", "分享列表记录缺少有效 shareId")
                safe_page.append(_share_output(row))
            items.extend(safe_page)
            pages += 1
            last_success = next_cursor
            if next_cursor == -1 or not all_pages:
                return {
                    "items": items,
                    "next_cursor": next_cursor,
                    "pages_fetched": pages,
                    "complete": next_cursor == -1,
                }
            if next_cursor in seen:
                raise Pan123Error("PROTOCOL_ERROR", "分享列表返回重复翻页游标")
            seen.add(next_cursor)
            current = next_cursor
        raise Pan123Error("PROTOCOL_ERROR", "分享列表超过本地 10000 页保护上限")
    except Pan123Error as error:
        original = error.details if isinstance(error.details, dict) else {}
        error.details = redact_sensitive(
            {
                **original,
                "partial": pages > 0,
                "items": items,
                "pages_fetched": pages,
                "last_success_cursor": last_success,
                "failed_page_cursor": current,
            }
        )
        raise
