from pydantic import BaseModel, Field

# Input schemas for tools
class SearchPayeeInput(BaseModel):
    name: str = Field(..., description="The name of the payee to search for.")

class ExecuteTransferInput(BaseModel):
    payee_id: str = Field(..., description="The exact ID of the payee to send money to.")
    amount: float = Field(..., description="The amount of money to transfer.")

# Return schemas
class Payee(BaseModel):
    name: str
    payee_id: str
    bank: str

class TransferRequest(BaseModel):
    payee_id: str
    amount: float
    currency: str = "PHP"
