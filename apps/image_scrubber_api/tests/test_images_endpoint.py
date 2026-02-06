from pathlib import Path

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_scrub_image(tmp_path: Path):
    img_path = tmp_path / "test.jpg"
    img_path.write_bytes(b"\xff\xd8\xff\xe0" + b"0" * 100)  # JPEG dummy minimal

    with img_path.open("rb") as f:
        response = client.post(
            "/images/scrub",
            files={"file": ("test.jpg", f, "image/jpeg")},
        )

    assert response.status_code == 200
    data = response.json()
    assert "output_filename" in data
    assert "sha256" in data