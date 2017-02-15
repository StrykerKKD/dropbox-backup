import click
import dropboxbackend


@click.group()
def cli():
    """This is a backup console application for backing up and restoring a directory from dropbox."""


@cli.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True))
@click.password_option()
def backup(directory: str, password: str):
    """Backup the directory to dropbox"""
    click.echo("Backing up %s directory to dropbox." % directory)
    dropboxbackend.backup(directory, password)
    click.echo("Finished backing up %s directory" % directory)


@cli.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True, resolve_path=True))
@click.password_option()
def restore(directory: str, password: str):
    """Restore the directory from dropbox"""
    click.echo("Restoring %s from dropbox." % directory)
    dropboxbackend.restore(directory, password)
    click.echo("Finished restoring %s directory" % directory)


@cli.command()
def list_backups():
    """Listing the backups on dropbox"""
    click.echo("Listing backups:")
    click.echo(dropboxbackend.list_backups())
