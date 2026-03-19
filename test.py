# pyproject.toml: typer[all] gives shell completion, prompts, etc.
import sys, typer
from typing import Optional

app = typer.Typer(help="Demo CLI")

@app.command()
def run(
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Your name"),
    count: int = typer.Option(1, min=1, help="Times to greet"),
):
    # If not provided, ask interactively only when attached to a TTY
    if name is None:
        if sys.stdin.isatty():
            name = typer.prompt("What's your name?")
        else:
            # non-interactive: fail fast & clear
            typer.echo("Error: --name required when stdin is not a TTY", err=True)
            raise typer.Exit(code=2)
    for _ in range(count):
        typer.echo(f"Hello, {name}!")

if __name__ == "__main__":
    app()
