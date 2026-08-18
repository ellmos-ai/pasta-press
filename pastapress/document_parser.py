import os
from .config import logger

try:
    import pypandoc
except ImportError:
    pypandoc = None

# Formats read directly as plain text.
TEXT_FORMATS = ['.txt', '.md', '.markdown', '.csv', '.json', '.yaml', '.yml', '.tex']
# Binary formats converted to Markdown via Pandoc.
# Note: legacy binary .doc is NOT supported by Pandoc (no reader exists).
PANDOC_FORMATS = ['.docx', '.rtf', '.odt']
SUPPORTED_FORMATS = TEXT_FORMATS + PANDOC_FORMATS


def ensure_pandoc():
    if pypandoc is None:
        return False
    try:
        pypandoc.get_pandoc_version()
        return True
    except OSError:
        logger.info("Pandoc is not installed. Attempting to download via pypandoc...")
        try:
            pypandoc.download_pandoc()
            return True
        except Exception as e:
            logger.error(f"Failed to download Pandoc: {e}")
            return False


def read_text_from_file(file_path):
    """
    Reads text from a file. If it's a Pandoc-supported format, it converts it to Markdown.
    Returns (text, was_converted)
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext == '.doc':
        raise RuntimeError(
            "Legacy binary .doc files are not supported (Pandoc has no .doc reader). "
            "Please convert the file to .docx first."
        )

    if ext in PANDOC_FORMATS:
        if not ensure_pandoc():
            raise RuntimeError("Pandoc is required to read this file format, but it is not available.")

        logger.info(f"Converting {ext} file to markdown using Pandoc...")
        text = pypandoc.convert_file(file_path, 'md')
        return text, True

    # Standard plain text. Try UTF-8 (with BOM handling) first, then fall
    # back to cp1252 which is common for legacy files on Windows.
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            return f.read(), False
    except UnicodeDecodeError:
        logger.warning(f"{file_path} is not valid UTF-8, falling back to cp1252.")
        with open(file_path, 'r', encoding='cp1252') as f:
            return f.read(), False
