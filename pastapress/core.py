import os
from .config import CONFIG, logger
from .chunker import TextChunker
from .llm_client import LLMClient, LLMProcessingError


class PastaPressCore:
    def __init__(self):
        self.chunker = TextChunker()
        self.llm = LLMClient()
        # Number of text chunks that failed during the last process_text_string call.
        self.last_failed_chunks = 0
        self.last_total_chunks = 0

    def process_text_string(self, text, style=None, target_language=None):
        """Verarbeitet einen String direkt über den LLM Workflow."""
        logger.info("Starting text processing...")
        chunks = self.chunker.split_text(text)

        processed_chunks = []
        text_chunk_count = sum(1 for c in chunks if c[0] == 'text')
        current = 0
        failed = 0

        for chunk_type, content in chunks:
            if chunk_type == 'delimiter':
                processed_chunks.append((chunk_type, content))
                continue

            current += 1
            logger.info(f"Processing text chunk {current}/{text_chunk_count}...")
            stripped = content.strip()
            if not stripped:
                processed_chunks.append((chunk_type, content))
                continue

            # Preserve leading/trailing whitespace (indentation, newlines at
            # chunk boundaries) — the LLM only sees the stripped core, so
            # reconstruction stays lossless even though responses are stripped.
            leading_ws = content[:len(content) - len(content.lstrip())]
            trailing_ws = content[len(content.rstrip()):]

            try:
                processed_content = self.llm.process_text(stripped, style=style, target_language=target_language)
            except LLMProcessingError as e:
                logger.error(f"Chunk {current}/{text_chunk_count} failed, keeping original text: {e}")
                failed += 1
                processed_content = stripped

            processed_chunks.append((chunk_type, leading_ws + processed_content + trailing_ws))

        self.last_failed_chunks = failed
        self.last_total_chunks = text_chunk_count

        if failed:
            logger.warning(f"Text processing completed with {failed}/{text_chunk_count} failed chunks (originals kept).")
        else:
            logger.info("Text processing completed.")

        return self.chunker.reassemble(processed_chunks)

    def get_output_path(self, input_path, overwrite=False, output_dir=None, suffix=None, forced_ext=None):
        if overwrite and forced_ext is None:
            return input_path

        if output_dir is None:
            output_dir = CONFIG.get("default_output_dir")

        if suffix is None:
            suffix = CONFIG.get("output_suffix", "_pasta-press")

        dir_name = os.path.dirname(input_path)
        base_name = os.path.basename(input_path)
        name, ext = os.path.splitext(base_name)

        if forced_ext is not None:
            ext = forced_ext

        new_name = f"{name}{suffix}{ext}"

        target_dir = output_dir if output_dir else dir_name

        # Sicherstellen, dass Zielverzeichnis existiert
        if target_dir and not os.path.exists(target_dir):
            os.makedirs(target_dir)

        return os.path.join(target_dir, new_name)

    def process_file(self, input_path, overwrite=False, output_dir=None, suffix=None, style=None, target_language=None):
        logger.info(f"Reading file: {input_path}")
        if not os.path.exists(input_path):
            logger.error(f"File not found: {input_path}")
            return False

        from .document_parser import read_text_from_file

        try:
            text, was_converted = read_text_from_file(input_path)
        except Exception as e:
            logger.error(f"Failed to read file: {e}")
            return False

        processed_text = self.process_text_string(text, style=style, target_language=target_language)

        # If every single chunk failed (e.g. Ollama unreachable), writing an
        # unmodified copy and reporting success would be misleading.
        if self.last_total_chunks > 0 and self.last_failed_chunks == self.last_total_chunks:
            logger.error("All chunks failed to process. No output file written.")
            return False

        # If it was converted from a binary format, force output extension to .md
        # because saving it back as .docx with raw markdown text would corrupt the file format.
        forced_ext = None
        if was_converted:
            forced_ext = ".md"
            if overwrite:
                logger.warning("Cannot overwrite original binary file directly. Saving as .md instead.")
                overwrite = False

        if overwrite:
            output_path = input_path
        else:
            output_path = self.get_output_path(input_path, overwrite=False, output_dir=output_dir,
                                               suffix=suffix, forced_ext=forced_ext)

        logger.info(f"Saving result to: {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(processed_text)

        return True
