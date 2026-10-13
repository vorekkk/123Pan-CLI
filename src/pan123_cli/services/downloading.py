"""Streaming downloads with verified bytes and no-clobber publication."""

from __future__ import annotations

import hashlib
import os
import uuid
from pathlib import Path
from typing import Any

from filelock import FileLock, Timeout

from pan123_cli.errors import Pan123Error
from pan123_cli.utils.files import (
    BLOCK_SIZE,
    publish_file,
    safe_filename,
    valid_md5,
    validate_target,
)


def download_file(
    client: Any,
    file_id: int,
    output: Path | None = None,
    *,
    overwrite: bool = False,
    progress: Any = None,
) -> dict[str, Any]:
    if isinstance(file_id, bool) or not isinstance(file_id, int) or file_id <= 0:
        raise Pan123Error("INVALID_INPUT", "A positive integer file ID is required.", exit_code=2)
    detail = client.request(
        "GET", "/api/v1/file/detail", params={"fileID": file_id}, retryable=True
    )
    if (
        not isinstance(detail, dict)
        or type(detail.get("fileID")) is not int
        or detail["fileID"] != file_id
        or type(detail.get("type")) is not int
        or detail["type"] != 0
    ):
        raise Pan123Error(
            "INVALID_INPUT", "The ID does not describe an ordinary downloadable file.", exit_code=2
        )
    if (
        detail.get("trashed") != 0
        or type(detail.get("status")) is not int
        or detail["status"] > 100
    ):
        raise Pan123Error(
            "INVALID_INPUT", "The file is trashed or rejected by review.", exit_code=2
        )
    expected_size = detail.get("size")
    expected_md5 = detail.get("etag")
    if (
        isinstance(expected_size, bool)
        or not isinstance(expected_size, int)
        or expected_size < 0
        or not valid_md5(expected_md5)
    ):
        raise Pan123Error(
            "PROTOCOL_ERROR", "File detail is missing valid size/MD5 verification metadata."
        )
    assert isinstance(expected_md5, str)
    if output is None:
        final = Path.cwd() / safe_filename(detail.get("filename"))
    else:
        selected = Path(output).expanduser()
        if selected.is_symlink():
            raise Pan123Error("LOCAL_IO", "The output path must not be a symbolic link.")
        final = selected / safe_filename(detail.get("filename")) if selected.is_dir() else selected
    final = Path(os.path.abspath(final))
    safe_filename(final.name)
    if not final.parent.is_dir():
        raise Pan123Error(
            "LOCAL_IO",
            "The output parent directory must already exist.",
            details={"path": str(final.parent)},
        )
    lock_dir = Path(client.settings.cache_dir)
    try:
        lock_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    except OSError:
        raise Pan123Error("LOCAL_IO", "Cannot create the download lock directory.") from None
    identity = hashlib.sha256(os.path.normcase(str(final)).encode()).hexdigest()
    lock = FileLock(str(lock_dir / f"download-{identity}.lock"), timeout=30)
    part: Path | None = None
    try:
        with lock:
            validate_target(final, overwrite=overwrite)
            data = client.request(
                "GET", "/api/v1/file/download_info", params={"fileId": file_id}, retryable=True
            )
            if (
                not isinstance(data, dict)
                or not isinstance(data.get("downloadUrl"), str)
                or not data["downloadUrl"]
            ):
                raise Pan123Error("PROTOCOL_ERROR", "Download API returned no usable URL.")
            part = final.with_name(f"{final.name}.{uuid.uuid4().hex}.part")
            # Create it before receiving any content so every partial transfer
            # has a concrete, unique and recoverable path.
            with part.open("xb") as handle:
                digest = hashlib.md5(usedforsecurity=False)
                received = 0
                with client.stream_download(data["downloadUrl"]) as response:
                    if response.status_code != 200:
                        raise Pan123Error(
                            "UPSTREAM_ERROR",
                            "The CDN did not return a complete file.",
                            http_status=response.status_code,
                        )
                    encoding = response.headers.get("content-encoding", "identity").strip().lower()
                    if encoding not in {"", "identity"}:
                        raise Pan123Error(
                            "PROTOCOL_ERROR", "The CDN returned a non-identity Content-Encoding."
                        )
                    length = response.headers.get("content-length")
                    if length is not None:
                        try:
                            declared_size = int(length)
                        except (TypeError, ValueError):
                            raise Pan123Error(
                                "PROTOCOL_ERROR", "The CDN Content-Length is invalid."
                            ) from None
                        if declared_size != expected_size:
                            raise Pan123Error(
                                "VERIFY_FAILED",
                                "CDN Content-Length differs from the cloud file size.",
                                exit_code=7,
                            )
                    for block in response.iter_raw(chunk_size=BLOCK_SIZE):
                        if not block:
                            continue
                        handle.write(block)
                        digest.update(block)
                        received += len(block)
                        if callable(progress):
                            progress(received, expected_size)
                        if received > expected_size:
                            raise Pan123Error(
                                "VERIFY_FAILED",
                                "Downloaded bytes exceed the expected size.",
                                exit_code=7,
                            )
                if received != expected_size or digest.hexdigest().lower() != expected_md5.lower():
                    raise Pan123Error(
                        "VERIFY_FAILED",
                        "Downloaded size or MD5 does not match file detail.",
                        exit_code=7,
                    )
                handle.flush()
                os.fsync(handle.fileno())
            publish_file(part, final, overwrite=overwrite)
            return {
                "file_id": file_id,
                "output_path": str(final),
                "size": received,
                "md5": digest.hexdigest(),
                "verified": True,
            }
    except KeyboardInterrupt:
        raise Pan123Error(
            "INTERRUPTED",
            "Download interrupted; partial file retained.",
            exit_code=130,
            details={"part_path": str(part) if part else None},
        ) from None
    except Timeout:
        raise Pan123Error(
            "LOCAL_IO", "Another command still holds the output path lock.", exit_code=5
        ) from None
    except OSError:
        raise Pan123Error(
            "LOCAL_IO",
            "Cannot read or write the local download file.",
            exit_code=5,
            details={"part_path": str(part) if part else None},
        ) from None
    except Pan123Error as error:
        if part is not None:
            error.details = {**(error.details or {}), "part_path": str(part)}
        raise
