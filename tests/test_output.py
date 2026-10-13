from pan123_cli.output import emit


def test_legacy_list_human_output_includes_file_id(capsys):
    emit(
        {
            "ok": True,
            "data": {
                "items": [{"fileID": 7654321, "filename": "旧版文件.txt", "type": 0}],
                "complete": True,
                "next_cursor": None,
            },
        }
    )
    assert "7654321" in capsys.readouterr().out
