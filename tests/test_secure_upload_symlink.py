import os
from pathlib import Path

from app.security.upload_secure import secure_save


def test_secure_save_symlink_parent(tmp_path: Path, monkeypatch):
    inner = tmp_path / "inner"
    inner.mkdir()

    symlink_path = inner / "link_to_parent"
    os.symlink(tmp_path, symlink_path)

    data = b"\x89PNG\r\n\x1a\n" + b"0"
    try:
        secure_save(str(symlink_path), data)
        assert False, "Expected ValueError"
    except ValueError as e:
        assert str(e) == "symlink_parent"
