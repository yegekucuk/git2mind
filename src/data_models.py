from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict

@dataclass
class Document:
    """Represents a parsed file"""
    id: str
    path: str
    language: str
    size_bytes: int
    lines: int
    content: str
    meta: Dict[str, Any]
    
    def to_dict(self):
        return asdict(self)

@dataclass
class Chunk:
    """Represents a chunk of content"""
    doc_id: str
    path: str
    content: str
    start_line: int
    end_line: int
    summary: Optional[str] = None
