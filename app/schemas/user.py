from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str

    model_config = {
        "from_attributes": True
    }
    
class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"