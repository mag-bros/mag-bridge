from constants import PASCAL_CONST


def calc_diamag_contr(input_data: list):
    sum_dia_contr = 0

    for element in input_data:
        if element.symbol in PASCAL_CONST:
            # retrieve const data
            covalent_data = PASCAL_CONST[element.symbol]["covalent"]
            ionic_data = PASCAL_CONST[element.symbol]["ionic"]["charge"]
            ox_state_data = PASCAL_CONST[element.symbol]["covalent"]["ox_state"]

            # for given element it takes ring constant and multiplies it with related atom No of the element
            if element.ring is not None and covalent_data["ring"] is not None:
                sum_dia_contr += covalent_data["ring"] * element.ring

            # for given element it takes chain constant and multiplies it with related atom No of the element
            if (
                element.open_chain is not None
                and covalent_data["open_chain"] is not None
            ):
                sum_dia_contr += covalent_data["open_chain"] * element.open_chain

            # calculate diamag contrib for given oxidation state data
            for state, atoms in element.ox_states.items():
                sum_dia_contr += ox_state_data.get(state, 0) * atoms

            # calculate diamag contrib for given ionic data
            for charge, atoms in element.ions.items():
                sum_dia_contr += ionic_data.get(charge, 0) * atoms

    return sum_dia_contr


def calc_atoms_no(formula: str):
    """
    Old version of input structure
    """
    input_data = {}

    key, value = "", ""
    for i in range(len(formula)):
        curr = formula[i]

        if i + 1 < len(formula):
            next = formula[i + 1]
            if curr.isalpha() and next.isalpha():
                key += curr
            elif curr.isalpha() and next.isdigit():
                key += curr
            elif curr.isdigit() and next.isdigit():
                value += curr
            elif curr.isdigit() and next.isalpha():
                value += curr
                input_data[key.capitalize()] = int(value)
                key, value = "", ""
        else:
            value += curr
            input_data[key.capitalize()] = int(value)

    return input_data
