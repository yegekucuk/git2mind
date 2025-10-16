from datetime import datetime
import json
from logging import Logger
from pathlib import Path
from typing import List

from src.data_models import Document


class MarkdownWriter:
    """Writes output in Markdown format"""
    def __init__(self, logger:Logger):
        self.logger = logger
    
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
        
        self.logger.info(f"Wrote markdown output to {output_path}")

class JsonWriter:
    def __init__(self, logger:Logger):
        self.logger = logger
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
        
        self.logger.info(f"Wrote JSON output to {output_path}")
