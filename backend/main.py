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

    common_params = {"host": host, "port": port, "workers": workers}

    is_prod = getattr(sys, "frozen", False)
    if is_prod:  # frozen user build
        from backend import app

        uvicorn.run(app, reload=False, **common_params)
    else:  # normal dev/runtime, full uvicorn features available
        uvicorn.run("backend:app", reload=reload, **common_params)


if __name__ == "__main__":
    runserver()
