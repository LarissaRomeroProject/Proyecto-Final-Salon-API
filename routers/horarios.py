from datetime import time
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from database import get_connection


router = APIRouter(
    prefix="/horarios",
    tags=["Horarios"],
)


DIAS_VALIDOS = {
    "lunes",
    "martes",
    "miercoles",
    "jueves",
    "viernes",
    "sabado",
    "domingo",
}


class HorarioCreate(BaseModel):
    salon_id: int
    dia_semana: str
    hora_apertura: Optional[time] = None
    hora_cierre: Optional[time] = None
    cerrado: bool = False


class HorarioUpdate(BaseModel):
    dia_semana: str
    hora_apertura: Optional[time] = None
    hora_cierre: Optional[time] = None
    cerrado: bool = False


class HorarioResponse(BaseModel):
    id: int
    salon_id: int
    dia_semana: str
    hora_apertura: Optional[time] = None
    hora_cierre: Optional[time] = None
    cerrado: bool


def validar_horario(
    dia_semana: str,
    hora_apertura: Optional[time],
    hora_cierre: Optional[time],
    cerrado: bool,
):
    dia = dia_semana.strip().lower()

    if dia not in DIAS_VALIDOS:
        raise HTTPException(
            status_code=400,
            detail="El día de la semana no es válido.",
        )

    if not cerrado:
        if hora_apertura is None or hora_cierre is None:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Debes indicar la hora de apertura y cierre."
                ),
            )

        if hora_cierre <= hora_apertura:
            raise HTTPException(
                status_code=400,
                detail=(
                    "La hora de cierre debe ser posterior "
                    "a la hora de apertura."
                ),
            )

    return dia


@router.post(
    "",
    response_model=HorarioResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear_horario(horario: HorarioCreate):
    dia = validar_horario(
        horario.dia_semana,
        horario.hora_apertura,
        horario.hora_cierre,
        horario.cerrado,
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
                (horario.salon_id,),
            )

            if cursor.fetchone() is None:
                raise HTTPException(
                    status_code=404,
                    detail="El salón no existe.",
                )

            cursor.execute(
                """
                INSERT INTO horarios (
                    salon_id,
                    dia_semana,
                    hora_apertura,
                    hora_cierre,
                    cerrado
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING
                    id,
                    salon_id,
                    dia_semana,
                    hora_apertura,
                    hora_cierre,
                    cerrado
                """,
                (
                    horario.salon_id,
                    dia,
                    None if horario.cerrado else horario.hora_apertura,
                    None if horario.cerrado else horario.hora_cierre,
                    horario.cerrado,
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

        if "uq_horarios_salon_dia" in str(error):
            raise HTTPException(
                status_code=409,
                detail=(
                    "Ya existe un horario para ese día."
                ),
            )

        raise HTTPException(
            status_code=500,
            detail=f"No fue posible crear el horario: {error}",
        )

    finally:
        connection.close()


@router.get(
    "/salon/{salon_id}",
    response_model=List[HorarioResponse],
)
def obtener_horarios_salon(salon_id: int):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    salon_id,
                    dia_semana,
                    hora_apertura,
                    hora_cierre,
                    cerrado
                FROM horarios
                WHERE salon_id = %s
                ORDER BY CASE dia_semana
                    WHEN 'lunes' THEN 1
                    WHEN 'martes' THEN 2
                    WHEN 'miercoles' THEN 3
                    WHEN 'jueves' THEN 4
                    WHEN 'viernes' THEN 5
                    WHEN 'sabado' THEN 6
                    WHEN 'domingo' THEN 7
                END
                """,
                (salon_id,),
            )

            return cursor.fetchall()

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"No fue posible obtener los horarios: {error}",
        )

    finally:
        connection.close()


@router.get(
    "/{horario_id}",
    response_model=HorarioResponse,
)
def obtener_horario(horario_id: int):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    salon_id,
                    dia_semana,
                    hora_apertura,
                    hora_cierre,
                    cerrado
                FROM horarios
                WHERE id = %s
                """,
                (horario_id,),
            )

            horario = cursor.fetchone()

            if horario is None:
                raise HTTPException(
                    status_code=404,
                    detail="El horario no existe.",
                )

            return horario

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"No fue posible obtener el horario: {error}",
        )

    finally:
        connection.close()


@router.put(
    "/{horario_id}",
    response_model=HorarioResponse,
)
def actualizar_horario(
    horario_id: int,
    horario: HorarioUpdate,
):
    dia = validar_horario(
        horario.dia_semana,
        horario.hora_apertura,
        horario.hora_cierre,
        horario.cerrado,
    )

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE horarios
                SET
                    dia_semana = %s,
                    hora_apertura = %s,
                    hora_cierre = %s,
                    cerrado = %s
                WHERE id = %s
                RETURNING
                    id,
                    salon_id,
                    dia_semana,
                    hora_apertura,
                    hora_cierre,
                    cerrado
                """,
                (
                    dia,
                    None if horario.cerrado else horario.hora_apertura,
                    None if horario.cerrado else horario.hora_cierre,
                    horario.cerrado,
                    horario_id,
                ),
            )

            actualizado = cursor.fetchone()

            if actualizado is None:
                raise HTTPException(
                    status_code=404,
                    detail="El horario no existe.",
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
            detail=f"No fue posible actualizar el horario: {error}",
        )

    finally:
        connection.close()


@router.delete(
    "/{horario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar_horario(horario_id: int):
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM horarios
                WHERE id = %s
                RETURNING id
                """,
                (horario_id,),
            )

            eliminado = cursor.fetchone()

            if eliminado is None:
                raise HTTPException(
                    status_code=404,
                    detail="El horario no existe.",
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
            detail=f"No fue posible eliminar el horario: {error}",
        )

    finally:
        connection.close()