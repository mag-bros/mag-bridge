from dataclasses import dataclass
from typing import Optional

from src import DATA_QUALITY_SUBDIR


@dataclass(frozen=True, slots=True)
class DataQualityDiamagContrTestsSDF:
    """
    Tests for evaluating the data quality of diamagnetic contribution calculations performed by MagBridge.
    The test cases are based on literature examples of chemical compounds with experimentally measured diamagnetic susceptibilities.

    Parameters
    ----------
    sdf_file : str
        Name of the SDF file used as input.
    measured_diamag_sus : float
        Experimentally measured diamagnetic susceptibility.
    literature_reference : str
        Reference for the literature value of experimentally measured diamagnetic susceptibility.
    """

    sdf_file: str
    measured_diamag_sus: float
    literature_reference: str
    description: Optional[str] = ""


CALC_DIAMAG_QUALITY_TESTS: list["DataQualityDiamagContrTestsSDF"] = [
    DataQualityDiamagContrTestsSDF(
        sdf_file="Na_HCOO_B(OH)3_2H2O.sdf",
        measured_diamag_sus=-88.9,
        literature_reference="M. Prasad, C. R. Kanekar, L.S. Kamat, J. Phys. Colloid. Chem. 55 (1957) 1534.",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Bi_Cl_2_PhMe_3.sdf",
        measured_diamag_sus=-263.4,
        literature_reference="P. Pascal, D. Voigt, M.-C. Labarre, L. Fournes, Comput. Rend. 269C (1966) 1481.",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Bi_Ph_3.sdf",
        measured_diamag_sus=-194.6,
        literature_reference="No. 211",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Bi3+_HO_C_COO-_3.sdf",
        measured_diamag_sus=-120.2,
        literature_reference="No. 209",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Be_NO3_2.sdf",
        measured_diamag_sus=-41.0,
        literature_reference="No. 183",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Ba2+_PhCOO-_2H2O.sdf",
        measured_diamag_sus=-203.2,
        literature_reference="No. 171",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="SbBr3.sdf",
        measured_diamag_sus=-111.4,
        literature_reference="No. 16",
    ),
    # DataQualityDiamagContrTestsSDF(
    #     sdf_file="",
    #     measured_diamag_sus=,
    #     literature_reference="...",
    # ),
    # DataQualityDiamagContrTestsSDF(
    #     sdf_file="",
    #     measured_diamag_sus=,
    #     literature_reference="...",
    # ),
    # DataQualityDiamagContrTestsSDF(
    #     sdf_file="",
    #     measured_diamag_sus=,
    #     literature_reference="...",
    # ),
]
