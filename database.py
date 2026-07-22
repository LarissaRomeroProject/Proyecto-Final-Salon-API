import os

import psycopg2
from psycopg2.extras import RealDictCursor


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://api_user:api_password@localhost:5432/salon_api",
)


def get_connection():
    """
    Crea una conexión con PostgreSQL.

    RealDictCursor permite acceder a las columnas como diccionario:
    usuario["correo"], usuario["password"], etc.
    """
    return psycopg2.connect(
        DATABASE_URL,
        cursor_factory=RealDictCursor,
    )


def create_tables() -> None:
    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(150) NOT NULL,
                    correo VARCHAR(255) NOT NULL UNIQUE,
                    password TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS salones (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(150) NOT NULL,
                    direccion TEXT NOT NULL,
                    descripcion TEXT,
                    imagen TEXT
                );

                CREATE TABLE IF NOT EXISTS servicios (
                    id SERIAL PRIMARY KEY,
                    salon_id INTEGER NOT NULL,
                    nombre VARCHAR(150) NOT NULL,
                    descripcion TEXT,
                    precio NUMERIC(10, 2) NOT NULL,
                    duracion_minutos INTEGER NOT NULL,
                    CONSTRAINT fk_servicios_salon
                        FOREIGN KEY (salon_id)
                        REFERENCES salones(id)
                        ON DELETE CASCADE
                );

                CREATE TABLE IF NOT EXISTS horarios (
                    id SERIAL PRIMARY KEY,
                    salon_id INTEGER NOT NULL,
                    fecha DATE NOT NULL,
                    hora TIME NOT NULL,
                    disponible BOOLEAN NOT NULL DEFAULT TRUE,
                    CONSTRAINT fk_horarios_salon
                        FOREIGN KEY (salon_id)
                        REFERENCES salones(id)
                        ON DELETE CASCADE,
                    CONSTRAINT uq_horario_salon
                        UNIQUE (salon_id, fecha, hora)
                );

                CREATE TABLE IF NOT EXISTS reservas (
                    id SERIAL PRIMARY KEY,
                    usuario_id INTEGER NOT NULL,
                    salon_id INTEGER NOT NULL,
                    servicio_id INTEGER NOT NULL,
                    horario_id INTEGER NOT NULL UNIQUE,
                    estado VARCHAR(50) NOT NULL DEFAULT 'confirmada',
                    fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    CONSTRAINT fk_reservas_usuario
                        FOREIGN KEY (usuario_id)
                        REFERENCES usuarios(id),
                    CONSTRAINT fk_reservas_salon
                        FOREIGN KEY (salon_id)
                        REFERENCES salones(id),
                    CONSTRAINT fk_reservas_servicio
                        FOREIGN KEY (servicio_id)
                        REFERENCES servicios(id),
                    CONSTRAINT fk_reservas_horario
                        FOREIGN KEY (horario_id)
                        REFERENCES horarios(id)
                );
                """
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
