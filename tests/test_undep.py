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
      path: "lib/external/helper.py"
    update:
      frequency: "weekly"
      auto_merge: false
      notifications: ["email"]
"""
    # Create .undep.yaml instead of .undep.yml
    config_path = tmp_path / ".undep.yaml"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(config_content)
    return tmp_path

@pytest.fixture
def mock_github_response(requests_mock):
    """Mock GitHub API responses"""
    content = "def example():\n    return 'test'"
    requests_mock.get(
        "https://api.github.com/repos/exitflynn/PyTubeAPI/contents/mainman.py",
        text=content,
        headers={"Accept": "application/vnd.github.v3.raw"}
    )
    return content

def test_config_loader(temp_project):
    """Test that the config loader can find and load the config file"""
    config, project_root = ConfigLoader.load(temp_project)
    assert config.version == "1.0"
    assert len(config.sources) == 1
    assert project_root == temp_project
    
    source = config.sources[0]
    assert source.source.repo == "exitflynn/PyTubeAPI"
    assert source.source.path == "mainman.py"
    assert source.target.path == "lib/external/helper.py"

def test_source_monitor(temp_project, mock_github_response):
    """Test that the source monitor can fetch and compare files"""
    monitor = SourceMonitor(temp_project)
    config, _ = ConfigLoader.load(temp_project)
    source = config.sources[0]
    
    # Create target directory
    target_path = temp_project / source.target.path
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Test with non-existent local file
    diff, content = monitor.check_updates(source)
    assert content == None
    assert diff is None  # No diff when local file doesn't exist
    
    # Test with different local file
    target_path.write_text("def example():\n    return 'old'")
    
    diff, content = monitor.check_updates(source)
    assert content == mock_github_response
    assert diff is not None
    assert "-    return 'old'" in diff
    assert "+    return 'test'" in diff

def test_update_manager(temp_project):
    """Test that the update manager can apply updates with proper backups"""
    config, _ = ConfigLoader.load(temp_project)
    source = config.sources[0]
    
    # Create the target file and directory
    target_path = temp_project / source.target.path
    target_path.parent.mkdir(parents=True, exist_ok=True)
    original_content = "def example():\n    return 'old'"
    target_path.write_text(original_content)
    
    updater = UpdateManager(temp_project)
    
    # Test successful update
    diff = "\n".join([
        "--- lib/external/helper.py",
        "+++ exitflynn/PyTubeAPI/mainman.py",
        "@@ -1,2 +1,2 @@",
        " def example():",
        "-    return 'old'",
        "+    return 'new'"
    ])
    new_content = "def example():\n    return 'new'"
    
    assert updater.apply_update(source, diff, new_content)
    assert target_path.read_text() == new_content
    
    # Test backup creation
    backup_path = target_path.with_suffix(target_path.suffix + '.bak')
    assert backup_path.exists()
    assert backup_path.read_text() == original_content

def test_full_update_flow(temp_project, mock_github_response):
    """Test the complete update flow from check to apply"""
    config, _ = ConfigLoader.load(temp_project)
    source = config.sources[0]
    
    # Setup initial file and directory
    target_path = temp_project / source.target.path
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text("def example():\n    return 'old'")
    
    # Check for updates
    monitor = SourceMonitor(temp_project)
    diff, content = monitor.check_updates(source)
    assert diff is not None
    assert content is not None
    
    # Apply updates
    updater = UpdateManager(temp_project)
    assert updater.apply_update(source, diff, content)
    assert target_path.read_text() == mock_github_response