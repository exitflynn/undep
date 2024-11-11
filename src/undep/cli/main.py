import click
from pathlib import Path
from typing import Optional
from ..config.loader import ConfigLoader
from ..core.monitor import SourceMonitor
from ..core.updater import UpdateManager
from ..utils.logger import get_logger

logger = get_logger(__name__)

@click.group()
@click.version_option()
def cli():
    """UnDep - Indirect dependency management system"""
    pass

@cli.command()
@click.option('--config', '-c', type=click.Path(exists=True), help='Path to config file')
def init(config: Optional[str]):
    """Initialize UnDep in the current directory"""
    try:
        config_path = Path(config) if config else None
        config = ConfigLoader.load(config_path)
        click.echo(f"Loaded configuration with {len(config.sources)} sources")
    except Exception as e:
        logger.error(f"Failed to initialize: {str(e)}")
        raise click.ClickException(str(e))

@cli.command()
def check():
    """Check for updates in tracked sources"""
    try:
        config = ConfigLoader.load()
        monitor = SourceMonitor()
        
        for source in config.sources:
            diff = monitor.check_updates(source)
            if diff:
                click.echo(f"Updates available for {source.source.repo}:{source.source.path}")
            else:
                click.echo(f"No updates for {source.source.repo}:{source.source.path}")
    except Exception as e:
        logger.error(f"Failed to check updates: {str(e)}")
        raise click.ClickException(str(e))

@cli.command()
@click.option('--yes', '-y', is_flag=True, help='Automatically approve all updates')
def update(yes: bool):
    """Apply available updates"""
    try:
        config = ConfigLoader.load()
        monitor = SourceMonitor()
        updater = UpdateManager(Path.cwd())
        
        for source in config.sources:
            diff = monitor.check_updates(source)
            if diff:
                if yes or click.confirm(f"Update {source.source.path}?"):
                    if updater.apply_update(source, diff):
                        click.echo(f"Successfully updated {source.target.path}")
                    else:
                        click.echo(f"Failed to update {source.target.path}")
    except Exception as e:
        logger.error(f"Failed to apply updates: {str(e)}")
        raise click.ClickException(str(e))

if __name__ == "__main__":
    cli()