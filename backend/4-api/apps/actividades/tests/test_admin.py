import pytest


@pytest.mark.django_db
def test_administrador_ve_las_actividades_en_el_panel(client, administrador):
    client.force_login(administrador)

    assert client.get("/admin/actividades/actividad/").status_code == 200
    assert client.get("/admin/actividades/actividad/add/").status_code == 200


@pytest.mark.django_db
def test_asociado_no_ve_las_actividades_en_el_panel(client, asociado):
    asociado.is_staff = True
    asociado.save()
    client.force_login(asociado)

    assert client.get("/admin/actividades/actividad/").status_code == 403
