import click


@click.group()
def main():
    """ESA DTE-S2GOS client"""
    click.echo("Hello, this is the S2GOS client CLI")


@main.command()
@click.option('--name', default="s2gos-request.yaml")
def create(name: str):
    """Create a processing request from template"""
    click.echo(f"Creating {name}")


@main.command()
@click.option('--name', default="s2gos-request.yaml")
def validate(name: str):
    """Validate a processing request"""
    click.echo(f"Validating {name}")


@main.command()
@click.option('--name', default="s2gos-request.yaml")
def submit(name: str):
    """Submit a processing request"""
    click.echo(f"Submitting {name}")


@main.command()
@click.option('--id')
def poll(id: str):
    """Poll the status for an existing processing job"""
    click.echo(f"Polling {id}")
