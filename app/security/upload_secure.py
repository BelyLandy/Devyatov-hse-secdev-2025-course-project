import os
import uuid
from pathlib import Path

MAX_BYTES = 5_000_000
PNG = b"\x89PNG\r\n\x1a\n"
JPEG_SOI = b"\xff\xd8"
JPEG_EOI = b"\xff\xd9"
ALLOWED = {"image/png", "image/jpeg"}


def sniff_image_type(data: bytes) -> str | None:
    if data.startswith(PNG):
        return "image/png"
    if data.startswith(JPEG_SOI) and data.endswith(JPEG_EOI):
        return "image/jpeg"
    return None


def secure_save(base_dir: str, data: bytes) -> str:
    if len(data) > MAX_BYTES:
        raise ValueError("too_big")
    mt = sniff_image_type(data)
    if mt not in ALLOWED:
        raise ValueError("bad_type")

    base = Path(base_dir)
    if os.path.islink(base) or any(p.is_symlink() for p in base.parents):
        raise ValueError("symlink_parent")

    root = base.resolve(strict=True)
    ext = ".png" if mt == "image/png" else ".jpg"
    name = f"{uuid.uuid4()}{ext}"
    path = (root / name).resolve()
    if not str(path).startswith(str(root)):
        raise ValueError("path_traversal")
    if any(p.is_symlink() for p in path.parents):
        raise ValueError("symlink_parent")
    path.write_bytes(data)
    return str(path)
