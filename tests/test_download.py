"""Verified publication is checked against real files and racing writers."""

import contextlib
import hashlib
from types import SimpleNamespace

import pytest


class StreamResponse:
    def __init__(self, body, *, on_read=None, interrupt=False, encoding=None):
        self.body = body
        self.status_code = 200
        self.headers = {"content-length": str(len(body))}
        if encoding:
            self.headers["content-encoding"] = encoding
        self.on_read = on_read
        self.interrupt = interrupt

    def iter_raw(self, chunk_size=None):
        yield self.body[:2]
        if self.on_read:
            self.on_read()
        if self.interrupt:
            raise KeyboardInterrupt
        yield self.body[2:]


class DownloadClient:
    def __init__(
        self, tmp_path, body=b"abcdef", *, expected=None, filename="source.bin", **stream_options
    ):
        self.settings = SimpleNamespace(cache_dir=tmp_path / "cache")
        self.body = body
        self.expected = body if expected is None else expected
        self.filename = filename
        self.stream_options = stream_options

    def request(self, method, path, *, params=None, **kwargs):
        if path.endswith("/detail"):
            assert params == {"fileID": 509}
            return {
                "fileID": 509,
                "filename": self.filename,
                "type": 0,
                "trashed": 0,
                "status": 0,
                "size": len(self.expected),
                "etag": hashlib.md5(self.expected).hexdigest(),
            }
        assert path.endswith("/download_info") and params == {"fileId": 509}
        return {"downloadUrl": "https://download-cdn.cjjd19.com/file"}

    @contextlib.contextmanager
    def stream_download(self, url):
        yield StreamResponse(self.body, **self.stream_options)


def test_download_publishes_verified_bytes_and_removes_part(tmp_path):
    from pan123_cli.services.downloading import download_file

    final = tmp_path / "final.bin"
    result = download_file(DownloadClient(tmp_path), 509, final)
    assert final.read_bytes() == b"abcdef"
    assert result["verified"] is True
    assert result["md5"] == "e80b5017098950fc58aad83c8c14978e"
    assert result["output_path"] == str(final.resolve())
    assert not list(tmp_path.glob("*.part"))


def test_racing_target_is_not_overwritten(tmp_path):
    from pan123_cli.errors import Pan123Error
    from pan123_cli.services.downloading import download_file

    final = tmp_path / "final.bin"
    client = DownloadClient(tmp_path, on_read=lambda: final.write_bytes(b"another-program"))
    with pytest.raises(Pan123Error):
        download_file(client, 509, final)
    assert final.read_bytes() == b"another-program"
    assert list(tmp_path.glob("*.part"))[0].read_bytes() == b"abcdef"


def test_bad_md5_preserves_part_and_existing_overwrite_target(tmp_path):
    from pan123_cli.errors import Pan123Error
    from pan123_cli.services.downloading import download_file

    final = tmp_path / "final.bin"
    final.write_bytes(b"old-target")
    with pytest.raises(Pan123Error) as caught:
        download_file(
            DownloadClient(tmp_path, body=b"abcdeg", expected=b"abcdef"), 509, final, overwrite=True
        )
    assert caught.value.kind == "VERIFY_FAILED"
    assert caught.value.exit_code == 7
    assert final.read_bytes() == b"old-target"
    assert list(tmp_path.glob("*.part"))[0].read_bytes() == b"abcdeg"


def test_interrupt_preserves_partial_bytes_with_exit_130(tmp_path):
    from pan123_cli.errors import Pan123Error
    from pan123_cli.services.downloading import download_file

    final = tmp_path / "final.bin"
    with pytest.raises(Pan123Error) as caught:
        download_file(DownloadClient(tmp_path, interrupt=True), 509, final)
    assert caught.value.exit_code == 130
    assert list(tmp_path.glob("*.part"))[0].read_bytes() == b"ab"
    assert not final.exists()


def test_symbolic_link_target_is_rejected_even_with_overwrite(tmp_path):
    from pan123_cli.errors import Pan123Error
    from pan123_cli.services.downloading import download_file

    source = tmp_path / "existing.bin"
    source.write_bytes(b"do-not-follow")
    target = tmp_path / "target.bin"
    target.symlink_to(source)
    with pytest.raises(Pan123Error):
        download_file(DownloadClient(tmp_path), 509, target, overwrite=True)
    assert source.read_bytes() == b"do-not-follow"
    assert target.is_symlink()


def test_non_identity_content_encoding_is_rejected(tmp_path):
    from pan123_cli.errors import Pan123Error
    from pan123_cli.services.downloading import download_file

    with pytest.raises(Pan123Error):
        download_file(DownloadClient(tmp_path, encoding="gzip"), 509, tmp_path / "final.bin")


def test_server_filename_cannot_escape_output_directory(tmp_path, monkeypatch):
    from pan123_cli.errors import Pan123Error
    from pan123_cli.services.downloading import download_file

    monkeypatch.chdir(tmp_path)
    with pytest.raises(Pan123Error):
        download_file(DownloadClient(tmp_path, filename="../escape.bin"), 509)
    assert not (tmp_path.parent / "escape.bin").exists()


def test_hardlink_unsupported_retains_verified_part_and_no_final(tmp_path, monkeypatch):
    from pan123_cli.errors import Pan123Error
    from pan123_cli.services.downloading import download_file
    from pan123_cli.utils import files

    def fail_link(*args, **kwargs):
        raise OSError("filesystem has no hardlinks")

    monkeypatch.setattr(files.os, "link", fail_link)
    final = tmp_path / "final.bin"
    with pytest.raises(Pan123Error):
        download_file(DownloadClient(tmp_path), 509, final)
    assert not final.exists()
    assert list(tmp_path.glob("*.part"))[0].read_bytes() == b"abcdef"


@pytest.mark.parametrize("name", ["CON", "AUX.txt", "folder\\file.bin", "bad.", "alternate:stream"])
def test_windows_reserved_filenames_are_rejected(name):
    from pan123_cli.errors import Pan123Error
    from pan123_cli.utils.files import safe_filename

    with pytest.raises(Pan123Error):
        safe_filename(name, windows=True)


def test_zero_byte_download_is_verified_and_published(tmp_path):
    from pan123_cli.services.downloading import download_file

    final = tmp_path / "empty.bin"
    result = download_file(DownloadClient(tmp_path, body=b""), 509, final)
    assert final.read_bytes() == b""
    assert result["size"] == 0
    assert result["md5"] == "d41d8cd98f00b204e9800998ecf8427e"


def test_download_rejects_boolean_metadata_before_fetching_content(tmp_path):
    from pan123_cli.errors import Pan123Error
    from pan123_cli.services.downloading import download_file

    client = DownloadClient(tmp_path)
    original = client.request

    def request(*args, **kwargs):
        data = original(*args, **kwargs)
        data["type"] = False
        return data

    client.request = request
    with pytest.raises(Pan123Error):
        download_file(client, 509, tmp_path / "final.bin")
    assert not list(tmp_path.glob("*.part"))
