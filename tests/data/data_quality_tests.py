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
    # Boron compounds
    DataQualityDiamagContrTestsSDF(
        sdf_file="Na_HCOO_B(OH)3_2H2O.sdf",
        measured_diamag_sus=-88.9,
        literature_reference="M. Prasad, C. R. Kanekar, L.S. Kamat, J. Phys. Colloid. Chem. 55 (1957) 1534.",
    ),
    # Bismuth compounds
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
    # Berylium compounds
    DataQualityDiamagContrTestsSDF(
        sdf_file="Be_NO3_2.sdf",
        measured_diamag_sus=-41.0,
        literature_reference="No. 183",
    ),
    # Barium compounds
    DataQualityDiamagContrTestsSDF(
        sdf_file="Ba2+_PhCOO-_2H2O.sdf",
        measured_diamag_sus=-203.2,
        literature_reference="No. 171",
    ),
    # Antimony compounds
    DataQualityDiamagContrTestsSDF(
        sdf_file="SbBr3.sdf",
        measured_diamag_sus=-111.4,
        literature_reference="No. 16",
    ),
    # Platinum compounds
    DataQualityDiamagContrTestsSDF(
        sdf_file="[Pt((NH2)2CS}4]Cl2.sdf",
        measured_diamag_sus=-246.5,
        literature_reference="No. 1845",
    ),
    # Niobium compounds
    DataQualityDiamagContrTestsSDF(
        sdf_file="[NbCp2]Br3.sdf",
        measured_diamag_sus=-240.0,
        literature_reference="No. 1503",
    ),
    # Nickel compounds
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
        sdf_file="[Ni(EtS)2].sdf",
        measured_diamag_sus=-77.8,
        literature_reference="No. 1299",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="[Ni{P(Et)(OH)S2}2].sdf",
        measured_diamag_sus=-247.0,
        literature_reference="No. 1301",
    ),
    # Zinc compounds
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
    # Silicon compounds
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
    DataQualityDiamagContrTestsSDF(
        sdf_file="HNO3.sdf",
        measured_diamag_sus=-19.91,
        literature_reference="No. 1559",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="NH4NO3.sdf",
        measured_diamag_sus=-32.6,
        literature_reference="No. 1565",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(NH4)3(cit).sdf",
        measured_diamag_sus=-109.5,
        literature_reference="No. 1534",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(Ph-C=C-COO)(NH4).sdf",
        measured_diamag_sus=-98.5,
        literature_reference="No. 1537",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="[HOC](AsF6)2.sdf",
        measured_diamag_sus=-334.0,
        literature_reference="No. 1539",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="[HOC](PF6)2.sdf",
        measured_diamag_sus=-277.0,
        literature_reference="No. 1542",
    ),
    # Test fails due to lack of pascal constant for Sb(V) oxidation state
    # TODO - resolve fails for cases with no data by taking first availbale, most relevant Pascal constant
    DataQualityDiamagContrTestsSDF(
        sdf_file="[HOC](SbF6)2.sdf",
        measured_diamag_sus=-430.0,
        literature_reference="No. 1545",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="[HOC].sdf",
        measured_diamag_sus=-190.0,
        literature_reference="No. 1546",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="[HOC](CF3SO3)2.sdf",
        measured_diamag_sus=-344.0,
        literature_reference="No. 1548",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="[HOC][C(CN)3]2.sdf",
        measured_diamag_sus=-266.0,
        literature_reference="No. 1550",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(NH4)2(CO3)_2H2O.sdf",
        measured_diamag_sus=-68.62,
        literature_reference="No. 1520",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="[NMe4]Br.sdf",
        measured_diamag_sus=-87.2,
        literature_reference="No. 1530",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="[NMe4]I.sdf",
        measured_diamag_sus=-105.0,
        literature_reference="No. 1531",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(PhCOO)(NH4).sdf",
        measured_diamag_sus=-77.98,
        literature_reference="No. 1535",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(HOPhCOO)(NH4).sdf",
        measured_diamag_sus=-86.49,
        literature_reference="No. 1536",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="NH4Cl.sdf",
        measured_diamag_sus=-36.7,
        literature_reference="No. 1551",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="[NH3OH]Cl.sdf",
        measured_diamag_sus=-42.4,
        literature_reference="No. 1552",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(NH4)(ClO3).sdf",
        measured_diamag_sus=-42.1,
        literature_reference="No. 1553",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(NH4)(ClO4).sdf",
        measured_diamag_sus=-46.3,
        literature_reference="No. 1554",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(NH4)MgCl3.sdf",
        measured_diamag_sus=-82.97,
        literature_reference="No. 1556",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="NH4F.sdf",
        measured_diamag_sus=-23.5,
        literature_reference="No. 1558",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(NH4)(IO3).sdf",
        measured_diamag_sus=-62.3,
        literature_reference="No. 1562",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(NH4)MgI3.sdf",
        measured_diamag_sus=-171.14,
        literature_reference="No. 1563",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(NHS)4.sdf",
        measured_diamag_sus=-88.0,
        literature_reference="No. 1566",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(NH4)(H2PO4).sdf",
        measured_diamag_sus=-61.0,
        literature_reference="No. 1567",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(NH4)2(S2O3).sdf",
        measured_diamag_sus=-75.1,
        literature_reference="No. 1568",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(NH4)2(SO4).sdf",
        measured_diamag_sus=-67.0,
        literature_reference="No. 1569",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(NH4)2(TeO4).sdf",
        measured_diamag_sus=-80.15,
        literature_reference="No. 1570",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(NH4)2(S2O8).sdf",
        measured_diamag_sus=-103.8,
        literature_reference="No. 1571",
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
]
