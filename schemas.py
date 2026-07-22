from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    correo: EmailStr
    password: str = Field(min_length=4, max_length=100)


class LoginResponse(BaseModel):
    success: bool
    mensaje: str
    usuario: dict | None = None