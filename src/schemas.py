from pydantic import BaseModel, EmailStr, Field
from datetime import date


class ContactSchema(BaseModel):
    name: str = Field(min_length=3, max_length=40)
    email: EmailStr
    phone: str = Field(min_length=10, max_length=13)
    birthday: date
    password: str = Field(min_length=6, max_length=8)


class ContactResponse(BaseModel):
    id: int = 1
    name: str
    email: EmailStr
    phone: str
    birthday: date
    avatar: str | None
    class Config:
        from_attributes = True


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RequestEmail(BaseModel):
    email: EmailStr
