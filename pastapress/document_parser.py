import os
from .config import logger

try:
    import pypandoc
except ImportError:
    pypandoc = None

SUPPORTED_FORMATS = ['.txt', '.md', '.csv', '.json', '.yaml', '.yml', '.doc', '.docx', '.rtf', '.odt', '.tex']
PANDOC_FORMATS = ['.doc', '.docx', '.rtf', '.odt']

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
    
    if ext in PANDOC_FORMATS:
        if not ensure_pandoc():
            raise RuntimeError("Pandoc is required to read this file format, but it is not available.")
        
        logger.info(f"Converting {ext} file to markdown using Pandoc...")
        text = pypandoc.convert_file(file_path, 'md')
        return text, True
    else:
        # Standard plain text
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read(), False
