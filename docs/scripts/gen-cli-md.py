#  Copyright (c) 2025 by ESA DTE-S2GOS team and contributors
#  Permissions are hereby granted under the terms of the Apache 2.0 License:
#  https://opensource.org/license/apache-2-0.

import click
from pathlib import Path
from click.testing import CliRunner
from s2gos.cli import main as cli

OUTPUT_FILE: Path = Path(__file__).parent.parent / "cli.md"


def generate_docs(cli_group: click.Group):
    runner = CliRunner()
    output_lines = []

    # Add main command help
    result = runner.invoke(cli_group, ["--help"])
    output_lines.append("# CLI Reference\n")
    output_lines.append("## Main Command\n")
    output_lines.append(f"```\n{result.output.strip()}\n```\n")

    output_lines.append("## Commands\n")

    # Add each subcommand
    for name, command in cli_group.commands.items():
        result = runner.invoke(cli_group, [name, "--help"])
        if result.exit_code != 0:
            print(f"⚠️ Error generating help for `{name}`")
            continue

        output_lines.append(f"### `{name}`\n")
        output_lines.append(f"```\n{result.output.strip()}\n```\n")

    # Write to file
    with OUTPUT_FILE.open("wt", encoding="utf-8") as f:
        f.write("\n".join(output_lines))

    print(f"📘 Documentation written to: {OUTPUT_FILE}")


if __name__ == "__main__":
    # noinspection PyTypeChecker
    generate_docs(cli)
