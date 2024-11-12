from pathlib import Path
from typing import Optional
from ..config.models import SourceConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)
class UpdateManager:
    def __init__(self, project_root: Path):
        self.project_root = project_root
        
    def apply_update(self, source: SourceConfig, diff: str) -> bool:
        target_path = self.project_root / source.target.path
        
        if not target_path.exists():
            logger.error(f"Target file not found: {target_path}")
            return False
        
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