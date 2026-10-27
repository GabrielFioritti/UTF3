from pydantic import BaseModel, ConfigDict, EmailStr, Field


class CustomerIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr


class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
