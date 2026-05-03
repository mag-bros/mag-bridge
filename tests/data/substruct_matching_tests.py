from collections import Counter
from dataclasses import dataclass, field
from typing import Counter, Optional


# TODO Literature search needed to confirm that all Ar-(functional group) corrections take into account the functional group corrections!
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
        description="When counting bond types C=C and C-Cl, the same C atom for both bond types is considered.",
    ),
    SubstructMatchTest(
        id=2,
        SMILES="C=CCC=C",
        expected_matches=Counter({"CH2=CH-CH2-": 1, "C=C": 1}),
        description="All carbon atoms of allyl group cannot belong to other bond type.",
    ),
    SubstructMatchTest(
        id=3,
        SMILES="CC(=CC=CC=C(C)C=CC=C(C)C(=O)OC1C(C(C(C(O1)COC2C(C(C(C(O2)CO)O)O)O)O)O)O)C=CC=C(C)C(=O)OC3C(C(C(C(O3)COC4C(C(C(C(O4)CO)O)O)O)O)O)O",
        expected_matches=Counter({"C=C-C=C": 3, "C=C": 1, "RCOOR": 2}),
        description="The C=C-C=C and C=C bond types cannot share one or more atoms.",
    ),
    SubstructMatchTest(
        id=4,
        SMILES="CC(=C)C1CC2=C(O1)C=CC3=C2OC4COC5=CC(=C(C=C5C4C3=O)OC)OC",
        expected_matches=Counter({"Ar-OR": 5, "benzene": 2, "C=C": 1, "Ar-C(=O)R": 1}),
        description="Saturated rings fused with aromatic rings are not assigned.",
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
                "Ar-OR": 1,
            }
        ),
        description="Ar-O-Ar fragment is allowed to match as Ar-OR bond type.",
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
        description="Test for saturated policyclic ring system.",
    ),
    SubstructMatchTest(
        id=7,
        SMILES="C1=CN(C(=O)N=C1N)C2C(C(C(O2)CO)O)O",
        expected_matches=Counter({"tetrahydrofuran": 1, "Ar-NR2": 1}),
        description="Pyrimidine ring is not matched as one of its carbons forms external C=O group, resulting in pyrimidinone ring.",
    ),
    SubstructMatchTest(
        id=8,
        SMILES="CCCCNC(=O)OCC#CI",
        expected_matches=Counter({"C#C": 1, "C-I": 1, "RC(=O)NH2": 1}),
        description="Carbamate ROC(=O)NHR fragment is assumed to be assigned using RCOONHR bond type as a rough approximation.",
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
                Note that for fused ring systems each ring is matched separately which is a rough approximation.""",
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
        expected_matches=Counter({"C=N": 1, "Ar-NR2": 2, "Ar-C=C": 1, "benzene": 2, "C=C": 2}),
        description="""
            Highlights the complexity of C=C-C=C, C=C and Ar-C=C matching. For the molecule, Ar-C=C cannot be matched twice!
            Note that C=C-C=C as well as C=C are not matched because of the presence of Ar-C=C bond type!
            The C=N bond is considered applicable to cases involving a positively charged [N+] atom.""",
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
        expected_matches=Counter({"RC(=O)NH2": 1, "Ar-OR": 4, "Ar-Ar": 1, "benzene": 1}),
        description="Test case for the assignment of the aromatic 7-membered tropone ring. See (DOI): https://doi.org/10.1021/acs.orglett.0c02343",
    ),
    SubstructMatchTest(
        id=14,
        SMILES="CC1=CC(=C(C(=C1C=CC(=CC=CC(=CC(=O)[O-])C)C)C)C)OC",
        expected_matches=Counter({"C=C-C=C": 1, "C=C": 1, "Ar-C=C": 1, "Ar-OR": 1, "benzene": 1, "RCOOH": 1}),
        description="""
            Check if Ar-C=C, C=C-C=C and C=C bond types are not matched with each other (self-matching). 
            Deprotonated RCOO- group is assumed to be assigned as RCOOH bond type.""",
    ),
    SubstructMatchTest(
        id=15,
        SMILES="COC1=C(C=CC(=C1)CC=C)[O-]",
        expected_matches=Counter({"CH2=CH-CH2-": 1, "Ar-OH": 1, "Ar-OR": 1, "benzene": 1}),
        description="Phenolate Ar-O(-) fragment is allowed to be assigned as Ar-OH bond type.",
    ),
    SubstructMatchTest(
        id=16,
        SMILES="C=CCN=C=S",
        expected_matches=Counter({"CH2=CH-CH2-": 1}),
        description="Isothiocyanate S=C=N group is not matched, i.e., assignment of C=N bond within S=C=N fragment is excluded.",
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
        expected_matches=Counter({"CH2=CH-CH2-": 1, "RC(=O)NH2": 3}),
        description="""
            Tricky amide group matching in a barbiturate ring.
            We assumed that two RCONHR bond types cannot share the same C=O bond, but they are allowed to share the same N atom.""",
    ),
    SubstructMatchTest(
        id=19,
        SMILES="CC1=C(C(=O)C=CO1)O",
        expected_matches=Counter({"pyrones": 1, "Ar-OH": 1}),
        description="Test for gamma-pyrone ring matching.",
    ),
    SubstructMatchTest(
        id=20,
        SMILES="CC(=O)CC(C1=CC=CC=C1)C2=C(C3=CC=CC=C3OC2=O)O",
        expected_matches=Counter({"C=O": 1, "Ar-OH": 1, "benzene": 2, "pyrones": 1}),
        description="Interesting case of alpha-pyrone being matched as part of fused aromatic ring system.",
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
            Highlights the possibility of matching of RCOOR within tetrahydrofuran ring. RCOOR is matched, while tetrahydrofuran ring is ignored. 
            Also, the C=O in thioester RC(=O)SR groups is allowed to be assigned.""",
    ),
    SubstructMatchTest(
        id=22,
        SMILES="CC(C)(C)C(=O)C(N1C=NC=N1)OC2=CC=C(C=C2)Cl",
        expected_matches=Counter({"C=O": 1, "Ar-OR": 1, "Ar-Cl": 1, "benzene": 1}),
        description="Shows that not all aromatic rings are considered in the query due to limited literature data.",
    ),
    SubstructMatchTest(
        id=23,
        SMILES="CC1C(C(C(O1)OC2C(C(C(C(C2O)O)N=C(N)N)O)N=C(N)N)OC3C(C(C(C(O3)CO)O)O)NC)(C=O)O",
        expected_matches=Counter({"C=O": 1, "cyclohexane": 1, "tetrahydrofuran": 1, "C=N": 2}),
        description="Highlights that C=N is assumed to be assigned when being part of guanidine group.",
    ),
    SubstructMatchTest(
        id=24,
        SMILES="CC1CCC2=C3N1C=C(C(=O)C3=CC(=C2)F)C(=O)[O-]",
        expected_matches=Counter({"Ar-COOH": 1, "benzene": 1}),
        description="Highlights that pyridine ring is not matched when one of its C atoms is a part of external C=O group.",
    ),
    SubstructMatchTest(
        id=25,
        SMILES="CC1=C(C(CCC1)(C)C)C=CC(=CC=CC(=CC(=O)O)C)C",
        expected_matches=Counter({"C=C-C=C": 2, "RCOOH": 1, "cyclohexene": 1}),
        description="Examine C=C-C=C self-matching and cross-matching with cyclohexane ring.",
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
        description="Test for the matching of C=C-C=C, C=C and cyclohexene bond types.",
    ),
    SubstructMatchTest(
        id=29,
        SMILES="C=CC1=C(N2C(C(C2=O)NC(=O)C(=NOCC(=O)O)C3=CSC(=N3)N)SC1)C(=O)O",
        expected_matches=Counter({"C=C-C=C": 1, "RCOOH": 2, "RC(=O)NH2": 2, "C=N": 1, "thiazole": 1, "Ar-NR2": 1}),
        description="Thiazole derivative example. RCONR2 matching allowed within 4-membered ring - a rough approximation.",
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
        expected_matches=Counter({"-C#N": 1, "Ar-Ar": 1, "Ar-OR": 2, "benzene": 1, "pyrrole": 1}),
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
        expected_matches=Counter({}),
        description="Thiocyanite group - C#N bond matching excluded.",
    ),
    SubstructMatchTest(
        id=35,
        SMILES="CC1=C(C(=O)CC1OC(=O)C2C(C2(C)C)C=C(C)C)CC=C",
        expected_matches=Counter({"C=O": 1, "RCOOR": 1, "cyclopropane": 1, "CH2=CH-CH2-": 1, "C=C": 2}),
        description="Check for matching of neighbouring C=C and CH2=CH-CH2- bond types.",
    ),
    SubstructMatchTest(
        id=36,
        SMILES="CC1(C2CCC1(C(=O)C2)C)C",
        expected_matches=Counter({"C=O": 1, "cyclohexane": 1}),
        description="Ring matching within bicyclic fragment. Saturated ring is still matched if one of its C atoms forms external C=O bond.",
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
        description="Check for the matching of piperazine anion and Ar-COO- group - an assumption.",
    ),
    SubstructMatchTest(
        id=38,
        SMILES="C(C(=O)O)(Cl)Cl",
        expected_matches=Counter({"C-Cl": 2, "RCOOH": 1}),
        description="Relevant RCHCl2 bond type is not matched if R = COOH.",
    ),
    SubstructMatchTest(
        id=39,
        SMILES="COC(=O)C(CC1=CC=CC=C1)NC(=O)C(CC(=O)O)N",
        expected_matches=Counter({"RCOOH": 1, "RCOOR": 1, "RC(=O)NH2": 1, "benzene": 1}),
        description="Shows proper distinction between RCOOH, RCOOR and RC(=O)NH2 groups.",
    ),
    SubstructMatchTest(
        id=40,
        SMILES="CC1=CC2C(CCC2(C(CC1)[N+]#[C-])C)C(C)C",
        expected_matches=Counter({"C=C": 1, "-N#C": 1, "cyclopentane": 1}),
        description="Test for simple isonitrile molecule example.",
    ),
    SubstructMatchTest(
        id=41,
        SMILES="CC(C(C1=NN=C(O1)C2=CC=C(C=C2)F)NC3=C4C=CSC4=C(C=C3)[N+]#[C-])O",
        expected_matches=Counter({"-N#C": 1, "Ar-Ar": 1, "benzene": 2, "thiophene": 1, "Ar-NR2": 1}),
        description="Example with Ar-N#C and benzothiophene fragment.",
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
        description="Matching of saturated rings within complicated fused ring system.",
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
        description="Both -C#N and -N#C groups in one molecule.",
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
        description="Test for Ar-C=C and cyclohexene overlap.",
    ),
    SubstructMatchTest(
        id=48,
        SMILES="C1CN2CCN1CC2",
        expected_matches=Counter({"piperazine": 1}),
        description="Only one piperazine ring is matched within DABCO molecule.",
    ),
    SubstructMatchTest(
        id=49,
        SMILES="[C-]#[N+]C(=CC1=CC=C(C=C1)O)C(=CC2=CC=C(C=C2)O)[N+]#[C-]",
        expected_matches=Counter({"-N#C": 2, "Ar-OH": 2, "benzene": 2, "Ar-C=C": 2}),
        description="Matching of adjacent Ar-C=C and -N#C groups.",
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
        description="Test for adamantane - only one out of four unique cyclohexane rings is matched.",
    ),
    SubstructMatchTest(
        id=52,
        SMILES="C1CC2CC2C1",
        expected_matches=Counter({"cyclopentane": 1, "cyclopropane": 1}),
        description="Test for bicyclo[3.1.0]hexane. Cyclohexane ring is not matched.",
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
        expected_matches=Counter({"RCOOH": 1, "cyclohexene": 1, "piperidine": 1, "RC(=O)NH2": 1}),
        description="Cyclohexene matching within bicyclo fragment that is directly connected with piperidine ring.",
    ),
    SubstructMatchTest(
        id=58,
        SMILES="C1CCC2C(C1)CC2=O",
        expected_matches=Counter({"cyclobutane": 1, "cyclohexane": 1, "C=O": 1}),
        description="Fused cyclohexane and cyclobutanon rings. Cyclobutane bond type is assigned if one of C forms C=O bond - an assumption.",
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
        expected_matches=Counter({"RCOOH": 1, "cyclopropane": 1, "pyrrolidine": 1, "RC(=O)NH2": 1}),
        description="Test for the matching of piperidine, pyrrolidine and cyclopropane rings within bicycle. Piperidine matching excluded.",
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
        description="Check for piperidine matching within azabicyclo[2.2.2] fragment.",
    ),
    SubstructMatchTest(
        id=63,
        SMILES="C1CCN(CC1)C2(C3CN(CC2COC3)CC4=CC=CC=C4)C5=CC=CC=C5",
        expected_matches=Counter({"benzene": 2, "piperidine": 2}),
        description="Assignment of two piperidine rings - one terminal and one incorporated in bicyclic fragment.",
    ),
    SubstructMatchTest(
        id=64,
        SMILES="CN1C2CCC1C=C(C2)C3=C(C=CS3)Br",
        expected_matches=Counter({"Ar-Br": 1, "pyrrolidine": 1, "thiophene": 1, "Ar-C=C": 1}),
        description="Azabicyclo[3:2:1]octene derivative with additional thiophene ring.",
    ),
    SubstructMatchTest(
        id=65,
        SMILES="C1C2CN(CC1C2=O)CC3=CC=CC=C3",
        expected_matches=Counter({"cyclobutane": 1, "C=O": 1, "benzene": 1}),
        description="Interesting case - cyclobutane and piperidine fused into bicyclic structure.",
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
        description="bicyclo[1.1.0], with heteroatom",
    ),
    SubstructMatchTest(
        id=68,
        SMILES="C12OC1C2",
        expected_matches=Counter({"cyclopropane": 1}),
        description="bicyclo[1.1.0], with heteroatom",
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
        description="bicyclo[2.1.0], with N/O",
    ),
    SubstructMatchTest(
        id=71,
        SMILES="C12CCC1N2",
        expected_matches=Counter({"cyclobutane": 1}),
        description="bicyclo[2.1.0], with N/O",
    ),
    SubstructMatchTest(
        id=72,
        SMILES="C12COC1C2",
        expected_matches=Counter({"cyclopropane": 1}),
        description="bicyclo[2.1.0], with N/O",
    ),
    SubstructMatchTest(
        id=73,
        SMILES="C12CCC1O2",
        expected_matches=Counter({"cyclobutane": 1}),
        description="bicyclo[2.1.0], with N/O",
    ),
    SubstructMatchTest(
        id=74,
        SMILES="C12C=CC1C2",
        expected_matches=Counter({"cyclopropane": 1, "C=C": 1}),
        description="bicyclo[2.1.0], with C=C",
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
        description="bicyclo[3.1.0], with N/O",
    ),
    SubstructMatchTest(
        id=77,
        SMILES="C12CCCC1N2",
        expected_matches=Counter({"cyclopentane": 1}),
        description="bicyclo[3.1.0], with N/O",
    ),
    SubstructMatchTest(
        id=78,
        SMILES="C12COCC1C2",
        expected_matches=Counter({"tetrahydrofuran": 1, "cyclopropane": 1}),
        description="bicyclo[3.1.0], with N/O",
    ),
    SubstructMatchTest(
        id=79,
        SMILES="C12CCCC1O2",
        expected_matches=Counter({"cyclopentane": 1}),
        description="bicyclo[3.1.0], with N/O",
    ),
    SubstructMatchTest(
        id=80,
        SMILES="C12CNCC1O2",
        expected_matches=Counter({"pyrrolidine": 1}),
        description="bicyclo[3.1.0], with N/O",
    ),
    SubstructMatchTest(
        id=81,
        SMILES="C12COCC1N2",
        expected_matches=Counter({"tetrahydrofuran": 1}),
        description="bicyclo[3.1.0], with N/O",
    ),
    SubstructMatchTest(
        id=82,
        SMILES="C12COCC1O2",
        expected_matches=Counter({"tetrahydrofuran": 1}),
        description="bicyclo[3.1.0], with N/O",
    ),
    SubstructMatchTest(
        id=83,
        SMILES="C12CNCC1N2",
        expected_matches=Counter({"pyrrolidine": 1}),
        description="bicyclo[3.1.0], with N/O",
    ),
    SubstructMatchTest(
        id=84,
        SMILES="C12CC=CC1C2",
        expected_matches=Counter({"cyclopropane": 1, "C=C": 1}),
        description="bicyclo[3.1.0], with C=C and C/N",
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
        description="bicyclo[1.1.1], with N/O",
    ),
    SubstructMatchTest(
        id=87,
        SMILES="C12OC(C1)C2",
        expected_matches=Counter({"cyclobutane": 1}),
        description="bicyclo[1.1.1], with N/O",
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
        description="bicyclo[2.2.0], carbocycle, with N/O",
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
        description="bicyclo[2.2.0], carbocycle, with N/O",
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
        description="bicyclo[2.2.0], with C=C",
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
        description="bicyclo[2.1.1], with N/O",
    ),
    SubstructMatchTest(
        id=97,
        SMILES="C12CCC(C1)N2",
        expected_matches=Counter({"pyrrolidine": 1}),
        description="bicyclo[2.1.1], with N/O",
    ),
    SubstructMatchTest(
        id=98,
        SMILES="C12COC(C1)C2",
        expected_matches=Counter({"cyclobutane": 1}),
        description="bicyclo[2.1.1], with N/O",
    ),
    SubstructMatchTest(
        id=99,
        SMILES="C12CCC(C1)O2",
        expected_matches=Counter({"tetrahydrofuran": 1}),
        description="bicyclo[2.1.1], with N/O",
    ),
    SubstructMatchTest(
        id=100,
        SMILES="C12C=CC(C1)C2",
        expected_matches=Counter({"cyclobutane": 1, "C=C": 1}),
        description="bicyclo[2.1.1], with C=C",
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
        description="bicyclo[2.2.1], with N/O",
    ),
    SubstructMatchTest(
        id=103,
        SMILES="C1CC2CCC1N2",
        expected_matches=Counter({"cyclohexane": 1}),
        description="bicyclo[2.2.1], with N/O",
    ),
    SubstructMatchTest(
        id=104,
        SMILES="C1CC2COC1C2",
        expected_matches=Counter({"tetrahydrofuran": 1}),
        description="bicyclo[2.2.1], with N/O",
    ),
    SubstructMatchTest(
        id=105,
        SMILES="C1CC2CCC1O2",
        expected_matches=Counter({"cyclohexane": 1}),
        description="bicyclo[2.2.1], with N/O",
    ),
    SubstructMatchTest(
        id=106,
        SMILES="C1NC2CNC1C2",
        expected_matches=Counter({"piperazine": 1}),
        description="bicyclo[2.2.1], with N/O",
    ),
    SubstructMatchTest(
        id=107,
        SMILES="C1OC2COC1C2",
        expected_matches=Counter({"dioxane": 1}),
        description="bicyclo[2.2.1], with N/O",
    ),
    SubstructMatchTest(
        id=108,
        SMILES="C1OC2CNC1C2",
        expected_matches=Counter({"morpholine": 1}),
        description="bicyclo[2.2.1], with N/O",
    ),
    SubstructMatchTest(
        id=109,
        SMILES="C1CC2CNC1N2",
        expected_matches=Counter({"piperidine": 1}),
        description="bicyclo[2.2.1], with N/O",
    ),
    SubstructMatchTest(
        id=110,
        SMILES="C1CC2COC1O2",
        expected_matches=Counter({"tetrahydrofuran": 1}),
        description="bicyclo[2.2.1], with N/O",
    ),
    SubstructMatchTest(
        id=111,
        SMILES="C1CC2COC1N2",
        expected_matches=Counter({"pyrrolidine": 1}),
        description="bicyclo[2.2.1], with N/O",
    ),
    SubstructMatchTest(
        id=112,
        SMILES="C1CC2CNC1O2",
        expected_matches=Counter({"piperidine": 1}),
        description="bicyclo[2.2.1], with N/O",
    ),
    SubstructMatchTest(
        id=113,
        SMILES="C1CC2C=CC1C2",
        expected_matches=Counter({"cyclohexene": 1}),
        description="bicyclo[2.2.1], with C=C and N/O",
    ),
    SubstructMatchTest(id=114, SMILES="C1CC2C=CC1N2", expected_matches=Counter({"cyclohexene": 1}), description="bicyclo[2.2.1], with C=C and N/O"),
    SubstructMatchTest(id=115, SMILES="C1CC2C=CC1O2", expected_matches=Counter({"cyclohexene": 1}), description="bicyclo[2.2.1], with C=C and N/O"),
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
        description="bicyclo[2.2.2], with N/O",
    ),
    SubstructMatchTest(id=118, SMILES="C1CC2COC1CC2", expected_matches=Counter({"cyclohexane": 1}), description="bicyclo[2.2.2], with N/O"),
    SubstructMatchTest(id=119, SMILES="N1CC2CNC1CC2", expected_matches=Counter({"piperidine": 1}), description="bicyclo[2.2.2], with N/O"),
    SubstructMatchTest(id=120, SMILES="C1NC2COC1CC2", expected_matches=Counter({"morpholine": 1}), description="bicyclo[2.2.2], with N/O"),
    SubstructMatchTest(id=121, SMILES="C1NC2CNC1CC2", expected_matches=Counter({"piperazine": 1}), description="bicyclo[2.2.2], with N/O"),
    SubstructMatchTest(id=122, SMILES="C1OC2COC1OC2", expected_matches=Counter({"dioxane": 1}), description="bicyclo[2.2.2], with N/O"),
    SubstructMatchTest(id=123, SMILES="C1NC2CNC1NC2", expected_matches=Counter({"piperazine": 1}), description="bicyclo[2.2.2], with N/O"),
    SubstructMatchTest(id=124, SMILES="C1OC2CNC1NC2", expected_matches=Counter({"morpholine": 1}), description="bicyclo[2.2.2], with N/O"),
    SubstructMatchTest(id=125, SMILES="C1OC2COC1NC2", expected_matches=Counter({"morpholine": 1}), description="bicyclo[2.2.2], with N/O"),
    SubstructMatchTest(
        id=126,
        SMILES="C1CC2C=CC1CC2",
        expected_matches=Counter({"cyclohexene": 1}),
        description="bicyclo[2.2.2], with C=C and N/O",
    ),
    SubstructMatchTest(
        id=127,
        SMILES="C1CC2C=CC1C=C2",
        expected_matches=Counter({"cyclohexene": 1, "C=C": 1}),
        description="bicyclo[2.2.2], with C=C and N/O",
    ),
    SubstructMatchTest(
        id=128,
        SMILES="C1CC2C=CC1CN2",
        expected_matches=Counter({"cyclohexene": 1}),
        description="bicyclo[2.2.2], with C=C and N/O",
    ),
    SubstructMatchTest(
        id=129,
        SMILES="C1CC2C=CC1CO2",
        expected_matches=Counter({"cyclohexene": 1}),
        description="bicyclo[2.2.2], with C=C and N/O",
    ),
    SubstructMatchTest(
        id=130,
        SMILES="N1CC2C=CC1CO2",
        expected_matches=Counter({"morpholine": 1, "C=C": 1}),
        description="bicyclo[2.2.2], with C=C and N/O",
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
        expected_matches=Counter({"-C#N": 1, "Ar-NO2": 1, "RCOOR": 2, "benzene": 1, "C=C": 2}),
        description="C=C bond is matched when connected to N atom.",
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
        description="The case of C(=O)N-C(=S)NR-Ar fragment - a rough approximation for amide group matching.",
    ),
    SubstructMatchTest(
        id=135,
        SMILES="C1=CC=C2C(=C1)N=C(S2)SCSC#N",
        expected_matches=Counter({"benzene": 1, "thiazole": 1}),
        description="-C#N bond matching rejected if found within thiocyanate -S-C#N group.",
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
        expected_matches=Counter({"cyclohexane": 1, "RCOOR": 1}),
        description="thiocyanate group and bicyclic fragment.",
    ),
    SubstructMatchTest(
        id=138,
        SMILES="CC1=CC(=CC(=C1NC2=NC(=NC=C2)NC3=CC=C(C=C3)C#N)C)C=CC#N",
        expected_matches=Counter({"-C#N": 2, "benzene": 2, "pyrimidine": 1, "Ar-C=C": 1, "Ar-NR2": 2}),
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
        description="Confirmation that N=O bond within isoxazole is not matched. Matching of Ar-C(=O)NHR, and RCONR2 within saturated ring.",
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
    SubstructMatchTest(
        id=148,
        SMILES="C1CSCCN1NC(=O)N(CCCl)N=O",
        expected_matches=Counter({"RC(=O)NH2": 1, "N=O": 1, "C-Cl": 1}),
        description="Molecule with NC(=O)N fragment. Thiomorpholine ring has no associated constitutive correction.",
    ),
    # TODO resolve COOH self-overlap
    SubstructMatchTest(
        id=149,
        SMILES="C(=O)(O)[O-]",
        expected_matches=Counter({"C=O": 1}),
        description="COOH assignement for HCO3- allowed.",
    ),
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
        SMILES="C1(=CC=CC=C1)[N+](C2=CC=CC=C2)(C3=CC=CC=C3)C4=CC=CC=C4",
        expected_matches=Counter({"benzene": 4}),
        description="[N+]Ar4 Test - assignment of Ar-NR2 group rejected due to significantly different electronic structure.",
    ),
    SubstructMatchTest(
        id=154,
        SMILES="C1=CC=C2C(=C1)C(=O)OC(=O)N2",
        expected_matches=Counter({"benzene": 1}),
        description="In aromatic system Ar-C(=O)NH2 and AR-COOR are not matched - expected result.",
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
        description="Nitrous oxide resonance form - a rough approximation.",
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
        description="Test for N=O matching for Ar-N=O fragment.",
    ),
    SubstructMatchTest(
        id=160,
        SMILES="CC(=O)OC/N=[N+](/C)\\[O-]",
        expected_matches=Counter({"RCOOR": 1, "N=N": 1}),
        description="Molecule with N=[N+]-[O-] group - assignment of N=N bond is allowed.",
    ),
    SubstructMatchTest(
        id=161,
        SMILES="CN(C(=O)N)N=O",
        expected_matches=Counter({"N=O": 1, "RC(=O)NH2": 1}),
        description="Matching of RC(=O)NH2 and N=O bond types within H2N-C(=O)N-N=O fragment.",
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
        description="Tetranitromethane - interesting -NO2 groups assignment.",
    ),
    SubstructMatchTest(
        id=164,
        SMILES="CC/C(=C\\C(=N\\O)\\C(=O)N)/C(C)[N+](=O)[O-]",
        expected_matches=Counter({"-NO2": 1, "C=N": 1, "C=C": 1, "RC(=O)NH2": 1}),
        description="Interesting resonance structure involving matching of C=C, C=N and amide bond types - an approximation.",
    ),
    SubstructMatchTest(
        id=165,
        SMILES="CN/C(=C\\[N+](=O)[O-])/NCCSCC1=CC=C(O1)C[N+](C)(C)[O-]",
        expected_matches=Counter({"-NO2": 1, "furan": 1, "C=C": 1}),
        description="R2[N+]-[O-] fragment is not matched as N=O - expected result.",
    ),
    SubstructMatchTest(
        id=166,
        SMILES="CN=C(NCC1CCOC1)N[N+](=O)[O-]",
        expected_matches=Counter({"tetrahydrofuran": 1, "-NO2": 1, "C=N": 1}),
        description="""
            The N=O assignment in the guanidine N–C(=N)–N fragment is allowed, but it is a rough approximation due to electron delocalization.
            -NO2 assignment allowed when N-N bond exists.""",
    ),
    SubstructMatchTest(
        id=167,
        SMILES="CCN(CC)CCOC1=CC=C(C=C1)C(=C(C2=CC=CC=C2)Cl)C3=CC=CC=C3",
        expected_matches=Counter({"Ar-OR": 1, "benzene": 3, "C-Cl": 1, "Ar-C=C": 1}),
        description="For Ar-C(-Ar)=C-Ar fragment the bond type Ar-C=C is matched only once - expected result.",
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
        description="-NO2 matching for Ar-ONO2 fragments.",
    ),
    SubstructMatchTest(
        id=171,
        SMILES="C1=CC(=CC=C1C(C2=CC=C(C=C2)Cl)C(Cl)(Cl)Cl)Cl",
        expected_matches=Counter({"Ar-Cl": 2, "C-Cl": 3, "benzene": 2}),
        description="Test for Ar-Cl and C-Cl distinction.",
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
        expected_matches=Counter({"cyclohexane": 1, "cyclohexene": 1, "R2CCl2": 1, "C-Cl": 4}),
        description="Two bicyclic fragments fused via C-C edge - test for ring matching, as well as C-Cl and R2CCl2 bond types.",
    ),
    SubstructMatchTest(
        id=174,
        SMILES="C(=O)(Cl)Cl",
        expected_matches=Counter({"C-Cl": 2, "C=O": 1}),
        description="Both C-Cl and C=O assigned as part of Cl2C=O - and approximation.",
    ),
    SubstructMatchTest(
        id=175,
        SMILES="N(=O)Cl",
        expected_matches=Counter({"N=O": 1}),
        description="Nitroso N atom bound to halogen - N=O bond assignment allowed.",
    ),
    SubstructMatchTest(
        id=176,
        SMILES="CC1=[N+](ON=C1[N+](=O)[O-])[O-]",
        expected_matches=Counter({"Ar-NO2"}),
        description="NO2 fragment not assigned when being part of aromatic ring - expected result.",
    ),
    SubstructMatchTest(
        id=177,
        SMILES="CC1=CN(C(=O)NC1=O)[C@H]2C[C@@H]([C@H](O2)CO)N=[N+]=[N-]",
        expected_matches=Counter({"tetrahydrofuran": 1, "N=N": 2}),
        description="R-N=[N+]=[N-] is matched as two N=N bond types.",
    ),
    SubstructMatchTest(
        id=178,
        SMILES="CCN(C)C1=CC=C(C=C1)N=NC2=CC=CC=C2",
        expected_matches=Counter({"N=N": 1, "benzene": 2, "Ar-NR2": 1}),
        description="Test for N=N assignment within Ar-N=N-Ar fragment.",
    ),
    SubstructMatchTest(
        id=179,
        SMILES="C(=O)(N)/N=N/C(=O)N",
        expected_matches=Counter({"N=N": 1, "RC(=O)NH2": 2}),
        description="N=N bond is assigned if it is connected to amide C(=O)NH2 group. ",
    ),
    SubstructMatchTest(
        id=180,
        SMILES="CN1C(=O)N2C=NC(=C2N=N1)C(=O)N",
        expected_matches=Counter({"imidazole": 1, "Ar-C(=O)NH2": 1}),
        description="N=N in aromatic ring is not assigned - expected result.",
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
        description="Matching N=N bond within N=N-NH or N(=N)NH2 fragment allowed.",
    ),
    SubstructMatchTest(
        id=183,
        SMILES="C=[N+]=[N-]",
        expected_matches=Counter({"C=N": 1, "N=N": 1}),
        description="[N-]=[N+]=C molecule is matched as N=N and C=N which is a rough approximation.",
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
        description="Check for N=N matching withing aromatic ring (not allowed).",
    ),
    SubstructMatchTest(
        id=187,
        SMILES="C([C@@H](C(=O)O)N)/[N+](=N/O)/[O-]",
        expected_matches=Counter({"N=N": 1, "RCOOH": 1}),
        description="N=N bond is allowed to be assigned within HO-N=[N+]-[O-] fragment.",
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
        description="Assignment of N=N bond is allowed when one of N is conneted to -SO3(-) group.",
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
        expected_matches=Counter({"N=N": 2, "benzene": 1}),
        description="Ar-COOR is NOT allowed to be matched when R = I or any atom.",
    ),
    SubstructMatchTest(
        id=192,
        SMILES="CC1=NC(=CC=C1)C#CC2=CC(=CC=C2)OC",
        expected_matches=Counter({"Ar-C#C-Ar": 1, "benzene": 1, "pyridine": 1, "Ar-OR": 1}),
        description="Test for assingment of Ar-C#C-Ar bond type.",
    ),
    SubstructMatchTest(
        id=193,
        SMILES="CN(C)C1=CC=C(C=C1)C2=C(N=CN=C2N)C#CC3=CN=C(C=C3)N4CCOCC4",
        expected_matches=Counter({"morpholine": 1, "Ar-Ar": 1, "Ar-C#C-Ar": 1, "Ar-NR2": 3, "benzene": 1, "pyridine": 1, "pyrimidine": 1}),
        description="Test for assignemnt for two Ar-NR2 - one terminal and one as part of the ring.",
    ),
    SubstructMatchTest(
        id=194,
        SMILES="CC1=NC(=CS1)C#CC2=CN=CC(=C2)C=C",
        expected_matches=Counter({"Ar-C#C-Ar": 1, "pyridine": 1, "Ar-C=C": 1, "thiazole": 1}),
        description="Test for thiazole ring.",
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
        description="Test for different aromatic rings linkages: Ar-Ar, Ar-C#C-Ar and Ar-C=C(Ar)-Ar.",
    ),
    SubstructMatchTest(
        id=197,
        SMILES="C1=CC=C(C=C1)C#CC2=C3C=CC=CC3=C(C4=CC=CC=C42)C#CC5=CC=CC=C5",
        expected_matches=Counter({"Ar-C#C-Ar": 2, "benzene": 5}),
        description="Anthracene fragment is matched as three separate benzene rings - a rough approximation.",
    ),
    SubstructMatchTest(
        id=198,
        SMILES="CC1=CC=C(C=C1)C#CC2=CC=C(C=C2)S(=O)(=O)NC(CC#CC3=CC=CC=C3)C(=O)O",
        expected_matches=Counter({"Ar-C#C-Ar": 1, "Ar-C#C": 1, "RCOOH": 1, "benzene": 3}),
        description="Both Ar-C#C-Ar and Ar-C#C-R in one structure.",
    ),
    SubstructMatchTest(
        id=199,
        SMILES="CCOC(=O)CCC(=O)CC1(C2(C3(C4(C1(C5(C2(C3(C(C45Cl)(Cl)Cl)Cl)Cl)Cl)Cl)Cl)Cl)Cl)O",
        expected_matches=Counter(
            {
                "C-Cl": 8,
                "C=O": 1,
                "R2CCl2": 1,
                "cyclobutane": 2,
                "cyclopentane": 2,
                "RCOOR": 1,
            }
        ),
        description="Check for assignment within complicated fused (saturated) ring system with terminal chlorine atoms.",
    ),
    SubstructMatchTest(
        id=200,
        SMILES="C1C2C3C4C1C5(C2C6(C3(C(C4(C56Cl)Cl)(Cl)Cl)Cl)Cl)O",
        expected_matches=Counter({"C-Cl": 4, "R2CCl2": 1, "cyclobutane": 1, "cyclohexane": 2}),
        description="Cl-CR2-CR2-Cl matching is excluded due to cross-overlap with rings via more than two C-C bonds.",
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
        expected_matches=Counter({"C-Cl": 5, "cyclohexene": 1, "R2CCl2": 1, "C=C": 1}),
        description="Cl–CR2–CR2–Cl is not assigned because it is overlapped with a ring via three C-C bonds.",
    ),
    SubstructMatchTest(
        id=203,
        SMILES="C1(=C(C2(C3(C(C1(C2(Cl)Cl)Cl)(C(=C(C3(Cl)Cl)Cl)Cl)Cl)Cl)Cl)Cl)Cl",
        expected_matches=Counter({"cyclohexene": 1, "C=C": 1, "R2CCl2": 2, "C-Cl": 8}),
        description="Cl-CR2-CR2-Cl is not matched because it is overlapped with rings via three C-C bonds.",
    ),
    SubstructMatchTest(
        id=204,
        SMILES="C12C3C(C4C1C5(C(C3(C4(C5(Cl)Cl)Cl)Cl)Cl)Cl)C6C2O6",
        expected_matches=Counter(
            {
                "cyclopentane": 1,
                "cyclohexane": 2,
                "C-Cl": 2,
                "R2CCl2": 1,
                "Cl-CR2-CR2-Cl": 1,
            }
        ),
        description="Photodieldrin: a complex case involving saturated rings, R2CCl2 and Cl-CR2-CR2-Cl (correct result!).",
    ),
    SubstructMatchTest(
        id=205,
        SMILES="C1C2C=CC1(C3(C2C4(CC3(C(=C4Cl)Cl)Cl)Cl)Cl)Cl",
        expected_matches=Counter({"C-Cl": 6, "cyclohexene": 2}),
        description="A case of two adjacent bicyclic fragments with no Cl-CR2-CR2-Cl matching - expected result.",
    ),
    SubstructMatchTest(
        id=206,
        SMILES="C1C2=CC=CC=C2C3(C1(CC4=CC(=C(C=C43)F)F)Cl)Cl",
        expected_matches=Counter({"C-Cl": 2, "benzene": 2}),
        description="Assignment of Cl-CR2-CR2-Cl is excluded if one of the R groups is replaced by Ar.",
    ),
    SubstructMatchTest(
        id=207,
        SMILES="C1C(C2(C1(C(=O)C(=C(C2=O)Cl)Cl)Cl)Cl)(C3=CC=C(C=C3)F)C4=CC=C(C=C4)F",
        expected_matches=Counter({"cyclobutane": 1, "cyclohexene": 1, "C-Cl": 4, "C=O": 2, "benzene": 2}),
        description="""
            Cyclohexene ring can still be assigned when one or more of its C atoms forms external C=O bond.
            Matching of Cl-CR2-CR2-Cl bond type is excluded due to overlap with a cyclobutane ring via three C-C bonds.""",
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
        expected_matches=Counter({"C-Cl": 4, "cyclohexene": 1, "cyclopentane": 1, "C=O": 2, "C=C": 1}),
        description="Cl-CR2-CR2-Cl is not matched when one of R = C=O. Additionally, this bond type overlay with two fused rings via 3 C-C bonds.",
    ),
    SubstructMatchTest(
        id=210,
        SMILES="CC1=C(C(C1(C)Cl)(C)Cl)C",
        expected_matches=Counter({"Cl-CR2-CR2-Cl": 1, "C=C": 1}),
        description="""
            Cl-CR2-CR2-Cl matching allowed for uncommon rings.
            Note that in this case Cl-CR2-CR2-Cl is a part of cyclobutene ring which is a rough approximation due to ring strain.""",
    ),
    SubstructMatchTest(
        id=211,
        SMILES="CC1(C2(CC(C1(C3CC3(Cl)Cl)Cl)(C(C2)(Cl)Cl)Cl)Cl)C",
        expected_matches=Counter(
            {
                "C-Cl": 3,
                "cyclopropane": 1,
                "R2CCl2": 2,
                "cyclohexane": 1,
            }
        ),
        description="""
            Cl-CR2-CR2-Cl share three C-C bonds with cyclohexane ring within bicyclic structure, which excludes its assignment.
            R2CCl2 is allowed to be assigned as part of cyclopropane ring - a rough approximation due to ring strain.""",
    ),
    SubstructMatchTest(
        id=212,
        SMILES="C1C2C3C4C1C5C2C6(C3(C4(C5(C6(Cl)Cl)Cl)Cl)Cl)Cl",
        expected_matches=Counter({"C-Cl": 4, "R2CCl2": 1, "cyclobutane": 1, "cyclohexane": 2}),
        description="Test for complicated fused ring system - correct result!",
    ),
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
        description="Ar-Ar matched correctly as part of a ring. C-Cl is not assigned since some R = Ar.",
    ),
    SubstructMatchTest(
        id=215,
        SMILES="C1(=C(C(C2(C1(C(C(=C2Cl)Cl)(Cl)Cl)Cl)Cl)(Cl)Cl)Cl)Cl",
        expected_matches=Counter({"C-Cl": 4, "Cl-CR2-CR2-Cl": 1, "R2CCl2": 2, "C=C": 2}),
        description="Cl-CR2-CR2-Cl matched because cyclopentene is an uncommon ring. Cl-CR2-CR2-Cl and R2CCl2 are allowed to match via one C-C bond.",
    ),
    SubstructMatchTest(
        id=216,
        SMILES="CC1=C(C2=C(C(=C1Cl)O)C(=O)C(C(C2=O)(C)Cl)(C)Cl)O",
        expected_matches=Counter({"C-Cl": 2, "Ar-C(=O)R": 2, "Ar-Cl": 1, "Ar-OH": 2, "benzene": 1}),
        description="Cl-CR2-CR2-Cl is not matched because some R = C=O",
    ),
    SubstructMatchTest(
        id=217,
        SMILES="C1C2(C1(C3(CC3(C4(C2=CC=CC4Cl)Cl)Cl)Cl)Cl)Cl",
        expected_matches=Counter(
            {
                "C-Cl": 6,
                "C=C-C=C": 1,
                "cyclopropane": 2,
                "cyclohexane": 1,
            }
        ),
        description="Corner case: For code simplicity, Cl-CR2-CR2-Cl was assumed to match when two but not three C-C bonds overlap with a one ring.",
    ),
    SubstructMatchTest(
        id=218,
        SMILES="CC1(C=CC=CC1(C)Cl)Cl",
        expected_matches=Counter({"Cl-CR2-CR2-Cl": 1, "C=C-C=C": 1}),
        description="Cl-CR2-CR2-Cl assignement for uncommon ring.",
    ),
    SubstructMatchTest(
        id=219,
        SMILES="C1CC2(CC1=C3C2(C(C(C3(Cl)Cl)(Cl)Cl)(Cl)Cl)Cl)Cl",
        expected_matches=Counter({"R2CCl2": 3, "C-Cl": 2, "cyclopentane": 1, "cyclohexene": 1}),
        description="R2CCl2 are allowed to overlap with rings via two C-C bonds and with each other via one C-C bond.",
    ),
    SubstructMatchTest(
        id=220,
        SMILES="C=C1C(=C(C(C(C1(Cl)Cl)(C(=O)O)Cl)(C(=O)O)Cl)Cl)Cl",
        expected_matches=Counter({"C-Cl": 4, "R2CCl2": 1, "RCOOH": 2, "cyclohexene": 1, "C=C": 1}),
        description="Cl-CR2-CR2-Cl is not matched since some R = C(=O)OH. This also holds for R = C(=O)NH2 or C(=O)OR.",
    ),
    SubstructMatchTest(
        id=221,
        SMILES="C1CC/2C(C(C(C(C3(/C(=C2/C=C1)/C4(CC4(C5(C3(C5)Cl)Cl)Cl)Cl)Cl)(Cl)Cl)(Cl)Cl)(Cl)Cl)Cl",
        expected_matches=Counter(
            {
                "R2CCl2": 3,
                "C-Cl": 6,
                "C=C": 1,
                "cyclohexene": 1,
                "cyclohexane": 1,
                "cyclopropane": 2,
            }
        ),
        description="Cl-CR2-CR2-Cl cannot overlay via three C-C bonds with the same ring. In such case, two C-Cl bonds are assigned instead.",
    ),
    SubstructMatchTest(
        id=222,
        SMILES="C1CCCC(CC1)(C2(CCCCCC2)Cl)Cl",
        expected_matches=Counter({"Cl-CR2-CR2-Cl": 1}),
        description="Cl-CR2-CR2-Cl is matched when both R in CR2 fragment belong to the same ring.",
    ),
    SubstructMatchTest(
        id=223,
        SMILES="C1C(C2CC(C3(C2C1C4C3(C4(Cl)Cl)Cl)Cl)(Cl)Cl)C=O",
        expected_matches=Counter({"C-Cl": 2, "R2CCl2": 2, "cyclopentane": 3, "cyclopropane": 1, "C=O": 1}),
        description="Cl-CR2-CR2-Cl overlap via three C-C bond of one ring - assignment rejected.",
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
        description="Cl-CR2-CR2-Cl can overlap with cyclopropane ring via 2 C-C bonds (2/3 of all C-C bonds in the ring). Allowed for code simplicity.",
    ),
    SubstructMatchTest(
        id=225,
        SMILES="C(C(C(F)(F)F)(C(F)(F)F)Cl)(C(F)(F)F)(C(F)(F)F)Cl",
        expected_matches=Counter({"Cl-CR2-CR2-Cl": 1}),
        description="Assignment of Cl-CR2-CR2-Cl allowed if R = CF3.",
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
        description="RDKit fails to draw fullerene structure. 15 pentagons are not assigned because they are treated as uncommon rings.",
    ),
    SubstructMatchTest(
        id=228,
        SMILES="CCOC1=CC2=C(C=C1)NC(C=C2C)(C)C",
        expected_matches=Counter({"benzene": 1, "Ar-OR": 1, "Ar-C=C": 1, "Ar-NR2": 1}),
        description="Test for Ar-NR2 assignment within the uncommon ring.",
    ),
    SubstructMatchTest(
        id=229,
        SMILES="C1CN(CC=C1N2C3=CC=CC=C3NC2=O)CCCC(=O)C4=CC=C(C=C4)F",
        expected_matches=Counter({"benzene": 2, "C=C": 1, "Ar-C(=O)R": 1}),
        description="Corner case of 2-imidazolidone ring for which matching of imidazole ring was forbidden.",
    ),
    SubstructMatchTest(
        id=230,
        SMILES="C12(C3(C4(C1(C5(C2(C3(C45Cl)Cl)Cl)Cl)Cl)Cl)Cl)Cl",
        expected_matches=Counter({"cyclobutane": 6, "C-Cl": 8}),
        description="RDKit fails to draw 3D cubane structure. Matching of Cl-CR2-CR2-Cl excluded due to cross-overlap with cyclobutane rings.",
    ),
    SubstructMatchTest(
        id=231,
        SMILES="CC1=CC(=C(C=C1N)C)C(=C2C(=C(C(=NC)C(C2(C)Cl)(C)Cl)C)C)C3=CC=C(C=C3)N",
        expected_matches=Counter({"cyclohexene": 1, "benzene": 2, "Ar-C=C": 1, "C=N": 1, "C-Cl": 2, "Ar-NR2": 2}),
        description="For Ar(Ar)-C=C-R fragment, Ar-C=C bond type is matched only once.",
    ),
    SubstructMatchTest(
        id=232,
        SMILES="ClC(C)(C)C(C)(Cl)C(C)(Cl)C(C)(Cl)C(C)(Cl)C",
        expected_matches=Counter({"Cl-CR2-CR2-Cl": 2, "C-Cl": 1}),
        description="Test for matching of adjacent Cl-CR2-CR2-Cl. Self-overlap allowed only via one C-C bond.",
    ),
    SubstructMatchTest(
        id=233,
        SMILES="CC1(C2(C(C(C(C1(C2Cl)Cl)(C(Cl)Cl)Cl)Cl)Cl)Cl)C",
        expected_matches=Counter({"Cl-CR2-CR2-Cl": 1, "C-Cl": 4, "RCHCl2": 1, "cyclobutane": 1}),
        description="RCHCl2 test. Note that Cl-CR2-CR2-Cl was assigned due to cyclobutane's seniority in bicycle which cancels cyclohexane assignment.",
    ),
    SubstructMatchTest(
        id=234,
        SMILES="CCOC(C(Cl)Cl)OCC",
        expected_matches=Counter({"RCHCl2": 1}),
        description="RCHCl2 is matched when R = C-O.",
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
        expected_matches=Counter({"furan": 1, "benzene": 1, "C-Cl": 2, "RC(=O)NH2": 1, "Ar-COOR": 1}),
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
        expected_matches=Counter({"C=O": 1, "C=C": 1, "C-Cl": 1, "RCHCl2": 1, "RCOOH": 1}),
        description="RCHCl2 is allowed to matched when R = C=C.",
    ),
    SubstructMatchTest(
        id=242,
        SMILES="C1=CC=C(C=C1)CC(Cl)Cl",
        expected_matches=Counter({"benzene": 1, "RCHCl2": 1}),
        description="Simple RCHCl2 test.",
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
        description="RCH2Cl2 is not matched when R = C#N and two C-Cl are assigned instead.",
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
        description="RCHCl2 is not matched when R = C(=O)NH2, C(=O)OR or C(=O)OH.",
    ),
    SubstructMatchTest(
        id=248,
        SMILES=" C(#N)Br",
        expected_matches=Counter({"C-Br": 1, "-C#N": 1}),
        description="For C(#N)Br matching of both C-Br and -C#N bonds is allowed.",
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
    SubstructMatchTest(
        id=251,
        SMILES="C1CCC2(CCCCC2(C1)Br)Br",
        expected_matches=Counter({"C-Br": 2, "cyclohexane": 2}),
        description="Matching of Br-CR2-CR2-Br is not allowed if three its C-C bonds are found in common ring.",
    ),
    SubstructMatchTest(
        id=252,
        SMILES="C12(C3(C4(C1(C5(C2(C3(C45Br)Br)Br)Br)Br)Br)Br)Br",
        expected_matches=Counter({"cyclobutane": 6, "C-Br": 8}),
        description="RDKit fails to draw 3D cubane structure. Br-CR2-CR2-Br is not assigned due to cross-overlap with cyclobutane rings.",
    ),
    SubstructMatchTest(
        id=253,
        SMILES="CC1(C=CC=CC1(C)Br)Br",
        expected_matches=Counter({"Br-CR2-CR2-Br": 1, "C=C-C=C": 1}),
        description="Br-CR2-CR2-Br is allowed to match when R = C=C.",
    ),
    SubstructMatchTest(
        id=254,
        SMILES="C(C(C)(C(C)(C(C)(Br)C(C)(Br)C)Br)Br)(C)(Br)C",
        expected_matches=Counter({"Br-CR2-CR2-Br": 2, "C-Br": 1}),
        description="Test for Br-CR2-CR2-Br self-overlap.",
    ),
    SubstructMatchTest(
        id=255,
        SMILES="CCC(C#N)(C(C)(C#N)Br)Br",
        expected_matches=Counter({"C-Br": 2, "-C#N": 2}),
        description="Br-CR2-CR2-Br not allowed to match when any R = C#N",
    ),
    SubstructMatchTest(
        id=256,
        SMILES="CC(CBr)(C(C)(CBr)Br)Br",
        expected_matches=Counter({"Br-CR2-CR2-Br": 1, "C-Br": 2}),
        description="C-Br and Br-CR2-CR2-Br bond types cannot cross-overlap with each other.",
    ),
    SubstructMatchTest(
        id=257,
        SMILES="C1C2(C1(C3(C2(C3)C4=CC=CC=C4)Br)Br)C5=CC=CC=C5",
        expected_matches=Counter({"cyclopropane": 2, "cyclobutane": 1, "C-Br": 2, "benzene": 2}),
        description="Br-CR2-CR2-Br is not due to cross-overlap with common rings via three C-C bonds.",
    ),
    SubstructMatchTest(
        id=258,
        SMILES="CC1(C(=NC(=O)C2=CC=CC=C2)C(=C(C(=O)C1(C)Br)Br)Br)Br",
        expected_matches=Counter({"C=N": 1, "C=O": 1, "cyclohexene": 1, "benzene": 1, "C-Br": 4}),
        description="A corner case of Ar-(C=O)NH2 matching. Here, it is excluded due to the presence of N=C bond.",
    ),
    SubstructMatchTest(
        id=259,
        SMILES="C1(C(C(=C(C(=C1Br)Br)Br)Br)Br)OC2=C(C(=C(C(=C2Br)Br)Br)Br)Br",
        expected_matches=Counter({"Ar-Br": 5, "C-Br": 5, "Ar-OR": 1, "benzene": 1, "C=C-C=C": 1}),
        description="Test for Ar-Br and C-Br bond matching in one structure",
    ),
    SubstructMatchTest(
        id=260,
        SMILES="C1(=C(C(=C(C(=C1Br)Br)Br)Br)Br)OC2=C(C(=C(C(=C2Br)Br)Br)Br)Br",
        expected_matches=Counter({"Ar-Br": 10, "Ar-OR": 1, "benzene": 2}),
        description="Ar-O-Ar is assumed to matched as one Ar-OR bond types.",
    ),
    SubstructMatchTest(
        id=261,
        SMILES="CC1=C(C=CC(=C1)C(C(I)(I)I)(C(I)(I)I)I)NC(=O)C2=C(C(=CC=C2)I)C(=O)NC(C)(C)CS(=O)(=O)C",
        expected_matches=Counter({"Ar-I": 1, "C-I": 7, "Ar-C(=O)NH2": 2, "benzene": 2}),
        description="Test for Ar-I and C-I bonds matching in one molecule.",
    ),
    SubstructMatchTest(
        id=262,
        SMILES="C(C(=O)I)I",
        expected_matches=Counter({"C-I": 2, "C=O": 1}),
        description="C-I bond is matched if found in RC(=O)I fragment.",
    ),
    SubstructMatchTest(
        id=263,
        SMILES="C(#N)I",
        expected_matches=Counter({"C-I": 1, "-C#N": 1}),
        description="For C(#N)I molecule, both C-I and -C#N are allowed to match.",
    ),
    SubstructMatchTest(
        id=264,
        SMILES="C1=CC=C2C(=C1)C3=CC=CC=C3[I+]2",
        expected_matches=Counter({"Ar-Ar": 1, "benzene": 2}),
        description="Ar-I bond is allowed to match only if iodine forms one covalent bond. Ar-Ar is matched because the 5-membered ring is not aromatic.",
    ),
    SubstructMatchTest(
        id=265,
        SMILES="C1=CC=C(C=C1)C(=O)C2=CC=CC=C2",
        expected_matches=Counter({"benzene": 2, "Ar-C(=O)R": 1}),
        description="Ar-C(=O)R is allowed to be matched even if R = Ar, BUT ONLY ONCE!",
    ),
    SubstructMatchTest(
        id=266,
        SMILES="CC(=O)OI(C1=CC=CC=C1)OC(=O)C",
        expected_matches=Counter({"benzene": 1}),
        description="Ar-I bond is not assigned for hypervalent iodine. Also, RCOOR match omitted for R = I.",
    ),
    SubstructMatchTest(
        id=267,
        SMILES="CC(=O)OC1=C(C=C(C=C1I)I)C(=O)NC2=CC=C(C=C2)Cl",
        expected_matches=Counter({"benzene": 2, "Ar-I": 2, "Ar-Cl": 1, "RCOOR": 1, "Ar-C(=O)NH2": 1}),
        description="RCOOR' bond type is matched if R' = Ar.",
    ),
    SubstructMatchTest(
        id=268,
        SMILES="C1=CC=C(C(=C1)C(=O)O)I=O",
        expected_matches=Counter({"benzene": 1, "Ar-COOH": 1}),
        description="Ar-I bond is not assigned for hypervalent iodine.",
    ),
    SubstructMatchTest(
        id=269,
        SMILES="C1=CC=C(C=C1)C#CI",
        expected_matches=Counter({"benzene": 1, "C-I": 1, "Ar-C#C": 1}),
        description="Test for Ar-C#C and C-I assignemnt in Ar-C#C-I fragment.",
    ),
    SubstructMatchTest(
        id=270,
        SMILES="C1=CC=C(C(=C1)C(=O)NCC(=O)[O-])[131I]",
        expected_matches=Counter({"Ar-I": 1, "Ar-C(=O)NH2": 1, "RCOOH": 1, "benzene": 1}),
        description="Test for Ar-I bond assignment for isotope-labeled molecule.",
    ),
    SubstructMatchTest(
        id=271,
        SMILES="C1=CC=C(C=C1)[I+]C2=CC=CC=C2",
        expected_matches=Counter({"benzene": 2}),
        description="Ar-I assignment is excluded if iodine forms more than one covalent bond.",
    ),
    SubstructMatchTest(
        id=272,
        SMILES="C(=IF)I=N",
        expected_matches=Counter({}),
        description="Ar-I assignment is excluded if iodine forms more than one covalent bond.",
    ),
    SubstructMatchTest(
        id=273,
        SMILES="C1=C(C=C(C=C1C#N)F)C#CC2=CSC(=N2)I",
        expected_matches=Counter({"thiazole": 1, "Ar-C#C-Ar": 1, "Ar-I": 1, "-C#N": 1, "benzene": 1}),
        description="Test encompassing Ar-C#C-Ar and thiazole assignment.",
    ),
    SubstructMatchTest(
        id=274,
        SMILES="COC1=C(C=CC(=C1)CC=C)O",
        expected_matches=Counter({"Ar-OR": 1, "Ar-OH": 1, "CH2=CH-CH2-": 1, "benzene": 1}),
        description="Allylic group is assigned if connected to aromatic ring.",
    ),
    SubstructMatchTest(
        id=275,
        SMILES="CNCCCN1C2=CC=CC=C2CCC3=CC=CC=C31",
        expected_matches=Counter({"benzene": 2, "Ar-NR2": 1}),
        description="Ar-NR-Ar fragment is assigned as one Ar-NR2 bonds.",
    ),
    SubstructMatchTest(
        id=276,
        SMILES="C[C@@]12CCN([C@@H]1N(C3=C2C=C(C=C3)OC(=O)NC)C)C",
        expected_matches=Counter({"pyrrolidine": 1, "Ar-NR2": 1, "RC(=O)NH2": 1, "benzene": 1}),
        description="Ar-NR2 is assigned, because N-methylpyrrolidine ring is fused with benzene.",
    ),
    SubstructMatchTest(
        id=277,
        SMILES="C[N+]1=CC=C(C=C1)C2=CC=[N+](C=C2)C",
        expected_matches=Counter({"Ar-Ar": 1, "pyridine": 2}),
        description="Pyridine ring is matched for N-methylpyridine fragment with postively charged N atom.",
    ),
    SubstructMatchTest(
        id=278,
        SMILES="CN(C)C1=NC(=NC(=N1)N(C)C)N(C)C",
        expected_matches=Counter({"Ar-NR2": 3, "triazine": 1}),
        description="Test for triazine derivative.",
    ),
    SubstructMatchTest(
        id=279,
        SMILES="CN(C)CCN(CC1=CC=C(C=C1)OC)C2=CC=CC=N2",
        expected_matches=Counter(
            {
                "Ar-NR2": 1,
                "Ar-OR": 1,
                "pyridine": 1,
                "benzene": 1,
            }
        ),
        description="Ar-NR2 is expectedly not matched for R-NR2 fragment.",
    ),
    SubstructMatchTest(
        id=280,
        SMILES="CN(C)C1=CC=C(C=C1)N=O",
        expected_matches=Counter({"Ar-NR2": 1, "N=O": 1, "benzene": 1}),
        description="N=O bond matching is allowed for Ar-N=O fragment.",
    ),
    SubstructMatchTest(
        id=281,
        SMILES="C[C@@H]1CCN(CCN1C(=O)C2=C(C=CC(=C2)C)N3N=CC=N3)C4=NC5=C(O4)C=CC(=C5)Cl",
        expected_matches=Counter({"Ar-NR2": 1, "benzene": 2, "Ar-C(=O)NH2": 1, "Ar-Cl": 1}),
        description="Ar-NR2 is matched when -NR2 fragment belongs to uncommon ring.",
    ),
    SubstructMatchTest(
        id=282,
        SMILES="C1CN1C2=NC(=NC(=N2)N3CC3)N4CC4",
        expected_matches=Counter({"Ar-NR2": 3, "triazine": 1}),
        description="Ar-NR2 assignemnt for aziridine ring should be treated with caution due to stained ring structure.",
    ),
    SubstructMatchTest(
        id=283,
        SMILES="C1C[N+]2=CC=CC=C2C3=CC=CC=[N+]31",
        expected_matches=Counter({"Ar-Ar": 1, "pyridine": 2}),
        description="Ar-Ar assignment within ring is correct provided that the ring is not part of polyaromatic ring system.",
    ),
    SubstructMatchTest(
        id=284,
        SMILES="CC1(N=C(N=C(N1C2=CC=C(C=C2)Cl)N)N)C",
        expected_matches=Counter({"C=N": 2, "Ar-NR2": 1, "benzene": 1, "Ar-Cl": 1}),
        description="Conjugated C=N bond and Ar-NR2 matching for the same uncommon ring.",
    ),
    SubstructMatchTest(
        id=285,
        SMILES="CC1=CC2=C(C(=C1)O)C(=O)C3=C(C2=O)C=CC=C3O",
        expected_matches=Counter({"Ar-OH": 2, "Ar-C(=O)R": 2, "benzene": 2}),
        description="Ar-C(=O)R and C=C bond types are assigned because C=O is not part of the aromatic system.",
    ),
    SubstructMatchTest(
        id=286,
        SMILES="C1=CC=C2C(=O)C=CC(=O)C2=C1",
        expected_matches=Counter({"benzene": 1, "Ar-C(=O)R": 2, "C=C": 1}),
        description="Ar-C(=O)R and C=C bond types are assigned because they are not part of aromatic system.",
    ),
    SubstructMatchTest(
        id=287,
        SMILES="COC1=CC=C(C=C1)C2=CC(=O)C3=C(O2)C(=C(C(=C3OC)OC)OC)OC",
        expected_matches=Counter(
            {
                "Ar-OR": 5,
                "benzene": 2,
                "Ar-Ar": 1,
                "pyrones": 1,
            }
        ),
        description="Pyrrone is correctly treated as aromatic ring. This implies no Ar-C(=O)R assignment.",
    ),
    SubstructMatchTest(
        id=288,
        SMILES="CCC(=C)C(=O)C1=C(C(=C(C=C1)OCC(=O)O)Cl)Cl",
        expected_matches=Counter({"Ar-C(=O)R": 1, "C=C": 1, "Ar-OR": 1, "Ar-Cl": 2, "RCOOH": 1, "benzene": 1}),
        description="C=C and Ar-C(=O)R matching for β-unsaturated carbonyl C=C-C=O fragment.",
    ),
    SubstructMatchTest(
        id=289,
        SMILES="CCN1C=C(C(=O)C2=CC(=C(C=C21)N3CCNCC3)F)C(=O)O",
        expected_matches=Counter({"piperazine": 1, "Ar-COOH": 1, "Ar-NR2": 1, "benzene": 1}),
        description="Ar-C(=O)R not matched because it is found in oxoquinoline fragment. Piperazine and Ar-NR2 assignment is allowed to overlap via two C-N bonds.",
    ),
    SubstructMatchTest(
        id=290,
        SMILES="C1=CC=C(C=C1)C(C2=CC=CC=C2)C(=O)C3C(=O)C4=CC=CC=C4C3=O",
        expected_matches=Counter({"benzene": 3, "Ar-C(=O)R": 2, "C=O": 1}),
        description="Ar-C(=O)R and C=O matching in one molecule.",
    ),
    SubstructMatchTest(
        id=291,
        SMILES="C1=CC=C2C(=C1)C=CC(=O)C2=O",
        expected_matches=Counter({"benzene": 1, "Ar-C=C": 1, "Ar-C(=O)R": 1, "C=O": 1}),
        description="Aromaticity check for 1,2-naphthoquinone.",
    ),
    SubstructMatchTest(
        id=292,
        SMILES="CC(C)(C)C1=CC=C(C=C1)C(=O)CC(=O)C2=CC=C(C=C2)OC",
        expected_matches=Counter({"Ar-C(=O)R": 2, "benzene": 2, "Ar-OR": 1}),
        description="Ar-C(=O)R matching for acetylacetone derivative.",
    ),
    SubstructMatchTest(
        id=293,
        SMILES="C(=C=CC1=CC=CC=C1)C2=CC=CC=C2",
        expected_matches=Counter({"Ar-C=C": 2, "benzene": 2}),
        description="For Ar-C=C=C-Ar fragment, two Ar-C=C bonds are assigned.",
    ),
    SubstructMatchTest(
        id=294,
        SMILES="C1=CC=C2C(=C1)C(=O)C(=O)N2",
        expected_matches=Counter({"benzene": 1, "RC(=O)NH2": 1, "Ar-C(=O)R": 1}),
        description="Aromaticity check for indole-2,3-dione (isatin).",
    ),
    SubstructMatchTest(
        id=295,
        SMILES="C1=CC=C(C=C1)C(=O)OOC(=O)C2=CC=CC=C2",
        expected_matches=Counter({"Ar-COOR": 2, "benzene": 2}),
        description="Ar-C(=O)O-OC(=O)-Ar fragment is allowed to be assigned as two Ar-COOR bond types.",
    ),
    SubstructMatchTest(
        id=296,
        SMILES="C1=CC=C2C(=C1)C(=O)OC2=O",
        expected_matches=Counter({"Ar-COOR": 2, "benzene": 1}),
        description="Test for Ar-C(=O)R assignment for aromatic anhydride. Phthalic anhydride.",
    ),
    SubstructMatchTest(
        id=297,
        SMILES="C1=CC2=C(C=C1O)OC3=C2C(=O)OC4=C3C=CC(=C4)O",
        expected_matches=Counter({"pyrones": 1, "furan": 1, "benzene": 2, "Ar-OH": 2}),
        description="Furan and pyrone ring matching in polyaromatic ring system.",
    ),
    SubstructMatchTest(
        id=298,
        SMILES="C1=CC=C(C=C1)OC(=O)C2=CC=CC=C2O",
        expected_matches=Counter({"benzene": 2, "Ar-OH": 1, "Ar-COOR": 1}),
        description="Ar-COOR is matched for R = Ar.",
    ),
    SubstructMatchTest(
        id=299,
        SMILES="CCCC[Sn](CCCC)(CCCC)OC(=O)C1=CC=CC=C1",
        expected_matches=Counter({"benzene": 1}),
        description="Ar-COOR is not allowed to be matched if R = Sn.",
    ),
    SubstructMatchTest(
        id=300,
        SMILES="C1=CC=C(C=C1)C(=O)ON=C2C=CC(=NOC(=O)C3=CC=CC=C3)C=C2",
        expected_matches=Counter({"benzene": 2, "Ar-COOR": 2, "C=C": 2, "C=N": 2}),
        description="Ar-COOR matching is allowed for Ar-C(=O)O-N fragment.",
    ),
    SubstructMatchTest(
        id=301,
        SMILES="C1=CC=C2C(=C1)C(=O)OS2(=O)=O",
        expected_matches=Counter({"benzene": 1}),
        description="Ar-COOR matching NOT allowed for Ar-C(=O)-SO2 fragment.",
    ),
    SubstructMatchTest(
        id=302,
        SMILES="C(=C=C(C1=CC=CC=C1)C2=CC=CC=C2)C3=CC=CC=C3",
        expected_matches=Counter({"Ar-C=C": 2, "benzene": 3}),
        description="Ar-C=C=C(Ar)-Ar fragment is expectedly matched as two Ar-C=C bond types.",
    ),
    SubstructMatchTest(
        id=303,
        SMILES="C1=CC=C2C(=C1)C(=O)O[Hg]O2",
        expected_matches=Counter({"benzene": 1}),
        description="Ar-COOR matching NOT allowed for Ar-C(=O)-Hg fragment.",
    ),
    SubstructMatchTest(
        id=304,
        SMILES="CCOC(=O)C#CC1=CC=CC=C1",
        expected_matches=Counter({"benzene": 1, "Ar-C#C": 1, "RCOOR": 1}),
        description="Ar-C#C is matched if one of the carbons is connected to C=O group.",
    ),
    SubstructMatchTest(
        id=305,
        SMILES="C1=CC=C(C=C1)S(=O)(=O)NC2=CC=CC(=C2)C#C/C=C/C(=O)NO",
        expected_matches=Counter({"benzene": 2, "Ar-C#C": 1, "C=C": 1, "RC(=O)NH2": 1}),
        description="Ar-C#C is matched if one of the carbons is connected to C=C bond type.",
    ),
    SubstructMatchTest(
        id=306,
        SMILES="C(=C=C(C)C)C1=CC=CC=C1",
        expected_matches=Counter({"C=C": 1, "Ar-C=C": 1, "benzene": 1}),
        description="R-C=C=C-Ar fragment is expectedly matched as C=C and Ar-C=C bond types.",
    ),
    SubstructMatchTest(
        id=307,
        SMILES="C1=CC=C(C=C1)C#CC#CC2=CC=CC=C2",
        expected_matches=Counter({"benzene": 2, "Ar-C#C": 2}),
        description="Test for Ar-C#C matching for conjugated Ar-C#C-C#C-Ar bonds.",
    ),
    SubstructMatchTest(
        id=308,
        SMILES="CC1=NC2=C(N1CC3=C(C=C(C=C3)C(=O)C4=CN(C5=CC=CC(=C54)C#C)C(=O)N(C)C)F)C=CN=C2",
        expected_matches=Counter(
            {
                "pyridine": 1,
                "imidazole": 1,
                "pyrrole": 1,
                "benzene": 2,
                "Ar-C(=O)R": 1,
                "Ar-C#C": 1,
            }
        ),
        description="RC(=O)NH2 is not matched if bonded to aromatic ring via its N atom.",
    ),
    SubstructMatchTest(
        id=309,
        SMILES="C1=CC=C(C=C1)C#C[P+](C2=CC=CC=C2)(C3=CC=CC=C3)C4=CC=CC=C4",
        expected_matches=Counter({"benzene": 4, "Ar-C#C": 1}),
        description="Ar-C#C matching is allowed for Ar-C#C-[P+] fragment.",
    ),
    SubstructMatchTest(
        id=310,
        SMILES="C1=CC=C(C=C1)C#CC#N",
        expected_matches=Counter({"-C#N": 1, "Ar-C#C": 1, "benzene": 1}),
        description="Test for Ar-C#C and -C#N bond type matching for conjugated Ar-C#C-C#N bonds.",
    ),
    SubstructMatchTest(
        id=311,
        SMILES="CCOC(=O)C1=C2[C@@H]3CCN3C(=O)C4=C(N2C=N1)C=CC(=C4)C#C[Si](C)(C)C",
        expected_matches=Counter({"Ar-C#C": 1, "Ar-COOR": 1, "Ar-C(=O)NH2": 1, "benzene": 1, "imidazole": 1}),
        description="Ar-C(=O)NH2 assignment for azetidine ring should be treated with caution due to strain of 4-membered ring.",
    ),
    SubstructMatchTest(
        id=312,
        SMILES="C1CCC(CC1)C#CC2=CC=CC=N2",
        expected_matches=Counter({"pyridine": 1, "cyclohexane": 1, "Ar-C#C": 1}),
        description="Ar-C#C bond type is correctly matched between aromatic and saturated ring.",
    ),
    SubstructMatchTest(
        id=313,
        SMILES="C1CC1C2(C3=C(C=CC(=C3)Br)NC(=O)N2)C#CC4=CN=CN=C4",
        expected_matches=Counter(
            {
                "benzene": 1,
                "cyclopropane": 1,
                "RC(=O)NH2": 1,
                "Ar-C#C": 1,
                "Ar-Br": 1,
                "pyrimidine": 1,
            }
        ),
        description="For cyclic ureas, RNH-C(=O)-NHR group is matched as one amide group - a rough approximation.",
    ),
    SubstructMatchTest(
        id=314,
        SMILES="CC#CC1=CC=C(S1)C2=CC=C(S2)C=O",
        expected_matches=Counter({"Ar-Ar": 1, "Ar-CHO": 1, "Ar-C#C": 1, "thiophene": 2}),
        description="Example of molecule with Ar-CHO bond type.",
    ),
    SubstructMatchTest(
        id=315,
        SMILES="CC1=C(C(CCC1)(C)C)/C=C/C#CC2=CC=C(C=C2)C(=O)O",
        expected_matches=Counter({"Ar-COOH": 1, "benzene": 1, "Ar-C#C": 1, "C=C": 1, "cyclohexene": 1}),
        description="Check for conjugated bond system with Ar-C#C, C=C and cyclohexene.",
    ),
    SubstructMatchTest(
        id=316,
        SMILES="CC1([C@H]([C@H]1C(=O)O[C@H](C#N)C2=CC(=CC=C2)OC3=CC=CC=C3)C=C(Br)Br)C",
        expected_matches=Counter(
            {
                "cyclopropane": 1,
                "-C#N": 1,
                "Ar-OR": 1,
                "C-Br": 2,
                "C=C": 1,
                "RCOOR": 1,
                "benzene": 2,
            }
        ),
        description="Ar-O-Ar is matched as one Ar-OR fragments.",
    ),
    SubstructMatchTest(
        id=317,
        SMILES="CCOP(=S)(OCC)OC1=CC=C(C=C1)[N+](=O)[O-]",
        expected_matches=Counter({"benzene": 1, "Ar-NO2": 1}),
        description="Ar-OR bond type matching for Ar-O-P fragment was forbidden.",
    ),
    SubstructMatchTest(
        id=318,
        SMILES="C1=CC(=CC=C1OS(=O)(=O)C2=CC=C(C=C2)Cl)Cl",
        expected_matches=Counter({"Ar-Cl": 2, "benzene": 2}),
        description="Ar-OR is not assigned for Ar-O-S fragment.",
    ),
    SubstructMatchTest(
        id=319,
        SMILES="CC1=CC(=C(C=C1C2=CC(=C(C=C2C)OI)C(C)C)C(C)C)OI",
        expected_matches=Counter({"Ar-Ar": 1, "benzene": 2}),
        description="Ar-OR is not assigned for Ar-O-I fragment.",
    ),
    SubstructMatchTest(
        id=320,
        SMILES="C1=CC(=C(C=C1[N+](=O)[O-])[N+](=O)[O-])O/N=C/C2=CC(=C(C(=C2)Br)O)Br",
        expected_matches=Counter({"Ar-Br": 2, "Ar-NO2": 2, "Ar-OH": 1, "Ar-OR": 1, "C=N": 1, "benzene": 2}),
        description="Ar-OR allowed to matched for Ar-O-N fragment.",
    ),
    SubstructMatchTest(
        id=321,
        SMILES="C1=CC2=C(C(=C1)O[Al](OC3=CC=CC4=C3N=CC=C4)OC5=CC=CC6=C5N=CC=C6)N=CC=C2",
        expected_matches=Counter({"benzene": 3, "pyridine": 3}),
        description="Ar-OR is not assigned for Ar-O-Al fragment.",
    ),
    SubstructMatchTest(
        id=322,
        SMILES="CC(C)C1=CC(=CC(=C1)OO)C(C)C",
        expected_matches=Counter({"Ar-OR": 1, "benzene": 1}),
        description="Ar-OR matching allowed for Ar-O-O fragment.",
    ),
    SubstructMatchTest(
        id=323,
        SMILES="CC1=CC(=C(C(=C1/C=C/C(=C/C=C/C(=C/C(=O)O)/C)/C)C)C)OC",
        expected_matches=Counter({"Ar-OR": 1, "Ar-C=C": 1, "benzene": 1, "C=C-C=C": 1, "C=C": 1, "RCOOH": 1}),
        description="Test for conjugated bond system encompassing Ar-C=C, C=C-C=C and C=C bond types matching.",
    ),
    SubstructMatchTest(
        id=324,
        SMILES="CC1=C(C2=C(N1C(=O)C3=CC=C(C=C3)Cl)C=CC(=C2)OC)CC(=O)O",
        expected_matches=Counter({"benzene": 2, "pyrrole": 1, "RCOOH": 1, "Ar-OR": 1, "Ar-Cl": 1}),
        description="Corner case of Ar-C(=O)N fragment with N atom forming aromatic ring. Left without assignment.",
    ),
    SubstructMatchTest(
        id=325,
        SMILES="CN1CCC(=C2C3=CC=CC=C3CCN4C2=NC=C4C=O)CC1",
        expected_matches=Counter({"benzene": 1, "piperidine": 1, "imidazole": 1, "Ar-CHO": 1, "Ar-C=C": 1}),
        description="An exocyclic double bond was assumed not to cancel the saturated ring (piperidine) assignment.",
    ),
    SubstructMatchTest(
        id=326,
        SMILES="CC(C)C(=O)OC1=C(C=C(C=C1)C=O)OC",
        expected_matches=Counter({"Ar-CHO": 1, "Ar-OR": 1, "RCOOR": 1, "benzene": 1}),
        description="The fragment RCOOAr is allowed to match as RCOOR bond type.",
    ),
    SubstructMatchTest(
        id=327,
        SMILES="C1=C(SC(=C1)[N+](=O)[O-])C=O",
        expected_matches=Counter({"Ar-CHO": 1, "Ar-NO2": 1, "thiophene": 1}),
        description="A simple test for the Ar-NO2 and Ar-CHO bond types assignemnt.",
    ),
    SubstructMatchTest(
        id=328,
        SMILES="CC1=CC(=C(C2=C1C(=O)OC3=C(O2)C4=C(C(=C3C)O)C(=O)OC4O)C=O)OC",
        expected_matches=Counter(
            {
                "Ar-CHO": 1,
                "Ar-COOR": 2,
                "Ar-OH": 1,
                "Ar-OR": 2,
                "benzene": 2,
            }
        ),
        description="""
            The Ar–O–Ar fragment, in which the oxygen is a part of the ring, is assigned as one Ar–OR bond types. 
            The ArC(=O)OAr fragment is allowed to match as Ar-COOR bond type.""",
    ),
    SubstructMatchTest(
        id=329,
        SMILES="CN(C)OC1=C(N2C=CSC2=N1)C=O",
        expected_matches=Counter({"imidazole": 1, "thiazole": 1, "Ar-OR": 1, "Ar-CHO": 1}),
        description="If a heteroatom is shared by two fused rings, this atom is considered in the assignment of each ring. Ar-OR assignment allowed if R = N.",
    ),
    SubstructMatchTest(
        id=330,
        SMILES="C1=CC=C2C(=C1)C(=O)OC23C4=C(C=C(C=C4)O)OC5=C3C=CC(=C5)[O-]",
        expected_matches=Counter({"benzene": 3, "Ar-COOR": 1, "Ar-OH": 2, "Ar-OR": 1}),
        description="Test for assignment of both Ar-OH and Ar-O(-) fragments. For this molecule RDKit fails to draw one of the benzene rings.",
    ),
    SubstructMatchTest(
        id=331,
        SMILES="[N+](C1=CC=CC=C1)(C2=CC=CC=C2)(C3=CC=CC=C3)C4=CC=CC=C4",
        expected_matches=Counter({"benzene": 4}),
        description="For [N+]-Ar4 molecule, assignment of Ar-NR2 bond type is rejected.",
    ),
    SubstructMatchTest(
        id=332,
        SMILES="CN1CCN(CC1)CCCN2C3=CC=CC=C3SC4=C2C=C(C=C4)C(Cl)(Br)I",
        expected_matches=Counter({"piperazine": 1, "benzene": 2, "C-Cl": 1, "C-Br": 1, "C-I": 1, "Ar-NR2": 1}),
        description="Ar-NR-Ar fragment assumed to be is assigned as one Ar-NR2.",
    ),
    SubstructMatchTest(
        id=333,
        SMILES="B(C1=CC(=C(C=C1)C)Cl)(C2=CC(=C(C=C2)C)Cl)OC(=O)C3=C(C=CC=N3)O",
        expected_matches=Counter({"pyridine": 1, "benzene": 2, "Ar-OH": 1, "Ar-Cl": 2}),
        description="Assignment omitted for Ar-C(=O)OR if R = B.",
    ),
    SubstructMatchTest(
        id=334,
        SMILES="C1=C2C3=C(C(=C1O)O)OC(=O)C4=CC(=C(C(=C43)OC2=O)O)O",
        expected_matches=Counter({"benzene": 2, "pyrones": 2, "Ar-OH": 4}),
        description="Ar-Ar correctly is not assigned within fused aromatic rings. In such case the Ar-Ar bond is no longer a single bond.",
    ),
    SubstructMatchTest(
        id=335,
        SMILES="C1=CC=C2C(=C1)C3=CC=CC=C3[S+]2Cl",
        expected_matches=Counter({"benzene": 2, "thiophene": 1}),
        description="Ar-Ar is not matched  because all fused rings are aromatic.",
    ),
    SubstructMatchTest(
        id=336,
        SMILES="C1=CC=C2C(=C1)C3=CC=CC=C3C(=O)C2=O",
        expected_matches=Counter({"Ar-C(=O)R": 2, "Ar-Ar": 1, "benzene": 2}),
        description="""
            Ar-Ar and Ar-C(=O)R assignment is allowed, since the middle ring is not aromatic. 
            1,2-diketone is assumed to be assigned as two Ar-C(=O)R bond types.""",
    ),
    SubstructMatchTest(
        id=337,
        SMILES="C1=CC=C2C=C3C4=CC=CC5=C4C(=CC=C5)C3=CC2=C1",
        expected_matches=Counter({"benzene": 4, "Ar-Ar": 2}),
        description="Assignment for non-alternat polyaromatic hydrocarbon (https://doi.org/10.1002/poc.4647). The resulat is correct!",
    ),
    SubstructMatchTest(
        id=338,
        SMILES="C1=CC=C2C(=C1)C3=CC=CC=C3C2=O",
        expected_matches=Counter({"benzene": 2, "Ar-Ar": 1, "Ar-C(=O)R": 1}),
        description="Ar-C(=O)-Ar fragment is assumed to be matched as Ar-C(=O)R bond type.",
    ),
    SubstructMatchTest(
        id=339,
        SMILES="C1(C=CC=C1)=O",
        expected_matches=Counter({"C=C-C=C": 1, "C=O": 1}),
        description="Aromaticity check. The cyclopentadienone is correctly recognized by RDKit as a non-aromatic ring.",
    ),
    SubstructMatchTest(
        id=340,
        SMILES="C1=C(OC(=C1)[N+](=O)[O-])C2=CSC(=N2)NC=O",
        expected_matches=Counter({"Ar-Ar": 1, "Ar-NO2": 1, "RC(=O)NH2": 1, "furan": 1, "thiazole": 1}),
        description="RC(=O)NH2 is matched when R = H.",
    ),
    SubstructMatchTest(
        id=341,
        SMILES="CC(=NN=C(C)C)C",
        expected_matches=Counter({"R2C=N-N=CR2": 1}),
        description="Simple test for R2C=N-N=CR2 bond type matching.",
    ),
    SubstructMatchTest(
        id=342,
        SMILES="C1=CC=C(C=C1)C(=NN=C(C2=CC=CC=C2)C3=CC=CC=C3)C4=CC=CC=C4",
        expected_matches=Counter({"R2C=N-N=CR2": 1, "benzene": 4}),
        description="R2C=N-N=CR2 bond type is allowed to be matched when R = Ar.",
    ),
    SubstructMatchTest(
        id=343,
        SMILES="C1C(=NN=C(CS1(=O)=O)C2=CC=CC=C2)C3=CC=CC=C3",
        expected_matches=Counter({"R2C=N-N=CR2": 1, "benzene": 2}),
        description="R2C=N-N=CR2 assignment within the ring.",
    ),
    SubstructMatchTest(
        id=344,
        SMILES="C/C(=N/N=C(\\C1=CC=CC=C1)/C)/C2=CC=CC=C2",
        expected_matches=Counter({"R2C=N-N=CR2": 1, "benzene": 2}),
        description="A simple test for R2C=N-N=CR2 bond type matching.",
    ),
    SubstructMatchTest(
        id=345,
        SMILES="C/C(=N\\N=C(\\C1C(C(C1)CC(=O)O)(C)C)/C)/C2C(C(C2)CC(=O)O)(C)C",
        expected_matches=Counter({"R2C=N-N=CR2": 1, "cyclobutane": 2, "RCOOH": 2}),
        description="R2C=N-N=CR2 bond type is allowed to be matched if any R corresponds to saturated ring.",
    ),
    SubstructMatchTest(
        id=346,
        SMILES="CN1C2=CC=CC=C2/C(=N/N=C\\3/C4=CC=CC=C4N(C=C3)C)/C=C1",
        expected_matches=Counter({"benzene": 2, "pyridine": 2}),
        description="Corner case: The R₂C=N–N=CR₂ bond type is not assigned because it is a part of an aromatic ring.",
    ),
    SubstructMatchTest(
        id=347,
        SMILES="CC(=N/N=C(/C1=CC=C(C=C1)[N+](=O)[O-])\\C23CN4CN(C2)CN(C3)C4)C",
        expected_matches=Counter({"Ar-NO2": 1, "benzene": 1, "R2C=N-N=CR2": 1}),
        description="R2C=N-N=CR2 bond type is assigned if any R corresponds to bicyclic fragment.",
    ),
    SubstructMatchTest(
        id=348,
        SMILES="CC(=NN=C1CC(N(C(C1)(C)C)O)(C)C)C2(CC(C3=C(C4C(C(=C3C2)O)C(=O)C5=C(C4=O)C(=CC=C5)OC)O)OC6CC(C(CO6)O)(C)N)O",
        expected_matches=Counter(
            {
                "piperidine": 1,
                "benzene": 1,
                "cyclohexane": 1,
                "Ar-C(=O)R": 2,
                "Ar-OR": 1,
                "R2C=N-N=CR2": 1,
                "C=C-C=C": 1,
            }
        ),
        description="R2C=N-N=CR2 bond type is allowed to match if its R2C fragment is a part of saturated ring. ",
    ),
    SubstructMatchTest(
        id=349,
        SMILES="C1=CC=C(C=C1)C(=NN=C2C=CC(=O)C=C2)C3=CC=CC=C3",
        expected_matches=Counter({"C=O": 1, "R2C=N-N=CR2": 1, "benzene": 2, "C=C": 2}),
        description="R₂C=N–N=CR₂ is matched because its R2C fragment is not found within aromatic ring.",
    ),
    SubstructMatchTest(
        id=350,
        SMILES="CC1=C(C2=CC=CC=C2N1)C3=CC(=NN=C(C3)C4=CC=CC=C4)C5=CC=CC=C5",
        expected_matches=Counter({"benzene": 3, "R2C=N-N=CR2": 1, "pyrrole": 1, "Ar-C=C": 1}),
        description="If conjugation extends beyond R2C=N-N=CR2 with addional C=C bonds, R2C=N-N=CR2 is matched along with relevant bond types (C=C, C=C-C=C, Ar-C=C, etc.).",
    ),
    SubstructMatchTest(
        id=351,
        SMILES="C/C(=N\\N)/C(=N/N=C(/C(=N/N=C(/C(=N/N)/C)\\C)/C)\\C)/C",
        expected_matches=Counter({"R2C=N-N=CR2": 2, "C=N": 2}),
        description="Test for R2C=N-N=CR2 self-matching, as well as R2C=N-N=CR2 and C=N cross-overlap.",
    ),
    SubstructMatchTest(
        id=352,
        SMILES="C/C(=N\\N)/C(=N/N=C(/C(=N/N=C(/C(=N/N=C(/C(=N/N)/C)\\C)/C)\\C)/C)\\C)/C",
        expected_matches=Counter({"R2C=N-N=CR2": 3, "C=N": 2}),
        description="Test for R2C=N-N=CR2 self-matching, as well as R2C=N-N=CR2 and C=N cross-overlap.",
    ),
    SubstructMatchTest(
        id=353,
        SMILES="CC12/C(=N/N=C\\3/C4(CN5CC3CN(C4)CC5)C)/C6CN(C1)CCN(C2)C6",
        expected_matches=Counter({"R2C=N-N=CR2": 1, "piperidine": 2}),
        description="R2C=N-N=CR2 bond type is allowed to match if its R2C fragment is a part of bicyclic structure.",
    ),
    SubstructMatchTest(
        id=354,
        SMILES="C1=CC=C\\2C(=C1)C3=NC4=CC=CC=C4N=C3/C2=N/N=C\\5/C6=CC=CC=C6C7=NC8=CC=CC=C8N=C75",
        expected_matches=Counter({"Ar-Ar": 2, "R2C=N-N=CR2": 1, "benzene": 4, "pyrazine": 2}),
        description="Assignment of R2C=N-N=CR2 as part of non-alternat five-membered ring in polyaromatic system.",
    ),
    SubstructMatchTest(
        id=355,
        SMILES="C1=CN(C=CC1=NN=C2C=C[N+](=O)C=C2)[O-]",
        expected_matches=Counter({"C=N": 1, "C=C": 2, "N=O": 1, "pyridine": 1}),
        description="If a C=N bond in R2C=N–N=CR2 is part of an aromatic system, the fragment is not assigned and only one C=N bond is matched instead.",
    ),
    SubstructMatchTest(
        id=356,
        SMILES="C1=CC2=C(/C(=N/N=C/3\\C4=C(C(=CC(=C4)[N+](=O)[O-])[N+](=O)[O-])C5=C3C=C(C=C5)[N+](=O)[O-])/C6=C2C(=CC(=C6)[N+](=O)[O-])[N+](=O)[O-])C=C1[N+](=O)[O-]",
        expected_matches=Counter({"Ar-NO2": 6, "benzene": 4, "Ar-Ar": 2, "R2C=N-N=CR2": 1}),
        description="Assignment of R2C=N-N=CR2 as part of non-alternat five-membered ring in polyaromatic system.",
    ),
    SubstructMatchTest(
        id=357,
        SMILES="C1/C(=N/N=C/2\\C3=CC=CC=C3C(=C4C(=O)C5=CC=CC=C5C4=O)C2)/C6=CC=CC=C6C1=C7C(=O)C8=CC=CC=C8C7=O",
        expected_matches=Counter({"benzene": 4, "Ar-C(=O)R": 4, "Ar-C=C": 2, "R2C=N-N=CR2": 1}),
        description="Test for Ar-C(=O)R, Ar-C=C and R2C=N–N=CR2 assignment.",
    ),
    SubstructMatchTest(
        id=358,
        SMILES="C/C(=N\\N=C(\\C1=CC=C(C=C1)N=NC(C#N)C#N)/C)/C2=CC=C(C=C2)N=NC(C#N)C#N",
        expected_matches=Counter({"-C#N": 4, "benzene": 2, "N=N": 2, "R2C=N-N=CR2": 1}),
        description="Test for N=N bond matching.",
    ),
    SubstructMatchTest(
        id=359,
        SMILES="C1=CC(=NN=[N-])C=CC1=NN=C2C=CC(=N[N+]#N)C=C2",
        expected_matches=Counter({"C=N": 2, "N=N": 1, "C=C": 4, "R2C=N-N=CR2": 1}),
        description="Test for matching of conjugated bonds system containing C=N, N=N, C=C and R2C=N-N=CR2 bond types.",
    ),
    SubstructMatchTest(
        id=360,
        SMILES="C1=CC(=NN=C2C=CC=CC2=N[N+]#N)C(=NN=[N-])C=C1",
        expected_matches=Counter({"C=C-C=C": 2, "N=N": 1, "C=N": 2, "R2C=N-N=CR2": 1}),
        description="""
            Lack of aromaticity implies complicated bond assignment. 
            The-N(+)#N group is not assigned because no constitutive correction is available for this functional group.""",
    ),
    SubstructMatchTest(
        id=361,
        SMILES="CCC1=C(C(=CC=C1)/C(=N/N=C(\\C)/C2=CC=CCC2(C)C)/C=C=C)F",
        expected_matches=Counter({"C=C-C=C": 1, "R2C=N-N=CR2": 1, "benzene": 1, "C=C": 2}),
        description="C=C=C fragment is correctly assigned as two C=C bonds.",
    ),
    SubstructMatchTest(
        id=362,
        SMILES="CC(C)C1=CC=CC=C1/C=C/C2=NN=C(C3C2CC3)CC4=CC=C(C=C4)OC(F)(F)F",
        expected_matches=Counter({"benzene": 2, "Ar-OR": 1, "cyclobutane": 1, "R2C=N-N=CR2": 1, "Ar-C=C": 1}),
        description="Test for Ar-C=C and R2C=N-N=CR2 bond types matching in one molecule.",
    ),
    SubstructMatchTest(
        id=363,
        SMILES="CC1=CC=C(C=C1)C(=O)C(=C=O)/C(=N\\N=C(C2=CC=CC=C2)C3=CC=CC=C3)/C(=O)OC",
        expected_matches=Counter(
            {
                "Ar-C(=O)R": 1,
                "C=O": 1,
                "R2C=N-N=CR2": 1,
                "RCOOR": 1,
                "benzene": 3,
                "C=C": 1,
            }
        ),
        description="C=C=O group is expectedly matched as separate C=C and C=O bonds.",
    ),
    SubstructMatchTest(
        id=364,
        SMILES="C1=CC=C2C(=C1)C3=CC=CC=C3C2=N/N=C\\4/C5=C(C=CC(=C5)F)NC4=O",
        expected_matches=Counter({"benzene": 3, "RC(=O)NH2": 1, "R2C=N-N=CR2": 1, "Ar-Ar": 1}),
        description="Test for matching of adjactent R2C=N-N=CR2 and RC(=O)NH2 bond types.",
    ),
    SubstructMatchTest(
        id=365,
        SMILES="CC#CC#CC(=O)C1=CC=CC=C1",
        expected_matches=Counter({"Ar-C(=O)R": 1, "C#C": 2, "benzene": 1}),
        description="RC#C-C(=O)R bond type is not matched if any R = Ar.",
    ),
    SubstructMatchTest(
        id=366,
        SMILES="CC(=O)C#CC1=CC=CC=C1",
        expected_matches=Counter({"C=O": 1, "Ar-C#C": 1, "benzene": 1}),
        description="RC#C-C(=O)R bond type is not matched if any R = Ar.",
    ),
    SubstructMatchTest(
        id=367,
        SMILES="CCCCCCCC1C(O1)CC#CC#CC(=O)CCO",
        expected_matches=Counter({"C#C": 1, "RC#C-C(=O)R": 1}),
        description="RC≡C–C(=O)R matching is allowed if the adjacent carbon atom forms a double or triple bond. ",
    ),
    SubstructMatchTest(
        id=368,
        SMILES="C#CC(=O)O",
        expected_matches=Counter({"C#C": 1, "RCOOH": 1}),
        description="RC≡C–C(=O)R is not matched if -C(=O)R fragment corresponds to carboxyl or ester group.",
    ),
    SubstructMatchTest(
        id=369,
        SMILES="C#CC=O",
        expected_matches=Counter({"RC#C-C(=O)R": 1}),
        description="RC#C-C=OR assignment allowed if R = H.",
    ),
    SubstructMatchTest(
        id=370,
        SMILES="CC(=O)C#CC(=O)C",
        expected_matches=Counter({"RC#C-C(=O)R": 1, "C=O": 1}),
        description="Check for self-matching of RC#C-C(=O)R bond type.",
    ),
    SubstructMatchTest(
        id=371,
        SMILES="CC(C)(C)C#CC(=O)C#CC(C)(C)C",
        expected_matches=Counter({"C#C": 1, "RC#C-C(=O)R": 1}),
        description="Check for self-matching of RC#C-C(=O)R bond type.",
    ),
    SubstructMatchTest(
        id=372,
        SMILES="CCCCC#CC(=O)C#CC1=CC=CC=C1",
        expected_matches=Counter({"Ar-C#C": 1, "RC#C-C(=O)R": 1, "benzene": 1}),
        description="Check for self-matching of RC#C-C(=O)R bond type.",
    ),
    SubstructMatchTest(
        id=373,
        SMILES="CC1=C(C(C[C@@H](C1)O)(C)C)C#CC(=O)C",
        expected_matches=Counter({"cyclohexene": 1, "RC#C-C(=O)R": 1}),
        description="Test for matching of RC#C-C(=O)R bond type, adjacent to cyclohexene ring.",
    ),
    SubstructMatchTest(
        id=374,
        SMILES="C#CC(=O)C#C",
        expected_matches=Counter({"C#C": 1, "RC#C-C(=O)R": 1}),
        description="Check for self-matching of RC#C-C(=O)R bond type.",
    ),
    SubstructMatchTest(
        id=375,
        SMILES="CC(C)(C#CC(=O)SC)N1CCOCC1",
        expected_matches=Counter({"morpholine": 1, "C#C": 1, "C=O": 1}),
        description="RC#C-C(=O)R' is not matched if R' = B,N,O,F,Si,P,S or Sn.",
    ),
    SubstructMatchTest(
        id=376,
        SMILES="C[Si](C)(C)C#CC(=O)Cl",
        expected_matches=Counter({"RC#C-C(=O)R": 1, "C-Cl": 1}),
        description="RC#C-C(=O)R' bond type is mathed if R = Si and R' = Cl - a rough approximation.",
    ),
    SubstructMatchTest(
        id=377,
        SMILES="CCC(C)N1C(=O)N(C=N1)C2=CC=C(C=C2)N3CCN(CC3)C4=CC=C(C=C4)OCC5COC(O5)(CN6C=NC=N6)C7=C(C=C(C=C7)Cl)Cl",
        expected_matches=Counter({"piperazine": 1, "Ar-OR": 1, "Ar-Cl": 2, "benzene": 3, "Ar-NR2": 2}),
        description="Rings without an available constitutive correction are left unassigned. Piperazine ring and two Ar-NR2 bond types are allowed to cross-overlap.",
    ),
    SubstructMatchTest(
        id=378,
        SMILES="C#CC(=O)F",
        expected_matches=Counter({"C=O": 1, "C#C": 1}),
        description="RC#C-C(=O)R' is not allowed to be matched if R' = F.",
    ),
    SubstructMatchTest(
        id=379,
        SMILES="C(=O)C#CI",
        expected_matches=Counter({"RC#C-C(=O)R": 1, "C-I": 1}),
        description="RC#C-C(=O)R' is allowed to be matched if R = I.",
    ),
    SubstructMatchTest(
        id=380,
        SMILES="C1CC2(CCC1(C#CC(=O)C3=CCC(C=C3)F)O)OCCO2",
        expected_matches=Counter({"cyclohexane": 1, "RC#C-C(=O)R": 1, "C=C-C=C": 1}),
        description="Test for RC#C-C(=O)R and C=C-C=C bond type matching.",
    ),
    SubstructMatchTest(
        id=381,
        SMILES="C(CC(=O)C#CC#CC(=O)CCC(F)F)C(F)F",
        expected_matches=Counter({"RC#C-C(=O)R": 2}),
        description="Test for RC#C-C(=O)R self-matching.",
    ),
    SubstructMatchTest(
        id=382,
        SMILES="COC1=CC=C(C=C1)N=C(C#CC=O)C(F)(F)F",
        expected_matches=Counter({"Ar-OR": 1, "benzene": 1, "C=N": 1, "RC#C-C(=O)R": 1}),
        description="Test for adjacent RC#C-C(=O)R and C=N bond types matching.",
    ),
    SubstructMatchTest(
        id=383,
        SMILES="CC1=CC2=C(C=C1)N=C3C(=N2)SC(=O)S3",
        expected_matches=Counter({"benzene": 1, "pyrazine": 1}),
        description="C=O bond is not matched for S2C=O fragment.",
    ),
    SubstructMatchTest(
        id=384,
        SMILES="C1=CC=C(C=C1)C2=NC3=C(N=C(N=C3N=C2N)N)N",
        expected_matches=Counter({"Ar-Ar": 1, "benzene": 1, "pyrazine": 1, "pyrimidine": 1, "Ar-NR2": 3}),
        description="Check for pyrazine and pyrimidine matching in one structure. Ar-NH2 is assume to be matched as Ar-NR2 bond type.",
    ),
    SubstructMatchTest(
        id=385,
        SMILES="C1(=C(N=C(C(=N1)Cl)N)N)C(=O)N=C(N)N",
        expected_matches=Counter({"C=N": 1, "Ar-Cl": 1, "pyrazine": 1, "Ar-NR2": 2}),
        description="C=N bond is allowed to be matched as a part of guanidine group - a rough approximation. C=O is intentionally left unassigned in C=N-N=N.",
    ),
    SubstructMatchTest(
        id=386,
        SMILES="CC1=C(SSC1=S)C2=NC=CN=C2",
        expected_matches=Counter({"Ar-Ar": 1, "pyrazine": 1}),
        description="Aromaticity check.",
    ),
    SubstructMatchTest(
        id=387,
        SMILES="CCOC(=O)C1=C(N=C2N1C=CN=C2)C",
        expected_matches=Counter({"imidazole": 1, "pyrazine": 1, "Ar-COOR": 1}),
        description="If a heteroatom is shared by two fused rings, this atom is considered in the assignment of each ring.",
    ),
    SubstructMatchTest(
        id=388,
        SMILES="CCOP(=S)(OCC)OC1=NOC(=C1)C2=CC=CC=C2",
        expected_matches=Counter({"benzene": 1, "isoxazole": 1, "Ar-Ar": 1}),
        description="Test encompassing an isoxazole ring.",
    ),
    SubstructMatchTest(
        id=389,
        SMILES="CC1=C(C(=NO1)C)CSC2=CN=C(S2)NC(=O)C",
        expected_matches=Counter({"RC(=O)NH2": 1, "thiazole": 1, "isoxazole": 1}),
        description="Test encompassing both isoxazole and thiazole rings in one molecule.",
    ),
    SubstructMatchTest(
        id=390,
        SMILES="CC1=CC(=NO1)N2C(N3CCCC3C2=O)C4=CC(=C(C(=C4)OC)OC)OC",
        expected_matches=Counter({"pyrrolidine": 1, "Ar-OR": 3, "RC(=O)NH2": 1, "benzene": 1, "isoxazole": 1}),
        description="RC(=O)NRAr group is assumed to be assigned as RC(=O)NH2 bond type.",
    ),
    SubstructMatchTest(
        id=391,
        SMILES="CC(C)NC1=NC(=NC(=N1)SC)N=[N+]=[N-]",
        expected_matches=Counter({"N=N": 2, "triazine": 1, "Ar-NR2": 1}),
        description="The -N=[N+]=[N-] group is assumed to be assigned as two N=N bond types.",
    ),
    SubstructMatchTest(
        id=392,
        SMILES="C1=CC=NC(=C1)C2=NC(=NC(=N2)C3=CC=CC=N3)C4=CC=CC=N4",
        expected_matches=Counter({"pyridine": 3, "triazine": 1, "Ar-Ar": 3}),
        description="Test encompassing triazine ring",
    ),
    SubstructMatchTest(
        id=393,
        SMILES="C1=CC=C(C(=C1)NC2=NC(=NC=N2)N3C=CC=C3)Cl",
        expected_matches=Counter({"pyrrole": 1, "triazine": 1, "benzene": 1, "Ar-Cl": 1, "Ar-NR2": 1}),
        description="Ar-NH-Ar fragment expectedly assigned as one Ar-NR2 bond type. Test encompassing both triazine and pyrrole rings.",
    ),
    SubstructMatchTest(
        id=394,
        SMILES="C1=CC=C(C=C1)N(C2=CC=CC=C2)C3=NC(=NC(=N3)N)CCl",
        expected_matches=Counter({"benzene": 2, "triazine": 1, "Ar-NR2": 2, "C-Cl": 1}),
        description="Ar-NAr2 fragment is assumed to be assigned as one Ar-NR2 bond type.",
    ),
    SubstructMatchTest(
        id=395,
        SMILES="C1=C(C=C(C(=C1Br)OC2=NC(=NC(=N2)OC3=C(C=C(C=C3Br)Br)Br)OC4=C(C=C(C=C4Br)I)I)I)I",
        expected_matches=Counter({"Ar-OR": 3, "Ar-I": 4, "Ar-Br": 5, "benzene": 3, "triazine": 1}),
        description="Each Ar-O-Ar fragment is expectedly assined as one Ar-OR bond type.",
    ),
    SubstructMatchTest(
        id=396,
        SMILES="CCOP(=S)(OCC)SC1C(OCCO1)SP(=S)(OCC)OCC",
        expected_matches=Counter({"dioxane": 1}),
        description="Test encompassing dioxane ring.",
    ),
    SubstructMatchTest(
        id=397,
        SMILES="C1C(=O)OCC(=O)O1",
        expected_matches=Counter({"RCOOR": 2}),
        description="Dioxane is not matched if any of C atoms belongs to carbonyl group.",
    ),
    SubstructMatchTest(
        id=398, SMILES="C1(C(OC2C(O1)OC(C(O2)O)O)O)O", expected_matches=Counter({"dioxane": 2}), description="Test for two fused dioxane rings."
    ),
    SubstructMatchTest(
        id=399,
        SMILES="C1CN(C2=C(C(=O)N1)OC3=C2C=C(C=C3)C(F)(F)F)CC[C@H]4COCCO4",
        expected_matches=Counter({"dioxane": 1, "benzene": 1, "furan": 1, "Ar-NR2": 1, "Ar-C(=O)NH2": 1}),
        description="Test encompassing both furan and dioxane rings in one molecule.",
    ),
    SubstructMatchTest(
        id=400,
        SMILES="C1=COC(=C1)CSSCC2=CC=CO2",
        expected_matches=Counter({"furan": 2}),
        description="Disulfide bridge -S-S- is not assigned due to lack of relevant constitutive correction.",
    ),
]
