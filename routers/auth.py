from fastapi import APIRouter, HTTPException, status
from werkzeug.security import check_password_hash

from backend.database import get_connection
from backend.schemas import LoginRequest, LoginResponse


router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
)


@router.post("/login", response_model=LoginResponse)
def login(datos: LoginRequest):
    connection = get_connection()

    try:
        usuario = connection.execute(
            """
            SELECT id, nombre, correo, password
            FROM usuarios
            WHERE correo = ?
            """,
            (datos.correo.lower(),),
        ).fetchone()

    finally:
        connection.close()

    if usuario is None or not check_password_hash(
        usuario["password"],
        datos.password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos.",
        )

    return LoginResponse(
        success=True,
        mensaje="Inicio de sesión exitoso.",
        usuario={
            "id": usuario["id"],
            "nombre": usuario["nombre"],
            "correo": usuario["correo"],
        },
    )