from pathlib import Path

ROOT_DIR: Path = next(
    p for p in Path(__file__).resolve().parents if (p / "requirements.txt").exists()
)

IMAGES_DIR: Path = ROOT_DIR.joinpath("images")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
SDF_DIR: Path = ROOT_DIR.joinpath("data/sdf")
