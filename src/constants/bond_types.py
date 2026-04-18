from dataclasses import dataclass
from enum import Enum
from typing import Optional


class OverlapGroup(int, Enum):
    Ar_N_BOND_TYPES = -2
    DEFAULT = -1
    DOUBLE_BONDS = 0
    BICYCLIC_STRUCTURES = 1
    CARBONYL_BOND_TYPES = 2


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
    dummy_bond_type: Optional[bool] = False
    cross_overlap_group: Optional[OverlapGroup] = OverlapGroup.DEFAULT


DOUBLE_BOND = BondType(
    id=1,
    formula="C=C",
    SMARTS="[C;X3,X2;!$([c]);!$([C]-[c]);!$(C1=CCCCC1)]=[C;X3,X2;!$([c]);!$([C]-[c]);!$(C1=CCCCC1)]",
    constitutive_corr=5.5,
    sdf_files=("C2H4.sdf",),
    description="Condition: C atoms not bound to aryl group. Also excluded: cyclohexene, C=C-C=C and H2C=CH-CH2- (allyl group).",
    cross_overlap_group=OverlapGroup.DOUBLE_BONDS,
)

AR_NR2 = BondType(
    id=40,
    formula="Ar-NR2",
    SMARTS="[c]-[N;H2,H1,H0]([$([H]),$([#6;!$([C]=[O,S])])])[$([H]),$([#6;!$([C]=[O,S])])]",
    constitutive_corr=1,
    sdf_files=("Ar-NR2.sdf",),
    cross_overlap_group=OverlapGroup.Ar_N_BOND_TYPES,
    description="""
        Assumption: The Ar3N and Ar2NR fragments are modeled by applying three or two Ar-NR2 corrections.
        Ar-NR2 correction is also applied for Ar-NH2 Ar-NHR and Ar-NH-Ar fragments.
        For Ar-NH-Ar two Ar-NR2 corrections are applied.""",
)

CARBON_HALOGEN_BOND = BondType(
    id=-1,
    formula="C-Cl",
    SMARTS="[C;!$([c]);!$([C]([C])([C])([Cl])[Cl]);!$([C;X4;H1]([C;!$(C=O);!$(C#N)])([Cl])[Cl]);!$([C;X4]([C;!$(C#N);!$(C=O)])([C;!$(C#N);!$(C=O)])([Cl])-[C;X4]([C;!$(C#N);!$(C=O)])([C;!$(C#N);!$(C=O)])[Cl])]-[Cl;X1]",
    constitutive_corr=3.1,
    sdf_files=("C-Cl.sdf",),
    description="Excluded: R2CCl2, RCHCl2, Ar-Cl and Cl-CR2-CR2-Cl",
)

CARBON_BROMINE_BOND = BondType(
    id=-2,
    formula="C-Br",
    SMARTS="[C;!$([c]);!$([C;X4]([C;!$(C#N);!$(C=O);!$(C=N)])([C;!$(C#N);!$(C=O);!$(C=N)])([Br;X1])-[C;X4]([C;!$(C#N);!$(C=O);!$(C=N)])([C;!$(C#N);!$(C=O);!$(C=N)])[Br;X1])]-[Br;X1]",
    constitutive_corr=4.1,
    sdf_files=("C-Br.sdf",),
    description="Excluded: Ar-Br and Br-CR2-CR2-Br",
)


CARBON_TRIPLE_BOND = BondType(
    id=25,
    formula="C#C",
    SMARTS="[C;!$([C]-[c]);!$([C]([!c])#[C]-[C](=[O])-[!c;!#7;!#8;!#9;!#14;!#15;!#16;!#5;!#50])]#[C;!$([C]-[c]);!$([C]([!c])#[C]-[C](=[O])-[!c;!#7;!#8;!#9;!#14;!#15;!#16;!#5;!#50])]",
    constitutive_corr=0.8,
    sdf_files=("C2H2.sdf",),
    description="Condition: Any of C atoms in the C#C bond are not further connected to aryl group. Also excluded: RC#C-C(=O)R",
)

CARBONYL_BOND = BondType(
    id=19,
    formula="C=O",
    SMARTS="[C;X3,X2;!$([C]-[c]);!$([C]([O])([O])=[O]);!$([C]([H])(=[O])[O*]);!$([C]([C])(=[O])[O*]);!$([C](=[O;X1])[N*]);!$([C]([C]#[C]-[!c])(=[O])[!c;!#7;!#8;!#9;!#14;!#15;!#16;!#5;!#50])]=[O;X1]",
    constitutive_corr=6.3,
    sdf_files=("C=O.sdf",),
    description="Condition: C cannot be bound to aryl group. Omitted additional bond to O/N in any form.",
    cross_overlap_group=OverlapGroup.CARBONYL_BOND_TYPES,
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
        cross_overlap_group=OverlapGroup.DOUBLE_BONDS,
    ),
    BondType(
        id=3,
        formula="Ar-C=C",
        SMARTS="[c]-[C;X3;!$([c]);!$(C1=CCCCC1)]=[C;!$([c])!$(C1=CCCCC1)]",
        constitutive_corr=-1.0,
        sdf_files=("Ar-C=C.sdf",),
        cross_overlap_group=OverlapGroup.DOUBLE_BONDS,
    ),
    BondType(
        id=4,
        formula="CH2=CH-CH2-",
        SMARTS="[C;X3;H2]=[C;X3;H1]-[$([C;X4;H2]),$([C;X4;H3])]",
        constitutive_corr=4.5,
        sdf_files=("allyl_group.sdf",),
        cross_overlap_group=OverlapGroup.DOUBLE_BONDS,
    ),
    BondType(
        id=5,
        formula="cyclopentane",
        SMARTS="C1CCCC1",
        constitutive_corr=0.0,
        sdf_files=("cyclopentane.sdf",),
        cross_overlap_group=OverlapGroup.BICYCLIC_STRUCTURES,
    ),
    BondType(
        id=6,
        formula="tetrahydrofuran",
        SMARTS="O1[C;!$([C]=O)][C][C][C;!$([C]=O)]1",
        constitutive_corr=0.0,
        sdf_files=("tetrahydrofuran.sdf",),
        description="Tetrahydrofuran attached to aromatic ring via edge (polyheterocyclic system) is ignored. Analogously for all saturated rings.",
        cross_overlap_group=OverlapGroup.BICYCLIC_STRUCTURES,
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
        description="Assumption: The same constitutive correction constant was assumed for different protonation states of the molecule.",
        cross_overlap_group=OverlapGroup.BICYCLIC_STRUCTURES,
    ),
    BondType(
        id=8,
        formula="cyclohexane",
        SMARTS="C1CCCCC1",
        constitutive_corr=3.0,
        sdf_files=("cyclohexane.sdf",),
        cross_overlap_group=OverlapGroup.BICYCLIC_STRUCTURES,
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
        description="Assumption: The same constitutive correction constant was assumed for different protonation states of the molecule.",
        cross_overlap_group=OverlapGroup.BICYCLIC_STRUCTURES,
    ),
    BondType(
        id=10,
        formula="dioxane",
        SMARTS="O1[C;!$(C=O)][C;!$(C=O)]O[C;!$(C=O)][C;!$(C=O)]1",
        constitutive_corr=5.5,
        sdf_files=("1,4-dioxane.sdf",),
        cross_overlap_group=OverlapGroup.BICYCLIC_STRUCTURES,
    ),
    BondType(
        id=11,
        formula="morpholine",
        SMARTS="O1CCNCC1",
        constitutive_corr=5.5,
        sdf_files=("1,4-morpholine.sdf",),
        cross_overlap_group=OverlapGroup.BICYCLIC_STRUCTURES,
    ),
    BondType(
        id=12,
        formula="cyclohexene",
        SMARTS="C1CC=CCC1",
        constitutive_corr=6.9,
        sdf_files=("cyclohexene.sdf",),
        cross_overlap_group=OverlapGroup.BICYCLIC_STRUCTURES,
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
        description="Assumption: The same constitutive correction constant was assumed for different protonation states of the molecule.",
        cross_overlap_group=OverlapGroup.BICYCLIC_STRUCTURES,
    ),
    BondType(
        id=14,
        formula="thiacyclopropane",
        SMARTS="C1CS1",
        constitutive_corr=0,
        sdf_files=("thiacyclopropane.sdf",),
        description="Dummy ring for proper assignement of 5-membered rings within bicyclo[3.1.0] structures",
        dummy_ring=True,
        cross_overlap_group=OverlapGroup.BICYCLIC_STRUCTURES,
    ),
    BondType(
        id=15,
        formula="oxacyclopropane",
        SMARTS="C1CO1",
        constitutive_corr=0,
        sdf_files=("oxacyclopropane.sdf",),
        description="Dummy ring for proper assignement of 5-membered rings within bicyclo[3.1.0] structures",
        dummy_ring=True,
        cross_overlap_group=OverlapGroup.BICYCLIC_STRUCTURES,
    ),
    BondType(
        id=16,
        formula="azacyclopropane",
        SMARTS="C1CN1",
        constitutive_corr=0,
        sdf_files=("azacyclopropane.sdf",),
        description="Dummy ring for proper assignement of 5-membered rings within bicyclo[3.1.0] structures",
        dummy_ring=True,
        cross_overlap_group=OverlapGroup.BICYCLIC_STRUCTURES,
    ),
    BondType(
        id=17,
        formula="cyclobutane",
        SMARTS="C1CCC1",
        constitutive_corr=7.2,
        sdf_files=("cyclobutane.sdf",),
        cross_overlap_group=OverlapGroup.BICYCLIC_STRUCTURES,
    ),
    BondType(
        id=18,
        formula="cyclopropane",
        SMARTS="C1CC1",
        constitutive_corr=7.2,
        sdf_files=("cyclopropane.sdf",),
        cross_overlap_group=OverlapGroup.BICYCLIC_STRUCTURES,
    ),
    #### -----
    CARBONYL_BOND,
    BondType(
        id=20,
        formula="RCOOR",
        SMARTS="[C;X3;!$([C]-[c]);!$(C([O])[N])](=[O;X1])[O;X2;H0][#6,N,O,Si]",
        constitutive_corr=-5.0,
        sdf_files=("RCOOR.sdf",),
        description="""
            Condition: R group connected to C=O carbon must be aliphatic.
            Assumption: Along with aliphatic R groups bonded to oxygen, aryl group and N, O, or Si atoms were also permitted.""",
        cross_overlap_group=OverlapGroup.CARBONYL_BOND_TYPES,
    ),
    BondType(
        id=21,
        formula="RC(=O)NH2",
        SMARTS="[C;X3;!$([C]-[c])](=[O;X1])[$([N;X3;H2]),$([N;X3;H1][#6]),$([N;X3;H0]([#6])[#6])]",
        constitutive_corr=-3.5,
        sdf_files=(
            "RCONH2.sdf",
            "RCONHR.sdf",
            "RCONR2.sdf",
        ),
        description="Assumption: RCONH2 constitutive correction is extended to RCONHR' and RCONR'R'', where R'/R'' = aliphatic or aryl group.",
        cross_overlap_group=OverlapGroup.CARBONYL_BOND_TYPES,
    ),
    BondType(
        id=22,
        formula="Ar-COOR",
        SMARTS="[c]-[C;X3](=[O;X1])[O;X2;H0][#6,N,O,Si]",
        constitutive_corr=-1.5,
        sdf_files=("Ar-COOR.sdf",),
        description="Assumption: Along with aliphatic R groups bonded to oxygen, aryl group and N, O, or Si atoms were also permitted.",
        cross_overlap_group=OverlapGroup.CARBONYL_BOND_TYPES,
    ),
    BondType(
        id=23,
        formula="Ar-COOH",
        SMARTS="[c]-[C;X3](=[O;X1])[$([O;H1;X2]),$([O-;X1])]",
        constitutive_corr=-1.5,
        sdf_files=(
            "Ar-COOH.sdf",
            "Ar-COO-.sdf",
        ),
        description="Assumption: Aromatic carboxylate Ar-COO- intentionally included.",
        cross_overlap_group=OverlapGroup.CARBONYL_BOND_TYPES,
    ),
    BondType(
        id=24,
        formula="Ar-C(=O)NH2",
        SMARTS="[c]-[C;X3](=[O;X1])[$([N;X3;H2]),$([N;X3;H1][#6]),$([N;X3;H0]([#6])[#6])]",
        constitutive_corr=-1.5,
        sdf_files=(
            "Ar-CONH2.sdf",
            "Ar-CONHR.sdf",
            "Ar-CONR2.sdf",
        ),
        description="""Assumption: Ar-CONH2 constitutive correction is extended to Ar-CONHR and Ar-CONR2, where R = aliphatic or aryl group.""",
        cross_overlap_group=OverlapGroup.CARBONYL_BOND_TYPES,
    ),
    CARBON_TRIPLE_BOND,
    BondType(
        id=26,
        formula="RCOOH",
        # SMARTS="[C;X3;!$([C]-[c]);!$([C]([O])([O])=[O])](=[O;X1])[$([O;H1;X2]),$([O-;X1])]",
        SMARTS="[C;X3;!$([C]-[c])](=[O;X1])[$([O;H1;X2]),$([O-;X1])]",
        constitutive_corr=-5.0,
        sdf_files=(
            "RCOOH.sdf",
            "RCOO-.sdf",
        ),
        description="Assumption: The RCOOH constitutive correction was extended to the deprotonated RCOO- group.",
    ),
    BondType(
        id=27,
        formula="-N#C",
        SMARTS="[N+;X2]#[C-;X1]",
        constitutive_corr=0.0,
        sdf_files=("-N#C.sdf",),
        description="Condition: Isocyanide (isonitrile) group -N#C must be represented by the charged resonance structure.",
    ),
    BondType(
        id=28,
        formula="-C#N",
        SMARTS="[C;X2;!$([C]-[S])]#[N;X1]",
        constitutive_corr=0.8,
        sdf_files=("-C#N.sdf",),
        description="Cyanide (nitrile) -C#N group.",
    ),
    BondType(
        id=29,
        formula="N=O",
        SMARTS="[N;!$([N+](=O)[O])]=[O;X1]",
        constitutive_corr=1.7,
        sdf_files=("N=O.sdf",),
        description="""
            Nitroso group -N=O
            Condition: N with formal charge +1 not allowed. This excludes nitro -NO2 group""",
    ),
    BondType(
        id=30,
        formula="-NO2",
        SMARTS="[*;!c]-[N+;X3]([O-;X1])=[O;X1]",
        constitutive_corr=-2.0,
        sdf_files=("-NO2.sdf",),
        description="""
            Nitro -NO2 group
            Condition: N not bound to aromatic C atom.
            Excluded: Nitroso -N=O group""",
    ),
    CARBON_HALOGEN_BOND,
    BondType(
        id=32,
        formula="Cl-CR2-CR2-Cl",
        SMARTS="[C;X4]([C;!$(C#N);!$(C=O)])([C;!$(C#N);!$(C=O)])([Cl])-[C;X4]([C;!$(C#N);!$(C=O)])([C;!$(C#N);!$(C=O)])[Cl]",
        constitutive_corr=4.3,
        sdf_files=("Cl-CR2-CR2-Cl.sdf",),
        description="""
            Condition: Cl-CR2-CR2-Cl cannot share three C-C bonds with a saturated ring. 
            If so, two C-Cl constitutive corrections are applied instead.""",
    ),
    BondType(
        id=33,
        formula="R2CCl2",
        SMARTS="[C;X4]([C])([C])([Cl])[Cl]",
        constitutive_corr=1.44,
        sdf_files=("R2CCl2.sdf",),
    ),
    BondType(
        id=34,
        formula="RCHCl2",
        SMARTS="[C;X4;H1]([C;!$(C=O);!$(C#N)])([Cl])[Cl]",
        constitutive_corr=6.43,
        sdf_files=("RCHCl2.sdf",),
    ),
    CARBON_BROMINE_BOND,
    BondType(
        id=36,
        formula="Br-CR2-CR2-Br",
        SMARTS="[C;X4]([C;!$(C#N);!$(C=O);!$(C=N)])([C;!$(C#N);!$(C=O);!$(C=N)])([Br;X1])-[C;X4]([C;!$(C#N);!$(C=O);!$(C=N)])([C;!$(C#N);!$(C=O);!$(C=N)])[Br;X1]",
        constitutive_corr=6.24,
        sdf_files=("Br-CR2-CR2-Br.sdf",),
        description="""
        Condition: Br-CR2-CR2-Br cannot share three C-C bonds with a saturated ring. 
        If so, two C-Br constitutive corrections are applied instead.""",
    ),
    BondType(
        id=37,
        formula="C-I",
        SMARTS="[C;!c]-[I;X1]",
        constitutive_corr=4.1,
        sdf_files=("C-I.sdf",),
        description="Condition: C is NOT aromatic.",
    ),
    BondType(
        id=38,
        formula="C=N",
        SMARTS="[C;X2,X3;!$([c]);!$(C(=[N])=[S])]=[N;!$([n]);!$([N](=[C]([#6])[#6])-[N]=[C]([#6])[#6])]",
        constitutive_corr=8.15,
        sdf_files=("C=N.sdf",),
        description="""
            Condition: N and C are NOT aromatic - this excludes aromatic rings that are not listed in the reference.
            Also excluded: Azines R2C=N-N=CR2""",
    ),
    BondType(
        id=39,
        formula="Ar-OH",
        SMARTS="[c]-[$([O;X2;H1]),$([O-;X1])]",
        constitutive_corr=-1,
        sdf_files=(
            "Ar-OH.sdf",
            "Ar-O-.sdf",
        ),
        description="Assumption: The constitutive correction for Ar–OH was extended to phenolate (Ar-O-) group.",
    ),
    AR_NR2,
    BondType(
        id=41,
        formula="Ar-C(=O)R",
        SMARTS="[c]-[C;X3](=[O;X1])[#6]",
        constitutive_corr=-1.5,
        sdf_files=("Ar-COR.sdf",),
        description="Assumption: R = aliphatic or aryl group. For Ar-C(=O)-Ar fragment, the Ar-C(=O)R constant is taken only once.",
    ),
    BondType(
        id=42,
        formula="N=N",
        SMARTS="[N;!$(n)]=[N;!$(n)]",
        constitutive_corr=1.85,
        sdf_files=("N=N.sdf",),
        description="""
            Condition: N are NOT aromatic - this excludes aromatic rings that are not listed in the reference.
            Also excluded: Azides R-N=N(+)=N(-)""",
    ),
    BondType(
        id=43,
        formula="Ar-C#C",
        SMARTS="[c]-[C;X2]#[C;X2;!$([C]-[c])]",
        constitutive_corr=-1.5,
        sdf_files=("Ar-C#C.sdf",),
        description="Condition: Only one C atom is connected with aryl group.",
    ),
    BondType(
        id=44,
        formula="Ar-C#C-Ar",
        SMARTS="[c]-[#6;X2]#[#6;X2]-[c]",
        constitutive_corr=3.85,
        sdf_files=("Ar-C#C-Ar.sdf",),
    ),
    BondType(
        id=45,
        formula="Ar-OR",
        SMARTS="[c]-[O;X2]-[#6,N,O;!$([C]=[O])]",
        constitutive_corr=-1,
        sdf_files=("Ar-OR.sdf",),
        description="""
            Assumption: Cyclic ethers bound to aromatic C atom are also considered.
            For Ar-O-Ar fragment, Ar-OR constant is considered and applied twice.""",
    ),
    BondType(
        id=46,
        formula="Ar-CHO",
        SMARTS="[c]-[C;X3;H1]=[O;X1]",
        constitutive_corr=-1.5,
        sdf_files=("Ar-CHO.sdf",),
    ),
    BondType(
        id=47,
        formula="Ar-Ar",
        SMARTS="[c]-[c]",
        constitutive_corr=-0.5,
        sdf_files=("Ar-Ar.sdf",),
    ),
    BondType(
        id=48,
        formula="Ar-NO2",
        SMARTS="[c]-[N+;X3](=[O;X1])[O-;X1]",
        constitutive_corr=-0.5,
        sdf_files=("Ar-NO2.sdf",),
    ),
    BondType(
        id=49,
        formula="Ar-Br",
        SMARTS="[c]-[Br;X1]",
        constitutive_corr=-3.5,
        sdf_files=("Ar-Br.sdf",),
    ),
    BondType(
        id=50,
        formula="Ar-Cl",
        SMARTS="[c]-[Cl;X1]",
        constitutive_corr=-2.5,
        sdf_files=("Ar-Cl.sdf",),
    ),
    BondType(
        id=51,
        formula="Ar-I",
        SMARTS="[c]-[I;X1]",
        constitutive_corr=-3.5,
        sdf_files=("Ar-I.sdf",),
    ),
    BondType(
        id=52,
        formula="R2C=N-N=CR2",
        SMARTS="[C;X3;!c]([#6])([#6])=[N;X2;!n]-[N;X2;!n]=[C;X3;!c]([#6])[#6]",
        constitutive_corr=10.2,
        sdf_files=("R2C=N-N=CR2.sdf", "R2C=N-N=CRAr.sdf"),
        description="Azines R2C=N-N=CR2. R is assumed to represent aliphatic or aryl moiety.",
    ),
    BondType(
        id=53,
        formula="RC#C-C(=O)R",
        SMARTS="[C;X2]([!c])#[C;X2]-[C;X3](=[O;X1])[!c;!#5;!#50;!#7;!#8;!#9;!#14;!#15;!#16]",
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
        description="Assumption: The same constitutive correction constant was assumed for different protonation states of the molecule.",
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
        description="Assumption: The same constitutive correction constant was assumed for different protonation states of the molecule.",
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
            Assumption: The same constitutive correction constant was assumed for different protonation states of the molecule.""",
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
            Assumption: The same constitutive correction constant was assumed for different protonation states of the molecule.""",
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
        description="Assumption: The same constitutive correction constant was assumed for different protonation states of the molecule.",
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
        description="Assumption: The same constitutive correction constant was assumed for different protonation states of the molecule.",
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
        description="Assumption: The same constitutive correction constant was assumed for different protonation states of the molecule.",
    ),
    BondType(
        id=65,
        formula="thiophene",
        SMARTS="s1cccc1",
        constitutive_corr=-7.0,
        sdf_files=("thiophene.sdf",),
    ),
    BondType(
        id=66,
        formula="Ar-[N+]Ar3",
        SMARTS="[c]-[N]([#6;!$([C]=[O,S])])([#6;!$([C]=[O,S])])[#6;!$([C]=[O,S])]",
        constitutive_corr=0,
        sdf_files=("Ar-[N+]Ar3.sdf",),
        dummy_bond_type=True,
        cross_overlap_group=OverlapGroup.Ar_N_BOND_TYPES,
    ),
]
