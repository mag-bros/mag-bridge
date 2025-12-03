import time

t0 = time.perf_counter()
print(f"[BOOT] Python code starting at {t0:.4f}", flush=True)

print("[BOOT] importing sys...", flush=True)
import sys

print("[BOOT] importing click...", flush=True)
import click


@click.command()
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8000, show_default=True)
@click.option("--reload", is_flag=True, help="Enable auto-reload (dev mode).")
@click.option("--workers", default=1, show_default=True)
def runserver(host: str, port: int, reload: bool, workers: int):
    """Run FastAPI using Uvicorn with CLI options."""
    print("[BOOT] importing uvicorn...", flush=True)
    import uvicorn

    is_release = getattr(sys, "frozen", False)

    if is_release:  # frozen user build
        print("[BOOT] importing fastapi app...", flush=True)
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
