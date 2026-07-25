from fastapi import APIRouter, HTTPException, status
from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)

from database import get_connection
from schemas import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)


router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
)


@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(datos: LoginRequest):
    correo = datos.correo.strip().lower()

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, nombre, correo, password
                FROM usuarios
                WHERE LOWER(correo) = %s
                """,
                (correo,),
            )

            usuario = cursor.fetchone()

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


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(datos: RegisterRequest):
    nombre_propietario = datos.nombre_propietario.strip()
    nombre_salon = datos.nombre_salon.strip()
    correo = str(datos.correo).strip().lower()
    password = datos.password
    telefono = datos.telefono.strip()
    direccion = datos.direccion.strip()

    descripcion = (
        datos.descripcion.strip()
        if datos.descripcion
        else None
    )

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM usuarios
                WHERE LOWER(correo) = %s
                """,
                (correo,),
            )

            if cursor.fetchone() is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Ya existe una cuenta con ese correo.",
                )

            password_hash = generate_password_hash(password)

            cursor.execute(
                """
                INSERT INTO usuarios (
                    nombre,
                    correo,
                    password
                )
                VALUES (%s, %s, %s)
                RETURNING id, nombre, correo
                """,
                (
                    nombre_propietario,
                    correo,
                    password_hash,
                ),
            )

            nuevo_usuario = cursor.fetchone()

            cursor.execute(
                """
                INSERT INTO salones (
                    nombre,
                    telefono,
                    direccion,
                    descripcion,
                    usuario_id
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING
                    id,
                    nombre,
                    telefono,
                    direccion,
                    descripcion,
                    usuario_id
                """,
                (
                    nombre_salon,
                    telefono,
                    direccion,
                    descripcion,
                    nuevo_usuario["id"],
                ),
            )

            nuevo_salon = cursor.fetchone()

        connection.commit()

    except HTTPException:
        connection.rollback()
        raise

    except Exception as error:
        connection.rollback()

        print("Error al registrar salón:", error)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No se pudo registrar el salón de belleza.",
        ) from error

    finally:
        connection.close()

    return RegisterResponse(
        success=True,
        mensaje="Salón de belleza registrado correctamente.",
        usuario={
            "id": nuevo_usuario["id"],
            "nombre": nuevo_usuario["nombre"],
            "correo": nuevo_usuario["correo"],
        },
        salon={
            "id": nuevo_salon["id"],
            "nombre": nuevo_salon["nombre"],
            "telefono": nuevo_salon["telefono"],
            "direccion": nuevo_salon["direccion"],
            "descripcion": nuevo_salon["descripcion"],
        },
    )