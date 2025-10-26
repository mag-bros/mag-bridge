import sys

import click


@click.command()
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8000, show_default=True)
@click.option("--reload", is_flag=True, help="Enable auto-reload (dev mode).")
@click.option("--workers", default=1, show_default=True)
def runserver(host: str, port: int, reload: bool, workers: int):
    """Run FastAPI using Uvicorn with CLI options."""
    import uvicorn

    running_frozen = getattr(sys, "frozen", False)

    if running_frozen:  # frozen user build
        from backend import app

        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=False,
            workers=1,
        )
    else:  # normal dev/runtime, full uvicorn features available
        uvicorn.run(
            "backend:app",
            host=host,
            port=port,
            reload=reload,
            workers=workers,
        )


if __name__ == "__main__":
    runserver()
