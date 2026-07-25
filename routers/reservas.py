from datetime import date, datetime, time
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from database import get_connection


router = APIRouter(
    prefix="/reservas",
    tags=["Reservas"],
)


ESTADOS_VALIDOS = {
    "pendiente",
    "aceptada",
    "completada",
    "anulada",
}


class ReservaCreate(BaseModel):
    salon_id: int
    servicio_id: Optional[int] = None
    fecha: date
    hora: Optional[time] = None
    nombre_cliente: Optional[str] = Field(
        default=None,
        max_length=150,
    )
    correo_cliente: Optional[str] = Field(
        default=None,
        max_length=255,
    )
    telefono_cliente: Optional[str] = Field(
        default=None,
        max_length=30,
    )
    estado: str = "pendiente"


class ReservaUpdate(BaseModel):
    servicio_id: Optional[int] = None
    fecha: date
    hora: Optional[time] = None
    nombre_cliente: Optional[str] = Field(
        default=None,
        max_length=150,
    )
    correo_cliente: Optional[str] = Field(
        default=None,
        max_length=255,
    )
    telefono_cliente: Optional[str] = Field(
        default=None,
        max_length=30,
    )


class ReservaEstadoUpdate(BaseModel):
    estado: str


class ReservaResponse(BaseModel):
    id: int
    salon_id: int
    servicio_id: Optional[int] = None
    fecha: date
    hora: Optional[time] = None
    nombre_cliente: Optional[str] = None
    correo_cliente: Optional[str] = None
    telefono_cliente: Optional[str] = None
    estado: str
    fecha_creacion: datetime


@router.post(
    "",
    response_model=ReservaResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_reserva(reserva: ReservaCreate):
    estado_reserva = reserva.estado.strip().lower()

    if estado_reserva not in ESTADOS_VALIDOS:
        raise HTTPException(
            status_code=400,
            detail="El estado de la reserva no es válido.",
        )

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM salones
                WHERE id = %s
                """,
                (reserva.salon_id,),
            )

            if cursor.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="El salón no existe.",
                )

            if reserva.servicio_id is not None:
                cursor.execute(
                    """
                    SELECT id
                    FROM servicios
                    WHERE id = %s
                      AND salon_id = %s
                    """,
                    (
                        reserva.servicio_id,
                        reserva.salon_id,
                    ),
                )

                if cursor.fetchone() is None:
                    raise HTTPException(
                        status_code=400,
                        detail=(
                            "El servicio no existe o no pertenece "
                            "al salón seleccionado."
                        ),
                    )

            cursor.execute(
                """
                INSERT INTO reservas (
                    salon_id,
                    servicio_id,
                    fecha,
                    hora,
                    nombre_cliente,
                    correo_cliente,
                    telefono_cliente,
                    estado
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING
                    id,
                    salon_id,
                    servicio_id,
                    fecha,
                    hora,
                    nombre_cliente,
                    correo_cliente,
                    telefono_cliente,
                    estado,
                    fecha_creacion
                """,
                (
                    reserva.salon_id,
                    reserva.servicio_id,
                    reserva.fecha,
                    reserva.hora,
                    reserva.nombre_cliente,
                    reserva.correo_cliente,
                    reserva.telefono_cliente,
                    estado_reserva,
                ),
            )

            creada = cursor.fetchone()

        connection.commit()
        return creada

    except HTTPException:
        connection.rollback()
        raise

    except Exception as error:
        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"No fue posible crear la reserva: {error}",
        )

    finally:
        connection.close()


@router.get(
    "/salon/{salon_id}",
    response_model=List[ReservaResponse],
)
def obtener_reservas_salon(salon_id: int):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    salon_id,
                    servicio_id,
                    fecha,
                    hora,
                    nombre_cliente,
                    correo_cliente,
                    telefono_cliente,
                    estado,
                    fecha_creacion
                FROM reservas
                WHERE salon_id = %s
                ORDER BY fecha DESC, hora DESC NULLS LAST
                """,
                (salon_id,),
            )

            return cursor.fetchall()

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"No fue posible obtener las reservas: {error}",
        )

    finally:
        connection.close()


@router.get(
    "/{reserva_id}",
    response_model=ReservaResponse,
)
def obtener_reserva(reserva_id: int):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    salon_id,
                    servicio_id,
                    fecha,
                    hora,
                    nombre_cliente,
                    correo_cliente,
                    telefono_cliente,
                    estado,
                    fecha_creacion
                FROM reservas
                WHERE id = %s
                """,
                (reserva_id,),
            )

            reserva = cursor.fetchone()

            if reserva is None:
                raise HTTPException(
                    status_code=404,
                    detail="La reserva no existe.",
                )

            return reserva

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"No fue posible obtener la reserva: {error}",
        )

    finally:
        connection.close()


@router.put(
    "/{reserva_id}",
    response_model=ReservaResponse,
)
def actualizar_reserva(
    reserva_id: int,
    reserva: ReservaUpdate,
):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE reservas
                SET
                    servicio_id = %s,
                    fecha = %s,
                    hora = %s,
                    nombre_cliente = %s,
                    correo_cliente = %s,
                    telefono_cliente = %s
                WHERE id = %s
                RETURNING
                    id,
                    salon_id,
                    servicio_id,
                    fecha,
                    hora,
                    nombre_cliente,
                    correo_cliente,
                    telefono_cliente,
                    estado,
                    fecha_creacion
                """,
                (
                    reserva.servicio_id,
                    reserva.fecha,
                    reserva.hora,
                    reserva.nombre_cliente,
                    reserva.correo_cliente,
                    reserva.telefono_cliente,
                    reserva_id,
                ),
            )

            actualizada = cursor.fetchone()

            if actualizada is None:
                raise HTTPException(
                    status_code=404,
                    detail="La reserva no existe.",
                )

        connection.commit()
        return actualizada

    except HTTPException:
        connection.rollback()
        raise

    except Exception as error:
        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"No fue posible actualizar la reserva: {error}",
        )

    finally:
        connection.close()


@router.patch(
    "/{reserva_id}/estado",
    response_model=ReservaResponse,
)
def cambiar_estado_reserva(
    reserva_id: int,
    datos: ReservaEstadoUpdate,
):
    estado = datos.estado.strip().lower()

    if estado not in ESTADOS_VALIDOS:
        raise HTTPException(
            status_code=400,
            detail="El estado indicado no es válido.",
        )

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE reservas
                SET estado = %s
                WHERE id = %s
                RETURNING
                    id,
                    salon_id,
                    servicio_id,
                    fecha,
                    hora,
                    nombre_cliente,
                    correo_cliente,
                    telefono_cliente,
                    estado,
                    fecha_creacion
                """,
                (
                    estado,
                    reserva_id,
                ),
            )

            actualizada = cursor.fetchone()

            if actualizada is None:
                raise HTTPException(
                    status_code=404,
                    detail="La reserva no existe.",
                )

        connection.commit()
        return actualizada

    except HTTPException:
        connection.rollback()
        raise

    except Exception as error:
        connection.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"No fue posible cambiar el estado: {error}",
        )

    finally:
        connection.close()


@router.delete(
    "/{reserva_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar_reserva(reserva_id: int):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM reservas
                WHERE id = %s
                RETURNING id
                """,
                (reserva_id,),
            )

            eliminada = cursor.fetchone()

            if eliminada is None:
                raise HTTPException(
                    status_code=404,
                    detail="La reserva no existe.",
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
            detail=f"No fue posible eliminar la reserva: {error}",
        )

    finally:
        connection.close()