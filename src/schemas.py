from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import date


class ContactSchema(BaseModel):
    name: str = Field(min_length=3, max_length=40)
    email: EmailStr
    phone: str = Field(min_length=10, max_length=13)
    birthday: date
    password: str = Field(min_length=6, max_length=8)


class UpdateSchema(BaseModel):
    name: str = Field(min_length=3, max_length=40)
    phone: str = Field(min_length=10, max_length=13)
    birthday: date


class ContactResponse(BaseModel):
    id: int = 1
    name: str
    email: EmailStr
    phone: str
    birthday: date
    avatar: str | None
    model_config = ConfigDict(from_attributes = True)


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr
