import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "salon_belleza.db"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_tables() -> None:
    connection = get_connection()

    try:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                correo TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS salones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                direccion TEXT NOT NULL,
                descripcion TEXT,
                imagen TEXT
            );

            CREATE TABLE IF NOT EXISTS servicios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                salon_id INTEGER NOT NULL,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                precio REAL NOT NULL,
                duracion_minutos INTEGER NOT NULL,
                FOREIGN KEY (salon_id)
                    REFERENCES salones(id)
                    ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS horarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                salon_id INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                hora TEXT NOT NULL,
                disponible INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (salon_id)
                    REFERENCES salones(id)
                    ON DELETE CASCADE,
                UNIQUE (salon_id, fecha, hora)
            );

            CREATE TABLE IF NOT EXISTS reservas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                salon_id INTEGER NOT NULL,
                servicio_id INTEGER NOT NULL,
                horario_id INTEGER NOT NULL UNIQUE,
                estado TEXT NOT NULL DEFAULT 'confirmada',
                fecha_creacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                FOREIGN KEY (salon_id) REFERENCES salones(id),
                FOREIGN KEY (servicio_id) REFERENCES servicios(id),
                FOREIGN KEY (horario_id) REFERENCES horarios(id)
            );
            """
        )

        connection.commit()

    finally:
        connection.close()
