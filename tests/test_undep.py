import os
import pytest
from pathlib import Path
from undep.config.loader import ConfigLoader
from undep.core.monitor import SourceMonitor
from undep.core.updater import UpdateManager
from undep.utils.logger import get_logger

logger = get_logger(__name__)

@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project directory with a sample .undep.yaml"""
    config_content = """
    version: "1.0"
    sources:
      - source:
          repo: "exitflynn/PyTubeAPI"
          branch: "main"
          path: "mainman.py"
        target:
          path: "lib/yt_api.py"
        update:
          frequency: "weekly"
          auto_merge: false
          notifications: ["email"]
    """
    config_path = tmp_path / ".undep.yaml"
    config_path.write_text(config_content)
    return tmp_path

def test_config_loader(temp_project):
    """Test that the config loader can find and load the config file"""
    config, project_root = ConfigLoader.load(temp_project)
    assert config.version == "1.0"
    assert len(config.sources) == 1
    assert project_root == temp_project

def test_source_monitor(temp_project):
    """Test that the source monitor can clone and fetch repositories"""
    monitor = SourceMonitor(temp_project)
    source = next(iter(ConfigLoader.load(temp_project)[0].sources))
    repo = monitor.get_repo(source.source.repo)
    assert repo.working_tree_dir.startswith(str(temp_project / ".undep" / "cache"))
    assert monitor.check_updates(source) is None

def test_update_manager(temp_project):
    """Test that the update manager can apply file-level updates"""
    config, _ = ConfigLoader.load(temp_project)
    source = next(iter(config.sources))
    
    # Create the target file before testing the update
    target_path = temp_project / source.target.path
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text("Original content")
    
    updater = UpdateManager(temp_project)
    
    # Simulate a file update
    assert updater.apply_update(source, "New content")
    assert target_path.read_text() == "New content"