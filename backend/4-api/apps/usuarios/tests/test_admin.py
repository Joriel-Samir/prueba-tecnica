import pytest

from apps.usuarios.models import Administrador, Asociado


@pytest.mark.django_db
def test_administrador_ve_la_lista_de_asociados(client, administrador, asociado):
    client.force_login(administrador)

    response = client.get("/admin/usuarios/asociado/")

    assert response.status_code == 200


@pytest.mark.django_db
def test_asociado_no_puede_entrar_al_panel(client, asociado):
    client.force_login(asociado)

    response = client.get("/admin/usuarios/asociado/")

    assert response.status_code == 302  # lo manda al login del admin


@pytest.mark.django_db
def test_asociado_con_is_staff_igual_recibe_403(client, asociado):
    asociado.is_staff = True
    asociado.save()
    client.force_login(asociado)

    response = client.get("/admin/usuarios/asociado/")

    assert response.status_code == 403


@pytest.mark.django_db
def test_administrador_crea_un_asociado_desde_el_panel(client, administrador, password):
    client.force_login(administrador)
    datos = {
        "email": "nuevo@example.com",
        "nombre": "Nuevo",
        "apellidos": "Asociado",
        "identificacion": "1001",
        "ciudad": "Cartagena",
        "password1": password,
        "password2": password,
    }

    response = client.post("/admin/usuarios/asociado/add/", datos)

    assert response.status_code == 302
    assert Asociado.objects.filter(email="nuevo@example.com").exists()


@pytest.mark.django_db
def test_administrador_crea_otro_administrador_y_queda_como_staff(
    client, administrador, password
):
    client.force_login(administrador)
    datos = {
        "email": "otro@example.com",
        "nombre": "Otro",
        "apellidos": "Admin",
        "identificacion": "2002",
        "ciudad": "Bogotá",
        "password1": password,
        "password2": password,
    }

    response = client.post("/admin/usuarios/administrador/add/", datos)

    assert response.status_code == 302
    assert Administrador.objects.get(email="otro@example.com").is_staff is True


@pytest.mark.django_db
def test_administrador_abre_el_formulario_de_edicion(client, administrador, asociado):
    client.force_login(administrador)

    response = client.get(f"/admin/usuarios/asociado/{asociado.pk}/change/")

    assert response.status_code == 200
