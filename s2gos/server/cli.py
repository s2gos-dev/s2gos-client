#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import typer

from s2gos.version import VERSION
from .defaults import DEFAULT_HOST, DEFAULT_PORT


cli = typer.Typer()


@cli.command()
def version():
    """Show server version."""
    typer.echo(f"Version {VERSION}")


@cli.command()
def run(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
):
    """Run server in production mode."""
    run_server(host=host, port=port, reload=False)


@cli.command()
def dev(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
):
    """Run server in development mode."""
    run_server(host=host, port=port, reload=True)


def run_server(**kwargs):
    import uvicorn

    # params = ", ".join(f"{k}={v}" for k, v in kwargs.items())
    # print(f"Starting with {params}")
    uvicorn.run("s2gos.server.main:app", **kwargs)


if __name__ == "__main__":
    cli()
