from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BondType:
    """Class representing a relevant bond type, including its SMARTS notation, constitutive correction, and SDF file(s) of molecules containing the given bond type."""

    formula: str
    SMARTS: str
    constitutive_corr: float
    sdf_files: list[str]
    description: Optional[str] = ""
    ignore_benzene_derivatives: Optional[bool] = False


# Relevant bond types representation used in reference https://doi.org/10.1021/ed085p532
RELEVANT_BOND_TYPES: list[BondType] = [
    BondType(
        formula="C=C",
        SMARTS="[C;!$([c]);!$([C]-[c]);!$(C1=CCCCC1);!$([C;!c]=[C;!c]-[C;!c]=[C;!c]);!$([C;X3;H2]=[C;X3;H1]-[$([C;X4;H2]),$([C;X4;H3])])]=[C;!$([c]);!$([C]-[c]);!$(C1=CCCCC1);!$([C;!c]=[C;!c]-[C;!c]=[C;!c]);!$([C;X3;H2]=[C;X3;H1]-[$([C;X4;H2]),$([C;X4;H3])])]",
        constitutive_corr=5.5,
        sdf_files=["C2H4.sdf"],
        description="""
            Condition: C are NOT aromatic theirself and not bound to aryl group  - this rejects all aromatic rings that are not listed; 
            Also excluded: cyclohexene, C=C-C=C and H2C=CH-CH2- (allyl group); 
            NOTE: All exclusions must be applied for both atoms
            """,
    ),
    BondType(
        formula="C#C",
        SMARTS="[C;!$([C]-[c]);!$([C]([C])#[C]-[C](=[O])-[C])]#[C;!$([C]-[c]);!$([C]([C])#[C]-[C](=[O])-[C])]",
        constitutive_corr=0.8,
        sdf_files=["C2H2.sdf"],
        description="""
            Condition: C#C atoms are not further connected to aryl group.
            Also excluded: RC#C-C(=O)R 
        """,
    ),
    BondType(
        formula="C=C-C=C",
        SMARTS="[C;!$([c])]=[C;!$([c])]-[C;!$([c])]=[C;!$([c])]",
        constitutive_corr=10.6,
        sdf_files=["C=C-C=C.sdf"],
        description="""
            Condition: all C atoms must be aliphatic.
        """,
    ),
    BondType(
        formula="Ar-C#C-Ar",
        SMARTS="[c]-[#6;X2]#[#6;X2]-[c]",
        constitutive_corr=3.85,
        sdf_files=["Ar-C#C-Ar.sdf"],
    ),
    BondType(
        formula="CH2=CH-CH2-",
        SMARTS="[C;X3;H2]=[C;X3;H1]-[$([C;X4;H2]),$([C;X4;H3])]",
        constitutive_corr=4.5,
        sdf_files=["allyl_group.sdf"],
    ),
    BondType(
        formula="C=O",
        SMARTS="[C;X3;!$([C]-[c]);!$([C](=[O;X1])[O*]);!$([C](=[O;X1])[N*]);!$([C]([C]#[C]-[C])(=[O])[C])]=[O;X1]",
        constitutive_corr=6.3,
        sdf_files=["C=O.sdf"],
        description="""
            Condition: C cannot be bound to aryl group. Omitted additional bond to O/N in any form.
        """,
    ),
    BondType(
        formula="RCOOH",
        SMARTS="[C;X3;!$([C]-[c])](=[O;X1])[$([O;H1;X2]),$([O-;X1])]",
        constitutive_corr=-5.0,
        sdf_files=["RCOOH.sdf", "RCOO-.sdf"],
        description="""
            Note: Both RCOO- and RCOOH groups will be matched. 
            This must be noted in Software's MANUAL.
        """,
    ),
    BondType(
        formula="RCOOR",
        SMARTS="[C;X3;!$([C]-[c])](=[O;X1])[O;X2]-[C]",
        constitutive_corr=-5.0,
        sdf_files=["RCOOR.sdf"],
        description="",
    ),
    BondType(
        formula="C(=O)NH2",
        SMARTS="[C;X3;!$([C]-[c])](=[O;X1])[$([N;X3;H2]),$([N;X3;H1][C])]",
        constitutive_corr=-3.5,
        sdf_files=["RCONH2.sdf", "RCONHR.sdf"],
        description="""
            Intentional extention for considering not only RCONH2, but also RCONHR. 
            This must be noted in Software's MANUAL.    
        """,
    ),
    BondType(
        formula="N=N",
        SMARTS="[N;X2;!n]=[N;X2;!n]",
        constitutive_corr=1.85,
        sdf_files=["N=N.sdf"],
        description="""
            N are NOT aromatic - this excludes aromatic rings that are not listed. 
            Azides R-N=N(+)=N(-) were omitted. 
            This should be noted in Software's MANUAL.    
    """,
    ),
    BondType(
        formula="C=N",
        SMARTS="[C;X2,X3;!$([c])]=[N;!$([n]);!$([N](=[C]([C])[C])-[N]=[C]([C])[C])]",
        constitutive_corr=8.15,
        sdf_files=["C=N.sdf", "R2C=N-N=CRAr.sdf"],
        description="",
    ),
    BondType(
        formula="-N#C",
        SMARTS="[N+;X2]#[C-;X1]",
        constitutive_corr=0.0,
        sdf_files=["-N#C.sdf"],
        description="",
    ),
    BondType(
        formula="-C#N",
        SMARTS="[C;X2]#[N;X1]",
        constitutive_corr=0.8,
        sdf_files=["-C#N.sdf"],
        description="",
    ),
    BondType(
        formula="N=O",
        SMARTS="[N;X2;!$([N+])]=[O;X1]",
        constitutive_corr=1.7,
        sdf_files=["N=O.sdf"],
        description="",
    ),
    BondType(
        formula="-NO2",
        SMARTS="[C;!c]-[N+;X3]([O-;X1])=[O;X1]",
        constitutive_corr=-2.0,
        sdf_files=["-NO2.sdf"],
        description="",
    ),
    BondType(
        formula="C-Cl",
        SMARTS="[C;!$([c]);!$([C]([C])([C])([Cl])[Cl]);!$([C;H1]([C])([Cl])[Cl]);!$([C]([C])([C])([Cl])-[C]([C])([C])[Cl])]-[Cl]",
        constitutive_corr=3.1,
        sdf_files=["C-Cl.sdf"],
        description="",
    ),
    BondType(
        formula="Cl-CR2-CR2-Cl",
        SMARTS="[C;X4]([C])([C])([Cl])-[C;X4]([C])([C])[Cl]",
        constitutive_corr=4.3,
        sdf_files=["Cl-CR2-CR2-Cl.sdf"],
        description="",
    ),
    BondType(
        formula="R2CCl2",
        SMARTS="[C;X4]([C])([C])([Cl])[Cl]",
        constitutive_corr=1.44,
        sdf_files=["R2CCl2.sdf"],
        description="",
    ),
    BondType(
        formula="RCHCl2",
        SMARTS="[C;X4;H1]([C])([Cl])[Cl]",
        constitutive_corr=6.43,
        sdf_files=["RCHCl2.sdf"],
        description="",
    ),
    BondType(
        formula="C-Br",
        SMARTS="[C;!$([c]);!$([C]([C])([C])([Br])-[C]([C])([C])[Br])]-[Br]",
        constitutive_corr=4.1,
        sdf_files=["C-Br.sdf"],
        description="",
    ),
    BondType(
        formula="Br-CR2-CR2-Br",
        SMARTS="[C;X4]([C])([C])([Br])-[C;X4]([C])([C])[Br]",
        constitutive_corr=6.24,
        sdf_files=["Br-CR2-CR2-Br.sdf"],
        description="",
    ),
    BondType(
        formula="C-I",
        SMARTS="[C;!c]-[I]",
        constitutive_corr=4.1,
        sdf_files=["C-I.sdf"],
        description="",
    ),
    BondType(
        formula="Ar-OH",
        SMARTS="[c]-[$([O;X2;H1]),$([O-;X1])]",
        constitutive_corr=-1,
        sdf_files=["Ar-OH.sdf", "Ar-O-.sdf"],
        description="",
    ),
    BondType(
        formula="Ar-NR2",
        SMARTS="[c]-[N;X3]([C])[C]",
        constitutive_corr=1,
        sdf_files=["Ar-NR2.sdf"],
        description="",
    ),
    BondType(
        formula="Ar-C(=O)R",
        SMARTS="[c]-[C;X3](=[O;X1])[C]",
        constitutive_corr=-1.5,
        sdf_files=["Ar-COR.sdf"],
        description="",
    ),
    BondType(
        formula="Ar-COOR",
        SMARTS="[c]-[C;X3](=[O;X1])[O;X2]-[C]",
        constitutive_corr=-1.5,
        sdf_files=["Ar-COOR.sdf"],
        description="",
    ),
    BondType(
        formula="Ar-C=C",
        SMARTS="[c]-[C;X3;!c]=[C;!c]",
        constitutive_corr=-1.0,
        sdf_files=["Ar-C=C.sdf"],
        description="",
    ),
    BondType(
        formula="Ar-C#C",
        SMARTS="[c]-[C;X2]#[C;X2;!$([C]-[c])]",
        constitutive_corr=-1.5,
        sdf_files=["Ar-C#C.sdf"],
        description="",
    ),
    BondType(
        formula="Ar-OR",
        SMARTS="[c]-[O;X2][C]",
        constitutive_corr=-1,
        sdf_files=["Ar-OR.sdf"],
        description="",
    ),
    BondType(
        formula="Ar-CHO",
        SMARTS="[c]-[C;X3;H1]=[O;X1]",
        constitutive_corr=-1.5,
        sdf_files=["Ar-CHO.sdf"],
        description="",
    ),
    BondType(
        formula="Ar-Ar",
        SMARTS="[c]-[c]",
        constitutive_corr=-0.5,
        sdf_files=["Ar-Ar.sdf"],
        description="",
    ),
    BondType(
        formula="Ar-NO2",
        SMARTS="[c]-[N+;X3](=[O;X1])[O-;X1]",
        constitutive_corr=-0.5,
        sdf_files=["Ar-NO2.sdf"],
        description="",
    ),
    BondType(
        formula="Ar-Br",
        SMARTS="[c]-[Br]",
        constitutive_corr=-3.5,
        sdf_files=["Ar-Br.sdf"],
        description="",
    ),
    BondType(
        formula="Ar-Cl",
        SMARTS="[c]-[Cl]",
        constitutive_corr=-2.5,
        sdf_files=["Ar-Cl.sdf"],
        description="",
    ),
    BondType(
        formula="Ar-I",
        SMARTS="[c]-[I]",
        constitutive_corr=-3.5,
        sdf_files=["Ar-I.sdf"],
        description="",
    ),
    BondType(
        formula="Ar-COOH",
        SMARTS="[c]-[C;X3](=[O;X1])[$([O;H1;X2]),$([O-;X1])]",
        constitutive_corr=-1.5,
        sdf_files=["Ar-COOH.sdf", "Ar-COO-.sdf"],
        description="",
    ),
    BondType(
        formula="Ar-C(=O)NH2",
        SMARTS="[c]-[C;X3](=[O;X1])[$([N;X3;H2]),$([N;X3;H1][C])]",
        constitutive_corr=-1.5,
        sdf_files=["Ar-CONH2.sdf", "Ar-CONHR.sdf"],
        description="",
    ),
    BondType(
        formula="R2C=N-N=CR2",
        SMARTS="[C;X3;!c]([C])([C])=[N;X2;!n]-[N;X2;!n]=[C;X3;!c]([C])[C]",
        constitutive_corr=10.2,
        sdf_files=["R2C=N-N=CR2.sdf"],
        description="",
    ),
    BondType(
        formula="RC#C-C(=O)R",
        SMARTS="[C;X2]([C])#[C;X2]-[C;X3](=[O;X1])[C]",
        constitutive_corr=0.8,
        sdf_files=["RC#C-C(=O)R.sdf"],
        description="",
    ),
    BondType(
        formula="benzene",
        SMARTS="c1ccccc1",
        constitutive_corr=-1.4,
        sdf_files=["benzene.sdf"],
        ignore_benzene_derivatives=True,
        description="",
    ),
    BondType(
        formula="cyclobutane",
        SMARTS="C1CCC1",
        constitutive_corr=7.2,
        sdf_files=["cyclobutane.sdf"],
        description="",
    ),
    BondType(
        formula="cyclohexane",
        SMARTS="C1CCCCC1",
        constitutive_corr=3.0,
        sdf_files=["cyclohexane.sdf"],
        description="",
    ),
    BondType(
        formula="cyclohexene",
        SMARTS="C1CC=CCC1",
        constitutive_corr=6.9,
        sdf_files=["cyclohexene.sdf"],
        description="",
    ),
    BondType(
        formula="cyclopentane",
        SMARTS="C1CCCC1",
        constitutive_corr=0.0,
        sdf_files=["cyclopentane.sdf"],
        description="",
    ),
    BondType(
        formula="cyclopropane",
        SMARTS="C1CC1",
        constitutive_corr=7.2,
        sdf_files=["cyclopropane.sdf"],
        description="",
    ),
    BondType(
        formula="dioxanes",
        SMARTS="[$(O1CCCCO1),$(O1CCOCC1),$(O1CCCOC1)]",
        constitutive_corr=5.5,
        sdf_files=["1,2-dioxane.sdf", "1,3-dioxane.sdf", "1,4-dioxane.sdf"],
        description="",
    ),
    BondType(
        formula="furan",
        SMARTS="o1cccc1",
        constitutive_corr=-2.5,
        sdf_files=["furan.sdf"],
        description="",
    ),
    BondType(
        formula="imidazole",
        SMARTS="[$(n1cncc1),$([n-]1cncc1),$(n1c[n-]cc1),$([n+]1cncc1),$(n1c[n+]cc1)]",
        constitutive_corr=8.0,
        sdf_files=["imidazole.sdf", "imidazole-.sdf", "imidazole+.sdf"],
        description="",
    ),
    BondType(
        formula="isoxazole",
        SMARTS="o1nccc1",
        constitutive_corr=1.0,
        sdf_files=["isoxazole.sdf"],
        description="",
    ),
    BondType(
        formula="morpholine",
        SMARTS="[$(O1CCNCC1),$(O1NCCCC1),$(O1CNCCC1)]",
        constitutive_corr=5.5,
        sdf_files=["1,2-morpholine.sdf", "1,3-morpholine.sdf", "1,4-morpholine.sdf"],
        description="",
    ),
    BondType(
        formula="piperazine",
        SMARTS="[$(N1CCNCC1),$([N+]1CCNCC1),$([N-]1CCNCC1)]",
        constitutive_corr=7.0,
        sdf_files=["piperazine.sdf", "piperazine-.sdf", "piperazine+.sdf"],
        description="",
    ),
    BondType(
        formula="piperidine",
        SMARTS="[$(N1CCCCC1),$([N-]1CCCCC1),$([N+]1CCCCC1)]",
        constitutive_corr=3.0,
        sdf_files=["piperidine.sdf", "piperidine-.sdf", "piperidine+.sdf"],
        description="",
    ),
    BondType(
        formula="pyrazine",
        SMARTS="[$(n1ccncc1),$([n+]1ccncc1),$(n1cc[n+]cc1)]",
        constitutive_corr=9.0,
        sdf_files=["pyrazine.sdf", "pyrazine+.sdf"],
        description="",
    ),
    BondType(
        formula="pyrimidine",
        SMARTS="[$(n1cnccc1),$([n+]1cnccc1),$(n1c[n+]ccc1)]",
        constitutive_corr=6.5,
        sdf_files=["pyrimidine.sdf", "pyrimidine+.sdf"],
        description="",
    ),
    BondType(
        formula="pyridine",
        SMARTS="[$(n1ccccc1),$([n+]1ccccc1)]",
        constitutive_corr=0.5,
        sdf_files=["pyridine.sdf", "pyridine+.sdf"],
        description="",
    ),
    BondType(
        formula="pyrones",
        SMARTS="[$([#8]=[#6]1:[#6]:[#6]:[#6]:[#6]:[#8]:1),$([#8]=[#6]1:[#6]:[#6]:[#8]:[#6]:[#6]:1)]",
        constitutive_corr=-1.4,
        sdf_files=["gamma-pyrone.sdf", "alpha-pyrone.sdf"],
        description="",
    ),
    BondType(
        formula="pyrrole",
        SMARTS="[$(n1cccc1),$([n-]1cccc1)]",
        constitutive_corr=-3.5,
        sdf_files=["pyrrole.sdf", "pyrrole-.sdf"],
        description="",
    ),
    BondType(
        formula="pyrrolidine",
        SMARTS="[$(N1CCCC1),$([N+]1CCCC1),$([N-]1CCCC1)]",
        constitutive_corr=0.0,
        sdf_files=["pyrrolidine.sdf", "pyrrolidine-.sdf", "pyrrolidine+.sdf"],
        description="",
    ),
    BondType(
        formula="tetrahydrofuran",
        SMARTS="O1CCCC1",
        constitutive_corr=0.0,
        sdf_files=["tetrahydrofuran.sdf"],
        description="",
    ),
    BondType(
        formula="thiazole",
        SMARTS="[$(n1cscc1),$([n+]1cscc1)]",
        constitutive_corr=-3.0,
        sdf_files=["thiazole.sdf", "thiazole+.sdf"],
        description="",
    ),
    BondType(
        formula="thiophene",
        SMARTS="s1cccc1",
        constitutive_corr=-7.0,
        sdf_files=["thiophene.sdf"],
        description="",
    ),
    BondType(
        formula="triazine",
        SMARTS="[$(n1cncnc1),$([nH+]1cncnc1),$(n1c[nH+]cnc1),$(n1cnc[nH+]c1)]",
        constitutive_corr=-1.4,
        sdf_files=["1,3,5-triazine.sdf", "1,3,5-triazine+.sdf"],
        description="",
    ),
]
