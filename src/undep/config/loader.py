import yaml
from pathlib import Path
from typing import Optional
from .models import UndepConfig

class ConfigLoader:
    DEFAULT_CONFIG_NAME = ".undep.yaml"
    
    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> UndepConfig:
        if config_path is None:
            config_path = Path.cwd() / cls.DEFAULT_CONFIG_NAME
            
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found at {config_path}")
            
        with open(config_path) as f:
            config_dict = yaml.safe_load(f)
            
        return UndepConfig.model_validate(config_dict)