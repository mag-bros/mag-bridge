SDF_TEST_COMPOUNDS = [
    {
        "sdf_file": "2-methylpropan-1-ol.sdf",
        "expected_diamag_total": -57.9,
        "expected_diamag_atoms": 0,
        "expected_diamag_mols": 0,
        "expected_diamag_constitutive": 0,
    },
    {"sdf_file": "chlorobenzene.sdf", "expected_diamag_total": -72.19},
    {
        "sdf_file": "chalconatronate.sdf",
        "expected_diamag_total": -999,
        "expected_diamag_atoms": 0,
        "expected_diamag_mols": -999,
        "expected_diamag_constitutive": 0,
    },
    {"sdf_file": "AsIIIAsVAlAl3+.sdf", "expected_diamag_total": -178.78},
    {"sdf_file": "ArenePbIIPb2+.sdf", "expected_diamag_total": -206.32},
    {
        "sdf_file": "[K(crown)][Dy(BC4Ph5)2].sdf",
        "expected_diamag_total": -788.64,
        "description": "RDKit is treating all C and N atoms as ring_atoms when molecule has macrocyclic structure.",
    },
    {"sdf_file": "[Ag(TACN)](HSO4).sdf", "expected_diamag_total": -160.99},
    {"sdf_file": "joint-ring-system.sdf", "expected_diamag_total": -169.88},
    {"sdf_file": "azabicycle_9_5.sdf", "expected_diamag_total": -116.92},
    {"sdf_file": "macrocycle_with_rings.sdf", "expected_diamag_total": -519.24},
    {
        "sdf_file": "Be2+_2CH3-.sdf",
        "expected_diamag_total": -29.98,
        "description": "This file must not contain Be-C bonds",
    },
]
