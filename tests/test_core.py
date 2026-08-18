import os
from pastapress.core import PastaPressCore


def test_process_text_string_roundtrip_with_echo_llm(mock_ollama_echo):
    """With a perfectly obedient (echo) LLM the output must equal the input —
    including delimiters, indentation and boundary whitespace. This covers the
    real path through requests/response .strip()."""
    core = PastaPressCore()
    text = "  Erster Absatz mit Einrueckung.\n\nZweiter Absatz.\n\n\nDritter mit trailing space. "
    result = core.process_text_string(text)

    assert result == text
    assert core.last_failed_chunks == 0
    assert core.last_total_chunks == 3


def test_process_text_string_counts_failures(mock_ollama_down):
    core = PastaPressCore()
    text = "Absatz eins.\n\nAbsatz zwei."
    result = core.process_text_string(text)

    # Graceful degradation: originals are kept, failures are counted.
    assert result == text
    assert core.last_failed_chunks == 2
    assert core.last_total_chunks == 2


def test_process_file_end_to_end(tmp_path, mock_ollama_echo):
    core = PastaPressCore()
    input_file = tmp_path / "brief.txt"
    content = "Sehr geehrte Damen und Herren,\n\nhiermit teste ich PastaPress.\n"
    input_file.write_text(content, encoding="utf-8")

    assert core.process_file(str(input_file)) is True

    output_file = tmp_path / "brief_pasta-press.txt"
    assert output_file.exists()
    assert output_file.read_text(encoding="utf-8") == content


def test_process_file_all_chunks_failed_returns_false(tmp_path, mock_ollama_down):
    core = PastaPressCore()
    input_file = tmp_path / "brief.txt"
    input_file.write_text("Inhalt der nicht verarbeitet werden kann.", encoding="utf-8")

    assert core.process_file(str(input_file)) is False
    # No misleading output copy must be written.
    assert not (tmp_path / "brief_pasta-press.txt").exists()


def test_process_file_missing_file_returns_false():
    core = PastaPressCore()
    assert core.process_file("does/not/exist.txt") is False


def test_process_file_custom_suffix_and_output_dir(tmp_path, mock_ollama_echo):
    core = PastaPressCore()
    input_file = tmp_path / "in.txt"
    input_file.write_text("Text.", encoding="utf-8")
    out_dir = tmp_path / "out"

    assert core.process_file(str(input_file), output_dir=str(out_dir), suffix="_x") is True
    assert (out_dir / "in_x.txt").exists()


def test_converted_binary_gets_md_extension(tmp_path, mock_ollama_echo, monkeypatch):
    """A converted binary file must be written as .md and never overwrite the original."""
    core = PastaPressCore()
    fake_docx = tmp_path / "doc.docx"
    fake_docx.write_bytes(b"PK\x03\x04 not a real docx")

    monkeypatch.setattr("pastapress.document_parser.read_text_from_file",
                        lambda path: ("# Konvertierter Inhalt", True))

    assert core.process_file(str(fake_docx), overwrite=True) is True
    output_file = tmp_path / "doc_pasta-press.md"
    assert output_file.exists()
    assert output_file.read_text(encoding="utf-8") == "# Konvertierter Inhalt"
    # Original binary untouched
    assert fake_docx.read_bytes().startswith(b"PK")


def test_get_output_path_overwrite_returns_input():
    core = PastaPressCore()
    assert core.get_output_path(os.path.join("a", "b.txt"), overwrite=True) == os.path.join("a", "b.txt")
