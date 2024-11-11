import yaml
from pathlib import Path
from typing import Optional
from .models import UndepConfig

class ConfigLoader:
    DEFAULT_CONFIG_NAME = ".undep.yaml"
    
    @classmethod
    def find_project_root(cls, start_path: Optional[Path] = None) -> Path:
        """
        Find the project root by looking for .undep.yaml
        Similar to how git finds .git directory
        """
        if start_path is None:
            start_path = Path.cwd()
        
        current = start_path.absolute()
        while current != current.parent:
            if (current / cls.DEFAULT_CONFIG_NAME).exists():
                return current
            current = current.parent
            
        raise FileNotFoundError(
            f"No {cls.DEFAULT_CONFIG_NAME} found in {start_path} or its parent directories. "
            "Are you inside a project with undep configured?"
        )
    
    @classmethod
    def load(cls, project_path: Optional[Path] = None) -> tuple[UndepConfig, Path]:
        """
        Load config and return both the config and the project root path
        """
        if project_path is None:
            project_root = cls.find_project_root()
        else:
            project_root = cls.find_project_root(project_path)
            
        config_path = project_root / cls.DEFAULT_CONFIG_NAME
            
        with open(config_path) as f:
            config_dict = yaml.safe_load(f)
            
        return UndepConfig.model_validate(config_dict), project_root
