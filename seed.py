from werkzeug.security import generate_password_hash

from backend.database import create_tables, get_connection


def seed_database():
    create_tables()

    connection = get_connection()

    try:
        usuario = connection.execute(
            "SELECT id FROM usuarios WHERE correo = ?",
            ("larissa@salon.com",),
        ).fetchone()

        if usuario is None:
            connection.execute(
                """
                INSERT INTO usuarios (nombre, correo, password)
                VALUES (?, ?, ?)
                """,
                (
                    "Larissa Romero",
                    "larissa@salon.com",
                    generate_password_hash("123456"),
                ),
            )

            connection.commit()
            print("Usuario creado correctamente.")
        else:
            print("El usuario ya existe.")

    finally:
        connection.close()


if __name__ == "__main__":
    seed_database()