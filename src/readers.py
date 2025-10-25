import fnmatch
from logging import Logger
from pathlib import Path
from typing import List
import pathspec

from src.data_models import Document
from src.parsers import get_parser


class RepoReader:
    """Reads files from a repository directory"""
    
    def __init__(self, path: str, logger:Logger, exclude_patterns: List[str] = None, use_gitignore: bool = True):
        self.path = Path(path)
        self.logger = logger
        self.exclude_patterns = exclude_patterns or []
        self.use_gitignore = use_gitignore
        
        # Add default excludes with proper glob patterns
        self.exclude_patterns.extend([
            '*.pyc', '__pycache__', '__pycache__/*', '.git', '.git/*',
            '.venv', '.venv/*', 'venv', 'venv/*',
            'node_modules', 'node_modules/*', 'dist', 'dist/*', 
            'build', 'build/*', '*.egg-info'
        ])

        if self.use_gitignore:
            logger.info("Using .gitignore for exclusions")
        
        # Load .gitignore patterns if they exist
        self.gitignore_spec = None
        if self.use_gitignore:
            gitignore_path = self.path / '.gitignore'
            if gitignore_path.exists():
                with open(gitignore_path, 'r') as f:
                    gitignore = f.read()
                self.gitignore_spec = pathspec.PathSpec.from_lines(
                    pathspec.patterns.GitWildMatchPattern,
                    gitignore.splitlines()
                )
                self.logger.debug("Loaded .gitignore patterns")

    def should_exclude(self, file_path: Path) -> bool:
        """Check if file should be excluded"""
        relative = file_path.relative_to(self.path)
        rel_str = str(relative)
        
        # First check gitignore patterns if enabled
        if self.use_gitignore and self.gitignore_spec:
            if self.gitignore_spec.match_file(rel_str):
                self.logger.debug(f"File excluded by .gitignore: {rel_str}")
                return True
        
        # Then check our custom exclude patterns
        for pattern in self.exclude_patterns:
            # Check against relative path and filename
            if fnmatch.fnmatch(rel_str, pattern):
                return True
            if fnmatch.fnmatch(file_path.name, pattern):
                return True
            # Check if any parent directory matches
            for parent in relative.parents:
                if fnmatch.fnmatch(parent.name, pattern.rstrip('/*')):
                    return True
        return False
    
    def read_files(self, max_files: int = 1000) -> List[Document]:
        """Read and parse files from repository"""
        documents = []
        file_count = 0
        
        for file_path in self.path.rglob('*'):
            if file_count >= max_files:
                self.logger.warning(f"Reached max files limit ({max_files})")
                break
                
            if not file_path.is_file():
                continue
                
            if self.should_exclude(file_path):
                self.logger.debug(f"Excluding: {file_path}")
                continue
            
            # Skip binary files
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except (UnicodeDecodeError, PermissionError):
                self.logger.debug(f"Skipping binary/inaccessible file: {file_path}")
                continue
            
            # Skip very large files
            if len(content) > 100000:  # 100KB
                self.logger.warning(f"Skipping large file: {file_path}")
                continue
            
            parser = get_parser(file_path)
            relative_path = file_path.relative_to(self.path)
            doc = parser.parse(relative_path, content)
            documents.append(doc)
            file_count += 1
            
            self.logger.debug(f"Processed: {relative_path}")
        
        self.logger.info(f"Read {len(documents)} files from {self.path}")
        return documents
