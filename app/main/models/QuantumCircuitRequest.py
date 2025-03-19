from pydantic import BaseModel


class QuantumCircuitRequest(BaseModel):
    qc: str