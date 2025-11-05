SDF_TEST_COMPOUNDS = [
    {"sdf_file": "2-methylpropan-1-ol.sdf", "expected_diamag": -57.9},
    {"sdf_file": "chlorobenzene.sdf", "expected_diamag": -72.19},
    {"sdf_file": "chalconatronate.sdf", "expected_diamag": -95.58},
    {"sdf_file": "AsIIIAsVAlAl3+.sdf", "expected_diamag": -178.78},
    {"sdf_file": "ArenePbIIPb2+.sdf", "expected_diamag": -206.32},
    {
        "sdf_file": "[K(crown)][Dy(BC4Ph5)2].sdf",
        "expected_diamag": -788.64,
        "description": "RDKit is treating all C and N atoms as ring_atoms when molecule has macrocyclic structure.",
    },
    # {"sdf_file": "Be(CH3)2.sdf", "expected_diamag": -29.98},
    # TODO: This test will not pass because Be-C bonds have to be omitted. To resolve it, error for user must be provided
    #       or additional function that delates certain coordination bonds and updates raw SDF file.#
]
