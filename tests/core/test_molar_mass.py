import pytest
from src.core.compound import MBCompound
from src.loader import MBLoader

# (SMILES, expected molar mass in g/mol, rounded to 2 dp) — reference values from RDKit.
MOLAR_MASS_TESTS = [
    ("O", 18.02),  # water
    ("C", 16.04),  # methane
    ("c1ccccc1", 78.11),  # benzene
]


@pytest.mark.parametrize("smiles, expected", MOLAR_MASS_TESTS)
def test_molecule_molar_mass(smiles: str, expected: float) -> None:
    """A single molecule's molar mass matches its known value."""
    molecule = MBLoader.MolFromSmiles(smiles)
    # TODO (you):
    #   1. call molecule.CalcMolarMass()
    #   2. assert it equals `expected` when rounded to 2 decimals (see test_diamag.py)
    raise NotImplementedError("write the act/assert — see TODO above")


def test_compound_molar_mass_sums_molecules() -> None:
    """A compound's molar mass is the sum of its molecules' molar masses."""
    molecules = [MBLoader.MolFromSmiles(s) for s in ("O", "C")]  # water + methane
    compound = MBCompound(mols=molecules, loaded_from="test")
    # TODO (you):
    #   1. call compound.CalcMolarMass()
    #   2. assert it equals 18.02 + 16.04 (= 34.06) when rounded to 2 decimals
    raise NotImplementedError("write the act/assert — see TODO above")
