#!/usr/bin/env python3
"""
git2mind - Turn repositories into AI-friendly summaries
MVP Version
Author: @yegekucuk
"""
import logging
from pathlib import Path
import argparse

from src.chunker import SimpleChunker
from src.readers import RepoReader
from src.writers import JsonWriter, MarkdownWriter


def main():
    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)

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
    reader = RepoReader(path=str(repo_path), logger=logger, exclude_patterns=args.exclude)
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
            writer = JsonWriter(logger)
        else:
            writer = MarkdownWriter(logger)
        
        writer.write(str(repo_path), documents, args.output)
        logger.info(f"✓ Output written to: {args.output}")
    else:
        logger.info("Dry run - no output written")
    
    return 0

if __name__ == '__main__':
    exit(main())
