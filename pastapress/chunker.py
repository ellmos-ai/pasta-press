import re


class TextChunker:
    def __init__(self, max_chars_per_chunk=4000):
        self.max_chars_per_chunk = max_chars_per_chunk

    def split_text(self, text):
        """
        Splits text into chunks preserving delimiters.
        Returns a list of tuples (chunk_type, content) where chunk_type is 'text' or 'delimiter'.

        Invariant: concatenating all chunk contents in order reproduces the
        input text exactly (lossless reconstruction).
        """
        # Split by double newlines or more to keep paragraphs together
        parts = re.split(r'(\n{2,})', text)

        chunks = []
        current_chunk = ""

        for i, part in enumerate(parts):
            is_delimiter = (i % 2 != 0)

            if is_delimiter:
                if current_chunk:
                    chunks.extend(self._emit_text(current_chunk))
                    current_chunk = ""
                chunks.append(('delimiter', part))
            else:
                if len(current_chunk) + len(part) > self.max_chars_per_chunk and current_chunk:
                    chunks.extend(self._emit_text(current_chunk))
                    current_chunk = part
                else:
                    current_chunk += part

        if current_chunk:
            chunks.extend(self._emit_text(current_chunk))

        return chunks

    def _emit_text(self, text):
        """
        Emits a text part as one or more 'text' chunks. Parts longer than
        max_chars_per_chunk are split further (secondary split) so that no
        single chunk exceeds the LLM-friendly size:
        1. accumulate whole lines up to the limit,
        2. cut oversized single lines at the last whitespace before the limit,
        3. hard-cut only if a segment contains no whitespace at all.
        The concatenation of all emitted chunks equals the input text.
        """
        if len(text) <= self.max_chars_per_chunk:
            return [('text', text)]

        pieces = []
        buffer = ""
        for line in text.splitlines(keepends=True):
            if len(buffer) + len(line) > self.max_chars_per_chunk and buffer:
                pieces.append(buffer)
                buffer = ""
            if len(line) > self.max_chars_per_chunk:
                pieces.extend(self._split_long_line(line))
                continue
            buffer += line
        if buffer:
            pieces.append(buffer)

        return [('text', piece) for piece in pieces]

    def _split_long_line(self, line):
        """Splits a single line longer than max_chars_per_chunk, preferring whitespace boundaries."""
        segments = []
        remaining = line
        limit = self.max_chars_per_chunk
        while len(remaining) > limit:
            window = remaining[:limit]
            # Cut after the last whitespace run inside the window so words stay intact.
            match = None
            for match in re.finditer(r'\s+', window):
                pass
            cut = match.end() if match and match.end() > 0 else limit
            segments.append(remaining[:cut])
            remaining = remaining[cut:]
        if remaining:
            segments.append(remaining)
        return segments

    def reassemble(self, chunks):
        """
        Reassembles a list of (chunk_type, content) tuples into a string.
        """
        return "".join([content for _, content in chunks])
