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
            
        with open(input_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        processed_text = self.process_text_string(text)
        
        output_path = self.get_output_path(input_path, overwrite, output_dir, suffix)
        
        logger.info(f"Saving result to: {output_path}")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(processed_text)
            
        return True
