from collections import Counter
from dataclasses import dataclass, field
from typing import Counter, Optional


@dataclass(frozen=True, slots=True)
class SubstructMatchTest:
    """Represents a single bond-matching test case: a molecule (SMILES) with the expected bond-type match counts and an optional description."""

    id: int  # indexing from 1
    SMILES: str
    expected_matches: Counter[str] = field(default_factory=Counter)
    description: Optional[str] = ""
    skip_test: bool = False


SUBSTRUCT_MATCH_TESTS: list[SubstructMatchTest] = [
    SubstructMatchTest(
        id=1,
        SMILES="ClC=CC(Cl)C=CCl",
        expected_matches=Counter({"C=C": 2, "C-Cl": 3}),
        description="When counting bond types C=C and C-Cl, the same C atom for both bond types can be considered.",
    ),
    SubstructMatchTest(
        id=2,
        SMILES="C=CCC=C",
        expected_matches=Counter({"CH2=CH-CH2-": 1, "C=C": 1}),
        description="All carbon atoms of allyl group cannot belong to other bond type!",
    ),
    SubstructMatchTest(
        id=3,
        SMILES="CC(=CC=CC=C(C)C=CC=C(C)C(=O)OC1C(C(C(C(O1)COC2C(C(C(C(O2)CO)O)O)O)O)O)O)C=CC=C(C)C(=O)OC3C(C(C(C(O3)COC4C(C(C(C(O4)CO)O)O)O)O)O)O",
        expected_matches=Counter({"C=C-C=C": 3, "C=C": 1, "RCOOR": 2}),
        description="All carbon atoms of C=C-C=C fragment cannot belong to other bond type! For ester RCOOR group the results are correct.",
    ),
    SubstructMatchTest(
        id=4,
        SMILES="CC(=C)C1CC2=C(O1)C=CC3=C2OC4COC5=CC(=C(C=C5C4C3=O)OC)OC",
        expected_matches=Counter({"Ar-OR": 5, "benzene": 2, "C=C": 1, "Ar-C(=O)R": 1}),
    ),
    # TODO Fix required - Ar-O-Ar should be matched twice as Ar-OR bond type.
    SubstructMatchTest(
        id=5,
        SMILES="CC1(C(C1C(=O)OC(C#N)C2=CC(=CC=C2)OC3=CC=CC=C3)C=C(Cl)Cl)C",
        expected_matches=Counter(
            {
                "-C#N": 1,
                "C-Cl": 2,
                "RCOOR": 1,
                "benzene": 2,
                "cyclopropane": 1,
                "C=C": 1,
                "Ar-OR": 2,
            }
        ),
        description="Tests if ArOAr was not incorrectly matched.",
    ),
    SubstructMatchTest(
        id=6,
        SMILES="CC1CC2C3CCC4=CC(=O)C=CC4(C3(C(CC2(C1(C(=O)CO)O)C)O)F)C",
        expected_matches=Counter(
            {
                "C=O": 2,
                "cyclohexane": 2,
                "cyclopentane": 1,
                "C=C": 2,
            }
        ),
        description="""
            Tests saturated policyclic systems. 
            Saturated rings will not be matched when attached to aromatic ring by the ring's edge.""",
    ),
    SubstructMatchTest(
        id=7,
        SMILES="C1=CN(C(=O)N=C1N)C2C(C(C(O2)CO)O)O",
        expected_matches=Counter({"tetrahydrofuran": 1}),
        description="""
            Tests tricky case of pyrimidinone ring in the structure, which cannot be matched as pyrimidine ring.
            Pyrimidine ring is not matched when one of the carbons is a part of carbonyl group.""",
    ),
    SubstructMatchTest(
        id=8,
        SMILES="CCCCNC(=O)OCC#CI",
        expected_matches=Counter({"C#C": 1, "C-I": 1, "RC(=O)NH2": 1}),
        description="""
            Important case of carbamate ROC(=O)NHR group.
            RCOOR and RCOONHR groups are not matched when being part of carbamate fragment.""",
    ),
    SubstructMatchTest(
        id=9,
        SMILES="CC#CC[N]1C3=C(N=C1N2CCCC(C2)N)N(C(=O)N(C3=O)CC5=NC4=CC=CC=C4C(=N5)C)C",
        expected_matches=Counter(
            {
                "Ar-NR2": 1,
                "C#C": 1,
                "benzene": 1,
                "imidazole": 1,
                "piperidine": 1,
                "pyrimidine": 1,
            }
        ),
        description="""
                Example of fused ring system and improtant case of piperidine and Ar-NR2 matching.
                Note that for fused ring systems each ring is matched separately which is a rough approximation. 
                Also, Ar-CONR2 group is omitted in query.""",
    ),
    SubstructMatchTest(
        id=10,
        SMILES="CC#CC1(CCC2C1(CC(C3=C4CCC(=O)C=C4CCC23)C5=CC=C(C=C5)N(C)C)C)O",
        expected_matches=Counter(
            {
                "Ar-NR2": 1,
                "C#C": 1,
                "C=O": 1,
                "benzene": 1,
                "cyclohexane": 1,
                "cyclohexene": 2,
                "cyclopentane": 1,
            }
        ),
        description="""
                Important case of cyclohexene fused system and cyclohexenone ring.
                For cyclohexenone separate C=O and cyclohexene ring matching is allowed. 
                C=C-C=C is NOT matched when C atoms are part of fused cyclohexene ring system.""",
    ),
    SubstructMatchTest(
        id=11,
        SMILES="CN(C)C1=CC=C(C=C1)C(=C2C=CC(=[N+](C)C)C=C2)C3=CC=C(C=C3)N(C)C",
        expected_matches=Counter(
            {"C=N": 1, "Ar-NR2": 2, "Ar-C=C": 1, "benzene": 2, "C=C": 2}
        ),
        description="""
            Highlights the complexity of C=C-C=C, C=C and Ar-C=C matching.
            Result:. For the molecule, Ar-C=C cannot be matched twice!
            Note that C=C-C=C as well as C=C are not matched because of the presence of Ar-C=C bond type!
            The C=N bond counts also with charged N+ atom.""",
    ),
    SubstructMatchTest(
        id=12,
        SMILES="C1C=C2C(=CC(=O)O2)C(O1)O",
        expected_matches=Counter({"C=C-C=C": 1, "RCOOR": 1}),
        description="Checks simple RCOOR and C=C-C=C matching.",
    ),
    SubstructMatchTest(
        id=13,
        SMILES="CC(=O)NC1CCC2=CC(=C(C(=C2C3=CC=C(C(=O)C=C13)OC)OC)OC)OC",
        expected_matches=Counter(
            {"RC(=O)NH2": 1, "Ar-OR": 4, "Ar-Ar": 1, "benzene": 1}
        ),
        description="""
            This is a corner case of aromaticity involving the seven-membered tropone ring. RDKit treats it as aromatic, but it is, in fact, antiaromatic.
            See (DOI): https://doi.org/10.1021/acs.orglett.0c02343
            Note that RDKit treats antiaromatic rings as aromatic.""",
    ),
    SubstructMatchTest(
        id=14,
        SMILES="CC1=CC(=C(C(=C1C=CC(=CC=CC(=CC(=O)[O-])C)C)C)C)OC",
        expected_matches=Counter(
            {"C=C-C=C": 1, "C=C": 1, "Ar-C=C": 1, "Ar-OR": 1, "benzene": 1, "RCOOH": 1}
        ),
        description="""
            Highlights the problem with self-matching of C=C-C=C bond type.
            The C=C-C=C-C=C fragment of the molecule should be matched as C=C-C=C (1) and C=C (1).""",
    ),
    SubstructMatchTest(
        id=15,
        SMILES="COC1=C(C=CC(=C1)CC=C)[O-]",
        expected_matches=Counter(
            {"CH2=CH-CH2-": 1, "Ar-OH": 1, "Ar-OR": 1, "benzene": 1}
        ),
        description="Checks matching of phenolate and allyl group attached to aromatic ring.",
    ),
    SubstructMatchTest(
        id=16,
        SMILES="C=CCN=C=S",
        expected_matches=Counter({"CH2=CH-CH2-": 1}),
        description="""
            Highlights the possibility of C=N matching in isothiocyanate S=C=N group.
            Should no match C=N.""",
    ),
    SubstructMatchTest(
        id=17,
        SMILES="C=CCN2CCC13C5C(=O)CCC1(C2CC4=C3C(=C(C=C4)O)O5)O",
        expected_matches=Counter(
            {
                "CH2=CH-CH2-": 1,
                "C=O": 1,
                "Ar-OH": 1,
                "Ar-OR": 1,
                "benzene": 1,
                "cyclohexane": 1,
                "piperidine": 1,
            }
        ),
        description="""
            Complex ring system with bicyclic fragment. Shows issue with saturated rings matching.
            Note that saturated rings are not matched when fused with aromatic rings via C=C edge.""",
    ),
    SubstructMatchTest(
        id=18,
        SMILES="CCCC(C)C1(C(=O)NC(=O)NC1=O)CC=C",
        expected_matches=Counter({"CH2=CH-CH2-": 1}),
        description="""
            Tricky amide group matching in a barbiturate ring.
            We assumed that RCONHR amide group is not matched when N atom is conneted to two carbonyl C atoms.""",
    ),
    SubstructMatchTest(
        id=19,
        SMILES="CC1=C(C(=O)C=CO1)O",
        expected_matches=Counter({"pyrones": 1, "Ar-OH": 1}),
        description="Example of gamma-pyrone derivative, which RDKit treats as aromatic molecule.",
    ),
    SubstructMatchTest(
        id=20,
        SMILES="CC(=O)CC(C1=CC=CC=C1)C2=C(C3=CC=CC=C3OC2=O)O",
        expected_matches=Counter({"C=O": 1, "Ar-OH": 1, "benzene": 2, "pyrones": 1}),
        description="Interesting case of alpha-pyrone being part of fused aromatic ring system.",
    ),
    SubstructMatchTest(
        id=21,
        SMILES="CC(=O)SC1CC2=CC(=O)CCC2(C3C1C4CCC5(C4(CC3)C)CCC(=O)O5)C",
        expected_matches=Counter(
            {
                "C=O": 2,
                "RCOOR": 1,
                "cyclohexane": 2,
                "cyclohexene": 1,
                "cyclopentane": 1,
            }
        ),
        description="""
            Highlights the possibility of matching of RCOOR within tetrahydrofuran ring.
            RCOOR matched, while tetrahydrofuran ring ignored. Also, the C=O in thioester RC(=O)SR groups is ignored.""",
    ),
    SubstructMatchTest(
        id=22,
        SMILES="CC(C)(C)C(=O)C(N1C=NC=N1)OC2=CC=C(C=C2)Cl",
        expected_matches=Counter({"C=O": 1, "Ar-OR": 1, "Ar-Cl": 1, "benzene": 1}),
        description="""
            Shows that not all aromatic rings are considered in the query due to limited literature data.
            Examine Triazole ring not matched.""",
    ),
    SubstructMatchTest(
        id=23,
        SMILES="CC1C(C(C(O1)OC2C(C(C(C(C2O)O)N=C(N)N)O)N=C(N)N)OC3C(C(C(C(O3)CO)O)O)NC)(C=O)O",
        expected_matches=Counter(
            {"C=O": 1, "cyclohexane": 1, "tetrahydrofuran": 1, "C=N": 2}
        ),
        description="""
            Highlights that C=N is ignored when being part of guanidine group.
            Examine C=N not matched.""",
    ),
    SubstructMatchTest(
        id=24,
        SMILES="CC1CCC2=C3N1C=C(C(=O)C3=CC(=C2)F)C(=O)[O-]",
        expected_matches=Counter({"Ar-COOH": 1, "benzene": 1}),
        description="Highlights that pyridine ring is not matched when one of its C atoms is a part of C=O group.",
    ),
    SubstructMatchTest(
        id=25,
        SMILES="CC1=C(C(CCC1)(C)C)C=CC(=CC=CC(=CC(=O)O)C)C",
        expected_matches=Counter({"C=C-C=C": 2, "RCOOH": 1, "cyclohexene": 1}),
        description="Examine C=C-C=C self-matching.",
    ),
    # TODO: rdkit error?
    SubstructMatchTest(
        id=26,
        SMILES="C1=CC=C(C(=C1)C2=C3C=CC(=O)C=C3OC4=C2C=CC(=C4)[O-])C(=O)[O-]",
        expected_matches=Counter({"Ar-OH": 1, "Ar-Ar": 1, "Ar-COOH": 1, "benzene": 3}),
        description="Corner case of Ar-Ar matching.",
        skip_test=True,
    ),
    # TODO: rdkit error?
    SubstructMatchTest(
        id=27,
        SMILES="CCN(CC)C1=CC2=C(C=C1)C(=C3C=CC(=[N+](CC)CC)C=C3O2)C4=CC=CC=C4C(=O)O",
        expected_matches=Counter({"Ar-NR2": 1, "Ar-Ar": 1, "Ar-COOH": 1, "benzene": 3}),
        description="Corner case of Ar-Ar matching.",
        skip_test=True,
    ),
    SubstructMatchTest(
        id=28,
        SMILES="CC1=C(C(CC(C1=O)O)(C)C)C=CC(=CC=CC(=CC=CC=C(C)C=CC=C(C)C=CC2=C(C(=O)C(CC2(C)C)O)C)C)C",
        expected_matches=Counter({"C=C-C=C": 4, "C=C": 1, "C=O": 2, "cyclohexene": 2}),
        description="Examine C=C-C=C self-matching.",
    ),
    SubstructMatchTest(
        id=29,
        SMILES="C=CC1=C(N2C(C(C2=O)NC(=O)C(=NOCC(=O)O)C3=CSC(=N3)N)SC1)C(=O)O",
        expected_matches=Counter(
            {"C=C-C=C": 1, "RCOOH": 2, "RC(=O)NH2": 2, "C=N": 1, "thiazole": 1}
        ),
        description="Thiazole derivative example. RCONR2 allowed.",
    ),
    SubstructMatchTest(
        id=30,
        SMILES="C=CCCCC(=C)C/C=C/C(C)=C/C=C/C(C)=C/C=C/C=C(C)/C=C/C=C(C)/C=C/C=C(C)/CC/C=C(C)\C",
        expected_matches=Counter(
            {
                "C=C-C=C": 5,
                "C=C": 2,
                "CH2=CH-CH2-": 1,
            }
        ),
        description="Example encompassing C=C-C=C, C=C and CH2=CH-CH2- bond types.",
    ),
    SubstructMatchTest(
        id=31,
        SMILES="CCN(CC)C(=O)C(=CC1=CC(=C(C(=C1)O)O)[N+](=O)[O-])C#N",
        expected_matches=Counter(
            {
                "-C#N": 1,
                "Ar-NO2": 1,
                "Ar-OH": 2,
                "benzene": 1,
                "Ar-C=C": 1,
                "RC(=O)NH2": 1,
            }
        ),
        description="Molecule with Ar-NO2.",
    ),
    SubstructMatchTest(
        id=32,
        SMILES="C1=CC(=C2C(=C1)OC(O2)(F)F)C3=CNC=C3C#N",
        expected_matches=Counter(
            {"-C#N": 1, "Ar-Ar": 1, "Ar-OR": 2, "benzene": 1, "pyrrole": 1}
        ),
        description="Interesting Ar-OR matching.",
    ),
    SubstructMatchTest(
        id=33,
        SMILES="C1C2CC2N(C1C#N)C(=O)C(C34CC5CC(C3)CC(C5)(C4)O)N",
        expected_matches=Counter(
            {
                "cyclopropane": 1,
                "cyclohexane": 1,
                "pyrrolidine": 1,
                "-C#N": 1,
                "RC(=O)NH2": 1,
            }
        ),
        description="Two bicyclic fragments and RCONR2 fragment.",
    ),
    SubstructMatchTest(
        id=34,
        SMILES="C(#N)S",
        expected_matches=Counter({"-C#N": 1}),
        description="Thiocyanite group - C#N bond matching accepted.",
    ),
    SubstructMatchTest(
        id=35,
        SMILES="CC1=C(C(=O)CC1OC(=O)C2C(C2(C)C)C=C(C)C)CC=C",
        expected_matches=Counter(
            {"C=O": 1, "RCOOR": 1, "cyclopropane": 1, "CH2=CH-CH2-": 1, "C=C": 2}
        ),
        description="Check for matching of neighbouring C=C and CH2=CH-CH2- bond types.",
    ),
    SubstructMatchTest(
        id=36,
        SMILES="CC1(C2CCC1(C(=O)C2)C)C",
        expected_matches=Counter({"C=O": 1, "cyclohexane": 1}),
        description="Bicycle molecule example.",
    ),
    SubstructMatchTest(
        id=37,
        SMILES="C1CC1N2C=C(C(=O)C3=CC(=C(C=C32)N4CC[N-]CC4)F)C(=O)[O-]",
        expected_matches=Counter(
            {
                "Ar-COOH": 1,
                "Ar-NR2": 1,
                "benzene": 1,
                "cyclopropane": 1,
                "piperazine": 1,
            }
        ),
        description="Check for piperazine anion and Ar-COO- group.",
    ),
    SubstructMatchTest(
        id=38,
        SMILES="C(C(=O)O)(Cl)Cl",
        expected_matches=Counter({"C-Cl": 2, "RCOOH": 1}),
        description="Adjacent RCHCl2 and RCOOH groups.",
    ),
    SubstructMatchTest(
        id=39,
        SMILES="COC(=O)C(CC1=CC=CC=C1)NC(=O)C(CC(=O)O)N",
        expected_matches=Counter(
            {"RCOOH": 1, "RCOOR": 1, "RC(=O)NH2": 1, "benzene": 1}
        ),
        description="Shows proper RCOOH, RCOOR and RC(=O)NH2 distinction.",
    ),
    SubstructMatchTest(
        id=40,
        SMILES="CC1=CC2C(CCC2(C(CC1)[N+]#[C-])C)C(C)C",
        expected_matches=Counter({"C=C": 1, "-N#C": 1, "cyclopentane": 1}),
        description="Simple isonitrile molecule example.",
    ),
    SubstructMatchTest(
        id=41,
        SMILES="CC(C(C1=NN=C(O1)C2=CC=C(C=C2)F)NC3=C4C=CSC4=C(C=C3)[N+]#[C-])O",
        expected_matches=Counter({"-N#C": 1, "Ar-Ar": 1, "benzene": 2, "thiophene": 1}),
        description="Example with Ar-N#C and benzothiophene.",
    ),
    SubstructMatchTest(
        id=42,
        SMILES="CC1CC2CC(C(C3C2C4C1CCC(C4CC3)(C)N=C=S)(C)[N+]#[C-])C",
        expected_matches=Counter({"cyclohexane": 4, "-N#C": 1}),
        description="Example of fused multiple cyclohexane ring system.",
    ),
    SubstructMatchTest(
        id=43,
        SMILES=" CC1CC2CC(C=C3C2C4C1CCC(C4CC3)(C)[N+]#[C-])(C)C",
        expected_matches=Counter({"cyclohexane": 3, "cyclohexene": 1, "-N#C": 1}),
        description="Example of fused multiple cyclohexane and cyclohexene ring system.",
    ),
    SubstructMatchTest(
        id=44,
        SMILES="CC1(C=C(C23C1CCC(C2)(CCC3)C)[N+]#[C-])C",
        expected_matches=Counter({"-N#C": 1, "cyclohexane": 1, "C=C": 1}),
        description="bicyclo[2.2.2]octane derivative.",
    ),
    SubstructMatchTest(
        id=45,
        SMILES="CC1(C2C3C(=O)C(C(C2=O)(C4=C5C1(O3)C(=O)N(C5=CC=C4)C)[N+]#[C-])(C)C=C)C",
        expected_matches=Counter(
            {
                "-N#C": 1,
                "C=O": 2,
                "C=C": 1,
                "benzene": 1,
                "cyclohexane": 1,
                "tetrahydrofuran": 1,
                "RC(=O)NH2": 1,
            }
        ),
        description="Alkyllated amide bond.",
    ),
    SubstructMatchTest(
        id=46,
        SMILES="CC1CCC(CC1)NC(=O)C2=CC3=C(C=C(C=C3N2)[N+]#[C-])C#N",
        expected_matches=Counter(
            {
                "-C#N": 1,
                "-N#C": 1,
                "Ar-C(=O)NH2": 1,
                "benzene": 1,
                "cyclohexane": 1,
                "pyrrole": 1,
            }
        ),
        description="Both -C#N and -N#C groups in the structure.",
    ),
    SubstructMatchTest(
        id=47,
        SMILES="CC1(C2CC(C(C(=C2C3=CNC4=CC=CC1=C43)[N+]#[C-])(C)C=C)Cl)C",
        expected_matches=Counter(
            {
                "-N#C": 1,
                "C-Cl": 1,
                "benzene": 1,
                "cyclohexene": 1,
                "pyrrole": 1,
                "C=C": 1,
            }
        ),
        description="Ar-C=C and cyclohexene overlap. Solved.",
    ),
    SubstructMatchTest(
        id=48,
        SMILES="C1CN2CCN1CC2",
        expected_matches=Counter({"piperazine": 1}),
        description="DABCO - one piperazine ring matching.",
    ),
    SubstructMatchTest(
        id=49,
        SMILES="[C-]#[N+]C(=CC1=CC=C(C=C1)O)C(=CC2=CC=C(C=C2)O)[N+]#[C-]",
        expected_matches=Counter({"-N#C": 2, "Ar-OH": 2, "benzene": 2, "Ar-C=C": 2}),
        description="Adjacent Ar-C=C and -N#C groups.",
    ),
    SubstructMatchTest(
        id=50,
        SMILES="CC1(CC(C23C1CCC(C2)(CCC3)C)[N+]#[C-])C",
        expected_matches=Counter({"cyclohexane": 1, "cyclopentane": 1, "-N#C": 1}),
        description="bicyclo[2.2.2]octane fused with cyclopentane.",
    ),
    SubstructMatchTest(
        id=51,
        SMILES="[C-]#[N+]C12CC3CC(C1)CC(C3)C2",
        expected_matches=Counter({"cyclohexane": 1, "-N#C": 1}),
        description="Adamantane - fusion of three cyclohexane rings.",
    ),
    SubstructMatchTest(
        id=52,
        SMILES="C1CC2CC2C1",
        expected_matches=Counter({"cyclopentane": 1, "cyclopropane": 1}),
        description="Corner case of bicyclo[3.1.0]hexane. To solve: cyclopropane must not share 3 atom indicies with cyclohexene ring.",
    ),
    SubstructMatchTest(
        id=53,
        SMILES="CC(C)(C)OC(=O)NC12CC(C1)(C2)C(=O)O",
        expected_matches=Counter({"cyclobutane": 1, "RCOOH": 1, "RC(=O)NH2": 1}),
        description="Bicyclo[1.1.1]pentane containing fused cyclobutane rings. Assignment of amide fragment allowed for carbamate group.",
    ),
    SubstructMatchTest(
        id=54,
        SMILES="CC(C)(C)OC(=O)NC12CCC(C1)(C2)C(=O)O",
        expected_matches=Counter({"cyclobutane": 1, "RCOOH": 1, "RC(=O)NH2": 1}),
        description="Bicyclo[2.1.1]hexane containing fused cyclobutane and cyclopentane rings. Assignment of amide fragment allowed for carbamate group.",
    ),
    SubstructMatchTest(
        id=55,
        SMILES="C1C[C@H]2C[C@@H]1[C@H]([C@H]2C(=O)[O-])C(=O)[O-]",
        expected_matches=Counter({"RCOOH": 2, "cyclohexane": 1}),
        description="Check for matching with stereo-SMILES.",
    ),
    SubstructMatchTest(
        id=56,
        SMILES="CC(C12CC(C1)(C2)C34CC(C3)(C4)C(=O)O)(F)F",
        expected_matches=Counter({"cyclobutane": 2, "RCOOH": 1}),
        description="Adjacent bicyclo[1.1.1]hexane groups",
    ),
    SubstructMatchTest(
        id=57,
        SMILES="CC(C)(C)OC(=O)N1CCC2(CC1)C3CC(C2C=C3)C(=O)O",
        expected_matches=Counter(
            {"RCOOH": 1, "cyclohexene": 1, "piperidine": 1, "RC(=O)NH2": 1}
        ),
        description="Cyclohexene containing bicyclo fragment bonded to piperidine ring. Assignment of amide fragment allowed for carbamate group.",
    ),
    SubstructMatchTest(
        id=58,
        SMILES="C1CCC2C(C1)CC2=O",
        expected_matches=Counter({"cyclobutane": 1, "cyclohexane": 1, "C=O": 1}),
        description="Fused cyclohexane and cyclobutanon rings.",
    ),
    SubstructMatchTest(
        id=59,
        SMILES="C1C2C=CC1NC2=O",
        expected_matches=Counter({"C=C": 1, "RC(=O)NH2": 1}),
        description="Pyrrolidine ring is not matched when N forms amid bond with adjacent C=O.",
    ),
    SubstructMatchTest(
        id=60,
        SMILES="CC(C)(C)OC(=O)N1CC2CC2C1C(=O)O",
        expected_matches=Counter(
            {"RCOOH": 1, "cyclopropane": 1, "pyrrolidine": 1, "RC(=O)NH2": 1}
        ),
        description="Corner case of azabicyclo[3.1.0]hexene with fused piperidine, pyrrolidine and cyclopropane.",
    ),
    SubstructMatchTest(
        id=61,
        SMILES="C1C2C1(C(=O)NC2=O)C3=CC=CC=C3",
        expected_matches=Counter({"benzene": 1, "cyclopropane": 1, "RC(=O)NH2": 2}),
        description="Check for imide group incorporated into azabicyclo[3.2.1]hexene.",
    ),
    SubstructMatchTest(
        id=62,
        SMILES="C1CCC2(CC1)CC3=C(O2)C(=CC(=C3)Cl)C(=O)N[C@@H]4CN5CCC4CC5",
        expected_matches=Counter(
            {
                "cyclohexane": 1,
                "benzene": 1,
                "Ar-OR": 1,
                "Ar-Cl": 1,
                "Ar-C(=O)NH2": 1,
                "piperidine": 1,
            }
        ),
        description="Check for azabicyclo[2.2.2] fragment with fused piperidine ring.",
    ),
    SubstructMatchTest(
        id=63,
        SMILES="C1CCN(CC1)C2(C3CN(CC2COC3)CC4=CC=CC=C4)C5=CC=CC=C5",
        expected_matches=Counter({"benzene": 2, "piperidine": 2}),
        description="Piperidine rings - one terminal and one incorporated in bicyclic fragment.",
    ),
    SubstructMatchTest(
        id=64,
        SMILES="CN1C2CCC1C=C(C2)C3=C(C=CS3)Br",
        expected_matches=Counter(
            {"Ar-Br": 1, "pyrrolidine": 1, "thiophene": 1, "Ar-C=C": 1}
        ),
        description="Azabicyclo[3:2:1]octene derivative with additional thiophene ring and Ar-Br bond.",
    ),
    SubstructMatchTest(
        id=65,
        SMILES="C1C2CN(CC1C2=O)CC3=CC=CC=C3",
        expected_matches=Counter({"cyclobutane": 1, "C=O": 1, "benzene": 1}),
        description="Corner case - cyclobutane and piperidine fused into bicyclic structure.",
    ),
    SubstructMatchTest(
        id=66,
        SMILES="C12CC1C2",
        expected_matches=Counter({"cyclopropane": 2}),
        description="bicyclo[1.1.0], carbocycle",
    ),
    SubstructMatchTest(
        id=67,
        SMILES="C12CC1N2",
        expected_matches=Counter({"cyclopropane": 1}),
        description="with heteroatoms",
    ),
    SubstructMatchTest(
        id=68,
        SMILES="C12OC1C2",
        expected_matches=Counter({"cyclopropane": 1}),
    ),
    SubstructMatchTest(
        id=69,
        SMILES="C12CCC1C2",
        expected_matches=Counter({"cyclopropane": 1, "cyclobutane": 1}),
        description="bicyclo[2.1.0], carbocycle",
    ),
    SubstructMatchTest(
        id=70,
        SMILES="C12CNC1C2",
        expected_matches=Counter({"cyclopropane": 1}),
        description="with N/O",
    ),
    SubstructMatchTest(
        id=71,
        SMILES="C12CCC1N2",
        expected_matches=Counter({"cyclobutane": 1}),
    ),
    SubstructMatchTest(
        id=72,
        SMILES="C12COC1C2",
        expected_matches=Counter({"cyclopropane": 1}),
    ),
    SubstructMatchTest(
        id=73,
        SMILES="C12CCC1O2",
        expected_matches=Counter({"cyclobutane": 1}),
    ),
    SubstructMatchTest(
        id=74,
        SMILES="C12C=CC1C2",
        expected_matches=Counter({"cyclopropane": 1, "C=C": 1}),
        description="with C=C",
    ),
    SubstructMatchTest(
        id=75,
        SMILES="C12CCCC1C2",
        expected_matches=Counter({"cyclopropane": 1, "cyclopentane": 1}),
        description="bicyclo[3.1.0], carbocycle",
    ),
    SubstructMatchTest(
        id=76,
        SMILES="C12CNCC1C2",
        expected_matches=Counter({"pyrrolidine": 1, "cyclopropane": 1}),
        description="with N/O",
    ),
    SubstructMatchTest(
        id=77,
        SMILES="C12CCCC1N2",
        expected_matches=Counter({"cyclopentane": 1}),
    ),
    SubstructMatchTest(
        id=78,
        SMILES="C12COCC1C2",
        expected_matches=Counter({"tetrahydrofuran": 1, "cyclopropane": 1}),
    ),
    SubstructMatchTest(
        id=79,
        SMILES="C12CCCC1O2",
        expected_matches=Counter({"cyclopentane": 1}),
    ),
    SubstructMatchTest(
        id=80,
        SMILES="C12CNCC1O2",
        expected_matches=Counter({"pyrrolidine": 1}),
    ),
    SubstructMatchTest(
        id=81,
        SMILES="C12COCC1N2",
        expected_matches=Counter({"tetrahydrofuran": 1}),
    ),
    SubstructMatchTest(
        id=82,
        SMILES="C12COCC1O2",
        expected_matches=Counter({"tetrahydrofuran": 1}),
    ),
    SubstructMatchTest(
        id=83,
        SMILES="C12CNCC1N2",
        expected_matches=Counter({"pyrrolidine": 1}),
    ),
    SubstructMatchTest(
        id=84,
        SMILES="C12CC=CC1C2",
        expected_matches=Counter({"cyclopropane": 1, "C=C": 1}),
        description="with C=C and C/N",
    ),
    SubstructMatchTest(
        id=85,
        SMILES="C12CC(C1)C2",
        expected_matches=Counter({"cyclobutane": 1}),
        description="bicyclo[1.1.1], carbocycle",
    ),
    SubstructMatchTest(
        id=86,
        SMILES="C12NC(C1)C2",
        expected_matches=Counter({"cyclobutane": 1}),
        description="with N/O",
    ),
    SubstructMatchTest(
        id=87,
        SMILES="C12OC(C1)C2",
        expected_matches=Counter({"cyclobutane": 1}),
    ),
    SubstructMatchTest(
        id=88,
        SMILES="C12CCC1CC2",
        expected_matches=Counter({"cyclobutane": 2}),
        description="bicyclo[2.2.0], carbocycle",
    ),
    SubstructMatchTest(
        id=89,
        SMILES="C12CNC1CC2",
        expected_matches=Counter({"cyclobutane": 1}),
        description="with N/O",
    ),
    SubstructMatchTest(
        id=90,
        SMILES="C12CNC1CN2",
        expected_matches=Counter({"piperazine": 1}),
        description="Strained fused piperazine ring - corner case accepted for code simplicity.",
    ),
    SubstructMatchTest(
        id=91,
        SMILES="C12COC1CC2",
        expected_matches=Counter({"cyclobutane": 1}),
    ),
    SubstructMatchTest(
        id=92,
        SMILES="C12COC1CO2",
        expected_matches=Counter({"dioxane": 1}),
        description="Strained fused dioxane ring - corner case accepted for code simplicity.",
    ),
    SubstructMatchTest(
        id=93,
        SMILES="C12COC1CN2",
        expected_matches=Counter({"morpholine": 1}),
        description="Strained fused dioxane ring - corner case accepted for code simplicity.",
    ),
    SubstructMatchTest(
        id=94,
        SMILES="C12C=CC1CC2",
        expected_matches=Counter({"cyclobutane": 1, "C=C": 1}),
        description="with C=C",
    ),
    SubstructMatchTest(
        id=95,
        SMILES="C12CCC(C1)C2",
        expected_matches=Counter({"cyclobutane": 1}),
        description="bicyclo[2.1.1], carbocycle",
    ),
    SubstructMatchTest(
        id=96,
        SMILES="C12CNC(C1)C2",
        expected_matches=Counter({"cyclobutane": 1}),
        description="with N/O",
    ),
    SubstructMatchTest(
        id=97,
        SMILES="C12CCC(C1)N2",
        expected_matches=Counter({"pyrrolidine": 1}),
    ),
    SubstructMatchTest(
        id=98,
        SMILES="C12COC(C1)C2",
        expected_matches=Counter({"cyclobutane": 1}),
    ),
    SubstructMatchTest(
        id=99,
        SMILES="C12CCC(C1)O2",
        expected_matches=Counter({"tetrahydrofuran": 1}),
    ),
    SubstructMatchTest(
        id=100,
        SMILES="C12C=CC(C1)C2",
        expected_matches=Counter({"cyclobutane": 1, "C=C": 1}),
        description="with C=C",
    ),
    SubstructMatchTest(
        id=101,
        SMILES="C1CC2CCC1C2",
        expected_matches=Counter({"cyclohexane": 1}),
        description="bicyclo[2.2.1], carbocycle",
    ),
    SubstructMatchTest(
        id=102,
        SMILES="C1CC2CNC1C2",
        expected_matches=Counter({"piperidine": 1}),
        description="with N/O",
    ),
    SubstructMatchTest(
        id=103,
        SMILES="C1CC2CCC1N2",
        expected_matches=Counter({"cyclohexane": 1}),
    ),
    SubstructMatchTest(
        id=104,
        SMILES="C1CC2COC1C2",
        expected_matches=Counter({"tetrahydrofuran": 1}),
    ),
    SubstructMatchTest(
        id=105,
        SMILES="C1CC2CCC1O2",
        expected_matches=Counter({"cyclohexane": 1}),
    ),
    SubstructMatchTest(
        id=106,
        SMILES="C1NC2CNC1C2",
        expected_matches=Counter({"piperazine": 1}),
    ),
    SubstructMatchTest(
        id=107,
        SMILES="C1OC2COC1C2",
        expected_matches=Counter({"dioxane": 1}),
    ),
    SubstructMatchTest(
        id=108,
        SMILES="C1OC2CNC1C2",
        expected_matches=Counter({"morpholine": 1}),
    ),
    SubstructMatchTest(
        id=109,
        SMILES="C1CC2CNC1N2",
        expected_matches=Counter({"piperidine": 1}),
    ),
    SubstructMatchTest(
        id=110,
        SMILES="C1CC2COC1O2",
        expected_matches=Counter({"tetrahydrofuran": 1}),
    ),
    SubstructMatchTest(
        id=111,
        SMILES="C1CC2COC1N2",
        expected_matches=Counter({"pyrrolidine": 1}),
    ),
    SubstructMatchTest(
        id=112,
        SMILES="C1CC2CNC1O2",
        expected_matches=Counter({"piperidine": 1}),
    ),
    SubstructMatchTest(
        id=113,
        SMILES="C1CC2C=CC1C2",
        expected_matches=Counter({"cyclohexene": 1}),
        description="with C=C and N/O",
    ),
    SubstructMatchTest(
        id=114,
        SMILES="C1CC2C=CC1N2",
        expected_matches=Counter({"cyclohexene": 1}),
    ),
    SubstructMatchTest(
        id=115,
        SMILES="C1CC2C=CC1O2",
        expected_matches=Counter({"cyclohexene": 1}),
    ),
    SubstructMatchTest(
        id=116,
        SMILES="C1CC2CCC1CC2",
        expected_matches=Counter({"cyclohexane": 1}),
        description="bicyclo[2.2.2], carbocycle",
    ),
    SubstructMatchTest(
        id=117,
        SMILES="C1CC2CNC1CC2",
        expected_matches=Counter({"piperidine": 1}),
        description="with N/O",
    ),
    # TODO allow overlap of RC(=O)NH2 only through N but NOT via C=O
    SubstructMatchTest(
        id=118,
        SMILES="C1CC2COC1CC2",
        expected_matches=Counter({"cyclohexane": 1}),
    ),
    SubstructMatchTest(
        id=119,
        SMILES="N1CC2CNC1CC2",
        expected_matches=Counter({"piperidine": 1}),
    ),
    SubstructMatchTest(
        id=120,
        SMILES="C1NC2COC1CC2",
        expected_matches=Counter({"morpholine": 1}),
    ),
    SubstructMatchTest(
        id=121,
        SMILES="C1NC2CNC1CC2",
        expected_matches=Counter({"piperazine": 1}),
    ),
    SubstructMatchTest(
        id=122,
        SMILES="C1OC2COC1OC2",
        expected_matches=Counter({"dioxane": 1}),
    ),
    SubstructMatchTest(
        id=123,
        SMILES="C1NC2CNC1NC2",
        expected_matches=Counter({"piperazine": 1}),
    ),
    SubstructMatchTest(
        id=124,
        SMILES="C1OC2CNC1NC2",
        expected_matches=Counter({"morpholine": 1}),
    ),
    SubstructMatchTest(
        id=125,
        SMILES="C1OC2COC1NC2",
        expected_matches=Counter({"morpholine": 1}),
    ),
    SubstructMatchTest(
        id=126,
        SMILES="C1CC2C=CC1CC2",
        expected_matches=Counter({"cyclohexene": 1}),
        description="with C=C and N/O",
    ),
    SubstructMatchTest(
        id=127,
        SMILES="C1CC2C=CC1C=C2",
        expected_matches=Counter({"cyclohexene": 1, "C=C": 1}),
    ),
    SubstructMatchTest(
        id=128,
        SMILES="C1CC2C=CC1CN2",
        expected_matches=Counter({"cyclohexene": 1}),
    ),
    SubstructMatchTest(
        id=129,
        SMILES="C1CC2C=CC1CO2",
        expected_matches=Counter({"cyclohexene": 1}),
    ),
    SubstructMatchTest(
        id=130,
        SMILES="N1CC2C=CC1CO2",
        expected_matches=Counter({"morpholine": 1, "C=C": 1}),
    ),
    SubstructMatchTest(
        id=131,
        SMILES="CC(C1=CN=C(C=C1)C(F)(F)F)S(=NC#N)(=O)C",
        expected_matches=Counter({"-C#N": 1, "pyridine": 1}),
        description="Corner case of N-C#N fragment.",
    ),
    SubstructMatchTest(
        id=132,
        SMILES="C1CSC(=NC#N)N1CC2=CN=C(C=C2)Cl",
        expected_matches=Counter({"-C#N": 1, "Ar-Cl": 1, "C=N": 1, "pyridine": 1}),
        description="Conjugated bond system containing N atoms.",
    ),
    SubstructMatchTest(
        id=133,
        SMILES="CC1=C(C(C(=C(N1)C#N)C(=O)OC)C2=CC(=CC=C2)[N+](=O)[O-])C(=O)OC(C)C",
        expected_matches=Counter(
            {"-C#N": 1, "Ar-NO2": 1, "RCOOR": 2, "benzene": 1, "C=C": 2}
        ),
        description="Unknown unsaturated N-ring matching.",
    ),
    SubstructMatchTest(
        id=134,
        SMILES="CNC(=O)C1=C(C=C(C=C1)N2C(=S)N(C(=O)C23CCC3)C4=CC(=C(N=C4)C#N)C(F)(F)F)F",
        expected_matches=Counter(
            {
                "cyclobutane": 1,
                "-C#N": 1,
                "Ar-C(=O)NH2": 1,
                "benzene": 1,
                "pyridine": 1,
                "RC(=O)NH2": 1,
            }
        ),
        description="The case of C(=S)NR-Ar fragment.",
    ),
    SubstructMatchTest(
        id=135,
        SMILES="C1=CC=C2C(=C1)N=C(S2)SCSC#N",
        expected_matches=Counter({"benzene": 1, "thiazole": 1, "-C#N": 1}),
        description="",
    ),
    SubstructMatchTest(
        id=136,
        SMILES="C1=CC=C(C(=C1)C=C(C#N)C#N)Cl",
        expected_matches=Counter({"-C#N": 2, "Ar-Cl": 1, "benzene": 1, "Ar-C=C": 1}),
        description="matching for conjugated bond system with -C#N groups.",
    ),
    SubstructMatchTest(
        id=137,
        SMILES="CC1(C2CCC1(C(C2)OC(=O)CSC#N)C)C",
        expected_matches=Counter({"cyclohexane": 1, "-C#N": 1, "RCOOR": 1}),
        description="thiocyanate groupe and bicyclic fragment.",
    ),
    SubstructMatchTest(
        id=138,
        SMILES="CC1=CC(=CC(=C1NC2=NC(=NC=C2)NC3=CC=C(C=C3)C#N)C)C=CC#N",
        expected_matches=Counter(
            {"-C#N": 2, "benzene": 2, "pyrimidine": 1, "Ar-C=C": 1}
        ),
        description="pryimidine derivative with conjugated bond system having -C#N groups",
    ),
    SubstructMatchTest(
        id=139,
        SMILES="CC(C)(COC1=CN2C(=C(C=N2)C#N)C(=C1)C3=CN=C(C=C3)N4CC5CC(C4)N5CC6=CN=C(C=C6)OC)O",
        expected_matches=Counter(
            {
                "piperazine": 1,
                "-C#N": 1,
                "Ar-Ar": 1,
                "Ar-NR2": 1,
                "Ar-OR": 2,
                "pyridine": 3,
            }
        ),
        description="Nontrival structure with mutliple N-rings and bicyclic fragment.",
    ),
    SubstructMatchTest(
        id=140,
        SMILES="CCCCCCCC(=O)OC1=C(C=C(C=C1Br)C#N)Br",
        expected_matches=Counter({"-C#N": 1, "Ar-Br": 2, "benzene": 1, "RCOOR": 1}),
        description="The case of RC(=O)O-Ar bond type.",
    ),
    SubstructMatchTest(
        id=141,
        SMILES="CCOP(=O)(C#N)N(C)C",
        expected_matches=Counter({"-C#N": 1}),
        description="Corner case of P-C#N bonding.",
    ),
    SubstructMatchTest(
        id=142,
        SMILES="C1CC1NC(=O)C2=CN(C3=C(C2=O)C=CC=N3)C4=CC=CC(=C4)C#CC5=C[N+](=CC=C5)[O-]",
        expected_matches=Counter(
            {
                "cyclopropane": 1,
                "Ar-C#C-Ar": 1,
                "Ar-C(=O)NH2": 1,
                "benzene": 1,
                "pyridine": 2,
            }
        ),
        description="The case of Ar-C#C-Ar bond and pirydine N-oxide fragment.",
    ),
    SubstructMatchTest(
        id=143,
        SMILES="C1CCC2=C(C1)C=C3C=CC4=C(C=CC5=C4C3=C2C=C5)N=O",
        expected_matches=Counter({"benzene": 4, "N=O": 1}),
        description="Nitroso bond type",
    ),
    SubstructMatchTest(
        id=144,
        SMILES="CC1C(OCCN1N=O)C2=CC=CC=C2",
        expected_matches=Counter({"morpholine": 1, "benzene": 1, "N=O": 1}),
        description="N-nitroso group (N-N=O).",
    ),
    SubstructMatchTest(
        id=145,
        SMILES="CC1=C(C(=NO1)C2=CC=CC=C2Cl)C(=O)N[C@H]3[C@@H]4N(C3=O)[C@H](C(S4)(C)C)C(=O)O",
        expected_matches=Counter(
            {
                "Ar-Ar": 1,
                "Ar-C(=O)NH2": 1,
                "RC(=O)NH2": 1,
                "RCOOH": 1,
                "Ar-Cl": 1,
                "benzene": 1,
                "isoxazole": 1,
            }
        ),
        description="Isoxazole is not matched with N=O bond. Ar-C(=O)NHR and RCONR2 within saturated ring.",
    ),
    SubstructMatchTest(
        id=146,
        SMILES="CC1=C(C(=NO1)C2=C(C=CC=C2Cl)Cl)C(=O)NC(=S)N3CCOCC3",
        expected_matches=Counter(
            {
                "morpholine": 1,
                "Ar-Ar": 1,
                "Ar-C(=O)NH2": 1,
                "Ar-Cl": 2,
                "benzene": 1,
                "isoxazole": 1,
            }
        ),
        description="N-acylthiourea C(=S)NHC(=O) derivative example.",
    ),
    SubstructMatchTest(
        id=147,
        SMILES="C1N(CN(CN1[N+](=O)[O-])[N+](=O)[O-])N=O",
        expected_matches=Counter({"N=O": 1, "-NO2": 2}),
        description="One molecule having -NO and -NO2 groups. N-N=O allowed.",
    ),
    # TODO: RCONH2 can overlap only by N atom but not carbonyl C=O fragment
    SubstructMatchTest(
        id=148,
        SMILES="C1CSCCN1NC(=O)N(CCCl)N=O",
        expected_matches=Counter({"RC(=O)NH2": 1, "N=O": 1, "C-Cl": 1}),
        description="Molecule with NC(=O)N fragment",
    ),
    SubstructMatchTest(
        id=149,
        SMILES="C(=O)(O)[O-]",
        expected_matches=Counter({"C=O": 1}),
        description="C=O assignement for HCO3- allowed.",
    ),
    # TODO: 1. Resolve ester RC(=O)OR overlap through C=O
    # TODO: 2. Exclude C=O overlap with ester groups!
    SubstructMatchTest(
        id=150,
        SMILES="CCOC1=NC2=CC=CC(=C2N1CC3=CC=C(C=C3)C4=CC=CC=C4C5=NNN=N5)C(=O)OC(C)OC(=O)OC6CCCCC6",
        expected_matches=Counter(
            {
                "cyclohexane": 1,
                "Ar-Ar": 2,
                "Ar-COOR": 1,
                "Ar-OR": 1,
                "RCOOR": 1,
                "benzene": 3,
                "imidazole": 1,
            }
        ),
        description="Carbonate RCOC(=O)OR example.",
    ),
    # TODO Ester and carbonyl overlap fix
    # TODO Consider adding cyclohexadiene ring that is omitted currently? It will be more elegant to model 6-membered rings with C=C-C(=O)-C=C fragment.
    SubstructMatchTest(
        id=151,
        SMILES="CCC(=O)OCC(=O)[C@]1(CC[C@@H]2[C@@]1(C[C@@H]([C@H]3[C@H]2CCC4=CC(=O)C=C[C@]34C)O)C)OC(=O)OCC",
        expected_matches=Counter(
            {
                "cyclohexane": 2,
                "cyclopentane": 1,
                "C=O": 2,
                "RCOOR": 2,
                "C=C": 2,
            }
        ),
        description="All C=O, RCOOR and ROCOOR possibilities.",
    ),
    SubstructMatchTest(
        id=152,
        SMILES="C[C@@]12[C@H]3CC[C@@H]([C@@]1(C(=O)OC2=O)C)O3",
        expected_matches=Counter({"RCOOR": 2, "cyclohexane": 1}),
        description="Cyclic anhydride fused with bicyclic fragment.",
    ),
    SubstructMatchTest(
        id=153,
        SMILES="C1=CC=C2C(=C1)C(=O)OC2=O",
        expected_matches=Counter({"benzene": 1, "Ar-COOR": 2}),
        description="Phthalic anhydride.",
    ),
    SubstructMatchTest(
        id=154,
        SMILES="C1=CC=C2C(=C1)C(=O)OC(=O)N2",
        expected_matches=Counter({"benzene": 1}),
        description="In aromatic system Ar-C(=O)NH2 and AR-COOR are correctly not matched.",
    ),
    SubstructMatchTest(
        id=155,
        SMILES="CC(C)[C@H]1C(=O)OC(=O)N1C(=O)OCC2=CC=CC=C2",
        expected_matches=Counter({"RC(=O)NH2": 2, "RCOOR": 1, "benzene": 1}),
        description="Structure with RC(=O)OC(=O)NC(=O)R motif.",
    ),
    SubstructMatchTest(
        id=156,
        SMILES="COC(=O)N1CC(=O)OC1=O",
        expected_matches=Counter({"RC(=O)NH2": 2, "RCOOR": 1}),
        description="Ring with RC(=O)OC(=O)NC(=O)R motif.",
    ),
    SubstructMatchTest(
        id=157,
        SMILES="[N-]=[N+]=O",
        expected_matches=Counter({"N=N": 1, "N=O": 1}),
        description="Nitrous oxide resonance form.",
    ),
    SubstructMatchTest(
        id=158,
        SMILES="[N]=O",
        expected_matches=Counter({"N=O": 1}),
        description="Simplest case of N=O bond matching.",
    ),
    SubstructMatchTest(
        id=159,
        SMILES="C1=CC2=C(C=CC(=C2N=C1)O)N=O",
        expected_matches=Counter({"N=O": 1, "benzene": 1, "pyridine": 1, "Ar-OH": 1}),
        description="N=O matching for Ar-N=O fragment allowed.",
    ),
    SubstructMatchTest(
        id=160,
        SMILES="CC(=O)OC/N=[N+](/C)\\[O-]",
        expected_matches=Counter({"RCOOR": 1, "N=N": 1}),
        description="Molecule with N=[N+]-[O-] group.",
    ),
    # TODO Fix RC(=O)NH2 self-matching via C=O
    SubstructMatchTest(
        id=161,
        SMILES="CN(C(=O)N)N=O",
        expected_matches=Counter({"N=O": 1, "RC(=O)NH2": 1}),
    ),
    SubstructMatchTest(
        id=162,
        SMILES="C([N+](=O)[O-])(I)(Cl)Br",
        expected_matches=Counter({"C-Cl": 1, "C-Br": 1, "C-I": 1, "-NO2": 1}),
        description="C-X halogen bond matching check. Adjacent -NO2 group.",
    ),
    SubstructMatchTest(
        id=163,
        SMILES="C([N+](=O)[O-])([N+](=O)[O-])([N+](=O)[O-])[N+](=O)[O-]",
        expected_matches=Counter({"-NO2": 4}),
        description="Tetranitromethane.",
    ),
    SubstructMatchTest(
        id=164,
        SMILES="CC/C(=C\\C(=N\\O)\\C(=O)N)/C(C)[N+](=O)[O-]",
        expected_matches=Counter({"-NO2": 1, "C=N": 1, "C=C": 1, "RC(=O)NH2": 1}),
    ),
    SubstructMatchTest(
        id=165,
        SMILES="CN/C(=C\\[N+](=O)[O-])/NCCSCC1=CC=C(O1)C[N+](C)(C)[O-]",
        expected_matches=Counter({"-NO2": 1, "furan": 1, "C=C": 1}),
        description="R2[N+]-[O-] fragment is (correctly) not matched as N=O.",
    ),
    SubstructMatchTest(
        id=166,
        SMILES="CN=C(NCC1CCOC1)N[N+](=O)[O-]",
        expected_matches=Counter({"tetrahydrofuran": 1, "-NO2": 1, "C=N": 1}),
        description="N=O in guanidine N-C(=N)-N fragment left unassigned due to electron delocalization. -NO2 excluded when N-N bond exists.",
    ),
    SubstructMatchTest(
        id=167,
        SMILES="CCN(CC)CCOC1=CC=C(C=C1)C(=C(C2=CC=CC=C2)Cl)C3=CC=CC=C3",
        expected_matches=Counter({"Ar-OR": 1, "benzene": 3, "C-Cl": 1, "Ar-C=C": 1}),
        description="For Ar-C(-Ar)=C-Ar fragment the bond type Ar-C=C is matched only once (correct).",
    ),
    SubstructMatchTest(
        id=168,
        SMILES="[N+](=O)(O)[O-]",
        expected_matches=Counter({"-NO2": 1}),
        description="-NO2 matched for nitric acid.",
    ),
    SubstructMatchTest(
        id=169,
        SMILES="C1[C@H]([C@@H]2[C@H](O1)[C@H](CO2)O[N+](=O)[O-])O[N+](=O)[O-]",
        expected_matches=Counter({"-NO2": 2, "tetrahydrofuran": 2}),
        description="-NO2 matching for R-ONO2 fragments.",
    ),
    SubstructMatchTest(
        id=170,
        SMILES="CN(C1=C(C=C(C=C1[N+](=O)[O-])[N+](=O)[O-])[N+](=O)[O-])[N+](=O)[O-]",
        expected_matches=Counter({"-NO2": 1, "Ar-NO2": 3, "benzene": 1}),
        description="",
    ),
    SubstructMatchTest(
        id=171,
        SMILES="C1=CC(=CC=C1C(C2=CC=C(C=C2)Cl)C(Cl)(Cl)Cl)Cl",
        expected_matches=Counter({"Ar-Cl": 2, "C-Cl": 3, "benzene": 2}),
        description="Ar-Cl and C-Cl matching.",
    ),
    SubstructMatchTest(
        id=172,
        SMILES="C1C2C(COS(=O)O1)C3(C(=C(C2(C3(Cl)Cl)Cl)Cl)Cl)Cl",
        expected_matches=Counter({"cyclohexene": 1, "R2CCl2": 1, "C-Cl": 4}),
        description="R2CCl2 and multiple C-Cl bonds in one bicyclic fragment.",
    ),
    SubstructMatchTest(
        id=173,
        SMILES="C1[C@@H]2[C@H]3[C@@H]([C@H]1[C@H]4[C@@H]2O4)[C@]5(C(=C([C@@]3(C5(Cl)Cl)Cl)Cl)Cl)Cl",
        expected_matches=Counter(
            {"cyclohexane": 1, "cyclohexene": 1, "R2CCl2": 1, "C-Cl": 4}
        ),
    ),
    SubstructMatchTest(
        id=174,
        SMILES="C(=O)(Cl)Cl",
        expected_matches=Counter({"C-Cl": 2, "C=O": 1}),
        description="Both C-Cl and C=O assigned when part of Cl2C=O.",
    ),
    SubstructMatchTest(
        id=175,
        SMILES="N(=O)Cl",
        expected_matches=Counter({"N=O": 1}),
        description="Nitroso N atom bound to halogen.",
    ),
    SubstructMatchTest(
        id=176,
        SMILES="CC1=[N+](ON=C1[N+](=O)[O-])[O-]",
        expected_matches=Counter({"Ar-NO2"}),
        description="NO2 fragment not assigned when being part of aromatic ring.",
    ),
    SubstructMatchTest(
        id=177,
        SMILES="CC1=CN(C(=O)NC1=O)[C@H]2C[C@@H]([C@H](O2)CO)N=[N+]=[N-]",
        expected_matches=Counter({"tetrahydrofuran": 1, "N=N": 2}),
        description="R-N=N=N is matched as two N=N.",
    ),
    SubstructMatchTest(
        id=178,
        SMILES="CCN(C)C1=CC=C(C=C1)N=NC2=CC=CC=C2",
        expected_matches=Counter({"N=N": 1, "benzene": 2, "Ar-NR2": 1}),
        description="N=N matched as part of Ar-N=N-Ar fragment.",
    ),
    SubstructMatchTest(
        id=179,
        SMILES="C(=O)(N)/N=N/C(=O)N",
        expected_matches=Counter({"N=N": 1, "RC(=O)NH2": 2}),
        description="N=N matched if adjacent to amid C(=O)NH2 group. ",
    ),
    SubstructMatchTest(
        id=180,
        SMILES="CN1C(=O)N2C=NC(=C2N=N1)C(=O)N",
        expected_matches=Counter({"imidazole": 1, "Ar-C(=O)NH2": 1}),
        description="N=N in aromatic ring not matched.",
    ),
    SubstructMatchTest(
        id=181,
        SMILES="C([C@@H](C(=O)O)N)OC(=O)C=[N+]=[N-]",
        expected_matches=Counter({"C=N": 1, "N=N": 1, "RCOOH": 1, "RCOOR": 1}),
        description="N=N=C fragment is matched as N=N and C=N which is a rough approximation.",
    ),
    SubstructMatchTest(
        id=182,
        SMILES="C1=CC(=CC=C1C(=N)N)NN=NC2=CC=C(C=C2)C(=N)N",
        expected_matches=Counter({"N=N": 1, "C=N": 2, "benzene": 2}),
        description="Matching N=N of N=N-N fragment allowed.",
    ),
    SubstructMatchTest(
        id=183,
        SMILES="C=[N+]=[N-]",
        expected_matches=Counter({"C=N": 1, "N=N": 1}),
    ),
    SubstructMatchTest(
        id=184,
        SMILES="C1=CC=C(C=C1)N=[N+](C2=CC=CC=C2)[O-]",
        expected_matches=Counter({"benzene": 2, "N=N": 1}),
        description="N=N matched if present in N=[N+]-[O-] fragment",
    ),
    SubstructMatchTest(
        id=185,
        SMILES="CN1C2=CC=CC=C2C(=C1O)N=NC(=S)N",
        expected_matches=Counter({"benzene": 1, "pyrrole": 1, "N=N": 1, "Ar-OH": 1}),
        description="N=N matching in N=N-C(=S) fragment allowed.",
    ),
    SubstructMatchTest(
        id=186,
        SMILES="C1COCCN1[N+]2=CC(=N)O[N-]2",
        expected_matches=Counter({"morpholine": 1}),
        description="Check for N=N matching (not allowed).",
    ),
    SubstructMatchTest(
        id=187,
        SMILES="C([C@@H](C(=O)O)N)/[N+](=N/O)/[O-]",
        expected_matches=Counter({"N=N": 1, "RCOOH": 1}),
        description="N=N matched for HO-N=[N+]-[O-] fragment.",
    ),
    SubstructMatchTest(
        id=188,
        SMILES="C[Si](C)(C)N=[N+]=[N-]",
        expected_matches=Counter({"N=N": 2}),
        description="N=N matching works for azide group conncted to Si atom.",
    ),
    SubstructMatchTest(
        id=189,
        SMILES="CN(C)C1=CC=C(C=C1)N=NS(=O)(=O)[O-]",
        expected_matches=Counter({"N=N": 1, "benzene": 1, "Ar-NR2": 1}),
        description="",
    ),
    SubstructMatchTest(
        id=190,
        SMILES="CCCC[Sn](CCCC)(CCCC)N=[N+]=[N-]",
        expected_matches=Counter({"N=N": 2}),
        description="N=N assignement works for azide group bound to any non-metal atom.",
    ),
    SubstructMatchTest(
        id=191,
        SMILES="C1=CC=C2C(=C1)C(=O)OI2N=[N+]=[N-]",
        expected_matches=Counter({"N=N": 2, "Ar-I": 1, "benzene": 1}),
        description="Corner case.",
    ),
    SubstructMatchTest(
        id=192,
        SMILES="CC1=NC(=CC=C1)C#CC2=CC(=CC=C2)OC",
        expected_matches=Counter(
            {"Ar-C#C-Ar": 1, "benzene": 1, "pyridine": 1, "Ar-OR": 1}
        ),
        description="Ar-C#C-Ar between different aromatic rings.",
    ),
    SubstructMatchTest(
        id=193,
        SMILES="CN(C)C1=CC=C(C=C1)C2=C(N=CN=C2N)C#CC3=CN=C(C=C3)N4CCOCC4",
        expected_matches=Counter(
            {
                "morpholine": 1,
                "Ar-Ar": 1,
                "Ar-C#C-Ar": 1,
                "Ar-NR2": 2,
                "benzene": 1,
                "pyridine": 1,
                "pyrimidine": 1,
            }
        ),
    ),
    SubstructMatchTest(
        id=194,
        SMILES="CC1=NC(=CS1)C#CC2=CN=CC(=C2)C=C",
        expected_matches=Counter(
            {"Ar-C#C-Ar": 1, "pyridine": 1, "Ar-C=C": 1, "thiazole": 1}
        ),
    ),
    SubstructMatchTest(
        id=195,
        SMILES="COC1=CC=C(C=C1)C2(C3=C(C=CC(=C3)O)C4=C2C(=C(C=C4)C=O)C#CC5=CC=C(C=C5)O)C6=CC=C(C=C6)OC",
        expected_matches=Counter(
            {
                "Ar-Ar": 1,
                "Ar-C#C-Ar": 1,
                "Ar-CHO": 1,
                "Ar-OH": 2,
                "Ar-OR": 2,
                "benzene": 5,
            }
        ),
        description="Ar-CHO and Ar-C#C-Ar in one structure.",
    ),
    SubstructMatchTest(
        id=196,
        SMILES="C1=CC(=O)C=CC1=C(C2=CC=C(C=C2)O)C3=C(C=CC(=C3C#CC4=CC=C(C=C4)O)CO)C5=CC=C(C=C5)O",
        expected_matches=Counter(
            {
                "Ar-Ar": 1,
                "Ar-C#C-Ar": 1,
                "Ar-OH": 3,
                "C=O": 1,
                "benzene": 4,
                "Ar-C=C": 1,
                "C=C": 2,
            }
        ),
    ),
    SubstructMatchTest(
        id=197,
        SMILES="C1=CC=C(C=C1)C#CC2=C3C=CC=CC3=C(C4=CC=CC=C42)C#CC5=CC=CC=C5",
        expected_matches=Counter({"Ar-C#C-Ar": 2, "benzene": 5}),
    ),
    SubstructMatchTest(
        id=198,
        SMILES="CC1=CC=C(C=C1)C#CC2=CC=C(C=C2)S(=O)(=O)NC(CC#CC3=CC=CC=C3)C(=O)O",
        expected_matches=Counter(
            {"Ar-C#C-Ar": 1, "Ar-C#C": 1, "RCOOH": 1, "benzene": 3}
        ),
        description="Both Ar-C#C-Ar and Ar-C#C-R in one structure.",
    ),
    # TODO Fix multiple Cl-CR2-CR2-Cl matching in endrin fragment (SELF-MATCHING).
    # TODO Count number of expected bond types.
    SubstructMatchTest(
        id=199,
        SMILES="CCOC(=O)CCC(=O)CC1(C2(C3(C4(C1(C5(C2(C3(C(C45Cl)(Cl)Cl)Cl)Cl)Cl)Cl)Cl)Cl)Cl)O",
        expected_matches=Counter({}),
        description="",
    ),
    # TODO Fix multiple Cl-CR2-CR2-Cl matching in endrin fragment (SELF-MATCHING).
    # TODO Count number of expected bond types.
    SubstructMatchTest(
        id=200,
        SMILES="C1C2C3C4C1C5(C2C6(C3(C(C4(C56Cl)Cl)(Cl)Cl)Cl)Cl)O",
        expected_matches=Counter({}),
        description="Identifying the number of bond types is too difficult due to the complexity of the structure.",
    ),
    SubstructMatchTest(
        id=201,
        SMILES="C1=CC=C(C=C1)C(C2=CC=CC=C2)(C(C3=CC=CC=C3)(C4=CC=CC=C4)Cl)Cl",
        expected_matches=Counter({"C-Cl": 2, "benzene": 4}),
        description="Cl-CR2-CR2-Cl is not matching if R -> Ar.",
    ),
    SubstructMatchTest(
        id=202,
        SMILES="C1C=CC2(C1C3(C(=C(C2(C3(Cl)Cl)Cl)Cl)Cl)Cl)Cl",
        expected_matches=Counter(
            {"C-Cl": 3, "cyclohexene": 1, "Cl-CR2-CR2-Cl": 1, "R2CCl2": 1, "C=C": 1}
        ),
        description="Double C=C bond prevents self-matching of Cl–CR2–CR2–Cl.",
    ),
    # TODO Cl-CR2-CR2-Cl and R2CCl2 should overlap over one C-R bond (for C-C bond const. is 0.0 cm3 mol-1)
    SubstructMatchTest(
        id=203,
        SMILES="C1(=C(C2(C3(C(C1(C2(Cl)Cl)Cl)(C(=C(C3(Cl)Cl)Cl)Cl)Cl)Cl)Cl)Cl)Cl",
        expected_matches=Counter(
            {"cyclohexene": 1, "C=C": 1, "R2CCl2": 2, "Cl-CR2-CR2-Cl": 2, "C-Cl": 4}
        ),
        description="Cl-CR2-CR2-Cl and R2CCl2 overlap allowed via C-R bond, since constitutive corr for C-C equals 0.0 cm3 mol-1.",
    ),
    # TODO Ring and Cl-CR2-CR2-Cl allowed only via 2 bonds. Fix!
    SubstructMatchTest(
        id=204,
        SMILES="C12C3C(C4C1C5(C(C3(C4(C5(Cl)Cl)Cl)Cl)Cl)Cl)C6C2O6",
        expected_matches=Counter(
            {
                "cyclopentane": 2,
                "cyclohexane": 2,
                "C-Cl": 4,
                "R2CCl2": 1,
            }
        ),
        description="Photodieldrin: a complex case involving saturated rings, R2CCl2 and Cl-CR2-CR2-Cl (correct result!).",
    ),
    # TODO resolve overlap
    SubstructMatchTest(
        id=205,
        SMILES="C1C2C=CC1(C3(C2C4(CC3(C(=C4Cl)Cl)Cl)Cl)Cl)Cl",
        expected_matches=Counter({"C-Cl": 6, "cyclohexene": 2}),
    ),
    SubstructMatchTest(
        id=206,
        SMILES="C1C2=CC=CC=C2C3(C1(CC4=CC(=C(C=C43)F)F)Cl)Cl",
        expected_matches=Counter({"C-Cl": 2, "benzene": 2}),
        description="When one C in Cl-CR2-CR2-Cl forms C-Ar bond instead of C-R this bond type is not matched.",
    ),
    # TODO Should not matched through more than 2 bonds with common rings! Resolve overlap
    SubstructMatchTest(
        id=207,
        SMILES="C1C(C2(C1(C(=O)C(=C(C2=O)Cl)Cl)Cl)Cl)(C3=CC=C(C=C3)F)C4=CC=C(C=C4)F",
        expected_matches=Counter(
            {"cyclobutane": 1, "cyclohexene": 1, "C-Cl": 4, "C=O": 2, "benzene": 2}
        ),
    ),
    SubstructMatchTest(
        id=208,
        SMILES="C1CC(C1(C#N)Cl)(C#N)Cl",
        expected_matches=Counter({"C-Cl": 2, "cyclobutane": 1, "-C#N": 2}),
        description="Cl-CR2-CR2-Cl is not matched when one of R = C#N. Additionally, this bond types overlay with cyclobutane via 3 C-C bonds.",
    ),
    SubstructMatchTest(
        id=209,
        SMILES="C1C2C=CC1C3(C2(C(=O)C(=C(Cl)Cl)C3=O)Cl)Cl",
        expected_matches=Counter(
            {"C-Cl": 4, "cyclohexene": 1, "cyclopentane": 1, "C=O": 2, "C=C": 1}
        ),
        description="Cl-CR2-CR2-Cl is not matched when one of R = C=O. Additionally, this bond types overlay with two fused rings via 3 C-C bonds.",
    ),
    SubstructMatchTest(
        id=210,
        SMILES="CC1=C(C(C1(C)Cl)(C)Cl)C",
        expected_matches=Counter({"Cl-CR2-CR2-Cl": 1, "C=C": 1}),
        description="Cl-CR2-CR2-Cl matching allowed for uncommon rings.",
    ),
    # TODO Fix overlay of Cl-CR2-CR2-Cl with cyclohexane.
    SubstructMatchTest(
        id=211,
        SMILES="CC1(C2(CC(C1(C3CC3(Cl)Cl)Cl)(C(C2)(Cl)Cl)Cl)Cl)C",
        expected_matches=Counter(
            {"C-Cl": 3, "cyclopropane": 1, "R2CCl2": 2, "cyclohexane": 1}
        ),
        description="Cl-CR2-CR2-Cl is not matched due to overlay of C-C bonds with cyclohexane ring within bicyclic structure.",
    ),
    # TODO Confirm number of bond types after fixes.
    SubstructMatchTest(
        id=212,
        SMILES="C1C2C3C4C1C5C2C6(C3(C4(C5(C6(Cl)Cl)Cl)Cl)Cl)Cl",
        expected_matches=Counter({}),
        description="Structure too complicated to analyse bond types.",
    ),
    # TODO After fix Cl-CR2-CR2-Cl should not match because 3 C-C bonds (max 2 C-C) overlay with one cyclobutane ring.
    SubstructMatchTest(
        id=213,
        SMILES="C12(C3(C4(C1(C5(C2(C3(C45Cl)F)F)Cl)F)F)F)F",
        expected_matches=Counter({"cyclobutane": 6, "C-Cl": 2}),
        description="RDKit fails to draw 3D cubane structure.",
    ),
    SubstructMatchTest(
        id=214,
        SMILES="C1=CC=C2C(=C1)C3=CC=CC=C3C2(C4(C5=CC=CC=C5C6=CC=CC=C64)Cl)Cl",
        expected_matches=Counter({"C-Cl": 2, "Ar-Ar": 2, "benzene": 4}),
        description="Ar-Ar matched correctly as part of saturated ring. C-Cl is not matching since some R = Ar.",
    ),
    SubstructMatchTest(
        id=215,
        SMILES="C1(=C(C(C2(C1(C(C(=C2Cl)Cl)(Cl)Cl)Cl)Cl)(Cl)Cl)Cl)Cl",
        expected_matches=Counter(
            {"C-Cl": 4, "Cl-CR2-CR2-Cl": 1, "R2CCl2": 2, "C=C": 2}
        ),
        description="Cl-CR2-CR2-Cl matched because cyclopentene is an uncommon ring. Cl-CR2-CR2-Cl and R2CCl2 are allowed to match via one C-C bond.",
    ),
    SubstructMatchTest(
        id=216,
        SMILES="CC1=C(C2=C(C(=C1Cl)O)C(=O)C(C(C2=O)(C)Cl)(C)Cl)O",
        expected_matches=Counter(
            {"C-Cl": 2, "Ar-C(=O)R": 2, "Ar-Cl": 1, "Ar-OH": 2, "benzene": 1}
        ),
        description="Cl-CR2-CR2-Cl is not matched because some R = C=O",
    ),
    # TODO Fix ring/Cl-CR2-CR2-Cl overlap
    SubstructMatchTest(
        id=217,
        SMILES="C1C2(C1(C3(CC3(C4(C2=CC=CC4Cl)Cl)Cl)Cl)Cl)Cl",
        expected_matches=Counter(
            {
                "C-Cl": 4,
                "Cl-CR2-CR2-Cl": 1,
                "C=C-C=C": 1,
                "cyclopropane": 2,
                "cyclohexane": 1,
            }
        ),
        description="Corner case: For code simplicity, Cl-CR2-CR2-Cl  was assumed to match when 2 C-C bonds overlap with a one ring.",
    ),
    SubstructMatchTest(
        id=218,
        SMILES="CC1(C=CC=CC1(C)Cl)Cl",
        expected_matches=Counter({"Cl-CR2-CR2-Cl": 1, "C=C-C=C": 1}),
        description="Cl-CR2-CR2-Cl assignement for ucommon ring.",
    ),
    # TODO Fix overlaping cyclohexane and Cl-CR2-CR2-Cl bond types
    SubstructMatchTest(
        id=219,
        SMILES="C1CC2(CC1=C3C2(C(C(C3(Cl)Cl)(Cl)Cl)(Cl)Cl)Cl)Cl",
        expected_matches=Counter(
            {"R2CCl2": 3, "C-Cl": 2, "cyclopentane": 1, "cyclohexane": 1}
        ),
        description="R2CCl2 are allowed to overlap with rings via 2 C-C bonds and with each other via 1 C-C bond.",
    ),
    SubstructMatchTest(
        id=220,
        SMILES="C=C1C(=C(C(C(C1(Cl)Cl)(C(=O)O)Cl)(C(=O)O)Cl)Cl)Cl",
        expected_matches=Counter(
            {"C-Cl": 4, "R2CCl2": 1, "RCOOH": 2, "cyclohexene": 1, "C=C": 1}
        ),
        description="Cl-CR2-CR2-Cl is not matched since some R = C(=O)OH. C(=O)NH2 and C(=O)OR are also excluded.",
    ),
    SubstructMatchTest(
        id=221,
        SMILES="C1CC/2C(C(C(C(C3(/C(=C2/C=C1)/C4(CC4(C5(C3(C5)Cl)Cl)Cl)Cl)Cl)(Cl)Cl)(Cl)Cl)(Cl)Cl)Cl",
        expected_matches=Counter(
            {
                "Cl-CR2-CR2-Cl": 2,
                "R2CCl2": 3,
                "C-Cl": 2,
                "C=C": 1,
                "cyclohexene": 1,
                "cyclohexane": 1,
                "cyclopropane": 2,
            }
        ),
        description="Cl-CR2-CR2-Cl can overlay via 2 C-C bonds with the same ring.",
    ),
    SubstructMatchTest(
        id=222,
        SMILES="C1CCCC(CC1)(C2(CCCCCC2)Cl)Cl",
        expected_matches=Counter({"Cl-CR2-CR2-Cl": 1}),
        description="Cl-CR2-CR2-Cl matching when both R in CR2 fragment belong to the same ring.",
    ),
    # TODO FIX ring/Cl-CR2-CR2-Cl overlap
    SubstructMatchTest(
        id=223,
        SMILES="C1C(C2CC(C3(C2C1C4C3(C4(Cl)Cl)Cl)Cl)(Cl)Cl)C=O",
        expected_matches=Counter(
            {"C-Cl": 2, "R2CCl2": 2, "cyclopentane": 3, "cyclopropane": 1, "C=O": 1}
        ),
        description="Cl-CR2-CR2-Cl overlap via 3 C-C bond of one ring.",
    ),
    SubstructMatchTest(
        id=224,
        SMILES="C1CC1(C(CC2=C(C(=CC=C2)F)F)(CN3C=NC=C3C#N)Cl)Cl",
        expected_matches=Counter(
            {
                "imidazole": 1,
                "benzene": 1,
                "-C#N": 1,
                "Cl-CR2-CR2-Cl": 1,
                "cyclopropane": 1,
            }
        ),
        description="NOTE: Cl-CR2-CR2-Cl overlap with cyclopropane ring via 2 C-C bonds (2/3 of all C-C bonds in the ring). Allowed for code simplicity.",
    ),
    SubstructMatchTest(
        id=225,
        SMILES="C(C(C(F)(F)F)(C(F)(F)F)Cl)(C(F)(F)F)(C(F)(F)F)Cl",
        expected_matches=Counter({"Cl-CR2-CR2-Cl": 1}),
    ),
    SubstructMatchTest(
        id=226,
        SMILES="C1C[C@H]2C3=CC=CC=C3[C@@H]1C2(C4([C@@H]5CC[C@H]4C6=CC=CC=C56)Cl)Cl",
        expected_matches=Counter({"cyclopentane": 2, "benzene": 2, "Cl-CR2-CR2-Cl": 1}),
        description="Rare case where Cl-CR2-CR2-Cl is correctly assigned as bridge between two bicyclic structures.",
    ),
    SubstructMatchTest(
        id=227,
        SMILES="C12=C3C4=C5C6=C1C7=C8C9=C1C%10=C%11C(=C29)C3=C2C3=C4C4=C5C5=C9C6=C7C6=C7C8=C1C1=C8C%10=C%10C%11=C2C2=C3C3=C4C4=C5C5=C%11C%12=C(C6=C95)C7=C1C1=C%12C5=C%11C4=C3C3=C5C(=C81)C%10=C23",
        expected_matches=Counter({"benzene": 20}),
        description="RDKit fails when drawing fullerene structure. 15 pentagons are not assigned because they are treated as uncommon rings.",
    ),
    # TODO Cl-CR2-CR2-Cl must not match due to ring overlap
    SubstructMatchTest(
        id=230,
        SMILES="C12(C3(C4(C1(C5(C2(C3(C45Cl)Cl)Cl)Cl)Cl)Cl)Cl)Cl",
        expected_matches=Counter({"cyclobutane": 6, "C-Cl": 8}),
    ),
    SubstructMatchTest(
        id=231,
        SMILES="CC1=CC(=C(C=C1N)C)C(=C2C(=C(C(=NC)C(C2(C)Cl)(C)Cl)C)C)C3=CC=C(C=C3)N",
        expected_matches=Counter(
            {"cyclohexene": 1, "benzene": 2, "Ar-C=C": 1, "C=N": 1, "Cl-CR2-CR2-Cl": 1}
        ),
        description="Cl-CR2-CR2-Cl assumed to match when one of R = C=N.",
    ),
    # TODO Fix self-overlap
    SubstructMatchTest(
        id=232,
        SMILES="ClC(C)(C)C(C)(Cl)C(C)(Cl)C(C)(Cl)C(C)(Cl)C",
        expected_matches=Counter({"Cl-CR2-CR2-Cl": 2, "C-Cl": 2}),
        description="Checks matching of adjacent Cl-CR2-CR2-Cl. Self-overlap allowed only through one C-C bond.",
    ),
    SubstructMatchTest(
        id=233,
        SMILES="CC1(C2(C(C(C(C1(C2Cl)Cl)(C(Cl)Cl)Cl)Cl)Cl)Cl)C",
        expected_matches=Counter(
            {"Cl-CR2-CR2-Cl": 1, "C-Cl": 4, "RCHCl2": 1, "cyclobutane": 1}
        ),
        description="RCHCl2 test. Note that Cl-CR2-CR2-Cl was assigned due to seniority of cyclobutane in bicycle which cancels cyclohexane assignment.",
    ),
    SubstructMatchTest(
        id=234,
        SMILES="CCOC(C(Cl)Cl)OCC",
        expected_matches=Counter({"RCHCl2": 1}),
    ),
    SubstructMatchTest(
        id=235,
        SMILES="C(C(Cl)Cl)Cl",
        expected_matches=Counter({"C-Cl": 1, "RCHCl2": 1}),
        description="C-Cl and RCHCl2 matches doesn't overlap.",
    ),
    SubstructMatchTest(
        id=236,
        SMILES="CN(C1=CC=C(C=C1)O)C(=O)C(Cl)Cl",
        expected_matches=Counter(
            {
                "benzene": 1,
                "Ar-OH": 1,
                "RC(=O)NH2": 1,
                "C-Cl": 2,
            }
        ),
        description="RCHCl2 is not matched when R = C=O.",
    ),
    SubstructMatchTest(
        id=237,
        SMILES="C1=CC(=CC=C1C(Cl)Cl)Cl",
        expected_matches=Counter({"C-Cl": 2, "benzene": 1, "Ar-Cl": 1}),
        description="RCHCl2 is not matched when R = Ar.",
    ),
    SubstructMatchTest(
        id=238,
        SMILES="C(C(C(C(Cl)Cl)(C)Cl)(C)Cl)(Cl)Cl",
        expected_matches=Counter({"RCHCl2": 2, "Cl-CR2-CR2-Cl": 1}),
        description="RCHCl2 and Cl-CR2-CR2-Cl are allowed to overlap via one C-C bond.",
    ),
    SubstructMatchTest(
        id=239,
        SMILES="CN(C1=CC=C(C=C1)OC(=O)C2=CC=CO2)C(=O)C(Cl)Cl",
        expected_matches=Counter(
            {"furan": 1, "benzene": 1, "C-Cl": 2, "RC(=O)NH2": 1, "Ar-COOR": 1}
        ),
        description="RCHCl2 is not matched when R = C(=O)NH2, C(=O)OR or C(=O)OH. Ar-C(=O)OR is allowed to match if R = Ar.",
    ),
    SubstructMatchTest(
        id=240,
        SMILES="C(C(C(Cl)Cl)(Cl)Cl)Cl",
        expected_matches=Counter({"RCHCl2": 1, "C-Cl": 1, "R2CCl2": 1}),
        description="RCHCl2 and R2CCl2 matches allowed to overlap by one C-C bond.",
    ),
    SubstructMatchTest(
        id=241,
        SMILES="C(=O)C(=C(C(=O)O)Cl)C(Cl)Cl",
        expected_matches=Counter(
            {"C=O": 1, "C=C": 1, "C-Cl": 1, "RCHCl2": 1, "RCOOH": 1}
        ),
    ),
    SubstructMatchTest(
        id=242,
        SMILES="C1=CC=C(C=C1)CC(Cl)Cl",
        expected_matches=Counter({"benzene": 1, "RCHCl2": 1}),
    ),
    SubstructMatchTest(
        id=243,
        SMILES="C(C(=O)OC(=O)C(Cl)Cl)(Cl)Cl",
        expected_matches=Counter({"RCOOR": 2, "C-Cl": 4}),
        description="RC(=O)OC(=O)R is matched as two RCOOR.",
    ),
    SubstructMatchTest(
        id=244,
        SMILES="C(C(Cl)Cl)(Cl)Cl",
        expected_matches=Counter({"RCHCl2": 2}),
        description="Self-overlap via C-C allowed for RCHCl2 bond types.",
    ),
    SubstructMatchTest(
        id=245,
        SMILES="C(#N)C(Cl)Cl",
        expected_matches=Counter({"-C#N": 1, "C-Cl": 2}),
    ),
    SubstructMatchTest(
        id=246,
        SMILES="C(C(=O)Cl)(Cl)Cl",
        expected_matches=Counter({"C=O": 1, "C-Cl": 3}),
        description="Acyl chloride group treated as separate C=O and C-Cl bond types.",
    ),
    SubstructMatchTest(
        id=247,
        SMILES="CC1COC2=CC=CC=C2N1C(=O)C(Cl)Cl",
        expected_matches=Counter({"C-Cl": 2, "Ar-OR": 1, "RC(=O)NH2": 1, "benzene": 1}),
        description="",
    ),
    SubstructMatchTest(
        id=248,
        SMILES=" C(#N)Br",
        expected_matches=Counter({"C-Br": 1, "-C#N": 1}),
        description="",
    ),
    SubstructMatchTest(
        id=249,
        SMILES="CC1(CS(=O)(=O)CC1(C)Br)Br",
        expected_matches=Counter({"Br-CR2-CR2-Br": 1}),
        description="Br-CR2-CR2-Br is matched when ring is uncommon.",
    ),
    SubstructMatchTest(
        id=250,
        SMILES="C1=CC=C(C=C1)C2=C(C(C2(C3=CC=CC=C3)Br)(C4=CC=CC=C4)Br)C5=CC=CC=C5",
        expected_matches=Counter({"benzene": 4, "C-Br": 2, "Ar-C=C": 1}),
        description="Br-CR2-CR2-Br is not matched when one of R = Ar.",
    ),
    # TODO Fix ring/Br-CBr2-CBr2-Br overlap
    SubstructMatchTest(
        id=251,
        SMILES="C1CCC2(CCCCC2(C1)Br)Br",
        expected_matches=Counter({"C-Br": 2, "cyclohexane": 2}),
        description="Matching of Br-CR2-CR2-Br is not allowed if three its C-C bonds are found in common ring.",
    ),
    # TODO Fix ring/Br-CBr2-CBr2-Br overlap
    SubstructMatchTest(
        id=252,
        SMILES="C12(C3(C4(C1(C5(C2(C3(C45Br)Br)Br)Br)Br)Br)Br)Br",
        expected_matches=Counter({"cyclobutane": 6, "C-Br": 8}),
    ),
    SubstructMatchTest(
        id=253,
        SMILES="CC1(C=CC=CC1(C)Br)Br",
        expected_matches=Counter({"Br-CR2-CR2-Br": 1, "C=C-C=C": 1}),
    ),
    # TODO Fix self-overlap
    SubstructMatchTest(
        id=254,
        SMILES="C(C(C)(C(C)(C(C)(Br)C(C)(Br)C)Br)Br)(C)(Br)C",
        expected_matches=Counter({"Br-CR2-CR2-Br": 2, "C-Br": 1}),
        description="Br-CR2-CR2-Br chain - self-overlap case.",
    ),
    SubstructMatchTest(
        id=255,
        SMILES="CCC(C#N)(C(C)(C#N)Br)Br",
        expected_matches=Counter({"C-Br": 2, "-C#N": 2}),
        description="",
    ),
    # SubstructMatchTest(
    #     id=149,
    #     SMILES="",
    #     expected_matches=Counter({}),
    #     description="",
    # ),
    # SubstructMatchTest(
    #     id=149,
    #     SMILES="",
    #     expected_matches=Counter({}),
    #     description="",
    # ),
    # SubstructMatchTest(
    #     id=149,
    #     SMILES="",
    #     expected_matches=Counter({}),
    #     description="",
    # ),
    # SubstructMatchTest(
    #     id=149,
    #     SMILES="",
    #     expected_matches=Counter({}),
    #     description="",
    # ),
    # SubstructMatchTest(
    #     id=149,
    #     SMILES="",
    #     expected_matches=Counter({}),
    #     description="",
    # ),
]
