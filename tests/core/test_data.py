from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class DiamagTestCase:
    """
    Descriptor for an SDF-based test compound.

    Parameters
    ----------
    sdf_file : str
        Name of the SDF file used as input.
    expected_diamag_contr : float
        Expected total diamagnetic susceptibility of the compound, source of truth.
    atomic_sum_ref : float, optional
        Expected sum of atomic Pascal constants - NOT used for validations, only informational.
    molecular_sum_ref : float, optional
        Expected sum of atomic Pascal constants and/or common molecule(s) diamagnetic contribution.  - NOT used for validations, only informational.
    constitutive_sum_ref : float, optional
        Expected sum of constitutive correction(s), atomic Pascal constants and/or common molecule(s) diamagnetic contribution. - NOT used for validations, only informational
    description : str, optional
        Optional note or context for the test case.
    """

    sdf_file: str
    expected_diamag_contr: float
    atomic_sum_ref: Optional[float] = None
    molecular_sum_ref: Optional[float] = None
    constitutive_sum_ref: Optional[float] = None
    description: Optional[str] = ""

    def __str__(self) -> str:
        parts = [
            f"sdf_file='{self.sdf_file}'",
            f"expected_diamag_contr={self.expected_diamag_contr}",
        ]
        if self.atomic_sum_ref is not None:
            parts.append(f"suminfo_atoms={self.atomic_sum_ref}")
        if self.molecular_sum_ref is not None:
            parts.append(f"suminfo_mols={self.molecular_sum_ref}")
        if self.constitutive_sum_ref is not None:
            parts.append(f"suminfo_constitutive={self.constitutive_sum_ref}")
        if self.description:
            parts.append(f"description='{self.description}'")

        return ", ".join(parts)


SDF_TEST_COMPOUNDS = [
    DiamagTestCase(
        sdf_file="2-methylpropan-1-ol.sdf",
        expected_diamag_contr=-57.9,
        atomic_sum_ref=-57.9,
        molecular_sum_ref=-57.9,
        constitutive_sum_ref=9999,
        description="Simple test for adding atomic Pascal constants",
    ),
    DiamagTestCase(
        sdf_file="chlorobenzene.sdf",
        expected_diamag_contr=-72.19,
        atomic_sum_ref=-72.19,
        molecular_sum_ref=-72.19,
        constitutive_sum_ref=9999,
        description="Tests adding Pascal constants for ring and non-ring atoms.",
    ),
    DiamagTestCase(
        sdf_file="chalconatronate.sdf",
        expected_diamag_contr=-119.6,
        atomic_sum_ref=-95.58,
        molecular_sum_ref=-119.6,
        constitutive_sum_ref=-119.6,
        description="Tests adding diamag contribution for metal cations and common polyatomic anions.",
    ),
    DiamagTestCase(
        sdf_file="AsIIIAsVAlAl3+.sdf",
        expected_diamag_contr=-187.72,
        atomic_sum_ref=-178.78,
        molecular_sum_ref=-187.72,
        constitutive_sum_ref=9999,
        description="Tests different oxidation state/charge scenario for given atom",
    ),
    DiamagTestCase(
        sdf_file="ArenePbIIPb2+.sdf",
        expected_diamag_contr=-206.32,
        atomic_sum_ref=-206.32,
        molecular_sum_ref=-206.32,
        constitutive_sum_ref=9999,
        description="...",
    ),
    DiamagTestCase(
        sdf_file="[K(crown)][Dy(BC4Ph5)2].sdf",
        expected_diamag_contr=-788.64,
        atomic_sum_ref=-788.64,
        molecular_sum_ref=-788.64,
        constitutive_sum_ref=9999,
        description="Real paramagnetic compound example. DOI: 10.1021/jacs.2c08568",
    ),
    DiamagTestCase(
        sdf_file="[Ag(TACN)](HSO4).sdf",
        expected_diamag_contr=-159.66,
        atomic_sum_ref=-160.99,
        molecular_sum_ref=-159.66,
        constitutive_sum_ref=9999,
        description="Tests both 9-membered macrocycle ring and adding diamag contribution for common anion.",
    ),
    DiamagTestCase(
        sdf_file="joint-ring-system.sdf",
        expected_diamag_contr=-169.88,
        atomic_sum_ref=-169.88,
        molecular_sum_ref=-169.88,
        constitutive_sum_ref=9999,
        description="Tests structure with joint rings and macrocyclic rings",
    ),
    DiamagTestCase(
        sdf_file="azabicycle_9_5.sdf",
        expected_diamag_contr=-116.92,
        atomic_sum_ref=-116.92,
        molecular_sum_ref=-116.92,
        constitutive_sum_ref=9999,
        description="Tests a macrocyclic ring within bicyclic structure",
    ),
    DiamagTestCase(
        sdf_file="macrocycle_with_rings.sdf",
        expected_diamag_contr=-519.24,
        atomic_sum_ref=-519.24,
        molecular_sum_ref=-519.24,
        constitutive_sum_ref=9999,
        description="Tests a large macrocycle containing 6-membered rings.",
    ),
    DiamagTestCase(
        sdf_file="Be2+_2CH3-.sdf",
        expected_diamag_contr=-29.98,
        atomic_sum_ref=-29.98,
        molecular_sum_ref=-29.98,
        constitutive_sum_ref=9999,
        description="This file must not contain Be-C bonds",
    ),
    DiamagTestCase(
        sdf_file="[Tb(C5H5)(C5F5)]Cl.sdf",
        expected_diamag_contr=-170.1,
        atomic_sum_ref=99999,
        molecular_sum_ref=-170.1,
        constitutive_sum_ref=9999,
        description="Tests combination of common ligand, monoatomic ions and unknown molecule",
    ),
    DiamagTestCase(
        sdf_file="[Tb(C5H5)(C5F5)](PF6).sdf",
        expected_diamag_contr=-210.8,
        atomic_sum_ref=99999,
        molecular_sum_ref=-210.8,
        constitutive_sum_ref=9999,
        description="Tests PF6- anion",
    ),
    DiamagTestCase(
        sdf_file="[Co(II)(bipy)(PPh3)(PMe3)](BF4)(ClO4).sdf",
        expected_diamag_contr=-423.67,
        atomic_sum_ref=99999,
        molecular_sum_ref=-423.67,
        constitutive_sum_ref=9999,
        description="Tests combination of common and unknown ligands, metal cation and common anions",
    ),
    DiamagTestCase(
        sdf_file="[La(H2Pc)(HPc)](NO3)(NO2).sdf",
        expected_diamag_contr=-781.11,
        atomic_sum_ref=99999,
        molecular_sum_ref=-781.11,
        constitutive_sum_ref=9999,
        description="Tests H2Pc (phthalocyanine) and HPc- ligands. Charged form of the same molecule should not be recognized.",
    ),
    DiamagTestCase(
        sdf_file="[Y(III)Hg(II)(Hgsal2-)(o-PBMA)](XCN)3_benz_MeCN.sdf",
        expected_diamag_contr=-643.33,
        atomic_sum_ref=99999,
        molecular_sum_ref=-643.33,
        constitutive_sum_ref=9999,
        description="Tests combination of o-PBMA ligand, large unknown molecule, different oxidation/charge scenario of one atom and solvents. ",
    ),
    DiamagTestCase(
        sdf_file="W(IV)(AcOEt)(AcOAc)(acac)3(H2O)(OH)(O).sdf",
        expected_diamag_contr=-322.9,
        atomic_sum_ref=99999,
        molecular_sum_ref=-322.9,
        constitutive_sum_ref=9999,
        description="Tests many common solvents and ligand with similar structures in compound with metal cation and H2O, OH- and O2- molecules.",
    ),
]
