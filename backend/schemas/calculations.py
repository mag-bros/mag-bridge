from enum import Enum
from pydantic import BaseModel

class InputType(str, Enum):
    SDF = "sdf"
    SMILES_FORMULA = "smiles_formula"
    SUSCEPTIBILITY = "susceptibility"

class ExperimentRequest(BaseModel):
    input_type: InputType
    path: str | None = None
    smiles_formula: str | None = None
    susceptibility: float | None = None
    selections: list[str] | None = None
