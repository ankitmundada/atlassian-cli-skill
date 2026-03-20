"""atlassian-cli — open-source CLI for Jira and Confluence."""

from typing import Optional

import typer

from atlassian_cli import __version__
from atlassian_cli.commands.auth import app as auth_app
from atlassian_cli.commands.jira import app as jira_app
from atlassian_cli.commands.confluence import app as confluence_app


def version_callback(value: bool) -> None:
    if value:
        print(f"atlassian-cli {__version__}")
        raise typer.Exit()


app = typer.Typer(
    name="atlassian-cli",
    help="Open-source CLI for Jira and Confluence.",
    no_args_is_help=True,
)


@app.callback(invoke_without_command=True)
def main_callback(
    version: Optional[bool] = typer.Option(None, "--version", "-V", callback=version_callback, is_eager=True, help="Show version and exit."),
) -> None:
    pass


app.add_typer(auth_app, name="auth")
app.add_typer(jira_app, name="jira")
app.add_typer(confluence_app, name="confluence")


def main() -> None:
    app()
