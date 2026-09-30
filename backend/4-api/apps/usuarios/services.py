from django.db import IntegrityError, transaction

from . import repositories


class AsociadoDuplicado(Exception):
    """An email or identification is already assigned to an account."""


@transaction.atomic
def crear_asociado(**datos):
    if repositories.email_ya_registrado(datos["email"]):
        raise AsociadoDuplicado("An account with this email already exists.")
    if repositories.identificacion_ya_registrada(datos.get("identificacion")):
        raise AsociadoDuplicado(
            "An account with this identification already exists."
        )
    try:
        return repositories.crear_asociado(**datos)
    except IntegrityError as error:
        raise AsociadoDuplicado(
            "An account with the supplied unique fields already exists."
        ) from error
