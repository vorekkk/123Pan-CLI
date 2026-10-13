"""Uploads exercise actual source/slice bytes with simulated API boundaries."""

import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace

import pytest


class UploadClient:
    def __init__(self, cache_dir, content, *, oss=False, reuse=False):
        self.settings = SimpleNamespace(
            cache_dir=cache_dir, fingerprint="test-account", auth_mode="developer"
        )
        self.content = content
        self.oss = oss
        self.reuse = reuse
        self.received = []
        self.requests = []
        self.file_id = "oss-file-509" if oss else 509
        self.on_slice = None

    def request(self, method, path, *, params=None, json=None, **kwargs):
        self.requests.append((method, path, params, json))
        if path.endswith("/folder/info"):
            return {"fileID": 81}
        if path.endswith("/create"):
            if self.reuse:
                return {"reuse": True, "fileID": self.file_id}
            return {
                "reuse": False,
                "preuploadID": "opaque-session",
                "sliceSize": 4,
                "servers": ["https://openapi-upload.123242.com"],
            }
        if path.endswith("/get_upload_url"):
            return {"presignedURL": "https://m74.123624.com/part?no=" + str(json["sliceNo"])}
        if path.endswith("/upload_complete"):
            if "/v1/" in path:
                return {"async": True, "completed": False, "fileID": "" if self.oss else 0}
            return {"completed": True, "fileID": self.file_id}
        if path.endswith("/upload_async_result"):
            return {"completed": True, "fileID": self.file_id}
        if path.endswith("/detail"):
            return {
                "fileId" if self.oss else "fileID": self.file_id,
                "filename": "actual-name.bin",
                "type": 0,
                "trashed": 0,
                "status": 0,
                "size": len(self.content),
                "etag": hashlib.md5(self.content).hexdigest(),
            }
        raise AssertionError(path)

    def upload_slice(self, server, *, data, files):
        binary = files["slice"][1].read()
        assert data["sliceMD5"] == hashlib.md5(binary).hexdigest()
        self.received.append(binary)
        if self.on_slice:
            self.on_slice()
        return None

    def put_external(self, url, fileobj):
        self.received.append(fileobj.read())


@pytest.mark.parametrize("content, lengths", [(b"abcdefgh", [4, 4]), (b"abcdefghi", [4, 4, 1])])
def test_v2_upload_sends_exact_slice_bytes_and_verifies_remote_file(tmp_path, content, lengths):
    from pan123_cli.services.uploading import upload_file

    source = tmp_path / "source.bin"
    source.write_bytes(content)
    client = UploadClient(tmp_path / "cache", content)
    result = upload_file(client, source)
    assert [len(part) for part in client.received] == lengths
    assert b"".join(client.received) == content
    assert result["md5"] == hashlib.md5(content).hexdigest()
    assert result["filename"] == "actual-name.bin"
    assert result["verified"] is True
    assert result["file_id"] == 509


def test_reuse_does_not_require_nonexistent_upload_session_fields(tmp_path):
    from pan123_cli.services.uploading import upload_file

    source = tmp_path / "source.bin"
    source.write_bytes(b"abc")
    client = UploadClient(tmp_path / "cache", b"abc", reuse=True)
    result = upload_file(client, source)
    assert result["reused"] is True
    assert client.received == []


def test_changed_source_is_not_completed_or_reported_successful(tmp_path):
    from pan123_cli.errors import Pan123Error
    from pan123_cli.services.uploading import upload_file

    source = tmp_path / "source.bin"
    source.write_bytes(b"abcdefgh")
    client = UploadClient(tmp_path / "cache", b"abcdefgh")
    client.on_slice = lambda: source.write_bytes(b"ABCDEFGH")
    with pytest.raises(Pan123Error) as caught:
        upload_file(client, source)
    assert caught.value.kind == "SOURCE_CHANGED"
    assert not any(request[1].endswith("/upload_complete") for request in client.requests)


def test_oss_upload_uses_legacy_presigned_put_and_string_ids(tmp_path):
    from pan123_cli.services.uploading import upload_file

    source = tmp_path / "source.jpg"
    source.write_bytes(b"abcdefgh")
    client = UploadClient(tmp_path / "cache", b"abcdefgh", oss=True)
    result = upload_file(client, source, parent_id="", business="image")
    create = next(request for request in client.requests if request[1].endswith("/create"))
    assert create[1] == "/upload/v1/oss/file/create"
    assert create[3]["parentFileID"] == ""
    assert create[3]["type"] == 1
    assert result["file_id"] == "oss-file-509"
    assert b"".join(client.received) == b"abcdefgh"


def test_transcode_upload_obtains_transcode_parent_and_uses_v1(tmp_path):
    from pan123_cli.services.uploading import upload_file

    source = tmp_path / "source.mp4"
    source.write_bytes(b"abcdefgh")
    client = UploadClient(tmp_path / "cache", b"abcdefgh")
    upload_file(client, source, business="transcode")
    create = next(request for request in client.requests if request[1].endswith("/create"))
    assert create[1] == "/upload/v1/file/create"
    assert create[3]["parentFileID"] == 81


def test_v2_completion_false_waits_a_second_and_requeries_control_endpoint(tmp_path, monkeypatch):
    from pan123_cli.services import uploading

    source = tmp_path / "source.bin"
    source.write_bytes(b"abc")
    client = UploadClient(tmp_path / "cache", b"abc")
    original_request = client.request
    clock = [0.0]
    calls = [0]

    def request(method, path, **kwargs):
        if path.endswith("/upload_complete"):
            calls[0] += 1
            if calls[0] == 1:
                return {"completed": False, "fileID": 0}
        return original_request(method, path, **kwargs)

    client.request = request
    monkeypatch.setattr(uploading.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        uploading.time, "sleep", lambda delay: clock.__setitem__(0, clock[0] + delay)
    )
    result = uploading.upload_file(client, source, complete_timeout=2)
    assert result["verified"] is True
    assert clock[0] == 1
    assert calls[0] == 2


def test_completion_wait_has_finite_deadline_and_retains_session(tmp_path, monkeypatch):
    from pan123_cli.errors import Pan123Error
    from pan123_cli.services import uploading

    source = tmp_path / "source.bin"
    source.write_bytes(b"abc")
    client = UploadClient(tmp_path / "cache", b"abc")
    original_request = client.request
    clock = [0.0]

    def request(method, path, **kwargs):
        if path.endswith("/upload_complete"):
            return {"completed": False, "fileID": 0}
        return original_request(method, path, **kwargs)

    client.request = request
    monkeypatch.setattr(uploading.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        uploading.time, "sleep", lambda delay: clock.__setitem__(0, clock[0] + delay)
    )
    with pytest.raises(Pan123Error) as caught:
        uploading.upload_file(client, source, complete_timeout=0.5)
    assert caught.value.exit_code == 6
    assert clock[0] == 0.5
    assert list((tmp_path / "cache").glob("upload-session-*.json"))


def test_lowlevel_create_to_v2_slice_to_completion_uses_protected_state(tmp_path):
    from pan123_cli.cache import read_private_json
    from pan123_cli.services.uploading import dispatch_upload

    client = UploadClient(tmp_path / "cache", b"abcdefgh")
    create = {
        "parentFileID": 0,
        "filename": "source.bin",
        "size": 8,
        "etag": "e8dc4081b13434b45189a720b77b6818",
    }
    created = dispatch_upload(
        client, ("file", "upload-api", "v2", "create"), create, {"request_file": "input.json"}
    )
    session_path = created["session_file"]
    assert "preuploadID" not in created
    assert read_private_json(Path(session_path))["preuploadID"] == "opaque-session"
    for number, body in [(1, b"abcd"), (2, b"efgh")]:
        part = tmp_path / f"part-{number}"
        part.write_bytes(body)
        dispatch_upload(
            client,
            ("file", "upload-api", "v2", "slice"),
            {},
            {"session_file": session_path, "slice_no": number, "slice": str(part)},
        )
    result = dispatch_upload(
        client,
        ("file", "upload-api", "v2", "complete"),
        {},
        {"session_file": session_path, "wait": True},
    )
    assert b"".join(client.received) == b"abcdefgh"
    assert result["verified"] is True
    assert result["file_id"] == 509


def test_lowlevel_rejects_a_session_from_another_identity_without_network(tmp_path):
    from pan123_cli.cache import write_private_json
    from pan123_cli.errors import Pan123Error
    from pan123_cli.services.uploading import dispatch_upload

    session = tmp_path / "session.json"
    write_private_json(
        session,
        {
            "schema_version": 1,
            "auth_mode": "developer",
            "fingerprint": "other",
            "business": "file",
            "api_version": "v2",
            "preuploadID": "sensitive",
        },
    )
    client = UploadClient(tmp_path / "cache", b"abc")
    with pytest.raises(Pan123Error):
        dispatch_upload(
            client, ("file", "upload-api", "v2", "complete"), {}, {"session_file": str(session)}
        )
    assert client.requests == []


def test_lowlevel_oss_url_file_can_be_consumed_without_printing_signed_url(tmp_path):
    from pan123_cli.cache import read_private_json
    from pan123_cli.services.uploading import dispatch_upload

    client = UploadClient(tmp_path / "cache", b"abcd", oss=True)
    created = dispatch_upload(
        client,
        ("image", "upload-api", "create"),
        {
            "parentFileID": "",
            "filename": "image.jpg",
            "etag": "e2fc714c4727ee9395f324cd2e7f331f",
            "size": 4,
            "type": 1,
        },
        {"request_file": "input.json"},
    )
    url_result = dispatch_upload(
        client,
        ("image", "upload-api", "get-url"),
        {},
        {"session_file": created["session_file"], "slice_no": 1},
    )
    assert "presignedURL" not in url_result
    address_file = Path(url_result["url_file"])
    assert read_private_json(address_file)["presignedURL"].startswith("https://")
    part = tmp_path / "slice.bin"
    part.write_bytes(b"abcd")
    dispatch_upload(
        client,
        ("image", "upload-api", "put-slice"),
        read_private_json(address_file),
        {"request_file": str(address_file), "slice_file": str(part)},
    )
    assert client.received == [b"abcd"]


def test_single_upload_hashes_real_bytes_and_requires_matching_metadata(tmp_path):
    from pan123_cli.cache import write_private_json
    from pan123_cli.errors import Pan123Error
    from pan123_cli.services.uploading import dispatch_upload

    part = tmp_path / "file.bin"
    part.write_bytes(b"abc")
    client = UploadClient(tmp_path / "cache", b"abc")
    domains = tmp_path / "domains.json"
    write_private_json(
        domains,
        {
            "schema_version": 1,
            "auth_mode": "developer",
            "fingerprint": "test-account",
            "api_version": "v2",
            "business": "file",
            "source_api": "/upload/v2/file/domain",
            "servers": ["https://openapi-upload.123242.com"],
        },
    )

    def single(server, *, data, files):
        client.received.append(files["file"][1].read())
        return {"completed": True, "fileID": 509}

    client.upload_single = single
    metadata = {
        "parentFileID": 0,
        "filename": "file.bin",
        "etag": "900150983cd24fb0d6963f7d28e17f72",
        "size": 3,
    }
    result = dispatch_upload(
        client,
        ("file", "upload-api", "v2", "single"),
        metadata,
        {"request_file": "input.json", "domains_file": str(domains), "file": str(part)},
    )
    assert result["verified"] is True
    assert client.received == [b"abc"]
    metadata["size"] = 4
    with pytest.raises(Pan123Error):
        dispatch_upload(
            client,
            ("file", "upload-api", "v2", "single"),
            metadata,
            {"request_file": "input.json", "domains_file": str(domains), "file": str(part)},
        )
    assert client.received == [b"abc"]


def test_sha1_miss_returns_nonreused_result_without_inventing_session(tmp_path):
    from pan123_cli.services.uploading import dispatch_upload

    client = UploadClient(tmp_path / "cache", b"abc")
    client.request = lambda method, path, **kwargs: {"reuse": False}
    result = dispatch_upload(
        client,
        ("file", "upload-api", "v2", "sha1-reuse"),
        {
            "parentFileID": 0,
            "filename": "file.bin",
            "sha1": "a9993e364706816aba3e25717850c26c9cd0d89d",
            "size": 3,
        },
        {"request_file": "input.json"},
    )
    assert result == {"reused": False, "verified": False}


def test_conservative_size_bound_fails_before_remote_create(tmp_path, monkeypatch):
    from pan123_cli.errors import Pan123Error
    from pan123_cli.services import uploading
    from pan123_cli.utils.files import FileSnapshot

    source = tmp_path / "huge.bin"
    source.write_bytes(b"abc")
    client = UploadClient(tmp_path / "cache", b"abc")
    monkeypatch.setattr(
        uploading,
        "hash_file",
        lambda path: ("900150983cd24fb0d6963f7d28e17f72", FileSnapshot(10_000_000_001, 1, 1, 1)),
    )
    with pytest.raises(Pan123Error) as caught:
        uploading.upload_file(client, source)
    assert caught.value.exit_code == 2
    assert client.requests == []


def test_lowlevel_slice_that_changes_after_hash_is_not_recorded(tmp_path, monkeypatch):
    from pan123_cli.cache import read_private_json
    from pan123_cli.errors import Pan123Error
    from pan123_cli.services import uploading

    client = UploadClient(tmp_path / "cache", b"abcd")
    created = uploading.dispatch_upload(
        client,
        ("file", "upload-api", "v2", "create"),
        {
            "parentFileID": 0,
            "filename": "file.bin",
            "etag": "e2fc714c4727ee9395f324cd2e7f331f",
            "size": 4,
        },
        {"request_file": "input.json"},
    )
    part = tmp_path / "slice.bin"
    part.write_bytes(b"abcd")
    original_open = uploading.open_source

    def changed_open(path):
        part.write_bytes(b"ABCD")
        return original_open(path)

    monkeypatch.setattr(uploading, "open_source", changed_open)
    with pytest.raises(Pan123Error) as caught:
        uploading.dispatch_upload(
            client,
            ("file", "upload-api", "v2", "slice"),
            {},
            {"session_file": created["session_file"], "slice_no": 1, "slice": str(part)},
        )
    assert caught.value.exit_code == 7
    assert read_private_json(Path(created["session_file"]))["parts"] == []
    assert client.received == []


def test_remote_verification_mismatch_has_protocol_exit_7(tmp_path):
    from pan123_cli.errors import Pan123Error
    from pan123_cli.services.uploading import upload_file

    source = tmp_path / "file.bin"
    source.write_bytes(b"abc")
    client = UploadClient(tmp_path / "cache", b"wrong")
    with pytest.raises(Pan123Error) as caught:
        upload_file(client, source)
    assert caught.value.exit_code == 7


def test_completed_upload_cannot_be_verified_with_rejected_review_status(tmp_path):
    from pan123_cli.errors import Pan123Error
    from pan123_cli.services.uploading import upload_file

    source = tmp_path / "file.bin"
    source.write_bytes(b"abc")
    client = UploadClient(tmp_path / "cache", b"abc")
    original = client.request

    def request(method, path, **kwargs):
        data = original(method, path, **kwargs)
        if path.endswith("/detail"):
            data["status"] = 101
        return data

    client.request = request
    with pytest.raises(Pan123Error) as caught:
        upload_file(client, source)
    assert caught.value.exit_code == 7


def test_detail_visibility_deadline_reports_verification_failure_not_completion_timeout(
    tmp_path, monkeypatch
):
    from pan123_cli.errors import Pan123Error
    from pan123_cli.services import uploading

    source = tmp_path / "file.bin"
    source.write_bytes(b"abc")
    client = UploadClient(tmp_path / "cache", b"abc", reuse=True)
    original = client.request
    clock = [0.0]

    def request(method, path, **kwargs):
        if path.endswith("/detail"):
            clock[0] += 9.5
            raise Pan123Error("UPSTREAM_ERROR", "File not visible yet", api_code=5066)
        return original(method, path, **kwargs)

    client.request = request
    monkeypatch.setattr(uploading.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(
        uploading.time, "sleep", lambda delay: clock.__setitem__(0, clock[0] + delay)
    )
    with pytest.raises(Pan123Error) as caught:
        uploading.upload_file(client, source)
    assert caught.value.kind == "VERIFY_FAILED"
    assert caught.value.exit_code == 7
    assert clock[0] == 10


def _created_v2_session(tmp_path, content=b"abcdefgh"):
    from pan123_cli.services.uploading import dispatch_upload

    client = UploadClient(tmp_path / "cache", content)
    created = dispatch_upload(
        client,
        ("file", "upload-api", "v2", "create"),
        {
            "parentFileID": 0,
            "filename": "file.bin",
            "etag": hashlib.md5(content).hexdigest(),
            "size": len(content),
        },
        {"request_file": "input.json"},
    )
    return client, created["session_file"]


@pytest.mark.parametrize("same_slice", [False, True])
def test_session_serializes_concurrent_slices_and_prevents_duplicate_replay(tmp_path, same_slice):
    from pan123_cli.cache import read_private_json
    from pan123_cli.errors import Pan123Error
    from pan123_cli.services.uploading import dispatch_upload

    client, session_file = _created_v2_session(tmp_path)
    first_part = tmp_path / "first.bin"
    second_part = tmp_path / "second.bin"
    first_part.write_bytes(b"abcd")
    second_part.write_bytes(b"abcd" if same_slice else b"efgh")
    entered = threading.Event()
    release = threading.Event()
    second_request = threading.Event()
    real_upload = client.upload_slice
    request_count = [0]
    counter_lock = threading.Lock()

    def blocked_upload(server, *, data, files):
        with counter_lock:
            request_count[0] += 1
            first = request_count[0] == 1
        if first:
            entered.set()
            assert release.wait(5)
        else:
            second_request.set()
        return real_upload(server, data=data, files=files)

    client.upload_slice = blocked_upload
    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(
            dispatch_upload,
            client,
            ("file", "upload-api", "v2", "slice"),
            {},
            {"session_file": session_file, "slice_no": 1, "slice": str(first_part)},
        )
        assert entered.wait(5)
        second = pool.submit(
            dispatch_upload,
            client,
            ("file", "upload-api", "v2", "slice"),
            {},
            {
                "session_file": session_file,
                "slice_no": 1 if same_slice else 2,
                "slice": str(second_part),
            },
        )
        try:
            entered_together = second_request.wait(0.2)
        finally:
            release.set()
        assert first.result(timeout=5)["uploaded"] is True
        if same_slice:
            with pytest.raises(Pan123Error):
                second.result(timeout=5)
            assert client.received == [b"abcd"]
        else:
            assert second.result(timeout=5)["uploaded"] is True
            assert {part["sliceNo"] for part in read_private_json(Path(session_file))["parts"]} == {
                1,
                2,
            }
        assert not entered_together


def test_json_slice_metadata_cannot_discard_an_incorrect_cli_md5(tmp_path):
    from pan123_cli.errors import Pan123Error
    from pan123_cli.services.uploading import dispatch_upload

    client, session_file = _created_v2_session(tmp_path, b"abcd")
    part = tmp_path / "slice.bin"
    part.write_bytes(b"abcd")
    with pytest.raises(Pan123Error) as caught:
        dispatch_upload(
            client,
            ("file", "upload-api", "v2", "slice"),
            {"sliceNo": 1},
            {
                "request_file": "metadata.json",
                "session_file": session_file,
                "slice": str(part),
                "slice_md5": "0" * 32,
            },
        )
    assert caught.value.exit_code == 7
    assert client.received == []


def test_json_and_cli_slice_hash_conflicts_are_rejected_before_network(tmp_path):
    from pan123_cli.errors import Pan123Error
    from pan123_cli.services.uploading import dispatch_upload

    client, session_file = _created_v2_session(tmp_path, b"abcd")
    part = tmp_path / "slice.bin"
    part.write_bytes(b"abcd")
    with pytest.raises(Pan123Error) as caught:
        dispatch_upload(
            client,
            ("file", "upload-api", "v2", "slice"),
            {"sliceNo": 1, "sliceMD5": "e2fc714c4727ee9395f324cd2e7f331f"},
            {
                "request_file": "metadata.json",
                "session_file": session_file,
                "slice": str(part),
                "slice_md5": "0" * 32,
            },
        )
    assert caught.value.exit_code == 2
    assert client.received == []


@pytest.mark.parametrize("payload", [[1], [], None])
def test_lowlevel_upload_request_file_requires_an_object_before_network(tmp_path, payload):
    from pan123_cli.errors import Pan123Error
    from pan123_cli.services.uploading import dispatch_upload

    client = UploadClient(tmp_path / "cache", b"abc")
    with pytest.raises(Pan123Error) as caught:
        dispatch_upload(
            client,
            ("file", "upload-api", "v2", "domains"),
            payload,
            {"request_file": "invalid.json"},
        )
    assert caught.value.exit_code == 2
    assert client.requests == []
