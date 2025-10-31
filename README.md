# git2mind

**Turn Python repositories into AI-friendly format (.md / .json/ .xml)**

git2mind scans a git repository, analyzes commits, branches, and contributors, extracts and chunks files intelligently, and produces concise Markdown, JSON or XML summaries that are ready for LLM consumption. Perfect for onboarding and documentation generation.

## 🚀 Features

- ✅ Basic CLI with essential flags
- ✅ Local repository scanning
- ✅ Analyze commits, branches and contributors
- ✅ Create project structure tree
- ✅ Gitignore file support & custom exclusions
- ✅ Exclude binary files and common ignore patterns
- ✅ Python, Markdown, Dockerfile and License parsers
- ✅ Simple line-based chunking
- ✅ Multiple output formats
- ✅ [PyPI package](https://pypi.org/project/git2mind/)

## 📦 Installation

```bash
# Install from PyPI
pip install git2mind

# or install from source
git clone https://github.com/yegekucuk/git2mind.git
pip install -e git2mind
```

## 🎯 Usage

### Basic Usage

```bash
# Generate summary of current directory (markdown by default)
g2m .

# Generate XML summary of current directory
g2m . -f xml

# Specify the name of output file & use gitignore to exclude files
g2m /path/to/repo -o summary.md -g

# Exclude specific patterns
g2m ./my-repo --exclude "tests" --exclude "*.log" --format md --output summary.md

# Verbose output with custom chunk size
g2m . --verbose --chunk-size 100 --format json
```

### Command Line Options

```
Usage: g2m PATH [OPTIONS]

Options:
  -f, --format [md|json|xml]    Output format (default: md)
  -o, --output PATH             Output file path (default: ./git2mind_output.[md|json|xml])
  --exclude PATTERN             Exclude path pattern (can be repeated)
  -g, --gitignore               Use .gitignore to exclude files
  --git-commits INT             Number of recent commits to include (default: 20)
  --chunk-size INT              Lines per chunk (default: 50)
  --max-files INT               Max files to process (default: 1000)
  --dry-run                     Do everything except writing output
  -v, --verbose                 Verbose logging
  -h, --help                    Show help message
```

## 📋 Default Exclusions

The following patterns are excluded by default:
- `*.pyc`, `__pycache__`
- `.git`, `.venv`, `venv`
- `node_modules`, `dist`, `build`
- `*.egg-info`
- Binary files
- Files larger than 100KB

## 🤝 Use Cases

- **Documentation Generation** - Create automatic project overviews
- **Onboarding** - Help new team members understand codebases
- **AI Context Preparation** - Prepare repositories for LLM analysis
- **Project Auditing** - Quick overview of project structure and content

## 📝 License

- Author: Yunus Ege Küçük
- MIT License - see [LICENSE](LICENSE) file for details
