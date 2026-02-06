from pathlib import Path

from security.hashing import FileHasher


def test_sha256(tmp_path: Path):
    f = tmp_path / "file.txt"
    f.write_text("test")
    digest = FileHasher.sha256(f)
    assert len(digest) == 64