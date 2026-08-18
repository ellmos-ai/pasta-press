import pytest
from pastapress.chunker import TextChunker

def test_text_chunker_basic_split():
    chunker = TextChunker(max_chars_per_chunk=100)
    text = "Dies ist ein Absatz.\n\nUnd hier ist noch einer."
    chunks = chunker.split_text(text)
    
    assert len(chunks) == 3
    assert chunks[0] == ('text', "Dies ist ein Absatz.")
    assert chunks[1] == ('delimiter', "\n\n")
    assert chunks[2] == ('text', "Und hier ist noch einer.")
    
def test_text_chunker_long_paragraph():
    chunker = TextChunker(max_chars_per_chunk=20)
    text = "Dieser Absatz ist ziemlich lang und hat keine Delimiter."
    chunks = chunker.split_text(text)
    
    # Since there's no double newline, it shouldn't split by default unless we implement secondary splitting.
    # Currently it just groups them. Let's see how current chunker behaves.
    assert len(chunks) == 1
    assert chunks[0] == ('text', "Dieser Absatz ist ziemlich lang und hat keine Delimiter.")

def test_text_chunker_reassemble():
    chunker = TextChunker()
    original_text = "Hallo.\n\nWelt.\n\n\nNoch mehr."
    chunks = chunker.split_text(original_text)
    reassembled = chunker.reassemble(chunks)
    
    assert reassembled == original_text
