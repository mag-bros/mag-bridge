from dataclasses import dataclass
from typing import Optional

FEATURE_NOT_IMPLEMENTED = float("nan")
NO_REFERENCE = float("nan")
from src import (
    DIAMAG_COMPOUND_ATOMS_SUBDIR,
    DIAMAG_COMPOUND_CONSTITUTIVE_CORR_SUBDIR,
    DIAMAG_COMPOUND_MOLECULES_SUBDIR,
)


@dataclass(frozen=True, slots=True)
class DiamagneticContributionTestSDF:
    """
    Test case for validating diamagnetic susceptibility contribution calculations - one compound per SDF file.

    Parameters
    ----------
    sdf_file : str
        Name of the SDF file used as input.
    expected_contribution : float
        Expected total diamagnetic susceptibility of the compound, source of truth.
    atomic_sum_reference : float, optional
        Expected sum of atomic Pascal constants - used ONLY as reference.
    molecular_sum_reference : float, optional
        Expected sum of atomic Pascal constants and/or common molecule(s) diamagnetic contribution - used ONLY as reference
    constitutive_sum_reference : float, optional
        Expected sum of constitutive correction(s), atomic Pascal constants and/or common molecule(s) diamagnetic contribution - used ONLY as reference
    description : str, optional
        Optional note or context for the test case.
    """

    sdf_file: str
    expected_contribution: float
    atomic_sum_reference: Optional[float] = None
    molecular_sum_reference: Optional[float] = None
    constitutive_sum_reference: Optional[float] = None
    description: Optional[str] = ""

    def __str__(self) -> str:
        parts = [
            f"sdf_file='{self.sdf_file}'",
            f"expected_contribution={self.expected_contribution}",
        ]
        if self.atomic_sum_reference is not None:
            parts.append(f"suminfo_atoms={self.atomic_sum_reference}")
        if self.molecular_sum_reference is not None:
            parts.append(f"suminfo_mols={self.molecular_sum_reference}")
        if self.constitutive_sum_reference is not None:
            parts.append(f"suminfo_constitutive={self.constitutive_sum_reference}")
        if self.description:
            parts.append(f"description='{self.description}'")

        return ", ".join(parts)


CALC_DIAMAG_CONTR_TESTS: dict[str, list[DiamagneticContributionTestSDF]] = {
    DIAMAG_COMPOUND_ATOMS_SUBDIR: [
        DiamagneticContributionTestSDF(
            sdf_file="2-methylpropan-1-ol.sdf",
            expected_contribution=-57.9,
            atomic_sum_reference=-57.9,
            molecular_sum_reference=-57.9,
            constitutive_sum_reference=FEATURE_NOT_IMPLEMENTED,
            description="Simple test for adding atomic Pascal constants",
        ),
        DiamagneticContributionTestSDF(
            sdf_file="chlorobenzene.sdf",
            expected_contribution=-72.19,
            atomic_sum_reference=-72.19,
            molecular_sum_reference=-72.19,
            constitutive_sum_reference=FEATURE_NOT_IMPLEMENTED,
            description="Tests adding Pascal constants for ring and non-ring atoms.",
        ),
        DiamagneticContributionTestSDF(
            sdf_file="chalconatronate.sdf",
            expected_contribution=-119.6,
            atomic_sum_reference=-95.58,
            molecular_sum_reference=-119.6,
            constitutive_sum_reference=-119.6,
            description="Tests adding diamag contribution for metal cations and common polyatomic anions.",
        ),
        DiamagneticContributionTestSDF(
            sdf_file="AsIIIAsVAlAl3+.sdf",
            expected_contribution=-187.72,
            atomic_sum_reference=-178.78,
            molecular_sum_reference=-187.72,
            constitutive_sum_reference=FEATURE_NOT_IMPLEMENTED,
            description="Tests different oxidation state/charge scenario for given atom",
        ),
        DiamagneticContributionTestSDF(
            sdf_file="ArenePbIIPb2+.sdf",
            expected_contribution=-206.32,
            atomic_sum_reference=-206.32,
            molecular_sum_reference=-206.32,
            constitutive_sum_reference=FEATURE_NOT_IMPLEMENTED,
            description="...",
        ),
        DiamagneticContributionTestSDF(
            sdf_file="[K(crown)][Dy(BC4Ph5)2].sdf",
            expected_contribution=-788.64,
            atomic_sum_reference=-788.64,
            molecular_sum_reference=-788.64,
            constitutive_sum_reference=FEATURE_NOT_IMPLEMENTED,
            description="Real paramagnetic compound example. DOI: 10.1021/jacs.2c08568",
        ),
        DiamagneticContributionTestSDF(
            sdf_file="[Ag(TACN)](HSO4).sdf",
            expected_contribution=-159.66,
            atomic_sum_reference=-160.99,
            molecular_sum_reference=-159.66,
            constitutive_sum_reference=FEATURE_NOT_IMPLEMENTED,
            description="Tests both 9-membered macrocycle ring and adding diamag contribution for common anion.",
        ),
        DiamagneticContributionTestSDF(
            sdf_file="joint-ring-system.sdf",
            expected_contribution=-169.88,
            atomic_sum_reference=-169.88,
            molecular_sum_reference=-169.88,
            constitutive_sum_reference=FEATURE_NOT_IMPLEMENTED,
            description="Tests structure with joint rings and macrocyclic rings",
        ),
        DiamagneticContributionTestSDF(
            sdf_file="azabicycle_9_5.sdf",
            expected_contribution=-116.92,
            atomic_sum_reference=-116.92,
            molecular_sum_reference=-116.92,
            constitutive_sum_reference=FEATURE_NOT_IMPLEMENTED,
            description="Tests a macrocyclic ring within bicyclic structure",
        ),
        DiamagneticContributionTestSDF(
            sdf_file="macrocycle_with_rings.sdf",
            expected_contribution=-519.24,
            atomic_sum_reference=-519.24,
            molecular_sum_reference=-519.24,
            constitutive_sum_reference=FEATURE_NOT_IMPLEMENTED,
            description="Tests a large macrocycle containing 6-membered rings.",
        ),
        DiamagneticContributionTestSDF(
            sdf_file="Be2+_2CH3-.sdf",
            expected_contribution=-29.98,
            atomic_sum_reference=-29.98,
            molecular_sum_reference=-29.98,
            constitutive_sum_reference=FEATURE_NOT_IMPLEMENTED,
            description="This file must not contain Be-C bonds",
        ),
    ],
    DIAMAG_COMPOUND_MOLECULES_SUBDIR: [
        DiamagneticContributionTestSDF(
            sdf_file="[Tb(C5H5)(C5F5)]Cl.sdf",
            expected_contribution=-170.1,
            atomic_sum_reference=NO_REFERENCE,
            molecular_sum_reference=-170.1,
            constitutive_sum_reference=FEATURE_NOT_IMPLEMENTED,
            description="Tests combination of common ligand, monoatomic ions and unknown molecule",
        ),
        DiamagneticContributionTestSDF(
            sdf_file="[Tb(C5H5)(C5F5)](PF6).sdf",
            expected_contribution=-210.8,
            atomic_sum_reference=NO_REFERENCE,
            molecular_sum_reference=-210.8,
            constitutive_sum_reference=FEATURE_NOT_IMPLEMENTED,
            description="Tests PF6- anion",
        ),
        DiamagneticContributionTestSDF(
            sdf_file="[Co(II)(bipy)(PPh3)(PMe3)](BF4)(ClO4).sdf",
            expected_contribution=-423.67,
            atomic_sum_reference=NO_REFERENCE,
            molecular_sum_reference=-423.67,
            constitutive_sum_reference=FEATURE_NOT_IMPLEMENTED,
            description="Tests combination of common and unknown ligands, metal cation and common anions",
        ),
        DiamagneticContributionTestSDF(
            sdf_file="[La(H2Pc)(HPc)](NO3)(NO2).sdf",
            expected_contribution=-781.11,
            atomic_sum_reference=NO_REFERENCE,
            molecular_sum_reference=-781.11,
            constitutive_sum_reference=FEATURE_NOT_IMPLEMENTED,
            description="Tests H2Pc (phthalocyanine) and HPc- ligands. Charged form of the same molecule should not be recognized.",
        ),
        DiamagneticContributionTestSDF(
            sdf_file="[Y(III)Hg(II)(Hgsal2-)(o-PBMA)](XCN)3_benz_MeCN.sdf",
            expected_contribution=-643.33,
            atomic_sum_reference=NO_REFERENCE,
            molecular_sum_reference=-643.33,
            constitutive_sum_reference=FEATURE_NOT_IMPLEMENTED,
            description="Tests combination of o-PBMA ligand, large unknown molecule, different oxidation/charge scenario of one atom and solvents. ",
        ),
        DiamagneticContributionTestSDF(
            sdf_file="W(IV)(AcOEt)(AcOAc)(acac)3(H2O)(OH)(O).sdf",
            expected_contribution=-322.9,
            atomic_sum_reference=NO_REFERENCE,
            molecular_sum_reference=-322.9,
            constitutive_sum_reference=FEATURE_NOT_IMPLEMENTED,
            description="Tests many common solvents and ligand with similar structures in compound with metal cation and H2O, OH- and O2- molecules.",
        ),
    ],
    DIAMAG_COMPOUND_CONSTITUTIVE_CORR_SUBDIR: [],
}
