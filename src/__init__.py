from pathlib import Path

ROOT_DIR: Path = next(p for p in Path(__file__).resolve().parents if (p / "requirements.txt").exists())

IMAGES_DIR: Path = ROOT_DIR.joinpath("images")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

SDF_DIR: Path = ROOT_DIR.joinpath("data/sdf")
MOLECULE_MATCH_SUBDIR = "molecule_match"
DIAMAG_COMPOUND_SUBDIR = "diamag_compound"
DATA_QUALITY_SUBDIR = "data_quality"
BOND_MATCH_SUBDIR = "bond_match"
