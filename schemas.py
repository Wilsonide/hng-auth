from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserPreferences(BaseModel):
    email: bool = False
    push: bool = False


class PushTokenOut(BaseModel):
    id: str
    user_id: str
    token: str
    created_at: str

    class Config:
        orm_mode = True


class UserOut(BaseModel):
    email: EmailStr
    name: str
    push_token: PushTokenOut | None = None
    password: str | None = None
    preferences: UserPreferences
    id: UUID

    class Config:
        orm_mode = True


class PushTokenData(BaseModel):
    user_id: str
    token: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    preferences: UserPreferences


class UserLogin(BaseModel):
    email: EmailStr
    password: str
