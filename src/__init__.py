from pathlib import Path

ROOT_DIR: Path = next(
    p for p in Path(__file__).resolve().parents if (p / "requirements.txt").exists()
)

IMAGES_DIR: Path = ROOT_DIR.joinpath("images")
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

SDF_DIR: Path = ROOT_DIR.joinpath("data/sdf")
MOLECULE_MATCH_SUBDIR = "molecule_match"
DIAMAG_COMPOUND_ATOMS_SUBDIR = "diamag_compound/atoms"
DIAMAG_COMPOUND_MOLECULES_SUBDIR = "diamag_compound/molecules"
DIAMAG_COMPOUND_CONSTITUTIVE_CORR_SUBDIR = "diamag_compound/constitutive_corr"
