# git2mind

**Turn Python repositories into AI-friendly format (.md / .json)**

git2mind scans a git repository, extracts and chunks files intelligently, and produces concise Markdown or JSON summaries that are ready for LLM consumption — perfect for code review automation, onboarding, and documentation generation.

## 🚀 Features

- **Local repository scanning** - Process any local git repository or directory
- **Multiple output formats** - Generate Markdown or JSON summaries
- **Smart file filtering** - Automatically excludes binary files, build artifacts, and common ignore patterns
- **Language-aware parsing** - Special handling different file types like Python, Markdown and Dockerfile
- **Chunking support** - Split large files into manageable chunks for processing
- **Customizable exclusions** - Add custom patterns to exclude specific files or directories

## 📦 Installation

```bash
# Install from source
git clone https://github.com/yegekucuk/git2mind.git
cd git2mind
pip install -e .

# Install from PyPI (when published)
pip install git2mind
```

## 🎯 Usage

### Basic Usage

```bash
# Generate summary of current directory (markdown by default)
git2mind .

# Generate JSON summary of current directory
git2mind . --format json

# Specify the name of output file
git2mind /path/to/repo --output summary.md

# Exclude specific patterns
git2mind ./my-repo --exclude "tests" --exclude "*.log" --format json --output summary.json

# Verbose output with custom chunk size
git2mind . --verbose --chunk-size 100 --format md
```

### Command Line Options

```
Usage: git2mind PATH [OPTIONS]

Options:
  -f, --format [md|json]    Output format (default: md)
  -o, --output PATH         Output file path (default: ./git2mind_output.[md|json])
  --exclude PATTERN         Exclude path pattern (can be repeated)
  --chunk-size INT          Lines per chunk (default: 50)
  --max-files INT           Max files to process (default: 1000)
  --dry-run                 Do everything except writing output
  -v, --verbose             Verbose logging
  -h, --help                Show help message
```

## 📄 Output Examples

### Markdown Output

```markdown
# Repo Summary: my-project

**Generated:** 2025-10-08T12:00:00  
**Files processed:** 15

---

## Files

### src/main.py
*Language:* python  
*Size:* 2048 bytes, 85 lines  
*Classes:* Application  
*Functions:* main, setup_logging, parse_args

### README.md
*Language:* markdown  
*Size:* 1024 bytes, 45 lines  
*Headers:* Installation, Usage, Contributing
```

### JSON Output

```json
{
  "repo": {
    "name": "my-project",
    "path": "/path/to/my-project",
    "generated_at": "2025-10-08T12:00:00",
    "files_processed": 15
  },
  "files": [
    {
      "path": "src/main.py",
      "language": "python",
      "size_bytes": 2048,
      "lines": 85,
      "metadata": {
        "functions": ["main", "setup_logging"],
        "classes": ["Application"]
      }
    }
  ]
}
```

## 🛠️ Development

### Project Structure

```
git2mind/
├── src/                 # Python source files
├── .gitignore           # Gitignore
├── git2mind.py          # Main file of the project
├── LICENSE              # The MIT License
├── pyproject.toml       # Package configuration
└── README.md            # This file
```

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 🗺️ Roadmap

### Current: MVP (v0.1.0)
- ✅ Basic CLI with essential flags
- ✅ Local repository reading
- ✅ Python, Markdown, and text parsers
- ✅ Simple line-based chunking
- ✅ Markdown and JSON output formats

### Future:
- [ ] PyPI package
- [ ] Configuration file support
- [ ] XML output format
- [ ] Caching system
- [ ] ML/NLP supported solutions for summarizing

## 📋 Default Exclusions

The following patterns are excluded by default:
- `*.pyc`, `__pycache__`
- `.git`, `.venv`, `venv`
- `node_modules`, `dist`, `build`
- `*.egg-info`
- Binary files
- Files larger than 100KB

## 🤝 Use Cases

- **Code Review Automation** - Generate summaries for PR reviews
- **Documentation Generation** - Create automatic project overviews
- **Onboarding** - Help new team members understand codebases
- **AI Context Preparation** - Prepare repositories for LLM analysis
- **Project Auditing** - Quick overview of project structure and content

## 🙏 Acknowledgments

- Inspired by the need to make codebases more accessible to AI models
- Built with Python standard library for maximum compatibility

## 📝 License

- Author: Yunus Ege Küçük.
- MIT License - see [LICENSE](LICENSE) file for details
