from pastapress.chunker import TextChunker


def test_text_chunker_basic_split():
    chunker = TextChunker(max_chars_per_chunk=100)
    text = "Dies ist ein Absatz.\n\nUnd hier ist noch einer."
    chunks = chunker.split_text(text)

    assert len(chunks) == 3
    assert chunks[0] == ('text', "Dies ist ein Absatz.")
    assert chunks[1] == ('delimiter', "\n\n")
    assert chunks[2] == ('text', "Und hier ist noch einer.")


def test_text_chunker_reassemble():
    chunker = TextChunker()
    original_text = "Hallo.\n\nWelt.\n\n\nNoch mehr."
    chunks = chunker.split_text(original_text)
    reassembled = chunker.reassemble(chunks)

    assert reassembled == original_text


def test_oversized_paragraph_is_split_at_lines():
    """A paragraph over the limit but with single newlines is split into
    multiple text chunks (secondary split), losslessly."""
    chunker = TextChunker(max_chars_per_chunk=30)
    text = "Zeile eins ist hier.\nZeile zwei ist hier.\nZeile drei ist hier."
    chunks = chunker.split_text(text)

    text_chunks = [c for c in chunks if c[0] == 'text']
    assert len(text_chunks) > 1
    assert all(len(c[1]) <= 30 for c in text_chunks)
    assert chunker.reassemble(chunks) == text


def test_oversized_single_line_is_split_at_whitespace():
    """A single line without newlines is cut at word boundaries."""
    chunker = TextChunker(max_chars_per_chunk=20)
    text = "eins zwei drei vier fuenf sechs sieben acht neun zehn"
    chunks = chunker.split_text(text)

    assert all(len(c[1]) <= 20 for c in chunks)
    # No chunk should cut a word in half: each piece ends at a boundary.
    assert chunker.reassemble(chunks) == text
    for _, content in chunks:
        assert not content or content.endswith(' ') or text.endswith(content)


def test_oversized_line_without_whitespace_hard_cut():
    """Pathological case: no whitespace at all still terminates and is lossless."""
    chunker = TextChunker(max_chars_per_chunk=10)
    text = "a" * 35
    chunks = chunker.split_text(text)

    assert all(len(c[1]) <= 10 for c in chunks)
    assert chunker.reassemble(chunks) == text


def test_roundtrip_various_shapes():
    """Lossless-reconstruction invariant over several tricky inputs."""
    chunker = TextChunker(max_chars_per_chunk=25)
    samples = [
        "",
        "\n\n",
        "  eingerueckt\n\nnormal  ",
        "a\n\n\n\nb",
        "Absatz eins.\n\nAbsatz zwei ist deutlich laenger als das Limit erlaubt.\n\nDrei.",
        "endet mit newline\n",
        "\n\nbeginnt mit delimiter",
    ]
    for text in samples:
        chunks = chunker.split_text(text)
        assert chunker.reassemble(chunks) == text, f"Roundtrip failed for: {text!r}"
