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
        suminfo_diamag_atoms=9999,
        suminfo_diamag_mols=9999,
        suminfo_diamag_constitutive=9999,
        description="...",
    ),
    SDFTestCompound(
        sdf_file="chlorobenzene.sdf",
        expected_diamag_total=-72.19,
    ),
    SDFTestCompound(
        sdf_file="chalconatronate.sdf",
        expected_diamag_total=-95.58,
    ),
    SDFTestCompound(
        sdf_file="AsIIIAsVAlAl3+.sdf",
        expected_diamag_total=-178.78,
    ),
    SDFTestCompound(
        sdf_file="ArenePbIIPb2+.sdf",
        expected_diamag_total=-206.32,
    ),
    SDFTestCompound(
        sdf_file="[K(crown)][Dy(BC4Ph5)2].sdf",
        expected_diamag_total=-788.64,
        description="RDKit is treating all C and N atoms as ring_atoms when molecule has macrocyclic structure.",
    ),
    SDFTestCompound(
        sdf_file="[Ag(TACN)](HSO4).sdf",
        expected_diamag_total=-160.99,
    ),
    SDFTestCompound(
        sdf_file="joint-ring-system.sdf",
        expected_diamag_total=-169.88,
    ),
    SDFTestCompound(
        sdf_file="azabicycle_9_5.sdf",
        expected_diamag_total=-116.92,
    ),
    SDFTestCompound(
        sdf_file="macrocycle_with_rings.sdf",
        expected_diamag_total=-519.24,
    ),
    SDFTestCompound(
        sdf_file="Be2+_2CH3-.sdf",
        expected_diamag_total=-29.98,
        description="This file must not contain Be-C bonds",
    ),
]
