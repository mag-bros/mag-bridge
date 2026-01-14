from collections import Counter
from dataclasses import dataclass, field
from typing import Counter, Optional


@dataclass(frozen=True)
class BondMatchTestCase:
    """
    Defines a single bond-matching test case.

    SMILES:
        SMILES string of the test molecule.

    expected_matches:
        Expected number of occurrences for each bond type,
        expressed as a Counter keyed by bond formula.

        Example:
            Counter({
                "C=C": 2,   # two carbon–carbon double bonds
                "C-Cl": 3,  # three carbon–chlorine single bonds
            })

        Each value represents how many substructure matches
        should be found for the given bond type in the molecule.

    description:
        Optional free-text description of the test case
        (e.g. structural features, edge cases, or notes).
    """

    SMILES: str
    expected_matches: Counter[str] = field(default_factory=Counter)
    description: Optional[str] = ""


BOND_MATCH_TEST_CASES: list[BondMatchTestCase] = [
    BondMatchTestCase(
        SMILES="ClC=CC(Cl)C=CCl",
        expected_matches=Counter({"C=C": 2, "C-Cl": 3}),
        description="The results are correct. This means that when counting bond types C=C and C-Cl, the same C atom for both bond types can be considered.",
    ),
    BondMatchTestCase(
        SMILES="C=CCC=C",
        expected_matches=Counter({"CH2=CH-CH2-": 1, "C=C": 1}),
        description="Incorrect, due to chemical reasons. All carbon atoms of allyl group cannot belong to other bond type!",
    ),
    BondMatchTestCase(
        SMILES="CC(=CC=CC=C(C)C=CC=C(C)C(=O)OC1C(C(C(C(O1)COC2C(C(C(C(O2)CO)O)O)O)O)O)O)C=CC=C(C)C(=O)OC3C(C(C(C(O3)COC4C(C(C(C(O4)CO)O)O)O)O)O)O",  # TODO: Fix the self-matching of C=C-C=C
        expected_matches=Counter({"C=C-C=C": 3, "C=C": 1, "RCOOR": 2}),
        description="Incorrect, due to chemical reasons. All carbon atoms of C=C-C=C fragment cannot belong to other bond type! For ester RCOOR group the results are correct.",
    ),
    BondMatchTestCase(
        SMILES="CC(=C)C1CC2=C(O1)C=CC3=C2OC4COC5=CC(=C(C=C5C4C3=O)OC)OC",
        expected_matches=Counter({"Ar-OR": 5, "benzene": 2, "C=C": 1, "Ar-C(=O)R": 1}),
        description="Expected result.",
    ),
    BondMatchTestCase(
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
        description="""
            Purpose: Tests if ArOAr was not incorrectly matched.
            Result: Expected.
            """,
    ),
    BondMatchTestCase(
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
            Purpose: Tests saturated policyclic systems
            Result: Expected - saturated rings will not be matched when attached to aromatic ring by the ring's edge.
        """,
    ),
    BondMatchTestCase(
        SMILES="C1=CN(C(=O)N=C1N)C2C(C(C(O2)CO)O)O",
        expected_matches=Counter({"tetrahydrofuran": 1}),
        description="""
            Purpose: Tests tricky case of pyrimidinone ring in the structure, which cannot be matched as pyrimidine ring.
            Result: Expected - pyrimidine ring is not matched when one of the carbons is a part of carbonyl group.
    """,
    ),
    BondMatchTestCase(
        SMILES="CCCCNC(=O)OCC#CI",
        expected_matches=Counter({"C#C": 1, "C-I": 1}),
        description="""
            Purpose: Important case of carbamate ROC(=O)NHR group.
            Result: Expected - RCOOR and RCOONHR groups are not matched when being part of carbamate fragment.
        """,
    ),
    BondMatchTestCase(
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
                Purpose: Example of fused ring system and improtant case of piperidine and Ar-NR2 matching.
                Result: Expected. Note that for fused ring systems each ring is matched separately which is a rough approximation. Also, Ar-CONR2 group is omitted in query.
            """,
    ),
    BondMatchTestCase(
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
                Purpose: Important case of cyclohexene fused system and cyclohexenone ring.
                Result: Expected. For cyclohexenone separate C=O and cyclohexene ring matching is allowed. C=C-C=C is NOT matched when C atoms are part of fused cyclohexene ring system.
    """,
    ),
    BondMatchTestCase(
        SMILES="CN(C)C1=CC=C(C=C1)C(=C2C=CC(=[N+](C)C)C=C2)C3=CC=C(C=C3)N(C)C",
        expected_matches=Counter(
            {"C=N": 1, "Ar-NR2": 2, "Ar-C=C": 1, "benzene": 2, "C=C": 2}
        ),
        description="""
            Purpose: Highlights the complexity of C=C-C=C, C=C and Ar-C=C matching.
            Result: FAILED. For the molecule, Ar-C=C cannot be matched twice!
            Note that C=C-C=C as well as C=C are not matched because of the presence of Ar-C=C bond type! The C=N bond counts also with charged N+ atom.
        """,
    ),
    BondMatchTestCase(
        SMILES="C1C=C2C(=CC(=O)O2)C(O1)O",
        expected_matches=Counter({"C=C-C=C": 1, "RCOOR": 1}),
        description="""
            Purpose: Checks simple RCOOR and C=C-C=C matching.
            Result: Expected.
        """,
    ),
    BondMatchTestCase(
        SMILES="CC(=O)NC1CCC2=CC(=C(C(=C2C3=CC=C(C(=O)C=C13)OC)OC)OC)OC",
        expected_matches=Counter(
            {"RC(=O)NH2": 1, "Ar-OR": 4, "Ar-Ar": 1, "benzene": 1}
        ),
        description="""
            Purpose: This is a corner case of aromaticity involving the seven-membered tropone ring. RDKit treats it as aromatic, but it is, in fact, antiaromatic.
            See (DOI): https://doi.org/10.1021/acs.orglett.0c02343
            Result: Expected. Note that RDKit treats antiaromatic rings as aromatic.
        """,
    ),
    BondMatchTestCase(
        SMILES="CC1=CC(=C(C(=C1C=CC(=CC=CC(=CC(=O)[O-])C)C)C)C)OC",  # TODO: Fix the self-matching of C=C-C=C bond type.
        expected_matches=Counter(
            {"C=C-C=C": 1, "C=C": 1, "Ar-C=C": 1, "Ar-OR": 1, "benzene": 1, "RCOOH": 1}
        ),
        description="""
            Purpose: Highlights the problem with self-matching of C=C-C=C bond type.
            Result: FAILED. The C=C-C=C-C=C fragment of the molecule should be matched as C=C-C=C (1) and C=C (1).
        """,
    ),
    BondMatchTestCase(
        SMILES="COC1=C(C=CC(=C1)CC=C)[O-]",
        expected_matches=Counter(
            {"CH2=CH-CH2-": 1, "Ar-OH": 1, "Ar-OR": 1, "benzene": 1}
        ),
        description="""
            Purpose: Checks matching of phenolate and allyl group attached to aromatic ring.
            Result: Expected.
        """,
    ),
    BondMatchTestCase(
        SMILES="C=CCN=C=S",
        expected_matches=Counter({"CH2=CH-CH2-": 1}),
        description="""
            Purpose: Highlights the possibility of C=N matching in isothiocyanate S=C=N group.
            Result: Expected - No C=N match.
        """,
    ),
    BondMatchTestCase(
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
            Purpose: Complex ring system with bicyclic fragment. Shows issue with saturated rings matching.
            Result. Expected. Note that saturated rings are not matched when fused with aromatic rings via C=C edge.
        """,
    ),
    BondMatchTestCase(
        SMILES="CCCC(C)C1(C(=O)NC(=O)NC1=O)CC=C",
        expected_matches=Counter({"CH2=CH-CH2-": 1}),
        description="""
            Purpose: Tricky amide group matching in a barbiturate ring.
            Result. Expected. Authors assumed that RCONHR amide group is not matched when N atom is conneted to two carbonyl C atoms.
        """,
    ),
    BondMatchTestCase(
        SMILES="CC1=C(C(=O)C=CO1)O",
        expected_matches=Counter({"pyrones": 1, "Ar-OH": 1}),
        description="""
            Purpose: Example of gamma-pyrone derivative, which RDKit treats as aromatic molecule.
            Result: Expected.
        """,
    ),
    BondMatchTestCase(
        SMILES="CC(=O)CC(C1=CC=CC=C1)C2=C(C3=CC=CC=C3OC2=O)O",
        expected_matches=Counter({"C=O": 1, "Ar-OH": 1, "benzene": 2, "pyrones": 1}),
        description="""
            Purpose: Interesting case of alpha-pyrone being part of fused aromatic ring system.
            Result: Expected.
        """,
    ),
    BondMatchTestCase(
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
            Purpose: Highlights the possibility of matching of RCOOR within tetrahydrofuran ring.
            Result. Expected - RCOOR matched, while tetrahydrofuran ring ignored. Also, the C=O in thioester RC(=O)SR groups is ignored.
        """,
    ),
    BondMatchTestCase(
        SMILES="CC(C)(C)C(=O)C(N1C=NC=N1)OC2=CC=C(C=C2)Cl",
        expected_matches=Counter({"C=O": 1, "Ar-OR": 1, "Ar-Cl": 1, "benzene": 1}),
        description="""
            Purpose: Shows that not all aromatic rings are considered in the query due to limited literature data.
            Result: Expected - triazole ring ignored.
        """,
    ),
    BondMatchTestCase(
        SMILES="CC1C(C(C(O1)OC2C(C(C(C(C2O)O)N=C(N)N)O)N=C(N)N)OC3C(C(C(C(O3)CO)O)O)NC)(C=O)O",
        expected_matches=Counter({"C=O": 1, "cyclohexane": 1, "tetrahydrofuran": 1}),
        description="""
            Purpose: Highlights that C=N is ignored when being part of guanidine group.
            Result: Expected - C=N ignored.
        """,
    ),
    BondMatchTestCase(
        SMILES="CC1CCC2=C3N1C=C(C(=O)C3=CC(=C2)F)C(=O)[O-]",
        expected_matches=Counter({"Ar-COOH": 1, "benzene": 1}),
        description="Purpose: Highlights that pyridine ring is not matched when one of its C atoms is a part of C=O group.",
    ),
    BondMatchTestCase(
        SMILES="CC1=C(C(CCC1)(C)C)C=CC(=CC=CC(=CC(=O)O)C)C",
        expected_matches=Counter({"C=C-C=C": 2, "RCOOH": 1, "cyclohexene": 1}),
        description="""Purpose: Examine C=C-C=C self-matching.""",
    ),
    BondMatchTestCase(
        SMILES="C1=CC=C(C(=C1)C2=C3C=CC(=O)C=C3OC4=C2C=CC(=C4)[O-])C(=O)[O-]",  # TODO: rdkit error?
        expected_matches=Counter({"Ar-OH": 1, "Ar-Ar": 1, "Ar-COOH": 1, "benzene": 3}),
        description="""Purpose: Corner case of Ar-Ar matching.""",
    ),
    BondMatchTestCase(
        SMILES="CCN(CC)C1=CC2=C(C=C1)C(=C3C=CC(=[N+](CC)CC)C=C3O2)C4=CC=CC=C4C(=O)O",  # TODO: rdkit error?
        expected_matches=Counter({"Ar-NR2": 1, "Ar-Ar": 1, "Ar-COOH": 1, "benzene": 3}),
        description="Purpose: Corner case of Ar-Ar matching.",
    ),
    BondMatchTestCase(
        SMILES="CC1=C(C(CC(C1=O)O)(C)C)C=CC(=CC=CC(=CC=CC=C(C)C=CC=C(C)C=CC2=C(C(=O)C(CC2(C)C)O)C)C)C",
        expected_matches=Counter({"C=C-C=C": 4, "C=C": 1, "C=O": 2, "cyclohexene": 2}),
        description="""
            Purpose: Examine C=C-C=C self-matching.
            Result. Failed.
        """,
    ),
    BondMatchTestCase(
        SMILES="C=CC1=C(N2C(C(C2=O)NC(=O)C(=NOCC(=O)O)C3=CSC(=N3)N)SC1)C(=O)O",
        expected_matches=Counter(
            {"C=C-C=C": 1, "RCOOH": 2, "RC(=O)NH2": 1, "C=N": 1, "thiazole": 1}
        ),
        description="""
            Purpose: Thiazole derivative example.
            Result. Failed.
        """,
    ),
    BondMatchTestCase(
        SMILES="C=CCCCC(=C)C/C=C/C(C)=C/C=C/C(C)=C/C=C/C=C(C)/C=C/C=C(C)/C=C/C=C(C)/CC/C=C(C)\C",
        expected_matches=Counter(
            {
                "C=C-C=C": 5,
                "C=C": 2,
                "CH2=CH-CH2-": 1,
            }
        ),
        description="""
            Purpose: Example encompassing C=C-C=C, C=C and  
            Result. Failed.
        """,
    ),
    BondMatchTestCase(
        SMILES="CC1=C(C(CCC1)(C)C)C=CC(=CC=CC(=CC(=O)O)C)C",
        expected_matches=Counter({"C=C-C=C": 2, "RCOOH": 1, "cyclohexene": 1}),
        description="""
            Purpose: Examine C=C-C=C self-matching.
            Result. Failed.
        """,
    ),
    BondMatchTestCase(
        SMILES="C1=CC=C(C(=C1)C2=C3C=CC(=O)C=C3OC4=C2C=CC(=C4)[O-])C(=O)[O-]",
        expected_matches=Counter({"Ar-OH": 1, "Ar-Ar": 1, "Ar-COOH": 1, "benzene": 3}),
        description="""
            Purpose: Corner case of Ar-Ar matching.
            Result: Expected.
        """,
    ),
    BondMatchTestCase(
        SMILES="CCN(CC)C1=CC2=C(C=C1)C(=C3C=CC(=[N+](CC)CC)C=C3O2)C4=CC=CC=C4C(=O)O",
        expected_matches=Counter({"Ar-NR2": 1, "Ar-Ar": 1, "Ar-COOH": 1, "benzene": 3}),
        description="""
            Purpose: Corner case of Ar-Ar matching.
            Result: Expected.
        """,
    ),
    BondMatchTestCase(
        SMILES="CC1=C(C(CC(C1=O)O)(C)C)C=CC(=CC=CC(=CC=CC=C(C)C=CC=C(C)C=CC2=C(C(=O)C(CC2(C)C)O)C)C)C",
        expected_matches=Counter({"C=C-C=C": 4, "C=C": 1, "C=O": 2, "cyclohexene": 2}),
        description="""
            Purpose: Examine C=C-C=C self-matching.
            Result. Failed.
        """,
    ),
    BondMatchTestCase(
        SMILES="C=CC1=C(N2C(C(C2=O)NC(=O)C(=NOCC(=O)O)C3=CSC(=N3)N)SC1)C(=O)O",
        expected_matches=Counter(
            {"C=C-C=C": 1, "RCOOH": 2, "RC(=O)NH2": 1, "C=N": 1, "thiazole": 1}
        ),
        description="""
            Purpose: Thiazole derivative example.
            Result. Failed.
        """,
    ),
    BondMatchTestCase(
        SMILES="C=CCCCC(=C)C/C=C/C(C)=C/C=C/C(C)=C/C=C/C=C(C)/C=C/C=C(C)/C=C/C=C(C)/CC/C=C(C)\C",
        expected_matches=Counter(
            {"C=C-C=C": 1, "RCOOH": 2, "RC(=O)NH2": 1, "C=N": 1, "thiazole": 1}
        ),
        description="""
            Purpose: Example encompassing C=C-C=C, C=C and  
            Result. Failed.
        """,
    ),
]
