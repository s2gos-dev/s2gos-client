#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import os
import click

from .defaults import DEFAULT_REQUEST_FILE, DEFAULT_SERVER_URL


class AliasedGroup(click.Group):
    @staticmethod
    def to_alias(name: str):
        return "".join(map(lambda n: n[0], name.split("-")))

    def get_command(self, ctx, cmd_name):
        rv = super().get_command(ctx, cmd_name)

        if rv is not None:
            return rv

        matches = [
            x
            for x in self.list_commands(ctx)
            if cmd_name == x or cmd_name == self.to_alias(x)
        ]

        if not matches:
            return None

        if len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])

        ctx.fail(f"Too many matches: {', '.join(sorted(matches))}")

    def resolve_command(self, ctx, args):
        # always return the full command name
        _, cmd, args = super().resolve_command(ctx, args)
        return cmd.name, cmd, args

    def list_commands(self, ctx):
        # prevent alphabetical ordering
        return list(self.commands)


@click.group(name="s2gos", cls=AliasedGroup)
def main():
    """Client tool for the ESA synthetic scene generator service DTE-S2GOS.

    The tool provides commands for managing processing request templates,
    processing requests, processing jobs, and gets processing results.

    You can use shorter command name aliases, e.g., use command name "vr"
    instead of "validate-request", or "lt" instead of "list-templates".
    """


@main.command()
@click.option("--user", "user_name")
@click.option("--token", "access_token")
@click.option("--url", "server_url")
def configure(user_name: str, access_token: str, server_url: str):
    """Configure the S2GOS client."""
    from .config import Config

    config = Config.get()
    if not user_name:
        user_name = click.prompt(
            "User name",
            default=(config and config.user_name)
            or os.environ.get("USER", os.environ.get("USERNAME")),
        )
    if not access_token:
        prev_access_token = config and config.access_token
        _access_token = click.prompt(
            "Access token",
            type=str,
            hide_input=True,
            default="*****" if prev_access_token else None,
        )
        if _access_token == "*****" and prev_access_token:
            access_token = prev_access_token
        else:
            access_token = _access_token
    if not server_url:
        server_url = click.prompt(
            "Server URL",
            default=(config and config.server_url) or DEFAULT_SERVER_URL,
        )
    config_path = Config(
        user_name=user_name, access_token=access_token, server_url=server_url
    ).write()
    click.echo(f"Configuration written to {config_path}")


@main.command()
@click.option("--request", "request_file", default=DEFAULT_REQUEST_FILE)
@click.argument("template_name")
def get_template(request_file: str, template_name: str):
    """Get a processing request template."""
    click.echo(f"Fetching template {template_name} and writing to {request_file}")


@main.command()
def list_templates():
    """List available processing request templates."""
    click.echo("Listing available processing request templates")


@main.command()
@click.option("--name", default=DEFAULT_REQUEST_FILE)
def validate_request(name: str):
    """Validate a processing request."""
    click.echo(f"Validating {name}")


@main.command()
@click.option("--name", default=DEFAULT_REQUEST_FILE)
def submit_request(name: str):
    """Submit a processing request."""
    config = _get_config()
    click.echo(f"Submitting request {name} for {config.user_name}")


@main.command()
@click.argument("job_ids", nargs=-1)
def cancel_jobs(job_ids: tuple[str, ...]):
    """Cancel running processing jobs."""
    config = _get_config()
    click.echo(
        f"Cancelling all jobs of {config.user_name}"
        if not job_ids
        else f"Cancelling jobs {job_ids} of {config.user_name}"
    )


@main.command()
@click.argument("job_ids", nargs=-1)
def poll_jobs(job_ids: tuple[str, ...]):
    """Poll the status of processing jobs."""
    config = _get_config()
    click.echo(
        f"Polling all jobs of user {config.user_name}"
        if not job_ids
        else f"Polling jobs {job_ids} of {config.user_name}"
    )


@main.command()
@click.argument("job_ids", nargs=-1)
def get_results(job_ids: tuple[str]):
    """Get processing results."""
    config = _get_config()
    click.echo(f"Getting result of job {job_ids!r} for {config.user_name}")


def _get_config():
    from .config import Config

    config = Config.get()
    if config is None:
        raise click.ClickException(
            "Tool is not yet configured,"
            " please use the 'configure' command to set it up."
        )
    return config
