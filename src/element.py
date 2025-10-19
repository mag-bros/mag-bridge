class Element:
    def __init__(
        self,
        symbol: str,
        total: int,
        ring: int = None,
        open_chain: int = None,
        ions: dict = None,
        ox_states: dict = None,
    ):
        """Examples:
        - Element("C", total=7, ring=3, open_chain=4, ox_states={"(IV)": 7})
        - Element(symbol='As', total=3, ox_states={'(III)': 3}, ions={'+3': 4})
        - Element(symbol='B', total=8, open_chain=8, ions={'+3': 2})
        """

        self.symbol = symbol
        self.total = total
        self.ring = ring
        self.open_chain = open_chain
        self.ions = ions if ions is not None else {}
        self.ox_states = ox_states if ox_states else {}
        self.is_covalent: bool = True if open_chain or ring or ox_states is not None else False
        assert open_chain or ring or ions or ox_states, 'One of these arguments must be provided.' 
