import os
from .config import CONFIG, logger
from .chunker import TextChunker
from .llm_client import LLMClient

class PastaPressCore:
    def __init__(self):
        self.chunker = TextChunker()
        self.llm = LLMClient()

    def process_text_string(self, text):
        """Verarbeitet einen String direkt über den LLM Workflow."""
        logger.info("Starting text processing...")
        chunks = self.chunker.split_text(text)
        
        processed_chunks = []
        text_chunk_count = sum(1 for c in chunks if c[0] == 'text')
        current = 0
        
        for chunk_type, content in chunks:
            if chunk_type == 'delimiter':
                processed_chunks.append((chunk_type, content))
            else:
                current += 1
                logger.info(f"Processing text chunk {current}/{text_chunk_count}...")
                if not content.strip():
                    processed_chunks.append((chunk_type, content))
                    continue
                    
                processed_content = self.llm.process_text(content)
                processed_chunks.append((chunk_type, processed_content))
            
        logger.info("Text processing completed.")
        
        final_text = self.chunker.reassemble(processed_chunks)
        return final_text

    def get_output_path(self, input_path, overwrite=False, output_dir=None, suffix=None):
        if overwrite:
            return input_path
            
        if output_dir is None:
            output_dir = CONFIG.get("default_output_dir")
            
        if suffix is None:
            suffix = CONFIG.get("output_suffix", "_pasta-press")
            
        dir_name = os.path.dirname(input_path)
        base_name = os.path.basename(input_path)
        name, ext = os.path.splitext(base_name)
        
        new_name = f"{name}{suffix}{ext}"
        
        target_dir = output_dir if output_dir else dir_name
        
        # Sicherstellen, dass Zielverzeichnis existiert
        if target_dir and not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        return os.path.join(target_dir, new_name)

    def process_file(self, input_path, overwrite=False, output_dir=None, suffix=None):
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
            
        processed_text = self.process_text_string(text)
        
        # If it was converted from a binary format, force output extension to .md
        # because saving it back as .docx with raw markdown text would corrupt the file format.
        dir_name = os.path.dirname(input_path)
        base_name = os.path.basename(input_path)
        name, ext = os.path.splitext(base_name)
        
        if was_converted:
            ext = ".md"
            # Never overwrite original binary file with a markdown file of the same name but wrong extension
            # actually we can overwrite but we should rename the extension.
            # However, --overwrite usually implies exact same file. 
            # We'll just write it as .md next to it if we converted it, to avoid deleting their docx.
            if overwrite:
                logger.warning("Cannot overwrite original binary file directly. Saving as .md instead.")
                overwrite = False
                
        if overwrite:
            output_path = input_path
        else:
            if output_dir is None:
                output_dir = CONFIG.get("default_output_dir")
            if suffix is None:
                suffix = CONFIG.get("output_suffix", "_pasta-press")
                
            new_name = f"{name}{suffix}{ext}"
            target_dir = output_dir if output_dir else dir_name
            
            if target_dir and not os.path.exists(target_dir):
                os.makedirs(target_dir)
                
            output_path = os.path.join(target_dir, new_name)
        
        logger.info(f"Saving result to: {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(processed_text)
            
        return True
