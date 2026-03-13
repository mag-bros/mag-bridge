from pathlib import Path

ROOT_DIR: Path = next(p for p in Path(__file__).resolve().parents if (p / "requirements.txt").exists())

RESEARCH_DIR: Path = ROOT_DIR.joinpath("mcpmenago/research")
PDF_DIR: Path = RESEARCH_DIR.joinpath("mcpmenago/pdf")
MD_DIR: Path = RESEARCH_DIR.joinpath("mcpmenago/md")
JSON_DIR: Path = RESEARCH_DIR.joinpath("mcpmenago/json")
