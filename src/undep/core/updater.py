from pathlib import Path
from typing import Optional
import click
from ..config.models import SourceConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class UpdateManager:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        
    def apply_update(self, source: SourceConfig, diff: str, content: str) -> bool:
        """
        Apply updates to the target file
        Args:
            source: Source configuration
            diff: Diff string for display purposes
            content: Actual new content to write
        """
        target_path = self.project_root / source.target.path
        
        if not target_path.exists():
            logger.error(f"Target file not found: {target_path}")
            return False
        
        try:
            # Display the colorized diff
            for line in diff.splitlines():
                if line.startswith('+'):
                    click.secho(line, fg='green')
                elif line.startswith('-'):
                    click.secho(line, fg='red')
                else:
                    click.echo(line)
            
            # Backup the original file
            backup_path = target_path.with_suffix(target_path.suffix + '.bak')
            target_path.rename(backup_path)
            
            # Write the actual updated content
            with open(target_path, 'w') as f:
                f.write(content)
                
            logger.info(f"Successfully updated {target_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update {target_path}: {str(e)}")
            # Restore from backup if update failed
            if backup_path.exists():
                backup_path.rename(target_path)
            return False