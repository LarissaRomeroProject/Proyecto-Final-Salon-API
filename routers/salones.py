from typing import List
from fastapi import APIRouter, HTTPException, status

from database import get_connection
from schemas import SalonCreateRequest, SalonResponse, SalonUpdateRequest


router = APIRouter(
    prefix="/salones",
    tags=["Salones"]
)


@router.post(
    "",
    response_model=SalonResponse,
    status_code=status.HTTP_201_CREATED
)
def crear_salon(salon: SalonCreateRequest):
    connection = get_connection()

    try:
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id
                    FROM usuarios
                    WHERE id = %s
                    """,
                    (salon.usuario_id,)
                )

                usuario = cursor.fetchone()

                if usuario is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="El usuario no existe."
                    )

                cursor.execute(
                    """
                    SELECT id
                    FROM salones
                    WHERE usuario_id = %s
                    """,
                    (salon.usuario_id,)
                )

                salon_existente = cursor.fetchone()

                if salon_existente is not None:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="El usuario ya tiene un salón registrado."
                    )

                cursor.execute(
                    """
                    INSERT INTO salones (
                        usuario_id,
                        nombre,
                        telefono,
                        direccion,
                        descripcion,
                        imagen
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING
                        id,
                        usuario_id,
                        nombre,
                        telefono,
                        direccion,
                        descripcion,
                        imagen
                    """,
                    (
                        salon.usuario_id,
                        salon.nombre,
                        salon.telefono,
                        salon.direccion,
                        salon.descripcion,
                        salon.imagen
                    )
                )

                return cursor.fetchone()

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"No fue posible crear el salón: {error}"
        )

    finally:
        connection.close()

@router.get(
    "",
    response_model=List[SalonResponse]
)
def obtener_salones():
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    usuario_id,
                    nombre,
                    telefono,
                    direccion,
                    descripcion,
                    imagen
                FROM salones
                ORDER BY id DESC
                """
            )

            salones = cursor.fetchall()

            return salones

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"No fue posible obtener los salones: {error}"
        )

    finally:
        connection.close()


@router.get(
    "/usuario/{usuario_id}",
    response_model=SalonResponse
)
def obtener_salon_por_usuario(usuario_id: int):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    usuario_id,
                    nombre,
                    telefono,
                    direccion,
                    descripcion,
                    imagen
                FROM salones
                WHERE usuario_id = %s
                """,
                (usuario_id,)
            )

            salon = cursor.fetchone()

            if salon is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No se encontró un salón para este usuario."
                )

            return salon

    finally:
        connection.close()

@router.get(
    "/{salon_id}",
    response_model=SalonResponse
)
def obtener_salon_por_id(salon_id: int):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    usuario_id,
                    nombre,
                    telefono,
                    direccion,
                    descripcion,
                    imagen
                FROM salones
                WHERE id = %s
                """,
                (salon_id,)
            )

            salon = cursor.fetchone()

            if salon is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="El salón no existe."
                )

            return salon

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"No fue posible obtener el salón: {error}"
        )

    finally:
        connection.close()

@router.put(
    "/{salon_id}",
    response_model=SalonResponse
)
def actualizar_salon(
    salon_id: int,
    datos: SalonUpdateRequest
):
    connection = get_connection()

    try:
        cambios = datos.model_dump(exclude_unset=True)

        if not cambios:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se enviaron datos para actualizar."
            )

        campos_permitidos = {
            "nombre",
            "telefono",
            "direccion",
            "descripcion",
            "imagen"
        }

        campos = []
        valores = []

        for campo, valor in cambios.items():
            if campo in campos_permitidos:
                campos.append(f"{campo} = %s")
                valores.append(valor)

        if not campos:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se enviaron campos válidos para actualizar."
            )

        valores.append(salon_id)

        consulta = f"""
            UPDATE salones
            SET {", ".join(campos)}
            WHERE id = %s
            RETURNING
                id,
                usuario_id,
                nombre,
                telefono,
                direccion,
                descripcion,
                imagen
        """

        with connection:
            with connection.cursor() as cursor:
                cursor.execute(consulta, valores)
                salon_actualizado = cursor.fetchone()

                if salon_actualizado is None:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="El salón no existe."
                    )

                return salon_actualizado

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"No fue posible actualizar el salón: {error}"
        )

    finally:
        connection.close()

