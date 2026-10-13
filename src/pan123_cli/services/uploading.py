"""Official sequential file/OSS upload workflows and protected capability files."""

from __future__ import annotations

import hashlib
import math
import os
import sys
import time
import uuid
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from pathlib import Path
from tempfile import SpooledTemporaryFile
from typing import Any
from urllib.parse import urlsplit

from filelock import FileLock, Timeout

from pan123_cli.cache import _private_directory, read_private_json, write_private_json
from pan123_cli.errors import Pan123Error
from pan123_cli.utils.files import (
    BLOCK_SIZE,
    FileSnapshot,
    assert_source_unchanged,
    hash_file,
    open_source,
    safe_filename,
    valid_md5,
)
from pan123_cli.utils.urls import validate_external_url


def _object(value: Any, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise Pan123Error("PROTOCOL_ERROR", f"{context} returned invalid data.")
    return value


def _file_id(value: Any, *, oss: bool) -> int | str:
    if oss:
        if not isinstance(value, str) or not value or value == "0":
            raise Pan123Error("PROTOCOL_ERROR", "Upload returned no valid OSS file ID.")
    elif isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise Pan123Error("PROTOCOL_ERROR", "Upload returned no positive file ID.")
    return value


def _server(value: Any) -> str:
    validate_external_url(value)
    parts = urlsplit(value)
    if parts.path not in {"", "/"} or parts.query or parts.fragment:
        raise Pan123Error("PROTOCOL_ERROR", "Upload server must be an HTTPS origin.")
    return value.rstrip("/")


def _servers(value: Any) -> list[str]:
    if not isinstance(value, list) or not value:
        raise Pan123Error("PROTOCOL_ERROR", "Upload did not return any servers.")
    return [_server(server) for server in value]


def _binding(client: Any) -> dict[str, Any]:
    return {"auth_mode": client.settings.auth_mode, "fingerprint": client.settings.fingerprint}


def _private_path(client: Any, supplied: Any, prefix: str) -> Path:
    path = (
        Path(supplied).expanduser()
        if supplied
        else Path(client.settings.cache_dir) / f"{prefix}-{uuid.uuid4().hex}.json"
    )
    return Path(os.path.abspath(path))


@contextmanager
def _session_lock(path: Path | None) -> Iterator[None]:
    """Serialize read-modify-write access to one protected upload session.

    A slice upload may take minutes, so the bounded wait is generous; a caller
    that cannot take the lock reports a conflict instead of replaying bytes.
    """
    if path is None:
        yield
        return
    try:
        _private_directory(path.parent)
        lock_path = path.with_suffix(path.suffix + ".lock")
        if lock_path.is_symlink():
            raise Pan123Error("LOCAL_IO", "The upload session lock cannot use a symbolic link.")
        with FileLock(lock_path, timeout=600, mode=0o600):
            yield
    except Timeout:
        raise Pan123Error(
            "CONFLICT",
            "Timed out waiting for another upload action on the same session.",
            exit_code=5,
        ) from None
    except OSError:
        raise Pan123Error(
            "LOCAL_IO", "Could not access the protected upload session.", exit_code=5
        ) from None


def _new_session(
    client: Any,
    response: Any,
    metadata: dict[str, Any],
    *,
    business: str,
    version: str,
    supplied: Any = None,
) -> tuple[dict[str, Any], Path | None]:
    data = _object(response, "Upload create")
    if type(data.get("reuse")) is not bool:
        raise Pan123Error("PROTOCOL_ERROR", "Create response is missing the reuse flag.")
    if data["reuse"]:
        _file_id(data.get("fileID"), oss=business == "image")
        return data, None
    if not isinstance(data.get("preuploadID"), str) or not data["preuploadID"]:
        raise Pan123Error("PROTOCOL_ERROR", "Create response is missing the upload session.")
    if type(data.get("sliceSize")) is not int or data["sliceSize"] <= 0:
        raise Pan123Error("PROTOCOL_ERROR", "Create response has an invalid sliceSize.")
    session = {
        "schema_version": 1,
        **_binding(client),
        "business": business,
        "api_version": version,
        "source_api": _prefix(business, version) + "/create",
        "metadata": metadata,
        "preuploadID": data["preuploadID"],
        "sliceSize": data["sliceSize"],
        "parts": [],
        "status": "created",
    }
    if version == "v2":
        session["servers"] = _servers(data.get("servers"))
    path = _private_path(client, supplied, "upload-session")
    write_private_json(path, session)
    return data, path


def _prefix(business: str, version: str) -> str:
    return "/upload/v1/oss/file" if business == "image" else f"/upload/{version}/file"


def _timed_request(
    client: Any, path: str, payload: dict[str, Any], deadline: float
) -> dict[str, Any]:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise Pan123Error("TIMEOUT", "Upload completion timed out.", exit_code=6)
    # No generic POST replay: the loop below only repeats the documented false
    # completion result, never a request with an unknown remote outcome.
    return _object(
        client.request(
            "POST",
            path,
            json=payload,
            retryable=False,
            timeout=min(getattr(client.settings, "api_timeout", 30), remaining),
        ),
        "Upload completion",
    )


def _sleep(deadline: float, interval: float = 1) -> None:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise Pan123Error("TIMEOUT", "Upload completion timed out.", exit_code=6)
    if remaining < interval:
        time.sleep(remaining)
        raise Pan123Error("TIMEOUT", "Upload completion timed out.", exit_code=6)
    time.sleep(interval)


def _complete(
    client: Any,
    *,
    business: str,
    version: str,
    preupload: str,
    deadline: float,
    wait: bool = True,
    result_only: bool = False,
) -> dict[str, Any]:
    prefix = _prefix(business, version)
    payload = {"preuploadID": preupload}
    endpoint = prefix + ("/upload_async_result" if result_only else "/upload_complete")
    result = _timed_request(client, endpoint, payload, deadline)
    if version == "v1" and not result_only:
        if type(result.get("async")) is not bool or type(result.get("completed")) is not bool:
            raise Pan123Error(
                "PROTOCOL_ERROR", "Legacy completion response has invalid state flags."
            )
        if result["async"]:
            if not wait:
                return result
            endpoint = prefix + "/upload_async_result"
            result = _timed_request(client, endpoint, payload, deadline)
        elif not result["completed"]:
            raise Pan123Error(
                "PROTOCOL_ERROR", "Legacy upload is neither complete nor asynchronously pending."
            )
    while True:
        if type(result.get("completed")) is not bool:
            raise Pan123Error("PROTOCOL_ERROR", "Upload response has no valid completed flag.")
        if result["completed"]:
            _file_id(result.get("fileID"), oss=business == "image")
            return result
        if not wait:
            return result
        _sleep(deadline)
        result = _timed_request(client, endpoint, payload, deadline)


def _verify(
    client: Any,
    file_id: int | str,
    metadata: dict[str, Any],
    *,
    business: str,
    reused: bool = False,
) -> dict[str, Any]:
    deadline = time.monotonic() + 10
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise Pan123Error(
                "VERIFY_FAILED",
                "Uploaded file is not visible for verification.",
                exit_code=7,
                details={"file_id": file_id},
            )
        try:
            detail = client.request(
                "GET",
                "/api/v1/oss/file/detail" if business == "image" else "/api/v1/file/detail",
                params={"fileID": file_id},
                retryable=False,
                timeout=min(getattr(client.settings, "api_timeout", 30), remaining),
            )
            break
        except Pan123Error as error:
            if error.api_code != 5066:
                raise
            remaining = deadline - time.monotonic()
            if remaining > 0:
                time.sleep(min(1, remaining))
    detail = _object(detail, "Uploaded file detail")
    remote_id = detail.get("fileId" if business == "image" else "fileID")
    if (
        remote_id != file_id
        or type(detail.get("type")) is not int
        or detail["type"] != 0
        or type(detail.get("size")) is not int
        or detail["size"] != metadata["size"]
        or not valid_md5(detail.get("etag"))
        or detail["etag"].lower() != metadata["etag"].lower()
        or detail.get("trashed", 0) != 0
        or type(detail.get("status")) is not int
        or detail["status"] > 100
    ):
        raise Pan123Error(
            "VERIFY_FAILED",
            "Uploaded file identity, size or MD5 failed readback verification.",
            exit_code=7,
            details={"file_id": file_id},
        )
    if not isinstance(detail.get("filename"), str) or not detail["filename"]:
        raise Pan123Error("PROTOCOL_ERROR", "Uploaded file detail has no valid filename.")
    return {
        "file_id": file_id,
        "filename": detail["filename"],
        "size": metadata["size"],
        "md5": metadata["etag"].lower(),
        "reused": reused,
        "verified": True,
    }


def upload_file(
    client: Any,
    file: Path,
    *,
    parent_id: int | str = 0,
    name: str | None = None,
    duplicate: str = "error",
    api_version: str = "v2",
    business: str = "file",
    complete_timeout: float = 300,
    progress: Any = None,
) -> dict[str, Any]:
    source = Path(file).expanduser()
    if business not in {"file", "image", "transcode"} or api_version not in {"v1", "v2"}:
        raise Pan123Error("INVALID_INPUT", "Unknown upload business or API version.", exit_code=2)
    if duplicate not in {"error", "keep-both", "overwrite"}:
        raise Pan123Error("INVALID_INPUT", "Unknown duplicate filename policy.", exit_code=2)
    if (
        not isinstance(complete_timeout, (int, float))
        or isinstance(complete_timeout, bool)
        or not math.isfinite(complete_timeout)
        or complete_timeout <= 0
    ):
        raise Pan123Error(
            "INVALID_INPUT", "Completion timeout must be positive and finite.", exit_code=2
        )
    filename = safe_filename(name if name is not None else source.name, upload=True)
    etag, original = hash_file(source)
    # The snapshot uses an undefined GB unit. The conservative decimal ceiling
    # never knowingly exceeds the documented 10 GB limit; this is a local bound.
    if original.size > 10_000_000_000:
        raise Pan123Error(
            "INVALID_INPUT",
            "The file exceeds the conservative local 10 GB upload limit.",
            exit_code=2,
        )
    version = "v1" if business in {"image", "transcode"} else api_version
    if business == "image":
        parent_id = "" if parent_id == 0 else parent_id
        if not isinstance(parent_id, str):
            raise Pan123Error("INVALID_INPUT", "OSS parent IDs must be strings.", exit_code=2)
        if duplicate != "error":
            raise Pan123Error(
                "INVALID_INPUT", "OSS image create has no duplicate policy parameter.", exit_code=2
            )
    else:
        if isinstance(parent_id, bool) or not isinstance(parent_id, int) or parent_id < 0:
            raise Pan123Error(
                "INVALID_INPUT", "Parent ID must be a nonnegative integer.", exit_code=2
            )
        if business == "transcode" and parent_id == 0:
            folder = _object(
                client.request("POST", "/api/v1/transcode/folder/info", retryable=True),
                "Transcode folder",
            )
            parent_id = _file_id(folder.get("fileID"), oss=False)
        elif parent_id:
            parent = _object(
                client.request(
                    "GET", "/api/v1/file/detail", params={"fileID": parent_id}, retryable=True
                ),
                "Parent directory",
            )
            if (
                parent.get("fileID") != parent_id
                or parent.get("type") != 1
                or parent.get("trashed", 0) != 0
            ):
                raise Pan123Error(
                    "INVALID_INPUT", "The upload parent ID is not a usable directory.", exit_code=2
                )
    metadata: dict[str, Any] = {
        "parentFileID": parent_id,
        "filename": filename,
        "etag": etag,
        "size": original.size,
    }
    if business == "image":
        metadata["type"] = 1
    elif duplicate != "error":
        metadata["duplicate"] = 1 if duplicate == "keep-both" else 2
    assert_source_unchanged(source, original)
    session_path: Path | None = None
    try:
        created, session_path = _new_session(
            client,
            client.request(
                "POST", _prefix(business, version) + "/create", json=metadata, retryable=False
            ),
            metadata,
            business=business,
            version=version,
        )
        if created["reuse"]:
            assert_source_unchanged(source, original)
            return _verify(client, created["fileID"], metadata, business=business, reused=True)
        assert session_path is not None
        session = read_private_json(session_path)
        transmitted = hashlib.md5(usedforsecurity=False)
        sent = 0
        parts: list[dict[str, Any]] = []
        with open_source(source) as handle:
            assert_source_unchanged(source, original)
            slice_count = math.ceil(original.size / session["sliceSize"])
            for number in range(1, slice_count + 1):
                assert_source_unchanged(source, original)
                length = min(session["sliceSize"], original.size - sent)
                with SpooledTemporaryFile(max_size=8 * BLOCK_SIZE, mode="w+b") as part:
                    part_md5 = hashlib.md5(usedforsecurity=False)
                    remaining = length
                    while remaining:
                        block = handle.read(min(BLOCK_SIZE, remaining))
                        if not block:
                            raise Pan123Error(
                                "SOURCE_CHANGED",
                                "The upload source ended before its recorded size.",
                                exit_code=7,
                            )
                        part.write(block)
                        part_md5.update(block)
                        transmitted.update(block)
                        remaining -= len(block)
                    part.seek(0)
                    if version == "v2":
                        client.upload_slice(
                            session["servers"][0],
                            data={
                                "preuploadID": session["preuploadID"],
                                "sliceNo": str(number),
                                "sliceMD5": part_md5.hexdigest(),
                            },
                            files={"slice": (filename, part, "application/octet-stream")},
                        )
                    else:
                        address = _object(
                            client.request(
                                "POST",
                                _prefix(business, version) + "/get_upload_url",
                                json={"preuploadID": session["preuploadID"], "sliceNo": number},
                                retryable=False,
                            ),
                            "Presigned upload URL",
                        )
                        url = address.get("presignedURL")
                        if not isinstance(url, str):
                            raise Pan123Error(
                                "PROTOCOL_ERROR", "Presigned upload URL is not a string."
                            )
                        validate_external_url(url)
                        client.put_external(url, part)
                    sent += length
                    parts.append({"sliceNo": number, "size": length, "md5": part_md5.hexdigest()})
                    session.update(parts=parts, status="uploading")
                    write_private_json(session_path, session)
                assert_source_unchanged(source, original)
                if callable(progress):
                    progress(sent, original.size)
            if handle.read(1):
                raise Pan123Error(
                    "SOURCE_CHANGED", "Upload source grew during the transfer.", exit_code=7
                )
        assert_source_unchanged(source, original)
        if sent != original.size or transmitted.hexdigest() != etag:
            raise Pan123Error(
                "SOURCE_CHANGED",
                "The transmitted file differs from the original hash.",
                exit_code=7,
            )
        completed = _complete(
            client,
            business=business,
            version=version,
            preupload=session["preuploadID"],
            deadline=time.monotonic() + complete_timeout,
        )
        result = _verify(client, completed["fileID"], metadata, business=business)
        session.update(status="verified", fileID=completed["fileID"])
        write_private_json(session_path, session)
        return result
    except KeyboardInterrupt:
        raise Pan123Error(
            "INTERRUPTED",
            "Upload interrupted; remote completion is not assumed.",
            exit_code=130,
            details={"session_file": str(session_path) if session_path else None},
        ) from None
    except OSError:
        raise Pan123Error(
            "LOCAL_IO",
            "Cannot read the source or prepare temporary upload storage.",
            exit_code=5,
            details={"session_file": str(session_path) if session_path else None},
        ) from None
    except Pan123Error as error:
        if session_path is not None:
            error.details = {**(error.details or {}), "session_file": str(session_path)}
        raise


def dispatch_upload(
    client: Any, command: tuple[str, ...], payload: dict[str, Any], options: Mapping[str, Any]
) -> Any:
    """Validate exact wire inputs, then dispatch one explicit protocol action.

    Capabilities are written to private files. Manually invoking protocol steps
    is supported; automatic recovery/replay of an unknown result is not.
    """
    from pan123_cli.catalog import ENDPOINTS, payload_for

    endpoint = next((entry for entry in ENDPOINTS if entry.command == command), None)
    if endpoint is None or command[:2] not in {("file", "upload-api"), ("image", "upload-api")}:
        raise Pan123Error("INVALID_INPUT", "Unknown upload protocol command.", exit_code=2)
    business = "image" if command[0] == "image" else "file"
    version = "v1" if business == "image" else command[2]
    action = command[-1]
    values = dict(options)
    if isinstance(payload, Mapping):
        request_data: dict[str, Any] | None = dict(payload) if options.get("request_file") else None
    elif options.get("request_file") or payload:
        raise Pan123Error(
            "INVALID_INPUT",
            "A request file must contain exactly one JSON object for this command.",
            exit_code=2,
        )
    else:
        request_data = None
    session: dict[str, Any] | None = None
    session_path: Path | None = None
    if options.get("session_file"):
        session_path = Path(options["session_file"])
        session = _load_session(client, session_path, business=business, version=version)
        values["preuploadID"] = session["preuploadID"]
    if request_data is None:
        values.update(payload)
    # Binary path is a local selector, not a JSON value to send to the server.
    # A request file can supply metadata while --file points to actual bytes.
    binary_key = "file" if action == "single" else "slice" if action == "slice" else None
    if binary_key:
        selected = options.get(binary_key) or options.get("slice_file")
        if selected:
            if request_data is not None:
                if binary_key in request_data and request_data[binary_key] != str(selected):
                    raise Pan123Error(
                        "INVALID_INPUT", "Binary path conflicts with the request file.", exit_code=2
                    )
                request_data[binary_key] = str(selected)
                values.pop(binary_key, None)
            else:
                values[binary_key] = str(selected)
    local_part: Path | None = None
    part_md5: str | None = None
    part_size: int | None = None
    if action == "slice":
        chosen = request_data.get("slice") if request_data is not None else values.get("slice")
        if not chosen:
            raise Pan123Error("INVALID_INPUT", "A local slice file is required.", exit_code=2)
        local_part = Path(chosen)
        part_md5, part_snapshot = hash_file(local_part)
        part_size = part_snapshot.size
        declared_md5 = request_data.get("sliceMD5") if request_data is not None else None
        cli_md5 = values.get("slice_md5")
        if (
            declared_md5 is not None
            and cli_md5 is not None
            and str(declared_md5).lower() != str(cli_md5).lower()
        ):
            raise Pan123Error(
                "INVALID_INPUT",
                "The request file and --slice-md5 disagree about the slice hash.",
                exit_code=2,
            )
        supplied_md5 = declared_md5 if declared_md5 is not None else cli_md5
        if supplied_md5 is not None and (
            not valid_md5(supplied_md5) or supplied_md5.lower() != part_md5
        ):
            raise Pan123Error(
                "VERIFY_FAILED",
                "The supplied slice MD5 does not match the local bytes.",
                exit_code=7,
            )
        if request_data is not None:
            request_data["sliceMD5"] = part_md5
            values.pop("slice_md5", None)
        else:
            values["slice_md5"] = part_md5
    if action in {"put", "put-slice"}:
        if options.get("upload_url"):
            values["presignedURL"] = options["upload_url"]
        elif options.get("upload_url_stdin"):
            values["presignedURL"] = sys.stdin.read().strip()
        elif options.get("upload_url_file"):
            address = _object(
                read_private_json(Path(options["upload_url_file"])), "Private upload URL file"
            )
            values["presignedURL"] = address.get("presignedURL")
    validated = payload_for(endpoint, values, request_data)
    if not isinstance(validated, dict):
        raise Pan123Error("PROTOCOL_ERROR", "Upload command validation did not return an object.")
    try:
        if action == "create":
            _validate_metadata(validated)
            data, saved = _new_session(
                client,
                client.request(endpoint.method, endpoint.path, json=validated, retryable=False),
                validated,
                business=business,
                version=version,
                supplied=options.get("session_out"),
            )
            if data["reuse"]:
                return _verify(client, data["fileID"], validated, business=business, reused=True)
            return {"reused": False, "session_file": str(saved), "slice_size": data["sliceSize"]}
        if action in {"url", "get-url"}:
            if session is not None:
                _check_slice_number(session, validated["sliceNo"])
            data = _object(
                client.request(
                    endpoint.method, endpoint.path, json=validated, retryable=endpoint.read_only
                ),
                "Presigned upload URL",
            )
            url = data.get("presignedURL")
            if not isinstance(url, str):
                raise Pan123Error("PROTOCOL_ERROR", "Presigned upload URL is not a string.")
            validate_external_url(url)
            path = _private_path(client, options.get("url_out"), "upload-url")
            write_private_json(path, {"presignedURL": url})
            # Keep the wire URL_FILE shape exact; account/session provenance
            # lives alongside it and never becomes part of the PUT/API payload.
            provenance = {
                "schema_version": 1,
                **_binding(client),
                "business": business,
                "api_version": version,
                "source_api": endpoint.path,
                "url_hash": hashlib.sha256(url.encode()).hexdigest(),
                "sliceNo": validated["sliceNo"],
                "session_file": str(session_path) if session_path else None,
            }
            write_private_json(path.with_suffix(path.suffix + ".meta.json"), provenance)
            return {"url_file": str(path), "slice_no": validated["sliceNo"]}
        if action in {"put", "put-slice"}:
            chosen = options.get("slice") or options.get("slice_file") or options.get("file")
            if not chosen:
                raise Pan123Error(
                    "INVALID_INPUT", "A local slice file is required for PUT.", exit_code=2
                )
            path = Path(chosen)
            digest, original = hash_file(path)
            url = validated["presignedURL"]
            validate_external_url(url)
            url_meta = _url_provenance(client, options, url, business=business, version=version)
            linked_path = (
                Path(url_meta["session_file"])
                if url_meta and url_meta.get("session_file")
                else None
            )
            with _session_lock(linked_path):
                linked = (
                    _load_session(client, linked_path, business=business, version=version)
                    if linked_path is not None
                    else None
                )
                if linked is not None:
                    assert url_meta is not None
                    _check_slice_size(linked, url_meta["sliceNo"], original.size)
                with _stable_binary(path, digest, original) as handle:
                    client.put_external(url, handle)
                assert_source_unchanged(path, original)
                if linked is not None and linked_path is not None:
                    assert url_meta is not None
                    _record_part(linked, url_meta["sliceNo"], original.size, digest)
                    write_private_json(linked_path, linked)
            return {"uploaded": True, "size": original.size, "md5": digest}
        if action == "slice":
            if session is None or session_path is None:
                raise Pan123Error(
                    "INVALID_INPUT",
                    "V2 multipart upload requires its protected --session-file.",
                    exit_code=2,
                )
            assert local_part is not None and part_md5 is not None and part_size is not None
            safe_values = {key: str(value) for key, value in validated.items() if key != "slice"}
            with _session_lock(session_path):
                # Re-read under the lock so a concurrent action cannot record the
                # same slice twice or drop a slice recorded by another process.
                session = _load_session(client, session_path, business=business, version=version)
                _check_slice_size(session, validated["sliceNo"], part_size)
                with _stable_binary(local_part, part_md5, part_snapshot) as handle:
                    client.upload_slice(
                        session["servers"][0],
                        data=safe_values,
                        files={
                            "slice": (
                                session["metadata"]["filename"],
                                handle,
                                "application/octet-stream",
                            )
                        },
                    )
                _record_part(session, validated["sliceNo"], part_size, part_md5)
                write_private_json(session_path, session)
            return {
                "uploaded": True,
                "slice_no": validated["sliceNo"],
                "size": part_size,
                "md5": part_md5,
            }
        if action == "parts":
            data = client.request(endpoint.method, endpoint.path, json=validated, retryable=True)
            if data is not None and (
                not isinstance(data, dict) or not isinstance(data.get("parts"), list)
            ):
                raise Pan123Error("PROTOCOL_ERROR", "List-parts returned invalid data.")
            return data
        if action in {"complete", "result", "async-result"}:
            timeout = options.get("wait_timeout", options.get("complete_timeout", 300))
            _validate_timeout(timeout)
            data = _complete(
                client,
                business=business,
                version=version,
                preupload=validated["preuploadID"],
                deadline=time.monotonic() + timeout,
                wait=bool(options.get("wait")),
                result_only=action != "complete",
            )
            if data.get("completed"):
                file_id = _file_id(data.get("fileID"), oss=business == "image")
                if session is not None:
                    result = _verify(client, file_id, session["metadata"], business=business)
                    session.update(status="verified", fileID=file_id)
                    if session_path:
                        write_private_json(session_path, session)
                    return {**result, "completed": True}
                return {"completed": True, "file_id": file_id, "verified": False}
            return {"completed": False, "async": data.get("async", version == "v1")}
        if action == "domains":
            servers = _servers(client.request(endpoint.method, endpoint.path, retryable=True))
            path = _private_path(client, options.get("domains_out"), "upload-domains")
            write_private_json(
                path,
                {
                    "schema_version": 1,
                    **_binding(client),
                    "business": business,
                    "api_version": version,
                    "source_api": endpoint.path,
                    "servers": servers,
                },
            )
            return {"domains_file": str(path), "server_count": len(servers)}
        if action == "single":
            if not options.get("domains_file"):
                raise Pan123Error(
                    "INVALID_INPUT",
                    "Single-step upload requires the private --domains-file.",
                    exit_code=2,
                )
            domains = _load_binding(
                client, Path(options["domains_file"]), business=business, version=version
            )
            if domains.get("source_api") != "/upload/v2/file/domain":
                raise Pan123Error(
                    "INVALID_INPUT",
                    "Domains file was not created by the V2 domain endpoint.",
                    exit_code=2,
                )
            servers = _servers(domains.get("servers"))
            binary_path = Path(validated.pop("file"))
            digest, original = hash_file(binary_path)
            _validate_metadata(validated, cap=1_000_000_000)
            if original.size != validated["size"] or digest.lower() != validated["etag"].lower():
                raise Pan123Error(
                    "VERIFY_FAILED",
                    "Single-upload metadata does not match the local file.",
                    exit_code=7,
                )
            multipart = {
                key: "true" if value is True else "false" if value is False else str(value)
                for key, value in validated.items()
            }
            with _stable_binary(binary_path, digest, original) as handle:
                data = _object(
                    client.upload_single(
                        servers[0],
                        data=multipart,
                        files={"file": (validated["filename"], handle, "application/octet-stream")},
                    ),
                    "Single upload",
                )
            assert_source_unchanged(binary_path, original)
            if data.get("completed") is not True:
                raise Pan123Error("PROTOCOL_ERROR", "Single upload did not report completed=true.")
            return _verify(
                client, _file_id(data.get("fileID"), oss=False), validated, business=business
            )
        if action == "sha1-reuse":
            _validate_metadata(validated, md5=False)
            data = _object(
                client.request(endpoint.method, endpoint.path, json=validated, retryable=False),
                "SHA1 reuse",
            )
            if type(data.get("reuse")) is not bool:
                raise Pan123Error("PROTOCOL_ERROR", "SHA1 reuse returned an invalid reuse flag.")
            if not data["reuse"]:
                return {"reused": False, "verified": False}
            return {
                "reused": True,
                "file_id": _file_id(data.get("fileID"), oss=False),
                "verified": False,
            }
    except KeyboardInterrupt:
        raise Pan123Error(
            "INTERRUPTED",
            "Upload action interrupted; remote outcome is not assumed.",
            exit_code=130,
        ) from None
    except OSError:
        raise Pan123Error(
            "LOCAL_IO", "Cannot access the upload state or local binary file.", exit_code=5
        ) from None
    raise Pan123Error("INVALID_INPUT", "Unknown upload protocol action.", exit_code=2)


def _validate_timeout(value: Any) -> None:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or value <= 0
    ):
        raise Pan123Error("INVALID_INPUT", "Wait timeout must be positive and finite.", exit_code=2)


@contextmanager
def _stable_binary(path: Path, expected_md5: str, original: FileSnapshot) -> Any:
    """Spool exact bytes before send so a changing file cannot falsify its hash."""
    with SpooledTemporaryFile(max_size=8 * BLOCK_SIZE, mode="w+b") as stable:
        digest = hashlib.md5(usedforsecurity=False)
        count = 0
        with open_source(path) as source:
            assert_source_unchanged(path, original)
            while block := source.read(BLOCK_SIZE):
                stable.write(block)
                digest.update(block)
                count += len(block)
                if count > original.size:
                    raise Pan123Error(
                        "SOURCE_CHANGED", "The binary source grew before upload.", exit_code=7
                    )
        assert_source_unchanged(path, original)
        if count != original.size or digest.hexdigest() != expected_md5:
            raise Pan123Error(
                "SOURCE_CHANGED", "The binary source changed before upload.", exit_code=7
            )
        stable.seek(0)
        yield stable
        assert_source_unchanged(path, original)


def _validate_metadata(
    metadata: dict[str, Any], *, cap: int = 10_000_000_000, md5: bool = True
) -> None:
    if type(metadata.get("size")) is not int or not 0 <= metadata["size"] <= cap:
        raise Pan123Error(
            "INVALID_INPUT", "File size exceeds the conservative local upload limit.", exit_code=2
        )
    if md5 and not valid_md5(metadata.get("etag")):
        raise Pan123Error("INVALID_INPUT", "A full-file MD5 is required.", exit_code=2)


def _load_binding(client: Any, path: Path, *, business: str, version: str) -> dict[str, Any]:
    value = _object(read_private_json(path), "Upload state")
    if (
        value.get("schema_version") != 1
        or value.get("auth_mode") != client.settings.auth_mode
        or value.get("fingerprint") != client.settings.fingerprint
        or value.get("business") != business
        or value.get("api_version") != version
    ):
        raise Pan123Error(
            "INVALID_INPUT",
            "Upload state belongs to a different account, protocol or business.",
            exit_code=2,
        )
    return value


def _load_session(client: Any, path: Path, *, business: str, version: str) -> dict[str, Any]:
    value = _load_binding(client, path, business=business, version=version)
    if (
        value.get("source_api") != _prefix(business, version) + "/create"
        or not isinstance(value.get("preuploadID"), str)
        or not value["preuploadID"]
        or type(value.get("sliceSize")) is not int
        or value["sliceSize"] <= 0
        or not isinstance(value.get("metadata"), dict)
    ):
        raise Pan123Error(
            "INVALID_INPUT", "The upload session is invalid or incomplete.", exit_code=2
        )
    _validate_metadata(value["metadata"])
    if version == "v2":
        value["servers"] = _servers(value.get("servers"))
    if not isinstance(value.get("parts"), list):
        raise Pan123Error("INVALID_INPUT", "The session parts metadata is invalid.", exit_code=2)
    return value


def _check_slice_number(session: dict[str, Any], number: int) -> None:
    count = math.ceil(session["metadata"]["size"] / session["sliceSize"])
    if type(number) is not int or number < 1 or number > count:
        raise Pan123Error(
            "INVALID_INPUT", "Slice number is outside the source file's boundaries.", exit_code=2
        )
    if any(part.get("sliceNo") == number for part in session["parts"]):
        raise Pan123Error(
            "INVALID_INPUT",
            "That slice is already recorded; unverified replay is not supported.",
            exit_code=2,
        )


def _check_slice_size(session: dict[str, Any], number: int, size: int) -> None:
    _check_slice_number(session, number)
    expected = min(
        session["sliceSize"], session["metadata"]["size"] - (number - 1) * session["sliceSize"]
    )
    if size != expected:
        raise Pan123Error(
            "VERIFY_FAILED",
            "The local slice size does not match the session boundaries.",
            exit_code=7,
        )


def _record_part(session: dict[str, Any], number: int, size: int, digest: str) -> None:
    session["parts"].append({"sliceNo": number, "size": size, "md5": digest})
    session["status"] = "uploading"


def _url_provenance(
    client: Any, options: Mapping[str, Any], url: str, *, business: str, version: str
) -> dict[str, Any] | None:
    input_file = options.get("upload_url_file") or options.get("request_file")
    if not input_file or input_file == "-":
        return None
    path = Path(input_file)
    companion = path.with_suffix(path.suffix + ".meta.json")
    if not companion.exists():
        return None  # Explicit manually supplied URL still has no API credentials.
    value = _load_binding(client, companion, business=business, version=version)
    if value.get("url_hash") != hashlib.sha256(url.encode()).hexdigest():
        raise Pan123Error(
            "INVALID_INPUT", "The private upload URL was modified after creation.", exit_code=2
        )
    if value.get("source_api") != _prefix(business, version) + "/get_upload_url":
        raise Pan123Error(
            "INVALID_INPUT", "The upload URL has an unexpected source API.", exit_code=2
        )
    return value
