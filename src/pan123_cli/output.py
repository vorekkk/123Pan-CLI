"""Human readable terminal output and stable script output."""

from __future__ import annotations

import json
import re
import sys
from contextlib import contextmanager
from typing import Any

from rich.console import Console
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn
from rich.table import Table


def plain(value: Any) -> str:
    text = str(value)
    return re.sub(r"[\x00-\x1f\x7f-\x9f]", "", text)


def emit(result: dict[str, Any], *, json_mode=False) -> None:
    if json_mode:
        print(json.dumps(result, ensure_ascii=False, default=str))
        return
    console = Console(markup=False, highlight=False)
    if not result["ok"]:
        error = result["error"]
        Console(stderr=True, markup=False, highlight=False).print(
            f"{plain(error['kind'])}: {plain(error['message'])}"
        )
        if error.get("details"):
            console.print(json.dumps(error["details"], ensure_ascii=False, default=str))
        return
    data = result.get("data")
    items = data.get("items") if isinstance(data, dict) else None
    if isinstance(items, list) and items:
        assert isinstance(data, dict)
        if "shareId" in items[0]:
            table = Table("ID", "名称", "过期时间", "已失效")
            for item in items:
                table.add_row(
                    *(
                        plain(item.get(key, ""))
                        for key in ("shareId", "shareName", "expiration", "expired")
                    )
                )
            console.print(table)
            console.print(f"next_cursor={data.get('next_cursor')} complete={data.get('complete')}")
            return
        table = Table("ID", "类型", "名称", "字节", "MD5", "回收站")
        for item in items:
            table.add_row(
                plain(item.get("fileId", item.get("fileID", item.get("file_id", "")))),
                "目录" if item.get("type") == 1 else "文件",
                plain(item.get("filename", "")),
                plain(item.get("size", "")),
                plain(item.get("etag", "")),
                plain(item.get("trashed", 0)),
            )
        console.print(table)
        console.print(f"next_cursor={data.get('next_cursor')} complete={data.get('complete')}")
    else:
        console.print(plain(json.dumps(data, ensure_ascii=False, indent=2, default=str)))


@contextmanager
def progress_callback(enabled: bool):
    if not enabled or not sys.stderr.isatty():
        yield None
        return
    progress = Progress(
        TextColumn("文件传输"), BarColumn(), TaskProgressColumn(), console=Console(stderr=True)
    )
    with progress:
        task = progress.add_task("transfer", total=1)

        def update(*args, **kwargs):
            completed = kwargs.get("completed", args[0] if args else 0)
            total = kwargs.get("total", args[1] if len(args) > 1 else 1)
            progress.update(task, total=total or 1, completed=completed)

        yield update
