from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SDFTestCompound:
    """
    Descriptor for an SDF-based test compound.

    Parameters
    ----------
    sdf_file : str
        Name of the SDF file used as input.
    expected_diamag_total : float
        Expected total diamagnetic susceptibility, source of truth.
    suminfo_diamag_atoms : float, optional
        Expected atomic-sum contribution - NOT used for validations, only informational.
    suminfo_diamag_mols : float, optional
        Expected molecular contribution - NOT used for validations, only informational.
    suminfo_diamag_constitutive : float, optional
        Expected constitutive correction term - NOT used for validations, only informational
    description : str, optional
        Optional note or context for the test case.
    """

    sdf_file: str
    expected_diamag_total: float
    suminfo_diamag_atoms: Optional[float] = None
    suminfo_diamag_mols: Optional[float] = None
    suminfo_diamag_constitutive: Optional[float] = None
    description: Optional[str] = ""

    def __str__(self) -> str:
        parts = [
            f"sdf_file='{self.sdf_file}'",
            f"expected_diamag_total={self.expected_diamag_total}",
        ]
        if self.suminfo_diamag_atoms is not None:
            parts.append(f"suminfo_atoms={self.suminfo_diamag_atoms}")
        if self.suminfo_diamag_mols is not None:
            parts.append(f"suminfo_mols={self.suminfo_diamag_mols}")
        if self.suminfo_diamag_constitutive is not None:
            parts.append(f"suminfo_constitutive={self.suminfo_diamag_constitutive}")
        if self.description:
            parts.append(f"description='{self.description}'")

        return ", ".join(parts)


SDF_TEST_COMPOUNDS = [
    SDFTestCompound(
        sdf_file="2-methylpropan-1-ol.sdf",
        expected_diamag_total=-57.9,
        suminfo_diamag_atoms=-57.9,
        suminfo_diamag_mols=-57.9,
        suminfo_diamag_constitutive=9999,
        description="Simple test for adding atomic Pascal constants",
    ),
    SDFTestCompound(
        sdf_file="chlorobenzene.sdf",
        expected_diamag_total=-72.19,
        suminfo_diamag_atoms=-72.19,
        suminfo_diamag_mols=-72.19,
        suminfo_diamag_constitutive=9999,
        description="Tests adding Pascal constants for ring and non-ring atoms.",
    ),
    SDFTestCompound(
        sdf_file="chalconatronate.sdf",
        expected_diamag_total=-119.6,
        suminfo_diamag_atoms=-95.58,
        suminfo_diamag_mols=-119.6,
        suminfo_diamag_constitutive=-119.6,
        description="Tests adding diamag contribution for metal cations and common polyatomic anions.",
    ),
    SDFTestCompound(
        sdf_file="AsIIIAsVAlAl3+.sdf",
        expected_diamag_total=-187.72,
        suminfo_diamag_atoms=-178.78,
        suminfo_diamag_mols=-187.72,
        suminfo_diamag_constitutive=9999,
        description="Tests different oxidation state/charge scenario for given atom",
    ),
    SDFTestCompound(
        sdf_file="ArenePbIIPb2+.sdf",
        expected_diamag_total=-206.32,
        suminfo_diamag_atoms=-206.32,
        suminfo_diamag_mols=-206.32,
        suminfo_diamag_constitutive=9999,
        description="...",
    ),
    SDFTestCompound(
        sdf_file="[K(crown)][Dy(BC4Ph5)2].sdf",
        expected_diamag_total=-788.64,
        suminfo_diamag_atoms=-788.64,
        suminfo_diamag_mols=-788.64,
        suminfo_diamag_constitutive=9999,
        description="Real paramagnetic compound example. DOI: 10.1021/jacs.2c08568",
    ),
    SDFTestCompound(
        sdf_file="[Ag(TACN)](HSO4).sdf",
        expected_diamag_total=-159.66,
        suminfo_diamag_atoms=-160.99,
        suminfo_diamag_mols=-159.66,
        suminfo_diamag_constitutive=9999,
        description="Tests both 9-membered macrocycle ring and adding diamag contribution for common anion.",
    ),
    SDFTestCompound(
        sdf_file="joint-ring-system.sdf",
        expected_diamag_total=-169.88,
        suminfo_diamag_atoms=-169.88,
        suminfo_diamag_mols=-169.88,
        suminfo_diamag_constitutive=9999,
        description="Tests structure with joint rings and macrocyclic rings",
    ),
    SDFTestCompound(
        sdf_file="azabicycle_9_5.sdf",
        expected_diamag_total=-116.92,
        suminfo_diamag_atoms=-116.92,
        suminfo_diamag_mols=-116.92,
        suminfo_diamag_constitutive=9999,
        description="Tests a macrocyclic ring within bicyclic structure",
    ),
    SDFTestCompound(
        sdf_file="macrocycle_with_rings.sdf",
        expected_diamag_total=-519.24,
        suminfo_diamag_atoms=-519.24,
        suminfo_diamag_mols=-519.24,
        suminfo_diamag_constitutive=9999,
        description="Tests a large macrocycle containing 6-membered rings.",
    ),
    SDFTestCompound(
        sdf_file="Be2+_2CH3-.sdf",
        expected_diamag_total=-29.98,
        suminfo_diamag_atoms=-29.98,
        suminfo_diamag_mols=-29.98,
        suminfo_diamag_constitutive=9999,
        description="This file must not contain Be-C bonds",
    ),
]
