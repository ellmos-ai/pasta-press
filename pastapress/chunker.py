import re

class TextChunker:
    def __init__(self, max_chars_per_chunk=4000):
        self.max_chars_per_chunk = max_chars_per_chunk

    def split_text(self, text):
        """
        Splits text into chunks preserving delimiters.
        Returns a list of tuples (chunk_type, content) where chunk_type is 'text' or 'delimiter'.
        """
        # Split by double newlines or more to keep paragraphs together
        parts = re.split(r'(\n{2,})', text)
        
        chunks = []
        current_chunk = ""
        
        for i, part in enumerate(parts):
            is_delimiter = (i % 2 != 0)
            
            if is_delimiter:
                if current_chunk:
                    chunks.append(('text', current_chunk))
                    current_chunk = ""
                chunks.append(('delimiter', part))
            else:
                if len(current_chunk) + len(part) > self.max_chars_per_chunk and current_chunk:
                    chunks.append(('text', current_chunk))
                    current_chunk = part
                else:
                    # Ansonsten fügen wir es zusammen (hier gibt es eigtl. immer einen delimiter dazwischen, 
                    # aber für den Fall der Fälle)
                    current_chunk += part
                    
        if current_chunk:
            chunks.append(('text', current_chunk))
            
        return chunks

    def split_into_process_batches(self, chunks):
        """
        Combines 'text' and 'delimiter' chunks into larger batches for the LLM 
        to process at once, up to max_chars_per_chunk.
        """
        batches = []
        current_batch = []
        current_length = 0
        
        for chunk_type, content in chunks:
            if chunk_type == 'text':
                if current_length + len(content) > self.max_chars_per_chunk and current_batch:
                    batches.append(current_batch)
                    current_batch = [(chunk_type, content)]
                    current_length = len(content)
                else:
                    current_batch.append((chunk_type, content))
                    current_length += len(content)
            else:
                current_batch.append((chunk_type, content))
                current_length += len(content)
                
        if current_batch:
            batches.append(current_batch)
            
        return batches
        
    def reassemble(self, chunks):
        """
        Reassembles a list of (chunk_type, content) tuples into a string.
        """
        return "".join([content for _, content in chunks])
