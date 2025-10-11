from src.data_models import Document, Chunk
from typing import List

class SimpleChunker:
    """Simple line-based chunker"""
    
    def __init__(self, chunk_size: int = 50):  # lines per chunk
        self.chunk_size = chunk_size
    
    def chunk_document(self, doc: Document) -> List[Chunk]:
        """Split document into chunks"""
        lines = doc.content.split('\n')
        chunks = []
        
        for i in range(0, len(lines), self.chunk_size):
            chunk_lines = lines[i:i + self.chunk_size]
            chunk = Chunk(
                doc_id=doc.id,
                path=doc.path,
                content='\n'.join(chunk_lines),
                start_line=i + 1,
                end_line=min(i + self.chunk_size, len(lines))
            )
            chunks.append(chunk)
        
        return chunks
