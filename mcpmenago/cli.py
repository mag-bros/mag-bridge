"""Click CLI for mcpmenago — MCP Manager."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import click

from mcpmenago.index_builder import build_index
from mcpmenago.learn import load_weights, scan_imports, update_weights
from mcpmenago.models import BookMeta, McpMenagoConfig
from mcpmenago.venv_check import VenvCheckError, check_venv

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent
LIBRARY = ROOT / "library"
CONFIG_PATH = ROOT / "mcpmenago.json"
PROJECT_ROOT = ROOT.parent


# ── Helpers ───────────────────────────────────────────────────────────────────
def _load_config() -> McpMenagoConfig:
    if CONFIG_PATH.exists():
        return McpMenagoConfig.model_validate_json(CONFIG_PATH.read_text())
    return McpMenagoConfig()


def _extract_book_name(url: str) -> str:
    """Extract book name from GitHub URL."""
    name = url.rstrip("/").split("/")[-1]
    if name.endswith(".git"):
        name = name[:-4]
    return name


def _ensure_gitignore(gitignore_path: Path, library_rel_path: str = "mcpmenago/library/") -> None:
    """Append managed section to .gitignore if not present."""
    marker = "# [mcpmenago]"
    content = gitignore_path.read_text() if gitignore_path.exists() else ""
    if marker in content:
        return
    section = f"\n{marker} automatically generated content — do not edit\n{library_rel_path}\n"
    gitignore_path.write_text(content.rstrip("\n") + "\n" + section)


# ── CLI ───────────────────────────────────────────────────────────────────────
@click.group()
def cli():
    """mcpmenago — MCP Manager. Manages source code indexes for GitHub repositories."""
    pass


@cli.command()
@click.argument("url")
@click.option("--lang", multiple=True, required=True, help="Languages to index (e.g., python, cpp)")
@click.option("--head-ref", default=None, help="Git tag or branch to clone")
@click.option("--book-name", default=None, help="Override derived book name")
def add(url: str, lang: tuple[str], head_ref: str | None, book_name: str | None):
    """Add a GitHub repository and build its index."""
    config = _load_config()

    # Validate languages
    for l in lang:
        if l not in config.supported_languages:
            click.secho(f"Unsupported language: {l}. Supported: {config.supported_languages}", fg="red")
            sys.exit(1)

    # Venv pre-check
    try:
        check_venv(project_root=PROJECT_ROOT)
    except VenvCheckError as e:
        click.secho(str(e), fg="red")
        sys.exit(1)

    name = book_name or _extract_book_name(url)
    book_dir = LIBRARY / name
    repo_dir = book_dir / "repo"

    if book_dir.exists():
        click.secho(f"Book '{name}' already exists. Use 'update' or 'remove' first.", fg="red")
        sys.exit(1)

    # Clone
    click.echo(f"Cloning {url}...")
    clone_cmd = ["git", "clone", "--depth", "1"]
    if head_ref:
        clone_cmd += ["--branch", head_ref]
    clone_cmd += [url, str(repo_dir)]

    result = subprocess.run(clone_cmd, capture_output=True, text=True)
    if result.returncode != 0:
        click.secho(f"Clone failed: {result.stderr}", fg="red")
        sys.exit(1)

    # Get resolved commit SHA
    sha_result = subprocess.run(
        ["git", "-C", str(repo_dir), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
    )
    resolved_sha = sha_result.stdout.strip() if sha_result.returncode == 0 else None

    # Build index
    click.echo("Building index...")
    index_path = book_dir / "index.json"
    build_index(
        repo_path=repo_dir,
        languages=list(lang),
        version=head_ref or "HEAD",
        output_path=index_path,
    )

    # Detect python_path
    python_path = Path(sys.executable).parent.parent / "lib"  # best effort
    for p in Path(sys.executable).parent.parent.rglob(f"site-packages/{name}"):
        python_path = p
        break

    # Write book.json
    meta = BookMeta(
        name=name,
        github_url=url,
        languages=list(lang),
        python_path=python_path,
        head_ref=head_ref,
        head_ref_resolved=resolved_sha,
        index_built_at=datetime.now(timezone.utc).isoformat(),
    )
    (book_dir / "book.json").write_text(meta.model_dump_json(indent=2))

    # Update .gitignore
    _ensure_gitignore(PROJECT_ROOT / ".gitignore")

    index = json.loads(index_path.read_text())
    symbol_count = sum(len(v) for v in index.get("symbols", {}).values())
    click.secho(f"Added '{name}': {symbol_count} symbols indexed.", fg="green")


@cli.command()
@click.argument("book")
def remove(book: str):
    """Remove a book and all its data."""
    book_dir = LIBRARY / book
    if not book_dir.exists():
        click.secho(f"Book '{book}' not found.", fg="red")
        sys.exit(1)
    shutil.rmtree(book_dir)
    click.echo(f"Removed '{book}'.")


@cli.command("list")
def list_books():
    """List all managed books."""
    if not LIBRARY.exists():
        click.echo("No books. Library is empty.")
        return
    books = [d.name for d in sorted(LIBRARY.iterdir()) if d.is_dir() and (d / "book.json").exists()]
    if not books:
        click.echo("No books in library.")
        return
    for name in books:
        meta = BookMeta.model_validate_json((LIBRARY / name / "book.json").read_text())
        click.echo(f"  {name}  ({meta.github_url})  ref={meta.head_ref or 'HEAD'}")


@cli.command()
@click.argument("book")
def show(book: str):
    """Show details for a book."""
    book_dir = LIBRARY / book
    if not (book_dir / "book.json").exists():
        click.secho(f"Book '{book}' not found.", fg="red")
        sys.exit(1)

    meta = BookMeta.model_validate_json((book_dir / "book.json").read_text())
    click.echo(f"Name:       {meta.name}")
    click.echo(f"URL:        {meta.github_url}")
    click.echo(f"Languages:  {', '.join(meta.languages)}")
    click.echo(f"Head ref:   {meta.head_ref or 'HEAD'}")
    click.echo(f"SHA:        {meta.head_ref_resolved or 'unknown'}")
    click.echo(f"Indexed at: {meta.index_built_at or 'never'}")

    weights = load_weights(book_dir / "weights.json")
    click.echo(f"Weights:    {len(weights)} symbols discovered")


@cli.command()
@click.argument("book", required=False)
@click.option("--all", "rebuild_all", is_flag=True, help="Rebuild all books")
def rebuild(book: str | None, rebuild_all: bool):
    """Rebuild index for a book (or all books)."""
    if not book and not rebuild_all:
        click.secho("Specify a book name or use --all.", fg="red")
        sys.exit(1)

    targets = []
    if rebuild_all:
        if LIBRARY.exists():
            targets = [d.name for d in LIBRARY.iterdir() if d.is_dir() and (d / "book.json").exists()]
    else:
        assert book is not None  # guaranteed by the guard above
        targets = [book]

    for name in targets:
        book_dir = LIBRARY / name
        if not (book_dir / "book.json").exists():
            click.secho(f"Book '{name}' not found.", fg="red")
            continue

        meta = BookMeta.model_validate_json((book_dir / "book.json").read_text())
        click.echo(f"Rebuilding index for '{name}'...")
        build_index(
            repo_path=book_dir / "repo",
            languages=meta.languages,
            version=meta.head_ref or "HEAD",
            output_path=book_dir / "index.json",
        )
        meta.index_built_at = datetime.now(timezone.utc).isoformat()
        (book_dir / "book.json").write_text(meta.model_dump_json(indent=2))
        click.secho(f"Rebuilt '{name}'.", fg="green")


@cli.command()
@click.argument("book")
@click.option("--head-ref", required=True, help="New git tag or branch")
def update(book: str, head_ref: str):
    """Update a book to a new git ref (clean re-clone + rebuild)."""
    book_dir = LIBRARY / book
    if not (book_dir / "book.json").exists():
        click.secho(f"Book '{book}' not found.", fg="red")
        sys.exit(1)

    meta = BookMeta.model_validate_json((book_dir / "book.json").read_text())
    repo_dir = book_dir / "repo"

    # Clean re-clone
    click.echo("Removing old clone...")
    if repo_dir.exists():
        shutil.rmtree(repo_dir)

    click.echo(f"Cloning at {head_ref}...")
    result = subprocess.run(
        ["git", "clone", "--depth", "1", "--branch", head_ref, meta.github_url, str(repo_dir)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        click.secho(f"Clone failed: {result.stderr}", fg="red")
        sys.exit(1)

    sha_result = subprocess.run(
        ["git", "-C", str(repo_dir), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
    )

    # Rebuild index
    click.echo("Rebuilding index...")
    build_index(
        repo_path=repo_dir,
        languages=meta.languages,
        version=head_ref,
        output_path=book_dir / "index.json",
    )

    # Update metadata (weights.json preserved)
    meta.head_ref = head_ref
    meta.head_ref_resolved = sha_result.stdout.strip() if sha_result.returncode == 0 else None
    meta.index_built_at = datetime.now(timezone.utc).isoformat()
    (book_dir / "book.json").write_text(meta.model_dump_json(indent=2))

    click.secho(f"Updated '{book}' to {head_ref}.", fg="green")


@cli.command()
@click.argument("book")
def learn(book: str):
    """Scan project imports and update weights for a book."""
    book_dir = LIBRARY / book
    if not (book_dir / "book.json").exists():
        click.secho(f"Book '{book}' not found.", fg="red")
        sys.exit(1)

    config = _load_config()
    meta = BookMeta.model_validate_json((book_dir / "book.json").read_text())
    index_data = json.loads((book_dir / "index.json").read_text())

    # Build symbol→module map from index (simplified: use file path as proxy for module)
    symbol_to_module: dict[str, str] = {}
    for sym_name, entries in index_data.get("symbols", {}).items():
        for entry in entries:
            # Derive module from file path: "Chem/rdmolops.py" → "Chem.rdmolops"
            rel = entry["file"]
            parts = Path(rel).with_suffix("").parts
            module = ".".join(parts)
            symbol_to_module[sym_name] = module
            break  # first entry is enough for module mapping

    # Scan project
    scan_dirs = [str(PROJECT_ROOT / d) for d in config.learn_dirs]
    discovered = scan_imports(package_name=meta.name, scan_dirs=scan_dirs)

    click.echo(f"Discovered modules: {discovered}")

    # Update weights
    weights = update_weights(
        discovered_modules=discovered,
        symbol_to_module=symbol_to_module,
        output_path=book_dir / "weights.json",
    )

    click.secho(f"Updated weights for '{book}': {len(weights)} symbols marked as DISCOVERED.", fg="green")


@cli.command()
def uninstall():
    """Remove all books and clean up."""
    if LIBRARY.exists():
        shutil.rmtree(LIBRARY)
        click.echo("Removed library/.")
    else:
        click.echo("Library already empty.")

    # Clean .gitignore
    gitignore = PROJECT_ROOT / ".gitignore"
    if gitignore.exists():
        content = gitignore.read_text()
        marker = "# [mcpmenago]"
        if marker in content:
            lines = content.splitlines()
            new_lines = []
            skip = False
            for line in lines:
                if marker in line:
                    skip = True
                    continue
                if skip and line.strip() == "":
                    skip = False
                    continue
                if skip and not line.startswith("#"):
                    continue
                skip = False
                new_lines.append(line)
            gitignore.write_text("\n".join(new_lines) + "\n")
    click.echo("Uninstall complete.")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    cli()
