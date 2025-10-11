#!/usr/bin/env python3
"""
git2mind - Turn repositories into AI-friendly summaries
MVP Version
Author: @yegekucuk
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List
import argparse
import fnmatch

from src.data_models import Document
from src.parsers import *
from src.chunker import SimpleChunker

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class RepoReader:
    """Reads files from a repository directory"""
    
    def __init__(self, path: str, exclude_patterns: List[str] = None):
        self.path = Path(path)
        self.exclude_patterns = exclude_patterns or []
        # Add default excludes with proper glob patterns
        self.exclude_patterns.extend([
            '*.pyc', '__pycache__', '__pycache__/*', '.git', '.git/*',
            '.venv', '.venv/*', 'venv', 'venv/*',
            'node_modules', 'node_modules/*', 'dist', 'dist/*', 
            'build', 'build/*', '*.egg-info'
        ])

    def should_exclude(self, file_path: Path) -> bool:
        """Check if file should be excluded"""
        relative = file_path.relative_to(self.path)
        rel_str = str(relative)
        
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
                logger.warning(f"Reached max files limit ({max_files})")
                break
                
            if not file_path.is_file():
                continue
                
            if self.should_exclude(file_path):
                logger.debug(f"Excluding: {file_path}")
                continue
            
            # Skip binary files
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            except (UnicodeDecodeError, PermissionError):
                logger.debug(f"Skipping binary/inaccessible file: {file_path}")
                continue
            
            # Skip very large files
            if len(content) > 100000:  # 100KB
                logger.warning(f"Skipping large file: {file_path}")
                continue
            
            parser = get_parser(file_path)
            relative_path = file_path.relative_to(self.path)
            doc = parser.parse(relative_path, content)
            documents.append(doc)
            file_count += 1
            
            logger.debug(f"Processed: {relative_path}")
        
        logger.info(f"Read {len(documents)} files from {self.path}")
        return documents

class MarkdownWriter:
    """Writes output in Markdown format"""
    
    def write(self, repo_path: str, documents: List[Document], output_path: str):
        """Generate markdown output"""
        content = []
        content.append(f"# Repo Summary: {Path(repo_path).absolute().name}\n")
        content.append(f"**Generated:** {datetime.now().isoformat()}  ")
        content.append(f"**Files processed:** {len(documents)}\n")
        content.append("## Files\n")
        
        for doc in documents:
            content.append(f"### {doc.path}")
            content.append(f"*Language:* {doc.language}  ")
            content.append(f"*Size:* {doc.size_bytes} bytes, {doc.lines} lines  ")

            # Add metadata
            if doc.language == "python":
                if doc.meta.get("classes", []):
                    content.append(f"*Classes:* {', '.join(doc.meta['classes'])}  ")
                if doc.meta.get("functions", []):
                    content.append(f"*Functions:* {', '.join(doc.meta['functions'])}  ")
            elif doc.language == "markdown":
                if doc.meta.get("headers", []):
                    content.append(f"*Headers:* {', '.join(doc.meta['headers'])}  ")
            elif doc.language == "license":
                if doc.meta.get("header", ""):
                    content.append(f"*Header:* {doc.meta['header']}  ")
            elif doc.language == "dockerfile":
                if doc.meta.get("image", ""):
                    content.append(f"*Image:* {doc.meta['image']}  ")
                if doc.meta.get("workdir", ""):
                    content.append(f"*Workdir:* {doc.meta['workdir']}  ")
                if doc.meta.get("entrypoint", ""):
                    content.append(f"*Entrypoint:* {doc.meta['entrypoint']}  ")
                if doc.meta.get("cmd", ""):
                    content.append(f"*CMD:* {doc.meta['cmd']}  ")
                if doc.meta.get("env", {}):
                    env_str = ', '.join([f"{k}={v}" for k, v in doc.meta['env'].items()])
                    content.append(f"*ENV:* {env_str}  ")            
            
            content.append("")

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        
        logger.info(f"Wrote markdown output to {output_path}")

class JsonWriter:
    """Writes output in JSON format"""
    
    def write(self, repo_path: str, documents: List[Document], output_path: str):
        """Generate JSON output"""
        output = {
            "repo": {
                "name": Path(repo_path).absolute().name,
                "path": str(Path(repo_path).absolute()),
                "generated_at": datetime.now().isoformat(),
                "files_processed": len(documents)
            },
            "files": []
        }
        
        for doc in documents:
            file_info = {
                "path": doc.path,
                "language": doc.language,
                "size_bytes": doc.size_bytes,
                "lines": doc.lines,
                "metadata": {}
            }
            
            if doc.language == "python":
                file_info["metadata"]["functions"] = doc.meta.get("functions", [])
                file_info["metadata"]["classes"] = doc.meta.get("classes", [])
            elif doc.language == "markdown":
                file_info["metadata"]["headers"] = doc.meta.get("headers", [])
            elif doc.language == "license":
                file_info["metadata"]["header"] = doc.meta.get("header", "")
            elif doc.language == "dockerfile":
                file_info["metadata"]["image"] = doc.meta.get("image", "")
                file_info["metadata"]["workdir"] = doc.meta.get("workdir", "")
                file_info["metadata"]["entrypoint"] = doc.meta.get("entrypoint", "")
                file_info["metadata"]["cmd"] = doc.meta.get("cmd", "")
                file_info["metadata"]["env"] = doc.meta.get("env", "")
            
            output["files"].append(file_info)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Wrote JSON output to {output_path}")

def main():
    parser = argparse.ArgumentParser(
        description="git2mind - Turn Python repositories into AI-friendly format.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  git2mind .
  git2mind ./my-repo --format md --output repo_summary.md
  git2mind . --exclude 'tests' --format json
  git2mind /path/to/repo --verbose --chunk-size 100
        """
    )
    
    parser.add_argument('path', help='Path to repository')
    parser.add_argument('-f', '--format', choices=['md', 'json'], default='md',
                       help='Output format (default: md)')
    parser.add_argument('-o', '--output', 
                       help='Output file path (default: ./git2mind_output.[md|json])')
    parser.add_argument('--exclude', action='append', default=[],
                       help='Exclude path pattern (can be repeated)')
    parser.add_argument('--chunk-size', type=int, default=50,
                       help='Lines per chunk (default: 50)')
    parser.add_argument('--max-files', type=int, default=1000,
                       help='Max files to process (default: 1000)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Do everything except writing output')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate path
    repo_path = Path(args.path)
    if not repo_path.exists():
        logger.error(f"Path does not exist: {args.path}")
        return 1
    
    # Set default output path
    if not args.output:
        ext = 'json' if args.format == 'json' else 'md'
        args.output = f"./git2mind_output.{ext}"
    
    logger.info(f"Processing repository: {repo_path}")
    logger.info(f"Output format: {args.format}")
    
    # Read files
    reader = RepoReader(str(repo_path), args.exclude)
    documents = reader.read_files(max_files=args.max_files)
    
    if not documents:
        logger.warning("No files found to process")
        return 1
    
    # Initialize components
    chunker = SimpleChunker(chunk_size=args.chunk_size)
    
    # Process chunks
    total_chunks = 0
    for doc in documents:
        chunks = chunker.chunk_document(doc)
        total_chunks += len(chunks)
    
    logger.info(f"Created {total_chunks} chunks from {len(documents)} documents")
    
    # Write output
    if not args.dry_run:
        if args.format == 'json':
            writer = JsonWriter()
        else:
            writer = MarkdownWriter()
        
        writer.write(str(repo_path), documents, args.output)
        logger.info(f"✓ Output written to: {args.output}")
    else:
        logger.info("Dry run - no output written")
    
    return 0

if __name__ == '__main__':
    exit(main())
