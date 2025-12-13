import pytest

from src import MOLECULE_MATCH_SUBDIR
from src.constants.common_molecules import COMMON_MOLECULES, CommonMolecule
from src.core.compound import MBCompound
from src.loader import SDFLoader


def _run_molecule_match(group: str, idx: int, cm: CommonMolecule) -> None:
    expected_smiles: set[str] = cm.SMILES

    compound: MBCompound = SDFLoader.Load(cm.sdf_file, subdir=MOLECULE_MATCH_SUBDIR)

    sdf_compound_smiles: set[str] = {
        mol.smiles for mol in compound.GetMols(to_rdkit=False)
    }

    # when comparing two sets with "==" the order of elements doesn't matter
    test_condition: bool = sdf_compound_smiles == expected_smiles
    error_msg = (
        f"[ERR]: group={group} found={sdf_compound_smiles}, expected={expected_smiles}"
    )
    assert test_condition, error_msg


def _params_for(group: str):
    return pytest.mark.parametrize(
        "common_mol_params",
        list(enumerate(COMMON_MOLECULES[group])),
        ids=lambda p: f"<test:{p[0]}> {p[1].formula}",
    )


@_params_for(group="ions")
def test_molecule_match_ions(
    common_mol_params: tuple[int, CommonMolecule],
) -> None:
    idx, common_mol = common_mol_params
    _run_molecule_match(group="ions", idx=idx, cm=common_mol)


@_params_for(group="ligands")
def test_molecule_match_ligands(
    common_mol_params: tuple[int, CommonMolecule],
) -> None:
    idx, common_mol = common_mol_params
    _run_molecule_match(group="ligands", idx=idx, cm=common_mol)


@_params_for(group="organic_solvents")
def test_molecule_match_organic_solvents(
    common_mol_params: tuple[int, CommonMolecule],
) -> None:
    idx, common_mol = common_mol_params
    _run_molecule_match(group="organic_solvents", idx=idx, cm=common_mol)
