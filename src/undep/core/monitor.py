from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import requests
import hashlib
from ..config.models import SourceConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class SourceMonitor:
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.github_api_base = "https://api.github.com/repos"
        
    def _get_source_content(self, repo: str, path: str, ref: str = "main") -> Optional[str]:
        """Fetch file content from GitHub API"""
        url = f"{self.github_api_base}/{repo}/contents/{path}?ref={ref}"
        headers = {"Accept": "application/vnd.github.v3.raw"}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to fetch file from GitHub: {e}")
            return None

    def check_updates(self, source: SourceConfig) -> Optional[str]:
        # Get the local file path
        local_path = self.project_root / source.target.path
        
        # Get current version from GitHub
        source_content = self._get_source_content(source.source.repo, source.source.path)
        if not source_content:
            return None
            
        # Compare with local file
        if local_path.exists():
            with open(local_path, 'r') as f:
                local_content = f.read()
                
            if local_content != source_content:
                # Create a diff
                from difflib import unified_diff
                diff = '\n'.join(unified_diff(
                    local_content.splitlines(),
                    source_content.splitlines(),
                    fromfile=str(local_path),
                    tofile=f"{source.source.repo}/{source.source.path}",
                    lineterm=''
                ))
                return diff if diff else None
        else:
            logger.warning(f"Local file not found: {local_path}")
            
        return None

    def apply_updates(self, source: SourceConfig) -> bool:
        """Apply updates from source to local file"""
        source_content = self._get_source_content(source.source.repo, source.source.path)
        if not source_content:
            return False

        local_path = self.project_root / source.local_path
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(local_path, 'w') as f:
            f.write(source_content)
        
        return True