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
        expected_matches=Counter({"C#C": 1, "C-I": 1}),
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
                "C=O": 1,
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
        expected_matches=Counter({"C=O": 1, "cyclohexane": 1, "tetrahydrofuran": 1}),
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
    ),
    # TODO: rdkit error?
    SubstructMatchTest(
        id=27,
        SMILES="CCN(CC)C1=CC2=C(C=C1)C(=C3C=CC(=[N+](CC)CC)C=C3O2)C4=CC=CC=C4C(=O)O",
        expected_matches=Counter({"Ar-NR2": 1, "Ar-Ar": 1, "Ar-COOH": 1, "benzene": 3}),
        description="Corner case of Ar-Ar matching.",
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
            {"C=C-C=C": 1, "RCOOH": 2, "RC(=O)NH2": 1, "C=N": 1, "thiazole": 1}
        ),
        description="Thiazole derivative example.",
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
        SMILES="CC1=C(C(CCC1)(C)C)C=CC(=CC=CC(=CC(=O)O)C)C",
        expected_matches=Counter({"C=C-C=C": 2, "RCOOH": 1, "cyclohexene": 1}),
        description="Examine C=C-C=C self-matching.",
    ),
    SubstructMatchTest(
        id=32,
        SMILES="CC1=C(C(CC(C1=O)O)(C)C)C=CC(=CC=CC(=CC=CC=C(C)C=CC=C(C)C=CC2=C(C(=O)C(CC2(C)C)O)C)C)C",
        expected_matches=Counter({"C=C-C=C": 4, "C=C": 1, "C=O": 2, "cyclohexene": 2}),
        description="Examine C=C-C=C self-matching.",
    ),
    SubstructMatchTest(
        id=33,
        SMILES="C=CC1=C(N2C(C(C2=O)NC(=O)C(=NOCC(=O)O)C3=CSC(=N3)N)SC1)C(=O)O",
        expected_matches=Counter(
            {"C=C-C=C": 1, "RCOOH": 2, "RC(=O)NH2": 1, "C=N": 1, "thiazole": 1}
        ),
        description="Thiazole derivative example.",
    ),
    SubstructMatchTest(
        id=34,
        SMILES="C=CCCCC(=C)C/C=C/C(C)=C/C=C/C(C)=C/C=C/C=C(C)/C=C/C=C(C)/C=C/C=C(C)/CC/C=C(C)\C",
        expected_matches=Counter({"C=C-C=C": 5, "C=C": 2, "CH2=CH-CH2-": 1}),
        description="Example encompassing C=C-C=C, C=C and CH2=CH-CH2- bond types.",
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
        expected_matches=Counter({"RCHCl2": 1, "RCOOH": 1}),
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
        expected_matches=Counter({"cyclopentane:": 1, "cyclopropane": 1}),
        description="Corner case of bicyclo[3.1.0]hexane. To solve: cyclopropane must not share 3 atom indicies with cyclohexene ring.",
    ),
    SubstructMatchTest(
        id=53,
        SMILES="CC(C)(C)OC(=O)NC12CC(C1)(C2)C(=O)O",
        expected_matches=Counter({"cyclobutane": 1, "RCOOH": 1}),
        description="Bicyclo[1.1.1]pentane containing fused cyclobutane rings.",
    ),
    SubstructMatchTest(
        id=54,
        SMILES="CC(C)(C)OC(=O)NC12CCC(C1)(C2)C(=O)O",
        expected_matches=Counter({"cyclobutane": 1, "RCOOH": 1}),
        description="Bicyclo[2.1.1]hexane containing fused cyclobutane and cyclopentane rings.",
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
        expected_matches=Counter({"RCOOH": 1, "cyclohexene": 1, "piperidine": 1}),
        description="Cyclohexene containing bicyclo fragment bonded to piperidine ring.",
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
        expected_matches=Counter({"RCOOH": 1, "cyclopropane": 1, "pyrrolidine": 1}),
        description="Corner case of azabicyclo[3.1.0]hexene with fused piperidine, pyrrolidine and cyclopropane.",
    ),
    SubstructMatchTest(
        id=61,
        SMILES="C1C2C1(C(=O)NC2=O)C3=CC=CC=C3",
        expected_matches=Counter({"benzene": 1, "cyclopropane": 1}),
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
        expected_matches=Counter({"cyclohexene": 1}),
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
]
