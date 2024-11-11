from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import git
from ..config.models import SourceConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class SourceMonitor:
    def __init__(self, cache_dir: Path = Path(".undep/cache")):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._repos: Dict[str, git.Repo] = {}
        
    def get_repo(self, repo_url: str) -> git.Repo:
        if repo_url not in self._repos:
            repo_path = self.cache_dir / repo_url.replace("/", "_")
            if not repo_path.exists():
                logger.info(f"Cloning repository: {repo_url}")
                repo = git.Repo.clone_from(
                    f"https://github.com/{repo_url}.git",
                    repo_path
                )
            else:
                repo = git.Repo(repo_path)
            self._repos[repo_url] = repo
        return self._repos[repo_url]
    
    def check_updates(self, source: SourceConfig) -> Optional[str]:
        repo = self.get_repo(source.source.repo)
        repo.remotes.origin.fetch()
        
        current = repo.head.commit
        repo.remotes.origin.pull()
        
        if current != repo.head.commit:
            file_path = Path(source.source.path)
            diff = repo.git.diff(current.hexsha, repo.head.commit.hexsha, str(file_path))
            if diff:
                return diff
        return None