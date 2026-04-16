import sys
import click
import os

APP_DATA_DIR = os.environ.get("APP_DATA_DIR")

if not APP_DATA_DIR:
    raise RuntimeError("APP_DATA_DIR is not set. Must be provided by Electron.")

APP_DATA_DIR = Path(APP_DATA_DIR).resolve()
APP_DATA_DIR.mkdir(parents=True, exist_ok=True)

@click.command()
@click.option("--host", default="0.0.0.0", show_default=True)
@click.option("--port", default=8000, show_default=True)
@click.option("--reload", is_flag=True, help="Enable auto-reload (dev mode).")
@click.option("--workers", default=1, show_default=True)

def runserver(host: str, port: int, reload: bool, workers: int):
    """Run FastAPI using Uvicorn with CLI options."""
    import uvicorn

    common_params = {"host": host, "port": port, "workersas": workers}

    is_prod = getattr(sys, "frozen", False)
    if is_prod:  # frozen user build
        from backend import app

        uvicorn.run(app, reload=False, **common_params)
    else:  # normal dev/runtime, full uvicorn features available
        uvicorn.run("backend:app", reload=reload, **common_params)

if __name__ == "__main__":
    runserver()
