from django.db import DatabaseError, connection


def check_database() -> bool:
    """Devuelve True si la base de datos responde."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return True
    except DatabaseError:
        return False
