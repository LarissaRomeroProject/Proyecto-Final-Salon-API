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
                -- =========================================
                -- USUARIOS
                -- =========================================
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    nombre VARCHAR(150) NOT NULL,
                    correo VARCHAR(255) NOT NULL UNIQUE,
                    password TEXT NOT NULL
                );


                -- =========================================
                -- SALONES
                -- =========================================
                CREATE TABLE IF NOT EXISTS salones (
                    id SERIAL PRIMARY KEY,
                    usuario_id INTEGER NOT NULL UNIQUE,
                    nombre VARCHAR(150) NOT NULL,
                    telefono VARCHAR(20) NOT NULL,
                    direccion TEXT NOT NULL,
                    descripcion TEXT,
                    imagen TEXT,

                    CONSTRAINT fk_salones_usuarios
                        FOREIGN KEY (usuario_id)
                        REFERENCES usuarios(id)
                        ON DELETE CASCADE
                );


                -- =========================================
                -- SERVICIOS
                -- =========================================
                CREATE TABLE IF NOT EXISTS servicios (
                    id SERIAL PRIMARY KEY,
                    salon_id INTEGER NOT NULL,
                    nombre VARCHAR(150) NOT NULL,
                    descripcion VARCHAR(500),
                    precio NUMERIC(10, 2) NOT NULL,
                    duracion_minutos INTEGER NOT NULL,
                    activo BOOLEAN NOT NULL DEFAULT TRUE,

                    CONSTRAINT fk_servicios_salones
                        FOREIGN KEY (salon_id)
                        REFERENCES salones(id)
                        ON DELETE CASCADE,

                    CONSTRAINT ck_servicios_precio
                        CHECK (precio >= 0),

                    CONSTRAINT ck_servicios_duracion
                        CHECK (duracion_minutos > 0)
                );


                -- =========================================
                -- HORARIOS SEMANALES DEL SALÓN
                -- =========================================
                CREATE TABLE IF NOT EXISTS horarios (
                    id SERIAL PRIMARY KEY,
                    salon_id INTEGER NOT NULL,
                    dia_semana VARCHAR(20) NOT NULL,
                    hora_apertura TIME,
                    hora_cierre TIME,
                    cerrado BOOLEAN NOT NULL DEFAULT FALSE,

                    CONSTRAINT fk_horarios_salones
                        FOREIGN KEY (salon_id)
                        REFERENCES salones(id)
                        ON DELETE CASCADE,

                    CONSTRAINT uq_horarios_salon_dia
                        UNIQUE (salon_id, dia_semana),

                    CONSTRAINT ck_horarios_dia
                        CHECK (
                            dia_semana IN (
                                'lunes',
                                'martes',
                                'miercoles',
                                'jueves',
                                'viernes',
                                'sabado',
                                'domingo'
                            )
                        ),

                    CONSTRAINT ck_horarios_horas
                        CHECK (
                            cerrado = TRUE
                            OR (
                                hora_apertura IS NOT NULL
                                AND hora_cierre IS NOT NULL
                                AND hora_cierre > hora_apertura
                            )
                        )
                );


                -- =========================================
                -- RESERVAS
                -- =========================================
                CREATE TABLE IF NOT EXISTS reservas (
                    id SERIAL PRIMARY KEY,
                    salon_id INTEGER NOT NULL,
                    servicio_id INTEGER,
                    fecha DATE NOT NULL,
                    hora TIME,

                    nombre_cliente VARCHAR(150),
                    correo_cliente VARCHAR(255),
                    telefono_cliente VARCHAR(30),

                    estado VARCHAR(30)
                        NOT NULL
                        DEFAULT 'pendiente',

                    fecha_creacion TIMESTAMP
                        NOT NULL
                        DEFAULT CURRENT_TIMESTAMP,

                    CONSTRAINT fk_reservas_salones
                        FOREIGN KEY (salon_id)
                        REFERENCES salones(id)
                        ON DELETE CASCADE,

                    CONSTRAINT fk_reservas_servicios
                        FOREIGN KEY (servicio_id)
                        REFERENCES servicios(id)
                        ON DELETE SET NULL,

                    CONSTRAINT ck_reservas_estado
                        CHECK (
                            estado IN (
                                'pendiente',
                                'aceptada',
                                'completada',
                                'anulada'
                            )
                        )
                );


                -- =========================================
                -- ÍNDICES
                -- =========================================
                CREATE INDEX IF NOT EXISTS idx_servicios_salon
                    ON servicios(salon_id);

                CREATE INDEX IF NOT EXISTS idx_horarios_salon
                    ON horarios(salon_id);

                CREATE INDEX IF NOT EXISTS idx_reservas_salon
                    ON reservas(salon_id);

                CREATE INDEX IF NOT EXISTS idx_reservas_fecha
                    ON reservas(fecha);

                CREATE INDEX IF NOT EXISTS idx_reservas_estado
                    ON reservas(estado);
                """
            )

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()