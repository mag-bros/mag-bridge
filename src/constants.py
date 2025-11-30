from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.atom import MBAtom
    from src.core.molecule import MBMolecule


class ConstProvider:
    @staticmethod
    def GetPascalValues(atom: "MBAtom") -> dict[str, float]:
        """Looks up relevant Pascal Constant data for given atom."""
        covalent = PASCAL_CONST.get(atom.symbol, {}).get("covalent", {})
        ionic = PASCAL_CONST.get(atom.symbol, {}).get("ionic", {})

        values = {
            "open_chain": covalent.get("open_chain"),
            "ring": covalent.get("ring"),
            "ox_state": covalent.get("ox_state", {}).get(atom.ox_state),
            "charge": ionic.get("charge", {}).get(atom.charge),
        }

        # Remove keys that are not present. Missing key means that no data was found for given atom.
        return {k: v for k, v in values.items() if v is not None}

    @staticmethod
    def GetRelevantRingAtoms() -> list[str]:
        return RELEVANT_RING_ATOMS

    @staticmethod
    def GetRelevantOxidationAtoms() -> list[str]:
        return RELEVANT_OXIDATION_ATOMS

    @staticmethod
    def GetCommonMolDiamagContr(mol: "MBMolecule") -> float:
        """Returns diamag contribution of common molecules."""

        # TODO: Finish.
        return ...


"""
unit: 10^(-6) cm^3/mol
Reference (DOI): 10.1021/ed085p532 (TABLE 5)
This dictionary represents the diamagnetic susceptibilities for common molecules (solvents, anions and ligands).

@note1: Only canonical SMILES are provided, which were generated using RDKit Chem.MolToSmiles(). 
The same RDKit function was utilized to generate SMILES from SDF. In this way, unambiguous comparison between SMILES from SDF and the dictionary is possible.
@note2: For aromatic molecules, one of the resonance structures should be provided in an input SDF file. 
Hybrid structures with shown aromaticity are prone to failure and should be used with caution by the users.
@note3: Thiosulfate (S2O32-) is an important exception, with two canonical SMILES related to different bonding of terminal sulphur atom in resonance structures.
@note4: RDKit does not support SMILES with double bonds for hypervalent halogen oxoanions. 
As a result, the generated SMILES for BrO3-, ClO3-, ClO4-, IO3- and IO4- anions do not reflect their correct structures.
@note5: For BF4- anion, the negative charge must be located on the boron atom. Otherwise SDF fails to parse. 
@note6: In the reference (Table 3), PO4(3-) anion was incorrectly written as PO3(3-).
@note7: PtCl6(2-) (Table 3 in the reference) was intentionally omited in the dictionary.
@note8: Our software does not support stereochemical structures.
@note9: carbonyl (CO) ligand must be drawn with (+) charge located on C and (-) on O. Otherwise, SDF fails to parse.

Here's a breakdown of the values:
"""

COMMON_MOLECULES = {
    # COMMON ANIONS
    "anions": {
        "AsO3(3-)": {
            "name": "arsenate(III)",
            "SMILES": {"[O-][As]([O-])[O-]"},
            "diamag_sus": -51,
            "sdf_file": "AsO33-.sdf",
        },
        "AsO4(3-)": {
            "name": "arsenate(V)",
            "SMILES": {"O=[As]([O-])([O-])[O-]"},
            "diamag_sus": -60,
            "sdf_file": "AsO43-.sdf",
        },
        "BF4(-)": {
            "name": "tetrafluoroborate",
            "SMILES": {"F[B-](F)(F)F"},
            "diamag_sus": -37,
            "sdf_file": "BF4-.sdf",
        },
        "BO3(3-)": {
            "name": "borate",
            "SMILES": {"[O-]B([O-])[O-]"},
            "diamag_sus": -35,
            "sdf_file": "BO33-.sdf",
        },
        "BrO3(-)": {
            "name": "bromate(V)",
            "SMILES": {"[O-][Br+2]([O-])[O-]"},
            "diamag_sus": -40,
            "sdf_file": "BrO3-.sdf",
        },
        "ClO3(-)": {
            "name": "chlorate(V)",
            "SMILES": {"[O-][Cl+2]([O-])[O-]"},
            "diamag_sus": -30.2,
            "sdf_file": "ClO3-.sdf",
        },
        "ClO4(-)": {
            "name": "chlorate(VII)",
            "SMILES": {"[O-][Cl+3]([O-])([O-])[O-]"},
            "diamag_sus": -32.0,
            "sdf_file": "ClO4-.sdf",
        },
        "CN(-)": {
            "name": "cyanide",
            "SMILES": {"[C-]#N"},
            "diamag_sus": -13.0,
            "sdf_file": "CN-.sdf",
        },
        "C5H5(-)": {
            "name": "cyclopentadienyl",
            "SMILES": {"c1cc[cH-]c1"},
            "diamag_sus": -65,
            "sdf_file": "C5H5-.sdf",
        },
        "C6H5COO(-)": {
            "name": "benzoate",
            "SMILES": {"O=C([O-])c1ccccc1"},
            "diamag_sus": -71,
            "sdf_file": "C6H5COO-.sdf",
        },
        "CO3(2-)": {
            "name": "carbonate",
            "SMILES": {"O=C([O-])[O-]"},
            "diamag_sus": -28.0,
            "sdf_file": "CO32-.sdf",
        },
        "C2O4(2-)": {
            "name": "oxalate",
            "SMILES": {"O=C([O-])C(=O)[O-]"},
            "diamag_sus": -34,
            "sdf_file": "C2O42-.sdf",
        },
        "HCOO(-)": {
            "name": "formate",
            "SMILES": {"O=C[O-]"},
            "diamag_sus": -17,
            "sdf_file": "HCOO-.sdf",
        },
        "IO3(-)": {
            "name": "iodate(V)",
            "SMILES": {"[O-][I+2]([O-])[O-]"},
            "diamag_sus": -51,
            "sdf_file": "IO3-.sdf",
        },
        "IO4(-)": {
            "name": "iodate(VII)",
            "SMILES": {"[O-][I+3]([O-])([O-])[O-]"},
            "diamag_sus": -51.9,
            "sdf_file": "IO4-.sdf",
        },
        "NO2(-)": {
            "name": "nitrate(III)",
            "SMILES": {"O=N[O-]"},
            "diamag_sus": -10.0,
            "sdf_file": "NO2-.sdf",
        },
        "NO3(-)": {
            "name": "nitrate(V)",
            "SMILES": {"O=[N+]([O-])[O-]"},
            "diamag_sus": -18.9,
            "sdf_file": "NO3-.sdf",
        },
        "NCO(-)": {
            "name": "cyanate",
            "SMILES": {"N#C[O-]"},
            "diamag_sus": -23,
            "sdf_file": "NCO-.sdf",
        },
        "NCS(-)": {
            "name": "thiocyanate",
            "SMILES": {"N#C[S-]"},
            "diamag_sus": -31.0,
            "sdf_file": "NCS-.sdf",
        },
        "OAc(-)": {
            "name": "acetate",
            "SMILES": {"CC(=O)[O-]"},
            "diamag_sus": -31.5,
            "sdf_file": "AcO-.sdf",  # TODO: is this file correct?
        },
        "OH(-)": {
            "name": "hydroxide",
            "SMILES": {"[OH-]"},
            "diamag_sus": -12.0,
            "sdf_file": "OH-.sdf",
        },
        "PO4(3-)": {  # In Table 3 in 10.1021/ed085p532 Authors provided incorrect formula, PO3(3-) instead of PO4(3-). EXPLANATION: 1. Phosphite exists as HPO3(2-) anion; 2. The diamag value in the article corresponds to phosphate (PO43-) anion (see: 10.1246/bcsj.66.371)
            "name": "phosphate",
            "SMILES": {"O=P([O-])([O-])[O-]"},
            "diamag_sus": -42,
            "sdf_file": "PO43-.sdf",
        },
        "SO3(2-)": {
            "name": "sulfate(IV)",
            "SMILES": {"O=S([O-])[O-]"},
            "diamag_sus": -38,
            "sdf_file": "SO32-.sdf",
        },
        "SO4(2-)": {
            "name": "sulfate(VI)",
            "SMILES": {"O=S(=O)([O-])[O-]"},
            "diamag_sus": -40.1,
            "sdf_file": "SO42-.sdf",
        },
        "S2O3(2-)": {
            "name": "thiosulfate",
            "SMILES": {  # Two canonical SMILES of this anion exist.
                "O=S([O-])([O-])=S",
                "O=S(=O)([O-])[S-]",
            },
            "diamag_sus": -46,
            "sdf_file": "S2O32-.sdf",
        },
        "S2O8(2-)": {
            "name": "peroxydisulfate",
            "SMILES": {"O=S(=O)([O-])OOS(=O)(=O)[O-]"},
            "diamag_sus": -78,
            "sdf_file": "S2O82-.sdf",
        },
        "HSO4(-)": {
            "name": "bisulfate",
            "SMILES": {"O=S(=O)([O-])O"},
            "diamag_sus": -35.0,
            "sdf_file": "HSO4-.sdf",
        },
        "SeO3(2-)": {
            "name": "selenite",
            "SMILES": {"O=[Se]([O-])[O-]"},
            "diamag_sus": -44,
            "sdf_file": "SeO32-.sdf",
        },
        "SeO4(2-)": {
            "name": "selenate",
            "SMILES": {"O=[Se](=O)([O-])[O-]"},
            "diamag_sus": -51,
            "sdf_file": "SeO42-.sdf",
        },
        "SiO3(2-)": {
            "name": "silicate",
            "SMILES": {
                "O=[Si]([O-])[O-]"
            },  # the double bond in this SMILES is a simplification of the actual [(SiO3)n]m- structure.
            "diamag_sus": -36,
            "sdf_file": "SiO32-.sdf",
        },
        "TeO3(2-)": {
            "name": "tellurite",
            "SMILES": {"O=[Te]([O-])[O-]"},
            "diamag_sus": -63,
            "sdf_file": "TeO32-.sdf",
        },
        "TeO4(2-)": {
            "name": "tellurate",
            "SMILES": {"O=[Te](=O)([O-])[O-]"},
            "diamag_sus": -55,
            "sdf_file": "TeO42-.sdf",
        },
    },
    # COMMON LIGANDS
    "ligands": {
        "acac-": {
            "name": "acetylacetonate",
            "SMILES": {"CC(=O)C=C(C)[O-]"},
            "diamag_sus": -52,
            "sdf_file": "acac-.sdf",
        },
        "bipy": {
            "name": "2,2′-bipyridine",
            "SMILES": {"c1ccc(-c2ccccn2)nc1"},
            "diamag_sus": -105,
            "sdf_file": "bipy.sdf",
        },
        "CO": {
            "name": "carbonyl",
            "SMILES": {"[C-]#[O+]"},
            "diamag_sus": -10,
            "sdf_file": "CO.sdf",
        },
        "en": {
            "name": "ethylenediamine",
            "SMILES": {"NCCN"},
            "diamag_sus": -46.5,
            "sdf_file": "en.sdf",
        },
        "C2H4": {
            "name": "ethylene",
            "SMILES": {"C=C"},
            "diamag_sus": -15,
            "sdf_file": "ethylene.sdf",
        },
        "gly": {
            "name": "glycinate",
            "SMILES": {"NCC(=O)[O-]"},
            "diamag_sus": -37,
            "sdf_file": "glycinate.sdf",  # TODO: is this file correct?
        },
        "H2O": {
            "name": "glycinate",
            "SMILES": {"O"},
            "diamag_sus": -13,
            "sdf_file": "",  # TODO: i couldnt find this file
        },
        "H2N-NH2": {
            "name": "hydrazine",
            "SMILES": {"NN"},
            "diamag_sus": -20,
            "sdf_file": "hydrazine.sdf",
        },
        "mal": {
            "name": "malonate",
            "SMILES": {"O=C([O-])CC(=O)[O-]"},
            "diamag_sus": -45,
            "sdf_file": "malonate.sdf",
        },
        "NH3": {
            "name": "ammonia",
            "SMILES": {"N"},
            "diamag_sus": -18,
            "sdf_file": "",  # TODO: couldnt find
        },
        "phen": {
            "name": "phenanthroline",
            "SMILES": {"c1cnc2c(c1)ccc1cccnc12"},
            "diamag_sus": -128,
            "sdf_file": "phen.sdf",
        },
        "o-PBMA": {
            "name": "o-phenylenebisdimethylarsine",
            "SMILES": {"C[As](C)c1ccccc1[As](C)C"},
            "diamag_sus": -194,
            "sdf_file": "o-PBMA.sdf",
        },
        "H2Pc": {
            "name": "phthalocyanine",
            "SMILES": {
                "c1ccc2c(c1)-c1nc-2nc2[nH]c(nc3nc(nc4[nH]c(n1)c1ccccc41)-c1ccccc1-3)c1ccccc21"
            },
            "diamag_sus": -442,
            "sdf_file": "phthalocyanine.sdf",
        },
        "PPh3": {
            "name": "triphenylphosphine",
            "SMILES": {"c1ccc(P(c2ccccc2)c2ccccc2)cc1"},
            "diamag_sus": -167,
            "sdf_file": "PPh3.sdf",
        },
        "pyz": {
            "name": "pyrazine",
            "SMILES": {"c1cnccn1"},
            "diamag_sus": -50,
            "sdf_file": "pyrazine.sdf",
        },
        "py": {
            "name": "pyridine",
            "SMILES": {"c1ccncc1"},
            "diamag_sus": -49,
            "sdf_file": "pyridine.sdf",
        },
        "sal(2-)": {
            "name": "salen2-",
            "SMILES": {"[O-]c1ccccc1C=NCCN=Cc1ccccc1[O-]"},
            "diamag_sus": -182,
            "sdf_file": "salen2-.sdf",
        },
        "urea": {
            "name": "urea",
            "SMILES": {"NC(N)=O"},
            "diamag_sus": -34,
            "sdf_file": "urea.sdf",
        },
    },
    # COMMON ORGANIC SOLVENTS
    "organic_solvents": {
        "CCl4": {
            "name": "tetrachloromethane",
            "SMILES": {"ClC(Cl)(Cl)Cl"},
            "diamag_sus": -66.8,
            "sdf_file": "CCl4.sdf",
        },
        "CHCl3": {
            "name": "chloroforom",
            "SMILES": {"ClC(Cl)Cl"},
            "diamag_sus": -58.9,
            "sdf_file": "CHCl3.sdf",
        },
        "CH2Cl2": {
            "name": "dichloromethane",
            "SMILES": {"ClCCl"},
            "diamag_sus": -46.6,
            "sdf_file": "CH2Cl2.sdf",
        },
        "CH3Cl": {
            "name": "chloromethane",
            "SMILES": {"CCl"},
            "diamag_sus": -32.0,
            "sdf_file": "CH3Cl.sdf",
        },
        "CH3NO2": {
            "name": "nitromethane",
            "SMILES": {"C[N+](=O)[O-]"},
            "diamag_sus": -21.0,
            "sdf_file": "CH3NO2.sdf",
        },
        "CH3OH": {
            "name": "methanol",
            "SMILES": {"CO"},
            "diamag_sus": -21.4,
            "sdf_file": "CH3OH.sdf",
        },
        "CCl3COOH": {
            "name": "trichloroacetic acid",
            "SMILES": {"O=C(O)C(Cl)(Cl)Cl"},
            "diamag_sus": -73.0,
            "sdf_file": "CCl3COOH.sdf",
        },
        "CF3COOH": {
            "name": "trifluoroacetic acid",
            "SMILES": {"O=C(O)C(F)(F)F"},
            "diamag_sus": -43.3,
            "sdf_file": "CF3COOH.sdf",
        },
        "CH3CN": {
            "name": "acetonitrile",
            "SMILES": {"CC#N"},
            "diamag_sus": -27.8,
            "sdf_file": "CH3CN.sdf",
        },
        "1,2-CH2Cl2": {
            "name": "1,2-dichloroethane",
            "SMILES": {"ClCCCl"},
            "diamag_sus": -59.6,
            "sdf_file": "ClCH2CH2Cl.sdf",
        },
        "CH3COOH": {
            "name": "acetic acid",
            "SMILES": {"CC(=O)O"},
            "diamag_sus": -31.8,
            "sdf_file": "CH3COOH.sdf",
        },
        "CH3CH2OH": {
            "name": "ethanol",
            "SMILES": {"CCO"},
            "diamag_sus": -33.7,
            "sdf_file": "CH3CH2OH.sdf",
        },
        "HOCH2CH2OH": {
            "name": "ethylene glycol",
            "SMILES": {"OCCO"},
            "diamag_sus": -38.9,
            "sdf_file": "HOCH2CH2OH.sdf",
        },
        "CH3CH2SH": {
            "name": "ethanethiol",
            "SMILES": {"CCS"},
            "diamag_sus": -44.9,
            "sdf_file": "CH3CH2SH.sdf",
        },
        "CH3C(=O)CH3": {
            "name": "acetone",
            "SMILES": {"CC(C)=O"},
            "diamag_sus": -33.8,
            "sdf_file": "CH3COCH3.sdf",
        },
        "CH3C(=O)OC(=O)CH3": {
            "name": "acetic anhydride",
            "SMILES": {"CC(=O)OC(C)=O"},
            "diamag_sus": -52.8,
            "sdf_file": "CH3CO_O_OCCH3.sdf",
        },
        "CH3CH2CH2CN": {
            "name": "butyronitrile",
            "SMILES": {"CCCC#N"},
            "diamag_sus": -50.4,
            "sdf_file": "CH3CH2CH2CN.sdf",
        },
        "CH3C(=O)OCH2CH3": {
            "name": "ethyl acetate",
            "SMILES": {"CCOC(C)=O"},
            "diamag_sus": -54.1,
            "sdf_file": "CH3CO_OCH2CH3.sdf",
        },
        "CH3CH2CH2CH2OH": {
            "name": "butanol",
            "SMILES": {"CCCCO"},
            "diamag_sus": -56.4,
            "sdf_file": "CH3CH2CH2CH2OH.sdf",
        },
        "CH3CH2OCH2CH3": {
            "name": "diethyl ether",
            "SMILES": {"CCOCC"},
            "diamag_sus": -55.5,
            "sdf_file": "CH3CH2OCH2CH3.sdf",
        },
        "CH3CH2CH2CH2CH3": {
            "name": "pentane",
            "SMILES": {"CCCCC"},
            "diamag_sus": -61.5,
            "sdf_file": "CH3CH2CH2CH2CH3.sdf",
        },
        "1,2-C6H4Cl2": {
            "name": "o-dichlorobenzene",
            "SMILES": {"Clc1ccccc1Cl"},
            "diamag_sus": -84.4,
            "sdf_file": "o-C6H4Cl2.sdf",
        },
        "C6H6": {
            "name": "benzene",
            "SMILES": {"c1ccccc1"},
            "diamag_sus": -54.8,
            "sdf_file": "C6H6.sdf",
        },
        "C6H12": {
            "name": "cyclohexane",
            "SMILES": {"C1CCCCC1"},
            "diamag_sus": -68,
            "sdf_file": "C6H12.sdf",
        },
        "CH3CH2CH2CH2CH2CH3": {
            "name": "hexane",
            "SMILES": {"CCCCCC"},
            "diamag_sus": -74.1,
            "sdf_file": "CH3CH2CH2CH2CH2CH3.sdf",
        },
        "N(CH2CH3)3": {
            "name": "triethylamine",
            "SMILES": {"CCN(CC)CC"},
            "diamag_sus": -83.3,
            "sdf_file": "N_CH2CH3_3.sdf",
        },
        "PhCN": {
            "name": "benzonitrile",
            "SMILES": {"N#Cc1ccccc1"},
            "diamag_sus": -65.2,
            "sdf_file": "PhCN.sdf",
        },
        "PhCH3": {
            "name": "toluene",
            "SMILES": {"Cc1ccccc1"},
            "diamag_sus": -65.6,
            "sdf_file": "PhCH3.sdf",
        },
        "CH3C(CH3)2CH2CH(CH3)2": {
            "name": "isooctane",
            "SMILES": {"CC(C)CC(C)(C)C"},
            "diamag_sus": -99.1,
            "sdf_file": "isooctane.sdf",
        },
        "C10H8": {
            "name": "naphthaline",
            "SMILES": {"c1ccc2ccccc2c1"},
            "diamag_sus": -91.6,
            "sdf_file": "naphthaline.sdf",
        },
    },
}

"""Lists of atoms for which it was specified that the atom may be part of a ring or has a defined oxidation state, according to 10.1021/ed085p532 (DOI)"""
RELEVANT_OXIDATION_ATOMS = ["As", "Hg", "Pb"]
RELEVANT_RING_ATOMS = ["N", "C"]


"""
unit: 10^(-6) cm^3/mol
Reference (DOI): 10.1021/ed085p532 (TABLES 1 and 6, and some anions from TABLE 3)
This dictionary represents the diamagnetic values for elements in
different bonding/oxidation_state/ionic_charge scenarios. Here's a breakdown of the values:
"""
PASCAL_CONST = {
    "C": {
        "covalent": {
            "ring": -6.24,
            "open_chain": -6.0,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                4: -0.1,
            },
        },
    },
    "H": {
        "covalent": {
            "ring": None,
            "open_chain": -2.93,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                1: 0,
                -1: -5.7,
            },
        },
    },
    "N": {
        "covalent": {
            "ring": -4.61,
            "open_chain": -5.57,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                5: -0.1,
            },
        },
    },
    "Ag": {
        "covalent": {
            "ring": None,
            "open_chain": -31.0,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                1: -28,
                2: -24,  # uncetrain value according to the article (DOI: 10.1021/ed085p532)
            },
        },
    },
    "Al": {
        "covalent": {
            "ring": None,
            "open_chain": -13.0,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                3: -2,
            },
        },
    },
    "As": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {
                3: -20.9,
                5: -43.0,
            },
        },
        "ionic": {
            "charge": {
                3: -9,  # uncetrain value according to the article (DOI: 10.1021/ed085p532)
                5: -6,
            },
        },
    },
    "Au": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                1: -40,  # uncetrain value according to the article (DOI: 10.1021/ed085p532)
                3: -32,
            },
        },
    },
    "B": {
        "covalent": {
            "ring": None,
            "open_chain": -7.0,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                3: -0.2,
            },
        },
    },
    "Ba": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                2: -26.5,
            },
        },
    },
    "Be": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                2: -0.4,
            },
        },
    },
    "Bi": {
        "covalent": {
            "ring": None,
            "open_chain": -192.0,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                3: -25,  # uncetrain value according to the article (DOI: 10.1021/ed085p532)
                5: -23,
            },
        },
    },
    "Br": {
        "covalent": {
            "ring": None,
            "open_chain": -30.6,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                -1: -34.6,
                5: -6,
            },
        },
    },
    "Ca": {
        "covalent": {
            "ring": None,
            "open_chain": -15.9,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                2: -10.4,
            },
        },
    },
    "Cd": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                2: -24,
            },
        },
    },
    "Ce": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                3: -20,
                4: -17,
            },
        },
    },
    "Cl": {
        "covalent": {
            "ring": None,
            "open_chain": -20.1,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                -1: -23.4,
                5: -2,
            },
        },
    },
    "Co": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                2: -12,
                3: -10,
            },
        },
    },
    "Cr": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                2: -15,
                3: -11,
                4: -8,
                5: -5,
                6: -3,
            },
        },
    },
    "Cs": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                1: -35.0,
            },
        },
    },
    "Cu": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                1: -12,
                2: -11,
            },
        },
    },
    "Dy": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                3: -19,
            },
        },
    },
    "Er": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                3: -18,
            },
        },
    },
    "Eu": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                2: -22,
                3: -20,
            },
        },
    },
    "F": {
        "covalent": {
            "ring": None,
            "open_chain": -6.3,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                -1: -9.1,
            },
        },
    },
    "Fe": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                2: -13,
                3: -10,
            },
        },
    },
    "Ga": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                3: -8,
            },
        },
    },
    "Ge": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                4: -7,
            },
        },
    },
    "Gd": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                3: -20,
            },
        },
    },
    "Hf": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                4: -16,
            },
        },
    },
    "Hg": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {
                2: -33.0,
            },
        },
        "ionic": {
            "charge": {
                2: -40.0,
            },
        },
    },
    "Ho": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                3: -19,
            },
        },
    },
    "I": {
        "covalent": {
            "ring": None,
            "open_chain": -44.6,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                -1: -50.6,
                5: -12,
                7: -10,
            },
        },
    },
    "In": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                3: -19,
            },
        },
    },
    "Ir": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                1: -50,
                2: -42,
                3: -35,
                4: -29,
                5: -20,
            },
        },
    },
    "K": {
        "covalent": {
            "ring": None,
            "open_chain": -18.5,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                1: -14.9,
            },
        },
    },
    "La": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                3: -20,
            },
        },
    },
    "Li": {
        "covalent": {
            "ring": None,
            "open_chain": -4.2,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                1: -1.0,
            },
        },
    },
    "Lu": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                3: -17,
            },
        },
    },
    "Mg": {
        "covalent": {
            "ring": None,
            "open_chain": -10.0,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                2: -5.0,
            },
        },
    },
    "Mn": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                2: -14,
                3: -10,
                4: -8,
                6: -4,
                7: -3,
            },
        },
    },
    "Mo": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                2: -31,
                3: -23,
                4: -17,
                5: -12,
                6: -7,
            },
        },
    },
    "Na": {
        "covalent": {
            "ring": None,
            "open_chain": -9.2,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                1: -6.8,
            },
        },
    },
    "Nb": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                5: -9,
            },
        },
    },
    "Nd": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                3: -20,
            },
        },
    },
    "Ni": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                2: -12,
            },
        },
    },
    "O": {
        "covalent": {
            "ring": None,
            "open_chain": -4.6,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                -2: -12.0,  # The value of χDi for O2– is reported as –6.0 in some sources
            },
        },
    },
    "Os": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                2: -44,
                3: -36,
                4: -29,
                6: -18,
                8: -11,
            },
        },
    },
    "P": {
        "covalent": {
            "ring": None,
            "open_chain": -26.3,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                3: -4,
                5: -1,
            },
        },
    },
    "Pb": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {
                2: -46.0,
            },
        },
        "ionic": {
            "charge": {
                2: -32.0,
                4: -26,
            },
        },
    },
    "Pd": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                2: -25,
                4: -18,
            },
        },
    },
    "Pm": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                3: -27,
            },
        },
    },
    "Pr": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                3: -20,
                4: -18,
            },
        },
    },
    "Pt": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                2: -40,
                3: -33,
                4: -28,
            },
        },
    },
    "Rb": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                1: -22.5,
            },
        },
    },
    "Re": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                3: -36,
                4: -28,
                6: -16,
                7: -12,
            },
        },
    },
    "Rh": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                3: -22,
                4: -18,
            },
        },
    },
    "Ru": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                3: -23,
                4: -18,
            },
        },
    },
    "S": {
        "covalent": {
            "ring": None,
            "open_chain": -15.0,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                -2: -30,
                4: -3,
                6: -1,
            },
        },
    },
    "Sb": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {
                3: -74.0,
            },
        },
        "ionic": {
            "charge": {
                3: -17,
                5: -14,
            },
        },
    },
    "Sc": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                3: -6,
            },
        },
    },
    "Se": {
        "covalent": {
            "ring": None,
            "open_chain": -23.0,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                -2: -48,  # This value is uncertain
                4: -8,
                6: -5,
            },
        },
    },
    "Si": {
        "covalent": {
            "ring": None,
            "open_chain": -13,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                4: -1,
            },
        },
    },
    "Sm": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                2: -23,
                3: -20,
            },
        },
    },
    "Sn": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {
                4: -30,
            },
        },
        "ionic": {
            "charge": {
                2: -20,
                4: -16,
            },
        },
    },
    "Sr": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                2: -19.0,
            },
        },
    },
    "Ta": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                5: -14,
            },
        },
    },
    "Tb": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                3: -19,
                4: -17,
            },
        },
    },
    "Te": {
        "covalent": {
            "ring": None,
            "open_chain": -37.3,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                -2: -70,
                4: -14,
                6: -12,
            },
        },
    },
    "Th": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                4: -23,
            },
        },
    },
    "Ti": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                3: -9,
                4: -5,
            },
        },
    },
    "Tl": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {
                1: -40.0,
            },
        },
        "ionic": {
            "charge": {
                1: -35.7,
                3: -31,
            },
        },
    },
    "Tm": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                3: -18,
            },
        },
    },
    "U": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                3: -46,
                4: -35,
                5: -26,
                6: -19,
            },
        },
    },
    "V": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                2: -15,
                3: -10,
                4: -7,
                5: -4,
            },
        },
    },
    "W": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                2: -41,
                3: -36,
                4: -23,
                5: -19,
                6: -13,
            },
        },
    },
    "Y": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                3: -12,
            },
        },
    },
    "Yb": {
        "covalent": {
            "ring": None,
            "open_chain": None,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                2: -20,
                3: -18,
            },
        },
    },
    "Zn": {
        "covalent": {
            "ring": None,
            "open_chain": -13.5,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                2: -15.0,
            },
        },
    },
    "Zr": {
        "covalent": {
            "ring": None,
            "open_chain": -13.5,
            "ox_state": {},
        },
        "ionic": {
            "charge": {
                4: -10,
            },
        },
    },
}

METAL_CATIONS = [
    "Au",
    "Ba",
    "Be",
    "Cd",
    "Ce",
    "Co",
    "Cr",
    "Cs",
    "Cu",
    "Dy",
    "Er",
    "Eu",
    "Fe",
    "Ga",
    "Ge",
    "Gd",
    "Hf",
    "Ho",
    "In",
    "Ir",
    "La",
    "Lu",
    "Mn",
    "Mo",
    "Nb",
    "Ni",
    "Os",
    "Pd",
    "Pm",
    "Pr",
    "Pt",
    "Rb",
    "Re",
    "Rh",
    "Ru",
    "Sc",
    "Sm",
    "Sr",
    "Ta",
    "Tb",
    "Th",
    "Ti",
    "Tm",
    "U",
    "V",
    "W",
    "Y",
    "Yb",
    "Zr",
]
