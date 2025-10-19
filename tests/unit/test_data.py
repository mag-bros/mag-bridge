from element import Element

MOLECULES_DATA = [
    {
        "formula": "C20H25NCl",
        "elements": [
            Element("C", 20, ring=12, open_chain=8),
            Element("H", 25, open_chain=25),
            Element("N", 1, ring=1),
            Element("Cl", 1, ions={"-1": 1}),
        ],
        "diamag": -224.14,
    },
    {
        "formula": "C45H30N9",
        "elements": [
            Element("C", 45, ring=25, open_chain=20),
            Element("H", 30, open_chain=30),
            Element("N", 9, ring=4, open_chain=5),
        ],
        "diamag": -410.19,
    },
    {
        "formula": "C25H22As(III)3Br2",
        "elements": [
            Element("C", 25, ring=15, open_chain=10),
            Element("H", 22, open_chain=22),
            Element("As", 3, ox_states={"(III)": 3}),
            Element("Br", 2, ions={"-1": 2}),
        ],
        "diamag": -349.96,
    },
    {
        "formula": "B10As(III)5",
        "elements": [
            Element("B", 10, open_chain=8, ions={"+3": 2}),
            Element("As", 5, ox_states={"(III)": 2}, ions={"+3": 3}),
        ],
        "diamag": -125.20,
    },
]
