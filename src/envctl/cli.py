import typer

app = typer.Typer(help="envctl - local environment vault manager")


@app.command()
def doctor():
    """Show basic configuration info"""
    typer.echo("envctl is working")


@app.command()
def init(project: str = typer.Argument(None)):
    """Initialize env for a project"""
    typer.echo(f"Initializing project: {project or 'auto-detect'}")
