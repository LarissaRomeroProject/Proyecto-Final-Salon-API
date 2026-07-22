from werkzeug.security import generate_password_hash

from database import create_tables, get_connection


def seed_database():
    create_tables()

    connection = get_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM usuarios
                WHERE correo = %s
                """,
                ("larissa@salon.com",),
            )

            usuario = cursor.fetchone()

            if usuario is None:
                cursor.execute(
                    """
                    INSERT INTO usuarios (nombre, correo, password)
                    VALUES (%s, %s, %s)
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

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    seed_database()
