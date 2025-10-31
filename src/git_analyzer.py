import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
from logging import Logger
from dataclasses import dataclass


@dataclass
class GitCommit:
    """Represents a git commit"""
    hash: str
    author: str
    email: str
    date: datetime
    message: str
    files_changed: int
    insertions: int
    deletions: int


@dataclass
class GitBranch:
    """Represents a git branch"""
    name: str
    is_current: bool
    last_commit: str
    last_commit_date: datetime


@dataclass
class GitContributor:
    """Represents a git contributor"""
    name: str
    email: str
    commits: int
    insertions: int
    deletions: int


class GitAnalyzer:
    """Analyzes git repository history"""
    
    def __init__(self, repo_path: str, logger: Logger):
        self.repo_path = Path(repo_path)
        self.logger = logger
        self.is_git_repo = self._check_git_repo()
    
    def _check_git_repo(self) -> bool:
        """Check if path is a git repository"""
        git_dir = self.repo_path / '.git'
        return git_dir.exists()
    
    def _run_git_command(self, args: List[str]) -> Optional[str]:
        """Run a git command and return output"""
        try:
            result = subprocess.run(
                ['git'] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                self.logger.warning(f"Git command failed: {' '.join(args)}")
                return None
        except Exception as e:
            self.logger.error(f"Error running git command: {e}")
            return None
    
    def get_current_branch(self) -> Optional[str]:
        """Get current branch name"""
        if not self.is_git_repo:
            return None
        return self._run_git_command(['branch', '--show-current'])
    
    def get_branches(self) -> List[GitBranch]:
        """Get all branches with info"""
        if not self.is_git_repo:
            return []
        
        branches = []
        current_branch = self.get_current_branch()
        
        # Get branch list
        output = self._run_git_command(['branch', '-a', '--format=%(refname:short)'])
        if not output:
            return []
        
        for branch_name in output.split('\n'):
            if not branch_name or 'HEAD' in branch_name:
                continue
            
            # Get last commit info
            commit_info = self._run_git_command([
                'log', branch_name, '-1', 
                '--format=%H|%ci'
            ])
            
            if commit_info:
                parts = commit_info.split('|')
                if len(parts) == 2:
                    branches.append(GitBranch(
                        name=branch_name,
                        is_current=(branch_name == current_branch),
                        last_commit=parts[0][:8],
                        last_commit_date=datetime.fromisoformat(parts[1])
                    ))
        
        return branches
    
    def get_commits(self, limit: int = 50) -> List[GitCommit]:
        """Get recent commits"""
        if not self.is_git_repo:
            return []
        
        commits = []
        
        # Get commit log
        output = self._run_git_command([
            'log', f'-{limit}',
            '--format=%H|%an|%ae|%ci|%s',
            '--shortstat'
        ])
        
        if not output:
            return []
        
        lines = output.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 5:
                    commit_hash = parts[0]
                    author = parts[1]
                    email = parts[2]
                    date_str = parts[3]
                    message = '|'.join(parts[4:])  # Handle messages with |
                    
                    # Parse stats from next non-empty line
                    files_changed = insertions = deletions = 0
                    j = i + 1
                    while j < len(lines):
                        next_line = lines[j].strip()
                        if not next_line:
                            j += 1
                            continue
                        if 'file' in next_line and 'changed' in next_line:
                            # Parse: " 3 files changed, 45 insertions(+), 12 deletions(-)"
                            import re
                            
                            files_match = re.search(r'(\d+)\s+files?\s+changed', next_line)
                            if files_match:
                                files_changed = int(files_match.group(1))
                            
                            insert_match = re.search(r'(\d+)\s+insertion', next_line)
                            if insert_match:
                                insertions = int(insert_match.group(1))
                            
                            delete_match = re.search(r'(\d+)\s+deletion', next_line)
                            if delete_match:
                                deletions = int(delete_match.group(1))
                        break
                    
                    commits.append(GitCommit(
                        hash=commit_hash[:8],
                        author=author,
                        email=email,
                        date=datetime.fromisoformat(date_str),
                        message=message,
                        files_changed=files_changed,
                        insertions=insertions,
                        deletions=deletions
                    ))
            i += 1
        
        return commits
    
    def get_contributors(self) -> List[GitContributor]:
        """Get contributor statistics"""
        if not self.is_git_repo:
            return []
        
        contributors_dict: Dict[str, GitContributor] = {}
        
        # Get all commits with stats
        output = self._run_git_command([
            'log', '--all',
            '--format=%an|%ae',
            '--numstat'
        ])
        
        if not output:
            return []
        
        lines = output.split('\n')
        current_author = None
        current_email = None
        
        for line in lines:
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 2:
                    current_author = parts[0]
                    current_email = parts[1]
                    
                    key = f"{current_author}|{current_email}"
                    if key not in contributors_dict:
                        contributors_dict[key] = GitContributor(
                            name=current_author,
                            email=current_email,
                            commits=0,
                            insertions=0,
                            deletions=0
                        )
                    contributors_dict[key].commits += 1
            
            elif line and current_author and '\t' in line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    try:
                        insertions = int(parts[0]) if parts[0] != '-' else 0
                        deletions = int(parts[1]) if parts[1] != '-' else 0
                        key = f"{current_author}|{current_email}"
                        contributors_dict[key].insertions += insertions
                        contributors_dict[key].deletions += deletions
                    except ValueError:
                        pass
        
        # Sort by commits
        contributors = sorted(
            contributors_dict.values(),
            key=lambda x: x.commits,
            reverse=True
        )
        
        return contributors
    
    def get_file_history(self, file_path: str, limit: int = 10) -> List[GitCommit]:
        """Get commit history for specific file"""
        if not self.is_git_repo:
            return []
        
        commits = []
        output = self._run_git_command([
            'log', f'-{limit}',
            '--format=%H|%an|%ae|%ci|%s',
            '--', file_path
        ])
        
        if not output:
            return []
        
        for line in output.split('\n'):
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 5:
                    commits.append(GitCommit(
                        hash=parts[0][:8],
                        author=parts[1],
                        email=parts[2],
                        date=datetime.fromisoformat(parts[3]),
                        message='|'.join(parts[4:]),
                        files_changed=0,
                        insertions=0,
                        deletions=0
                    ))
        
        return commits
    
    def get_summary(self) -> Dict:
        """Get overall git repository summary"""
        if not self.is_git_repo:
            return {}
        
        # Total commits
        total_commits_output = self._run_git_command(['rev-list', '--count', 'HEAD'])
        total_commits = int(total_commits_output) if total_commits_output else 0
        
        # First commit date
        first_commit_output = self._run_git_command([
            'log', '--reverse', '--format=%ci', '--max-count=1'
        ])
        first_commit_date = None
        if first_commit_output:
            first_commit_date = datetime.fromisoformat(first_commit_output)
        
        # Last commit date
        last_commit_output = self._run_git_command([
            'log', '--format=%ci', '--max-count=1'
        ])
        last_commit_date = None
        if last_commit_output:
            last_commit_date = datetime.fromisoformat(last_commit_output)
        
        # Total contributors
        contributors_output = self._run_git_command(['shortlog', '-sn', '--all'])
        total_contributors = len(contributors_output.split('\n')) if contributors_output else 0
        
        return {
            'is_git_repo': True,
            'current_branch': self.get_current_branch(),
            'total_commits': total_commits,
            'total_contributors': total_contributors,
            'first_commit_date': first_commit_date.isoformat() if first_commit_date else None,
            'last_commit_date': last_commit_date.isoformat() if last_commit_date else None
        }
