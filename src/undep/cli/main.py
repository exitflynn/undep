import click
from pathlib import Path
from typing import Optional
from undep.config.loader import ConfigLoader
from undep.core.monitor import SourceMonitor
from undep.core.updater import UpdateManager
from undep.utils.logger import get_logger

logger = get_logger(__name__)

@click.group()
@click.version_option()
def cli():
    """UnDep - Indirect dependency management system"""
    pass

@cli.command()
@click.option('--project', '-p', type=click.Path(exists=True), 
              help='Path to project directory (default: current directory)')
def init(project: Optional[str]):
    """Initialize UnDep in the project directory"""
    try:
        project_path = Path(project) if project else None
        config, project_root = ConfigLoader.load(project_path)
        click.echo(f"Loaded configuration from {project_root}")
        click.echo(f"Found {len(config.sources)} tracked sources")
    except FileNotFoundError as e:
        logger.error(str(e))
        raise click.ClickException(str(e))

@cli.command()
def check():
    """Check for updates in tracked sources"""
    try:
        config, project_root = ConfigLoader.load()
        monitor = SourceMonitor(project_root)
        
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