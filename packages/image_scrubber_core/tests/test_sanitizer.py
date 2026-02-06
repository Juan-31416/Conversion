from filenames.sanitizer import FilenameSanitizer


def test_sanitize_basic():
    assert FilenameSanitizer.sanitize("Mi Foto Bonita") == "mi-foto-bonita.jpg"


def test_sanitize_special_chars():
    assert FilenameSanitizer.sanitize("foto@@@###.png") == "foto.jpg"


def test_sanitize_empty():
    assert FilenameSanitizer.sanitize("") == "image.jpg"