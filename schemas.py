from typing import Any

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    correo: EmailStr
    password: str = Field(min_length=4, max_length=100)


class LoginResponse(BaseModel):
    success: bool
    mensaje: str
    usuario: dict[str, Any] | None = None


class RegisterRequest(BaseModel):
    nombre_propietario: str = Field(min_length=3, max_length=100)
    nombre_salon: str = Field(min_length=3, max_length=150)
    correo: EmailStr
    password: str = Field(min_length=8, max_length=100)
    telefono: str = Field(min_length=8, max_length=20)
    direccion: str = Field(min_length=5, max_length=255)
    descripcion: str | None = Field(default=None, max_length=500)

class RegisterResponse(BaseModel):
    success: bool
    mensaje: str
    usuario: dict[str, Any]
    salon: dict[str, Any]


class SalonCreateRequest(BaseModel):
    usuario_id: int
    nombre: str = Field(min_length=3, max_length=150)
    telefono: str = Field(min_length=8, max_length=20)
    direccion: str = Field(min_length=5)
    descripcion: str | None = None
    imagen: str | None = None


class SalonUpdateRequest(BaseModel):
    nombre: str | None = Field(default=None, min_length=3, max_length=150)
    telefono: str | None = Field(default=None, min_length=8, max_length=20)
    direccion: str | None = Field(default=None, min_length=5)
    descripcion: str | None = None
    imagen: str | None = None


class SalonResponse(BaseModel):
    id: int
    usuario_id: int
    nombre: str
    telefono: str
    direccion: str
    descripcion: str | None = None
    imagen: str | None = None