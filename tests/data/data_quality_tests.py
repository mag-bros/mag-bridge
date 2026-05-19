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
    skip_test: bool = False


CALC_DIAMAG_QUALITY_TESTS: list["DataQualityDiamagContrTestsSDF"] = [
    # Aluminum compounds
    DataQualityDiamagContrTestsSDF(
        sdf_file="Al(NH4)(SO4)2.sdf",
        measured_diamag_sus=-98.11,
        literature_reference="No. 3",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Al(IO4)3_6H2O.sdf",
        measured_diamag_sus=-286.9,
        literature_reference="No. 4",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="AlK(SO4)2_12H2O.sdf",
        measured_diamag_sus=-251.28,
        literature_reference="No. 6",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="AlLi(SO4)2_12H2O.sdf",
        measured_diamag_sus=-240.0,
        literature_reference="No. 7",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="AlTl(SO4)2_12H2O.sdf",
        measured_diamag_sus=-266.0,
        literature_reference="No. 8",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Al(NH4)(SO4)2_12H2O.sdf",
        measured_diamag_sus=-253.63,
        literature_reference="No. 9",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="AlK(SO4)2.sdf",
        measured_diamag_sus=-102.33,
        literature_reference="No. 10",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Al2(SO4)3_18H2O.sdf",
        measured_diamag_sus=-335.6,
        literature_reference="No. 12",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Al2O3.sdf",
        measured_diamag_sus=-37.0,
        literature_reference="No. 13",
    ),
    # Antimony compounds
    DataQualityDiamagContrTestsSDF(
        sdf_file="SbBr3.sdf",
        measured_diamag_sus=-111.4,
        literature_reference="No. 16",
    ),
    # TODO How it is correct if there is no Pascal const for Sb(IV)?
    DataQualityDiamagContrTestsSDF(
        sdf_file="(NH4)2[SbBr6].sdf",
        measured_diamag_sus=-249.0,
        literature_reference="No. 19",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Sb(V)(Ph)3Br2.sdf",
        measured_diamag_sus=-232.4,
        literature_reference="No. 22",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Sb(V)(Ph)3Cl2.sdf",
        measured_diamag_sus=-232.4,
        literature_reference="No. 22",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Sb(V)(Ph)3I2.sdf",
        measured_diamag_sus=-261.1,
        literature_reference="No. 24",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Sb(V)(p-MePh)3Br2.sdf",
        measured_diamag_sus=-267.4,
        literature_reference="No. 28",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Sb(V)(p-MePh)3Cl2.sdf",
        measured_diamag_sus=-249.2,
        literature_reference="No. 29",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Sb(V)(o-MePh)3Cl2.sdf",
        measured_diamag_sus=-249.6,
        literature_reference="No. 30",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Sb(V)(p-MePh)3I2.sdf",
        measured_diamag_sus=-295.3,
        literature_reference="No. 31",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Sb(V)(o-MePh)3S.sdf",
        measured_diamag_sus=-233.2,
        literature_reference="No. 33",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Sb(III)(p-MeOPh)3.sdf",
        measured_diamag_sus=-230.1,
        literature_reference="No. 32",
        description="Calculations performed with Sb(III) covalent Pascal constant.",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Sb(3+)(p-MeOPh)3.sdf",
        measured_diamag_sus=-230.1,
        literature_reference="No. 32",
        description="Calculations performed with Sb(3+) ionic Pascal constant.",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Sb(V)(p-MePh)3S.sdf",
        measured_diamag_sus=-231.9,
        literature_reference="No. 34",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Sb(3+)(o-MePh)3.sdf",
        measured_diamag_sus=-217.0,
        literature_reference="No. 35",
        description="Calculations performed with Sb(3+) ionic Pascal constant.",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Sb(III)(o-MePh)3.sdf",
        measured_diamag_sus=-217.0,
        literature_reference="No. 35",
        description="Calculations performed with Sb(III) covalent Pascal constant.",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Sb(V)(1,2-Me2Ph)3Br2.sdf",
        measured_diamag_sus=-300.7,
        literature_reference="No. 37",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Sb(III)(PhOEt)3.sdf",
        measured_diamag_sus=-265.9,
        literature_reference="No. 38",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Sb(3+)(PhOEt)3.sdf",
        measured_diamag_sus=-265.9,
        literature_reference="No. 38",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Sb(III)(1,4-Me2Ph)3.sdf",
        measured_diamag_sus=-251.1,
        literature_reference="No. 39",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Sb(3+)(1,4-Me2Ph)3.sdf",
        measured_diamag_sus=-251.1,
        literature_reference="No. 39",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="SbCl3.sdf",
        measured_diamag_sus=-86.7,
        literature_reference="No. 41",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="[Sb3+][Cl-]3.sdf",
        measured_diamag_sus=-86.7,
        literature_reference="No. 41",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="[Sb5+][Cl-]5.sdf",
        measured_diamag_sus=-120.5,
        literature_reference="No. 42",
    ),
    # Arsenic compounds
    DataQualityDiamagContrTestsSDF(
        sdf_file="AsBr3.sdf",
        measured_diamag_sus=-106.0,
        literature_reference="No. 57",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="AsCl3.sdf",
        measured_diamag_sus=-72.5,
        literature_reference="No. 60",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="AsI3.sdf",
        measured_diamag_sus=-142.2,
        literature_reference="No. 63",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="As(CH3)2O(OH).sdf",
        measured_diamag_sus=-78.7,
        literature_reference="No. 68",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="As(CH2CH3)O(OH)2.sdf",
        measured_diamag_sus=-81.7,
        literature_reference="No. 69",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="As(CH2CH2CH3)O(OH)2.sdf",
        measured_diamag_sus=-93.19,
        literature_reference="No. 70",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="PhAsH2.sdf",
        measured_diamag_sus=-79.71,
        literature_reference="No. 72",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="PhAs(V)O(OH)2.sdf",
        measured_diamag_sus=-108.8,
        literature_reference="No. 73",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="HOPhAs(V)O(OH)2.sdf",
        measured_diamag_sus=-113.8,
        literature_reference="No. 74",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="[1,3-(HO)2Ph]As(V)O(OH)2.sdf",
        measured_diamag_sus=-116.9,
        literature_reference="No. 75",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="{[p-[+H3N]Ph]As(V)O(OH)2.sk2}[Cl-].sdf",
        measured_diamag_sus=-139.8,
        literature_reference="No. 76",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(p-NCPh)As(V)O(OH)2.sdf",
        measured_diamag_sus=-115.7,
        literature_reference="No. 78",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(p-MePh)As(III)H2.sdf",
        measured_diamag_sus=-91.27,
        literature_reference="No. 79",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(p-MePh)As(III)O(OH)2.sdf",
        measured_diamag_sus=-120.0,
        literature_reference="No. 90",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Ph2As(III)Cl.sdf",
        measured_diamag_sus=-145.5,
        literature_reference="No. 83",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="[(Ph)2As(III)]2.sdf",
        measured_diamag_sus=-144.5,
        literature_reference="No. 84",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="{[(+H3NPh)2As(III)]2}[Cl-]2.sdf",
        measured_diamag_sus=-205.0,
        literature_reference="No. 85",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="[(MePh)2As(III)]2.sdf",
        measured_diamag_sus=-165.2,
        literature_reference="No. 92",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(MePh)2(EtO)As(III).sdf",
        measured_diamag_sus=-182.6,
        literature_reference="No. 93",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Ph3As(III).sdf",
        measured_diamag_sus=-177.6,
        literature_reference="No. 95",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Ph3As(V)O.sdf",
        measured_diamag_sus=-199.0,
        literature_reference="No. 96",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Ph3As(V)S.sdf",
        measured_diamag_sus=-193.2,
        literature_reference="No. 98",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Ph3As(V)(OH)2.sdf",
        measured_diamag_sus=-211.0,
        literature_reference="No. 99",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(o-MePh)3As(III).sdf",
        measured_diamag_sus=-213.5,
        literature_reference="No. 102",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(p-MePh)3As(III).sdf",
        measured_diamag_sus=-212.1,
        literature_reference="No. 103",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(m-MePh)3As(V)O.sdf",
        measured_diamag_sus=-217.1,
        literature_reference="No. 104",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(p-MeOPh)3As(III).sdf",
        measured_diamag_sus=-225.6,
        literature_reference="No. 105",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(PhCH2O)3As(III).sdf",
        measured_diamag_sus=-244.0,
        literature_reference="No. 106",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(p-MePh)3As(V)S.sdf",
        measured_diamag_sus=-227.9,
        literature_reference="No. 107",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(1,4-MecyO)3As(III).sdf",
        measured_diamag_sus=-278.0,
        literature_reference="No. 108",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="[(Ph4)As(III)][Re(VI)OBr4].sdf",
        measured_diamag_sus=-360.0,
        literature_reference="No. 109",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(p-EtOPh)3As(III).sdf",
        measured_diamag_sus=-261.0,
        literature_reference="No. 110",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(Ph-CH=CH-CH2O)3As(III).sdf",
        measured_diamag_sus=-259.0,
        literature_reference="No. 111",
    ),
    # Barium compounds
    DataQualityDiamagContrTestsSDF(
        sdf_file="Ba3(AsO3)2.sdf",
        measured_diamag_sus=-183.9,
        literature_reference="No. 112",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="BaBr2_H2O.sdf",
        measured_diamag_sus=-116.6,
        literature_reference="No. 114",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Ba(BrO3)2_H2O.sdf",
        measured_diamag_sus=-117.5,
        literature_reference="No. 115",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="BaBr2_2H2O.sdf",
        measured_diamag_sus=-128.3,
        literature_reference="No. 116",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Ba(BrO3)2.sdf",
        measured_diamag_sus=-105.8,
        literature_reference="No. 117",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="BaCO3.sdf",
        measured_diamag_sus=-58.9,
        literature_reference="No. 118",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Ba(C2O4).sdf",
        measured_diamag_sus=-64.8,
        literature_reference="No. 119",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Ba[Pd(CN)4].sdf",
        measured_diamag_sus=-125.6,
        literature_reference="No. 120",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Ba[Pt(CN)4].sdf",
        measured_diamag_sus=-137.3,
        literature_reference="No. 121",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="BaCl2.sdf",
        measured_diamag_sus=-72.6,
        literature_reference="No. 122",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Ba(ClO3)2_H2O.sdf",
        measured_diamag_sus=-99.2,
        literature_reference="No. 123",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Ba(ClO4)2_H2O.sdf",
        measured_diamag_sus=-106.8,
        literature_reference="No. 124",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="BaCl2_2H2O.sdf",
        measured_diamag_sus=-100.0,
        literature_reference="No. 125",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Ba(ClO4)2_2H2O.sdf",
        measured_diamag_sus=-119.5,
        literature_reference="No. 127",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Ba(ClO3)2.sdf",
        measured_diamag_sus=-87.5,
        literature_reference="No. 128",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Ba(ClO4)2.sdf",
        measured_diamag_sus=-94.7,
        literature_reference="No. 129",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="BaF2.sdf",
        measured_diamag_sus=-51.0,
        literature_reference="No. 130",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Ba(IO3)2_H2O.sdf",
        measured_diamag_sus=-135.0,
        literature_reference="No. 131",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Ba(NO2)2_H2O.sdf",
        measured_diamag_sus=-58.7,
        literature_reference="No. 132",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Ba(OH)2.sdf",
        measured_diamag_sus=-53.2,
        literature_reference="No. 133",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="BaI2_2H2O.sdf",
        measured_diamag_sus=-163.0,
        literature_reference="No. 134",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Ba(IO3)2_2H2O.sdf",
        measured_diamag_sus=-163.7,
        literature_reference="No. 135",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Ba(S2O6)_2H2O.sdf",
        measured_diamag_sus=-120.0,
        literature_reference="No. 136",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Ba(OH)2_8H2O.sdf",
        measured_diamag_sus=-157.0,
        literature_reference="No. 139",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="BaI2.sdf",
        measured_diamag_sus=-124.4,
        literature_reference="No. 140",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Ba(NO3)2.sdf",
        measured_diamag_sus=-66.5,
        literature_reference="No. 143",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="BaSO4.sdf",
        measured_diamag_sus=-71.3,
        literature_reference="No. 146",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Ba[WO4].sdf",
        measured_diamag_sus=-57.4,
        literature_reference="No. 147",
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
    # Boron compounds
    DataQualityDiamagContrTestsSDF(
        sdf_file="Na_HCOO_B(OH)3_2H2O.sdf",
        measured_diamag_sus=-88.9,
        literature_reference="No. 1534.",
    ),
    # Bismuth compounds
    DataQualityDiamagContrTestsSDF(
        sdf_file="Bi_Cl_2_PhMe_3.sdf",
        measured_diamag_sus=-263.4,
        literature_reference="No. 1481.",
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
    # Nitrogen compounds
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
        skip_test=True,
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
    DataQualityDiamagContrTestsSDF(
        sdf_file="(NH4)2(HPO4).sdf",
        measured_diamag_sus=-71.0,
        literature_reference="No. 1572",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(NH4)2(SO3)_H2O.sdf",
        measured_diamag_sus=-70.3,
        literature_reference="No. 1573",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="(NH4)MgI3_6H2O.sdf",
        measured_diamag_sus=-250.9,
        literature_reference="No. 1575",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="N2.sdf",
        measured_diamag_sus=-12.04,
        literature_reference="No. 1576",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="[-N]=[N+]=O_resonance_form_of_N2O.sdf",
        measured_diamag_sus=-18.9,
        literature_reference="No. 1577",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="N#[N+]-[O-]_resonance_form_of_N2O.sdf",
        measured_diamag_sus=-18.9,
        literature_reference="No. 1577",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="N2O2.sdf",
        measured_diamag_sus=-25.4,
        literature_reference="No. 1578",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="N2O3.sdf",
        measured_diamag_sus=-23.2,
        literature_reference="No. 1579",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="N2O4.sdf",
        measured_diamag_sus=-25.2,
        literature_reference="No. 1580",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="N2O5.sdf",
        measured_diamag_sus=-35.6,
        literature_reference="No. 1581",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="N4S4.sdf",
        measured_diamag_sus=-102.0,
        literature_reference="No. 1582",
    ),
    # Osmium compounds
    DataQualityDiamagContrTestsSDF(
        sdf_file="K4[Os(CN6)]_3H2O.sdf",
        measured_diamag_sus=-223.8,
        literature_reference="No. 1589",
    ),
    DataQualityDiamagContrTestsSDF(
        sdf_file="Os(cp)2.sdf",
        measured_diamag_sus=-193.0,
        literature_reference="No. 1591",
    ),
    # TODO No Os(0) constant available - use Os(II) constant instead
    DataQualityDiamagContrTestsSDF(
        sdf_file="[Os(CO)4]3.sdf",
        measured_diamag_sus=-293.0,
        literature_reference="No. 1592",
        skip_test=True,
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
]
