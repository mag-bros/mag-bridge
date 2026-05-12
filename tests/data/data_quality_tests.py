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
    DataQualityDiamagContrTestsSDF(
        sdf_file="[Pt((NH2)2CS}4]Cl2.sdf",
        measured_diamag_sus=-246.5,
        literature_reference="No. 1845",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="[Ni(imam)2](BF4)2.sdf",
        measured_diamag_sus=-111.0,
        literature_reference="No. 1349",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Ni(L1).sdf",
        measured_diamag_sus=-56.0,
        literature_reference="No. 1361",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="[NbCp2]Br3.sdf",
        measured_diamag_sus=-240.0,
        literature_reference="No. 1503",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="[Ni(EtS)2].sdf",
        measured_diamag_sus=-77.8,
        literature_reference="No. 1299",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="[Ni{P(Et)(OH)S2}2].sdf",
        measured_diamag_sus=-247.0,
        literature_reference="No. 1301",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="[Zn{Ph(NO3)(NHNH2)}]Br2_5H2O.sdf",
        measured_diamag_sus=-444.2,
        literature_reference="No. 2929",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Zn3(cit)3_2H2O.sdf",
        measured_diamag_sus=-246.0,
        literature_reference="No. 2923",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Zn(AcO)2_2H2O.sdf",
        measured_diamag_sus=-100.9,
        literature_reference="No. 2900",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="HSiPr3.sdf",
        measured_diamag_sus=-130.0,
        literature_reference="No. 2313",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="K2SiO3.sdf",
        measured_diamag_sus=-59.0,
        literature_reference="No. 2048",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="MeSiBr3.sdf",
        measured_diamag_sus=-115.5,
        literature_reference="No. 2229",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Si_N_heterocycle.sdf",
        measured_diamag_sus=-81.8,
        literature_reference="No. 2247",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Me3SiOAc.sdf",
        measured_diamag_sus=-86.09,
        literature_reference="No. 2255",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="PhSiCl3.sdf",
        measured_diamag_sus=-120.4,
        literature_reference="No. 2262",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Si(AcO)4.sdf",
        measured_diamag_sus=-129.25,
        literature_reference="No. 2295",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Me2Si(OEt){ON=C(Pr)NH2}.sdf",
        measured_diamag_sus=-135.8,
        literature_reference="No. 2301",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="BrPh+N_S_Si_cycle.sdf",
        measured_diamag_sus=-199.37,
        literature_reference="No. 2329",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(Ph2SiO)4.sdf",
        measured_diamag_sus=-485.3,
        literature_reference="No. 2369",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Me3Si-NH-C(Ph)=N-O-SiMe3.sdf",
        measured_diamag_sus=-199.5,
        literature_reference="No. 2344",
    ),
    # DataQualityDiamagContrTestsSDF(
    #     sdf_file="",
    #     measured_diamag_sus=,
    #     literature_reference="",
    # ),
    # DataQualityDiamagContrTestsSDF(
    #     sdf_file="",
    #     measured_diamag_sus=,
    #     literature_reference="",
    # ),
    # DataQualityDiamagContrTestsSDF(
    #     sdf_file="",
    #     measured_diamag_sus=,
    #     literature_reference="",
    # ),
    # DataQualityDiamagContrTestsSDF(
    #     sdf_file="",
    #     measured_diamag_sus=,
    #     literature_reference="",
    # ),
    # DataQualityDiamagContrTestsSDF(
    #     sdf_file="",
    #     measured_diamag_sus=,
    #     literature_reference="",
    # ),
    # DataQualityDiamagContrTestsSDF(
    #     sdf_file="",
    #     measured_diamag_sus=,
    #     literature_reference="",
    # ),
    # DataQualityDiamagContrTestsSDF(
    #     sdf_file="",
    #     measured_diamag_sus=,
    #     literature_reference="",
    # ),
    # DataQualityDiamagContrTestsSDF(
    #     sdf_file="",
    #     measured_diamag_sus=,
    #     literature_reference="",
    # ),
    # DataQualityDiamagContrTestsSDF(
    #     sdf_file="",
    #     measured_diamag_sus=,
    #     literature_reference="",
    # ),
    # DataQualityDiamagContrTestsSDF(
    #     sdf_file="",
    #     measured_diamag_sus=,
    #     literature_reference="",
    # ),
    # DataQualityDiamagContrTestsSDF(
    #     sdf_file="",
    #     measured_diamag_sus=,
    #     literature_reference="",
    # ),
    # DataQualityDiamagContrTestsSDF(
    #     sdf_file="",
    #     measured_diamag_sus=,
    #     literature_reference="",
    # ),
    # DataQualityDiamagContrTestsSDF(
    #     sdf_file="",
    #     measured_diamag_sus=,
    #     literature_reference="",
    # ),
    # DataQualityDiamagContrTestsSDF(
    #     sdf_file="",
    #     measured_diamag_sus=,
    #     literature_reference="",
    # ),
    # DataQualityDiamagContrTestsSDF(
    #     sdf_file="",
    #     measured_diamag_sus=,
    #     literature_reference="",
    # ),
    # DataQualityDiamagContrTestsSDF(
    #     sdf_file="",
    #     measured_diamag_sus=,
    #     literature_reference="",
    # ),
    # DataQualityDiamagContrTestsSDF(
    #     sdf_file="",
    #     measured_diamag_sus=,
    #     literature_reference="",
    # ),
    # DataQualityDiamagContrTestsSDF(
    #     sdf_file="",
    #     measured_diamag_sus=,
    #     literature_reference="",
    # ),
    # DataQualityDiamagContrTestsSDF(
    #     sdf_file="",
    #     measured_diamag_sus=,
    #     literature_reference="",
    # ),
]
