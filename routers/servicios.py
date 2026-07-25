from decimal import Decimal
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from database import get_connection


router = APIRouter(
    prefix="/servicios",
    tags=["Servicios"],
)


class ServicioCreate(BaseModel):
    salon_id: int
    nombre: str = Field(min_length=2, max_length=150)
    descripcion: Optional[str] = Field(
        default=None,
        max_length=500,
    )
    precio: Decimal = Field(ge=0)
    duracion_minutos: int = Field(gt=0)
    activo: bool = True


class ServicioUpdate(BaseModel):
    nombre: str = Field(min_length=2, max_length=150)
    descripcion: Optional[str] = Field(
        default=None,
        max_length=500,
    )
    precio: Decimal = Field(ge=0)
    duracion_minutos: int = Field(gt=0)
    activo: bool = True


class ServicioResponse(BaseModel):
    id: int
    salon_id: int
    nombre: str
    descripcion: Optional[str] = None
    precio: Decimal
    duracion_minutos: int
    activo: bool


@router.post(
    "",
    response_model=ServicioResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_servicio(servicio: ServicioCreate):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM salones
                WHERE id = %s
                """,
                (servicio.salon_id,),
            )

            if cursor.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="El salón no existe.",
                )

            cursor.execute(
                """
                INSERT INTO servicios (
                    salon_id,
                    nombre,
                    descripcion,
                    precio,
                    duracion_minutos,
                    activo
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING
                    id,
                    salon_id,
                    nombre,
                    descripcion,
                    precio,
                    duracion_minutos,
                    activo
                """,
                (
                    servicio.salon_id,
                    servicio.nombre.strip(),
                    servicio.descripcion,
                    servicio.precio,
                    servicio.duracion_minutos,
                    servicio.activo,
                ),
            )

            creado = cursor.fetchone()

        connection.commit()
        return creado

    except HTTPException:
        connection.rollback()
        raise

    except Exception as error:
        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"No fue posible crear el servicio: {error}",
        )

    finally:
        connection.close()


@router.get(
    "/salon/{salon_id}",
    response_model=List[ServicioResponse],
)
def obtener_servicios_salon(salon_id: int):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    salon_id,
                    nombre,
                    descripcion,
                    precio,
                    duracion_minutos,
                    activo
                FROM servicios
                WHERE salon_id = %s
                ORDER BY id DESC
                """,
                (salon_id,),
            )

            return cursor.fetchall()

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"No fue posible obtener los servicios: {error}",
        )

    finally:
        connection.close()


@router.get(
    "/{servicio_id}",
    response_model=ServicioResponse,
)
def obtener_servicio(servicio_id: int):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    salon_id,
                    nombre,
                    descripcion,
                    precio,
                    duracion_minutos,
                    activo
                FROM servicios
                WHERE id = %s
                """,
                (servicio_id,),
            )

            servicio = cursor.fetchone()

            if servicio is None:
                raise HTTPException(
                    status_code=404,
                    detail="El servicio no existe.",
                )

            return servicio

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"No fue posible obtener el servicio: {error}",
        )

    finally:
        connection.close()


@router.put(
    "/{servicio_id}",
    response_model=ServicioResponse,
)
def actualizar_servicio(
    servicio_id: int,
    servicio: ServicioUpdate,
):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE servicios
                SET
                    nombre = %s,
                    descripcion = %s,
                    precio = %s,
                    duracion_minutos = %s,
                    activo = %s
                WHERE id = %s
                RETURNING
                    id,
                    salon_id,
                    nombre,
                    descripcion,
                    precio,
                    duracion_minutos,
                    activo
                """,
                (
                    servicio.nombre.strip(),
                    servicio.descripcion,
                    servicio.precio,
                    servicio.duracion_minutos,
                    servicio.activo,
                    servicio_id,
                ),
            )

            actualizado = cursor.fetchone()

            if actualizado is None:
                raise HTTPException(
                    status_code=404,
                    detail="El servicio no existe.",
                )

        connection.commit()
        return actualizado

    except HTTPException:
        connection.rollback()
        raise

    except Exception as error:
        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"No fue posible actualizar el servicio: {error}",
        )

    finally:
        connection.close()


@router.delete(
    "/{servicio_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar_servicio(servicio_id: int):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM servicios
                WHERE id = %s
                RETURNING id
                """,
                (servicio_id,),
            )

            eliminado = cursor.fetchone()

            if eliminado is None:
                raise HTTPException(
                    status_code=404,
                    detail="El servicio no existe.",
                )

        connection.commit()
        return None

    except HTTPException:
        connection.rollback()
        raise

    except Exception as error:
        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"No fue posible eliminar el servicio: {error}",
        )

    finally:
        connection.close()