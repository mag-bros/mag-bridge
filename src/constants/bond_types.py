from dataclasses import dataclass
from typing import Optional

SENIORITY_THRESHOLD = 40


@dataclass(frozen=True, slots=True)
class BondType:
    """Class representing a relevant bond type, including its SMARTS notation, constitutive correction, and SDF file(s) of molecules containing the given bond type."""

    id: int  # indexing from 1
    formula: str
    SMARTS: str
    constitutive_corr: float
    sdf_files: tuple[str, ...]
    description: Optional[str] = ""
    dummy_ring: Optional[bool] = False
    seniority: int = SENIORITY_THRESHOLD  # TODO find better name for this variable?


DOUBLE_BOND = BondType(
    id=1,
    formula="C=C",
    SMARTS="[C;!$([c]);!$([C]-[c]);!$(C1=CCCCC1)]=[C;!$([c]);!$([C]-[c]);!$(C1=CCCCC1)]",
    constitutive_corr=5.5,
    sdf_files=("C2H4.sdf",),
    description="""
            Condition: C are NOT aromatic theirself and not bound to aryl group  - this rejects all aromatic rings that are not listed; 
            Also excluded: cyclohexene, C=C-C=C and H2C=CH-CH2- (allyl group). The C atoms in C=C-C=C cannot be part of C=C-Ar bond type.
            Note: All exclusions must be applied for both atoms""",
    seniority=0,
)

# Relevant bond type representation (see reference https://doi.org/10.1021/ed085p532)
RELEVANT_BOND_TYPES: list[BondType] = [
    DOUBLE_BOND,
    BondType(
        id=2,
        formula="C=C-C=C",
        SMARTS="[C;!$([c]);!$(C1=CCCCC1)!$([C]=[C]-[c]);!$([c]-[C]=[C])]=[C;!$([c]);!$(C1=CCCCC1)!$([C]=[C]-[c]);!$([c]-[C]=[C])]-[C;!$([c]);!$(C1=CCCCC1)!$([C]=[C]-[c]);!$([c]-[C]=[C])]=[C;!$([c]);!$(C1=CCCCC1)!$([C]=[C]-[c]);!$([c]-[C]=[C])]",
        constitutive_corr=10.6,
        sdf_files=("C=C-C=C.sdf",),
        description="Condition: all C atoms must be aliphatic.",
        seniority=10,
    ),
    BondType(
        id=3,
        formula="Ar-C=C",
        SMARTS="[c]-[C;X3;!$([c]);!$(C1=CCCCC1)]=[C;!$([c])!$(C1=CCCCC1)]",
        constitutive_corr=-1.0,
        sdf_files=("Ar-C=C.sdf",),
        seniority=20,
    ),
    BondType(
        id=4,
        formula="CH2=CH-CH2-",
        SMARTS="[C;X3;H2]=[C;X3;H1]-[$([C;X4;H2]),$([C;X4;H3])]",
        constitutive_corr=4.5,
        sdf_files=("allyl_group.sdf",),
        seniority=30,
    ),
    BondType(
        id=5,
        formula="cyclopentane",
        SMARTS="C1CCCC1",
        constitutive_corr=0.0,
        sdf_files=("cyclopentane.sdf",),
        seniority=42,
    ),
    BondType(
        id=6,
        formula="tetrahydrofuran",
        SMARTS="O1[C;!$([C]=O)][C][C][C;!$([C]=O)]1",
        constitutive_corr=0.0,
        sdf_files=("tetrahydrofuran.sdf",),
        description="Tetrahydrofuran attached to aromatic ring via edge (polyheterocyclic system) is ignored.",
        seniority=45,
    ),
    BondType(
        id=7,
        formula="pyrrolidine",
        SMARTS="N1[C;!$(C=O)]CC[C;!$(C=O)]1",
        constitutive_corr=0.0,
        sdf_files=(
            "pyrrolidine.sdf",
            "pyrrolidine-.sdf",
            "pyrrolidine+.sdf",
        ),
        description="""
            Note: The same constitutive correction constant was assumed for different protonation states of the molecule.
            This must be stated in MANUAL""",
        seniority=48,
    ),
    BondType(
        id=8,
        formula="cyclohexane",
        SMARTS="C1CCCCC1",
        constitutive_corr=3.0,
        sdf_files=("cyclohexane.sdf",),
        seniority=51,
    ),
    BondType(
        id=9,
        formula="piperidine",
        SMARTS="N1[C;!$(C=O)]CCC[C;!$(C=O)]1",
        constitutive_corr=3.0,
        sdf_files=(
            "piperidine.sdf",
            "piperidine-.sdf",
            "piperidine+.sdf",
        ),
        description="""
            Note: The same constitutive correction constant was assumed for different protonation states of the molecule.
            This must be stated in MANUAL""",
        seniority=54,
    ),
    BondType(
        id=10,
        formula="dioxane",
        SMARTS="O1CCOCC1",
        constitutive_corr=5.5,
        sdf_files=("1,4-dioxane.sdf",),
        seniority=57,
    ),
    BondType(
        id=11,
        formula="morpholine",
        SMARTS="O1CCNCC1",
        constitutive_corr=5.5,
        sdf_files=("1,4-morpholine.sdf",),
        seniority=60,
    ),
    BondType(
        id=12,
        formula="cyclohexene",
        SMARTS="C1CC=CCC1",
        constitutive_corr=6.9,
        sdf_files=("cyclohexene.sdf",),
        seniority=63,
    ),
    BondType(
        id=13,
        formula="piperazine",
        SMARTS="N1CCNCC1",
        constitutive_corr=7.0,
        sdf_files=(
            "piperazine.sdf",
            "piperazine-.sdf",
            "piperazine+.sdf",
        ),
        description="""
            Note: The same constitutive correction constant was assumed for different protonation states of the molecule.
            This must be stated in MANUAL""",
        seniority=66,
    ),
    BondType(
        id=14,
        formula="thiacyclopropane",
        SMARTS="C1CS1",
        constitutive_corr=0,
        sdf_files=("thiacyclopropane.sdf",),
        description="Dummy ring for proper assignement of 5-membered rings within bicyclo[3.1.0] structures",
        seniority=88,
        dummy_ring=True,
    ),
    BondType(
        id=15,
        formula="oxacyclopropane",
        SMARTS="C1CO1",
        constitutive_corr=0,
        sdf_files=("oxacyclopropane.sdf",),
        description="Dummy ring for proper assignement of 5-membered rings within bicyclo[3.1.0] structures",
        seniority=89,
        dummy_ring=True,
    ),
    BondType(
        id=16,
        formula="azacyclopropane",
        SMARTS="C1CN1",
        constitutive_corr=0,
        sdf_files=("azacyclopropane.sdf",),
        description="Dummy ring for proper assignement of 5-membered rings within bicyclo[3.1.0] structures",
        seniority=90,
        dummy_ring=True,
    ),
    BondType(
        id=17,
        formula="cyclobutane",
        SMARTS="C1CCC1",
        constitutive_corr=7.2,
        sdf_files=("cyclobutane.sdf",),
        seniority=95,
    ),
    # TODO: RCONH2 can overlap only by N atom but not carbonyl C=O fragment
    BondType(
        id=18,
        formula="cyclopropane",
        SMARTS="C1CC1",
        constitutive_corr=7.2,
        sdf_files=("cyclopropane.sdf",),
        seniority=99,
    ),
    BondType(
        id=19,
        formula="C#C",
        SMARTS="[C;!$([C]-[c]);!$([C]([C])#[C]-[C](=[O])-[C])]#[C;!$([C]-[c]);!$([C]([C])#[C]-[C](=[O])-[C])]",
        constitutive_corr=0.8,
        sdf_files=("C2H2.sdf",),
        description="""
            Condition: C#C atoms are not further connected to aryl group.
            Also excluded: RC#C-C(=O)R""",
    ),
    BondType(
        id=20,
        formula="C=O",
        SMARTS="[C;X3;!$([C]-[c]);!$([C]([H])(=[O])[O*]);!$([C]([C])(=[O])[O*]);!$([C](=[O;X1])[N*]);!$([C]([C]#[C]-[C])(=[O])[C])]=[O;X1]",
        constitutive_corr=6.3,
        sdf_files=("C=O.sdf",),
        description="Condition: C cannot be bound to aryl group. Omitted additional bond to O/N in any form. C=O can be assigned as part of thioester RC(=O)SR.",
    ),
    BondType(
        id=21,
        formula="RCOOH",
        SMARTS="[C;X3;!$([C]-[c]);!$([C]([O])([O])=[O])](=[O;X1])[$([O;H1;X2]),$([O-;X1])]",
        constitutive_corr=-5.0,
        sdf_files=(
            "RCOOH.sdf",
            "RCOO-.sdf",
        ),
        description="""
            Note: Both RCOO- and RCOOH groups will be matched. 
            This must be noted in Software's MANUAL.""",
    ),
    BondType(
        id=22,
        formula="-N#C",
        SMARTS="[N+;X2]#[C-;X1]",
        constitutive_corr=0.0,
        sdf_files=("-N#C.sdf",),
        description="Condition: Isocyanide (isonitrile) group -N#C must be represented by the charged resonance structure",
    ),
    BondType(
        id=23,
        formula="-C#N",
        SMARTS="[C;X2]#[N;X1]",
        constitutive_corr=0.8,
        sdf_files=("-C#N.sdf",),
        description="Cyanide (nitrile) -C#N group",
    ),
    BondType(
        id=24,
        formula="N=O",
        SMARTS="[N;!$([N+])]=[O;X1]",
        constitutive_corr=1.7,
        sdf_files=("N=O.sdf",),
        description="""
            Nitroso group -N=O
            Condition: N with formal charge +1 not allowed. This excludes nitro -NO2 group""",
    ),
    BondType(
        id=25,
        formula="-NO2",
        SMARTS="[*;!c]-[N+;X3]([O-;X1])=[O;X1]",
        constitutive_corr=-2.0,
        sdf_files=("-NO2.sdf",),
        description="""
            Nitro -NO2 group
            Condition: N not bound to aromatic C atom.
            Excluded: Nitroso -N=O group""",
    ),
    BondType(
        id=26,
        formula="C-Cl",
        SMARTS="[C;!$([c]);!$([C]([C])([C])([Cl])[Cl]);!$([C;H1]([C])([Cl])[Cl]);!$([C]([C])([C])([Cl])-[C]([C])([C])[Cl])]-[Cl]",
        constitutive_corr=3.1,
        sdf_files=("C-Cl.sdf",),
        description="Excluded: R2CCl2, RCHCl2, Ar-Cl and Cl-CR2-CR2-Cl",
    ),
    BondType(
        id=27,
        formula="Cl-CR2-CR2-Cl",
        SMARTS="[C;X4]([C])([C])([Cl])-[C;X4]([C])([C])[Cl]",
        constitutive_corr=4.3,
        sdf_files=("Cl-CR2-CR2-Cl.sdf",),
    ),
    BondType(
        id=28,
        formula="R2CCl2",
        SMARTS="[C;X4]([C])([C])([Cl])[Cl]",
        constitutive_corr=1.44,
        sdf_files=("R2CCl2.sdf",),
    ),
    BondType(
        id=29,
        formula="RCHCl2",
        SMARTS="[C;X4;H1]([C])([Cl])[Cl]",
        constitutive_corr=6.43,
        sdf_files=("RCHCl2.sdf",),
    ),
    BondType(
        id=30,
        formula="C-Br",
        SMARTS="[C;!$([c]);!$([C]([C])([C])([Br])-[C]([C])([C])[Br])]-[Br]",
        constitutive_corr=4.1,
        sdf_files=("C-Br.sdf",),
        description="Excluded: Ar-Br and Br-CR2-CR2-Br",
    ),
    BondType(
        id=31,
        formula="Br-CR2-CR2-Br",
        SMARTS="[C;X4]([C])([C])([Br])-[C;X4]([C])([C])[Br]",
        constitutive_corr=6.24,
        sdf_files=("Br-CR2-CR2-Br.sdf",),
    ),
    BondType(
        id=32,
        formula="C-I",
        SMARTS="[C;!c]-[I]",
        constitutive_corr=4.1,
        sdf_files=("C-I.sdf",),
        description="Condition: C is NOT aromatic.",
    ),
    BondType(
        id=33,
        formula="RCOOR",
        SMARTS="[C;X3;!$([C]-[c]);!$(C([O])[N])](=[O;X1])[O;X2]-[C]",
        constitutive_corr=-5.0,
        sdf_files=("RCOOR.sdf",),
        description="R = aliphatic group",
    ),
    BondType(
        id=34,
        formula="RC(=O)NH2",
        SMARTS="[C;X3;!$([C]-[c])](=[O;X1])[$([N;X3;H2]),$([N;X3;H1][C]),$([N;X3;H0]([C])[C])]",
        constitutive_corr=-3.5,
        sdf_files=(
            "RCONH2.sdf",
            "RCONHR.sdf",
            "RCONR2.sdf",
        ),
        description="""
            Note: Intentional extention for considering not only RCONH2, but also RCONHR. 
            Eexcluded: RNHC(=O)OR group - for this motif only C(=O)OR but not RNHC(=O) fragment will be assigned due to higher constitutive corr value of the former.
            This must be noted in Software's MANUAL.""",
    ),
    BondType(
        id=35,
        formula="C=N",
        SMARTS="[C;X2,X3;!$([c]);!$(C(=[N])=[S])]=[N;!$([n]);!$([N](=[C]([C])[C])-[N]=[C]([C])[C])]",
        constitutive_corr=8.15,
        sdf_files=(
            "C=N.sdf",
            "R2C=N-N=CRAr.sdf",
        ),
        description="""
            Condition: N and C are NOT aromatic - this excludes aromatic rings that are not listed in the reference.
            Also excluded: Azines R2C=N-N=CR2""",
    ),
    BondType(
        id=36,
        formula="Ar-OH",
        SMARTS="[c]-[$([O;X2;H1]),$([O-;X1])]",
        constitutive_corr=-1,
        sdf_files=(
            "Ar-OH.sdf",
            "Ar-O-.sdf",
        ),
        description="""
            Note: Phenolate Ar-O- intentionally included.
            This must be stated in the MANUAL.""",
    ),
    BondType(
        id=37,
        formula="Ar-NR2",
        SMARTS="[c]-[N;X3]([C;!$([C]=[O,S])])[C;!$([C]=[O,S])]",
        constitutive_corr=1,
        sdf_files=("Ar-NR2.sdf",),
    ),
    BondType(
        id=38,
        formula="Ar-C(=O)R",  ## NOT unique atoms
        SMARTS="[c]-[C;X3](=[O;X1])[C]",
        constitutive_corr=-1.5,
        sdf_files=("Ar-COR.sdf",),
    ),
    BondType(
        id=39,
        formula="Ar-COOR",
        SMARTS="[c]-[C;X3](=[O;X1])[O;X2]-[C]",
        constitutive_corr=-1.5,
        sdf_files=("Ar-COOR.sdf",),
    ),
    BondType(
        id=40,
        formula="N=N",
        SMARTS="[N;X2;!n]=[N;X2;!n]",
        constitutive_corr=1.85,
        sdf_files=("N=N.sdf",),
        description="""
            Condition: N are NOT aromatic - this excludes aromatic rings that are not listed in the reference 
            Also excluded: Azides R-N=N(+)=N(-)    
            This should be noted in Software's MANUAL.""",
    ),
    BondType(
        id=41,
        formula="Ar-C#C",
        SMARTS="[c]-[C;X2]#[C;X2;!$([C]-[c])]",
        constitutive_corr=-1.5,
        sdf_files=("Ar-C#C.sdf",),
        description="Condition: Only one C atom is connected with aryl group.",
    ),
    BondType(
        id=42,
        formula="Ar-C#C-Ar",
        SMARTS="[c]-[#6;X2]#[#6;X2]-[c]",
        constitutive_corr=3.85,
        sdf_files=("Ar-C#C-Ar.sdf",),
    ),
    BondType(
        id=43,
        formula="Ar-OR",  # NOT unique atoms
        SMARTS="[c]-[O;X2][C;!$([C]=[O])]",
        constitutive_corr=-1,
        sdf_files=("Ar-OR.sdf",),
        description="Cyclic ethers bound to aromatic C atom are also considered",
    ),
    BondType(
        id=44,
        formula="Ar-CHO",
        SMARTS="[c]-[C;X3;H1]=[O;X1]",
        constitutive_corr=-1.5,
        sdf_files=("Ar-CHO.sdf",),
    ),
    BondType(
        id=45,
        formula="Ar-Ar",
        SMARTS="[c]-[c]",
        constitutive_corr=-0.5,
        sdf_files=("Ar-Ar.sdf",),
    ),
    BondType(
        id=46,
        formula="Ar-NO2",
        SMARTS="[c]-[N+;X3](=[O;X1])[O-;X1]",
        constitutive_corr=-0.5,
        sdf_files=("Ar-NO2.sdf",),
    ),
    BondType(
        id=47,
        formula="Ar-Br",
        SMARTS="[c]-[Br]",
        constitutive_corr=-3.5,
        sdf_files=("Ar-Br.sdf",),
    ),
    BondType(
        id=48,
        formula="Ar-Cl",
        SMARTS="[c]-[Cl]",
        constitutive_corr=-2.5,
        sdf_files=("Ar-Cl.sdf",),
    ),
    BondType(
        id=49,
        formula="Ar-I",
        SMARTS="[c]-[I]",
        constitutive_corr=-3.5,
        sdf_files=("Ar-I.sdf",),
    ),
    BondType(
        id=50,
        formula="Ar-COOH",
        SMARTS="[c]-[C;X3](=[O;X1])[$([O;H1;X2]),$([O-;X1])]",
        constitutive_corr=-1.5,
        sdf_files=(
            "Ar-COOH.sdf",
            "Ar-COO-.sdf",
        ),
        description="""
            Note: Aromatic carboxylate Ar-COO- intentionally included.
            This must be stated in MANUAL.""",
    ),
    BondType(
        id=51,
        formula="Ar-C(=O)NH2",
        SMARTS="[c]-[C;X3](=[O;X1])[$([N;X3;H2]),$([N;X3;H1][C]),$([N;X3;H0]([C])[C])]",
        constitutive_corr=-1.5,
        sdf_files=(
            "Ar-CONH2.sdf",
            "Ar-CONHR.sdf",
            "Ar-CONR2.sdf",
        ),
        description="""
            Note: Intentional extention for considering not only ArCONH2, but also Ar-CONHR and Ar-CONR2. 
            This must be noted in Software's MANUAL.""",
    ),
    BondType(
        id=52,
        formula="R2C=N-N=CR2",
        SMARTS="[C;X3;!c]([C])([C])=[N;X2;!n]-[N;X2;!n]=[C;X3;!c]([C])[C]",
        constitutive_corr=10.2,
        sdf_files=("R2C=N-N=CR2.sdf",),
        description="Azines R2C=N-N=CR2",
    ),
    BondType(
        id=53,
        formula="RC#C-C(=O)R",
        SMARTS="[C;X2]([C])#[C;X2]-[C;X3](=[O;X1])[C]",
        constitutive_corr=0.8,
        sdf_files=("RC#C-C(=O)R.sdf",),
    ),
    BondType(
        id=54,
        formula="benzene",
        SMARTS="c1ccccc1",
        constitutive_corr=-1.4,
        sdf_files=("benzene.sdf",),
    ),
    BondType(
        id=55,
        formula="furan",
        SMARTS="o1cccc1",
        constitutive_corr=-2.5,
        sdf_files=("furan.sdf",),
    ),
    BondType(
        id=56,
        formula="imidazole",
        SMARTS="n1cncc1",
        constitutive_corr=8.0,
        sdf_files=(
            "imidazole.sdf",
            "imidazole-.sdf",
            "imidazole+.sdf",
        ),
        description="""
            Note: The same constitutive correction constant was assumed for different protonation states of the molecule.
            This must be stated in MANUAL""",
    ),
    BondType(
        id=57,
        formula="isoxazole",
        SMARTS="o1nccc1",
        constitutive_corr=1.0,
        sdf_files=("isoxazole.sdf",),
    ),
    BondType(
        id=58,
        formula="pyrazine",
        SMARTS="n1ccncc1",
        constitutive_corr=9.0,
        sdf_files=(
            "pyrazine.sdf",
            "pyrazine+.sdf",
        ),
        description="""
            Note: The same constitutive correction constant was assumed for different protonation states of the molecule.
            This must be stated in MANUAL""",
    ),
    BondType(
        id=59,
        formula="pyrimidine",
        SMARTS="[n]1[c;!$(c=O)][n][c;!$(c=O)][c;!$(c=O)][c;!$(c=O)]1",
        constitutive_corr=6.5,
        sdf_files=(
            "pyrimidine.sdf",
            "pyrimidine+.sdf",
        ),
        description="""
            Excluded: pyrimidinone rings (C atoms in pyrimidine ring cannot form C=O bond)
            Note: The same constitutive correction constant was assumed for different protonation states of the molecule.
            This must be stated in MANUAL""",
    ),
    BondType(
        id=60,
        formula="pyridine",
        SMARTS="n1[c;!$([c]=[O])][c;!$([c]=[O])][c;!$([c]=[O])][c;!$([c]=[O])][c;!$([c]=[O])]1",
        constitutive_corr=0.5,
        sdf_files=(
            "pyridine.sdf",
            "pyridine+.sdf",
        ),
        description="""
            Condition: Aromatic C atoms cannot be a part of C=O group.
            Note: The same constitutive correction constant was assumed for different protonation states of the molecule.
            This must be stated in MANUAL""",
    ),
    BondType(
        formula="pyrones",
        id=61,
        SMARTS="[$([#8]=[#6]1:[#6]:[#6]:[#6]:[#6]:[#8]:1),$([#8]=[#6]1:[#6]:[#6]:[#8]:[#6]:[#6]:1)]",
        constitutive_corr=-1.4,
        sdf_files=(
            "gamma-pyrone.sdf",
            "alpha-pyrone.sdf",
        ),
    ),
    BondType(
        id=62,
        formula="pyrrole",
        SMARTS="n1cccc1",
        constitutive_corr=-3.5,
        sdf_files=(
            "pyrrole.sdf",
            "pyrrole-.sdf",
        ),
        description="""
            Note: The same constitutive correction constant was assumed for different protonation states of the molecule.
            This must be stated in MANUAL""",
    ),
    BondType(
        id=63,
        formula="triazine",
        SMARTS="n1cncnc1",
        constitutive_corr=-1.4,
        sdf_files=(
            "1,3,5-triazine.sdf",
            "1,3,5-triazine+.sdf",
        ),
        description="""
            Note: The same constitutive correction constant was assumed for different protonation states of the molecule.
            This must be stated in MANUAL""",
    ),
    BondType(
        id=64,
        formula="thiazole",
        SMARTS="n1cscc1",
        constitutive_corr=-3.0,
        sdf_files=(
            "thiazole.sdf",
            "thiazole+.sdf",
        ),
        description="""
            Note: The same constitutive correction constant was assumed for different protonation states of the molecule.
            This must be stated in MANUAL""",
    ),
    BondType(
        id=65,
        formula="thiophene",
        SMARTS="s1cccc1",
        constitutive_corr=-7.0,
        sdf_files=("thiophene.sdf",),
    ),
]
