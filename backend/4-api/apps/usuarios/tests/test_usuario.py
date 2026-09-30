import pytest
from django.db import IntegrityError

from apps.usuarios.models import Administrador, Asociado, Usuario


def test_crear_usuario_con_email_y_password_encriptada(db, password):
    usuario = Usuario.objects.create_user(email="Ana@Example.com", password=password)

    assert usuario.email == "Ana@example.com"
    assert usuario.check_password(password)
    assert usuario.password != password
    assert usuario.is_staff is False


def test_crear_usuario_sin_email_falla(db, password):
    with pytest.raises(ValueError):
        Usuario.objects.create_user(email="", password=password)


def test_el_email_es_el_identificador_de_login():
    assert Usuario.USERNAME_FIELD == "email"


def test_el_email_no_se_puede_repetir(db, password):
    Usuario.objects.create_user(email="ana@example.com", password=password)

    with pytest.raises(IntegrityError):
        Usuario.objects.create_user(email="ana@example.com", password=password)


def test_nombre_completo(asociado):
    assert asociado.get_full_name() == "Ana Pérez"


def test_asociado_no_es_staff_ni_administrador(asociado):
    assert asociado.is_staff is False
    assert asociado.es_asociado is True
    assert asociado.es_administrador is False


def test_administrador_es_staff_aunque_no_se_indique(administrador):
    assert administrador.is_staff is True
    assert administrador.es_administrador is True
    assert administrador.es_asociado is False


def test_administrador_y_asociado_son_entidades_separadas(administrador, asociado):
    assert Usuario.objects.count() == 2
    assert Administrador.objects.count() == 1
    assert Asociado.objects.count() == 1


def test_crear_superusuario_crea_un_administrador(db, password):
    admin = Usuario.objects.create_superuser(
        email="root@example.com", password=password
    )

    assert isinstance(admin, Administrador)
    assert admin.is_superuser is True
    assert admin.is_staff is True
    assert admin.es_administrador is True
