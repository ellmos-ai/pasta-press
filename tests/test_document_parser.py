import pytest
from pastapress.document_parser import read_text_from_file, SUPPORTED_FORMATS, TEXT_FORMATS, PANDOC_FORMATS


def test_reads_plain_utf8(tmp_path):
    f = tmp_path / "plain.txt"
    f.write_text("Hallo Welt mit Umlauten: äöüß", encoding="utf-8")
    text, converted = read_text_from_file(str(f))
    assert text == "Hallo Welt mit Umlauten: äöüß"
    assert converted is False


def test_utf8_bom_is_stripped(tmp_path):
    f = tmp_path / "bom.txt"
    f.write_bytes(b"\xef\xbb\xbf" + "Text mit BOM".encode("utf-8"))
    text, _ = read_text_from_file(str(f))
    assert text == "Text mit BOM"


def test_cp1252_fallback(tmp_path):
    f = tmp_path / "legacy.txt"
    f.write_bytes("Grüße aus Bernau".encode("cp1252"))
    text, _ = read_text_from_file(str(f))
    assert text == "Grüße aus Bernau"


def test_legacy_doc_raises_clear_error(tmp_path):
    f = tmp_path / "old.doc"
    f.write_bytes(b"\xd0\xcf\x11\xe0 legacy word file")
    with pytest.raises(RuntimeError, match=r"\.doc"):
        read_text_from_file(str(f))


def test_supported_formats_are_consistent():
    assert set(SUPPORTED_FORMATS) == set(TEXT_FORMATS) | set(PANDOC_FORMATS)
    assert '.doc' not in SUPPORTED_FORMATS
    assert '.docx' in PANDOC_FORMATS
