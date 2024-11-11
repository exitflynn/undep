from pathlib import Path
from typing import Optional
from ..config.models import SourceConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)

class UpdateManager:
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        
    def apply_update(self, source: SourceConfig, diff: str) -> bool:
        target_path = self.workspace_dir / source.target.path
        
        if not target_path.exists():
            logger.error(f"Target file not found: {target_path}")
            return False
            
        # For Phase 1, we'll implement a simple file replacement
        # In later phases, we'll add more sophisticated merge strategies
        try:
            # Backup the original file
            backup_path = target_path.with_suffix(target_path.suffix + '.bak')
            target_path.rename(backup_path)
            
            # Write the updated content
            with open(target_path, 'w') as f:
                f.write(diff)
                
            logger.info(f"Successfully updated {target_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update {target_path}: {str(e)}")
            # Restore from backup if update failed
            if backup_path.exists():
                backup_path.rename(target_path)
            return False