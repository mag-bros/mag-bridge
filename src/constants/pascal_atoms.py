"""
Lists of atoms for which it was specified that the atom may be part of a ring or has a defined oxidation state, according to 10.1021/ed085p532 (DOI)
unit: 10^(-6) cm^3/mol
Reference (DOI): 10.1021/ed085p532 (TABLES 1 and 6, and some ions from TABLE 3)
This dictionary represents the Pascal constants for elements in
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
