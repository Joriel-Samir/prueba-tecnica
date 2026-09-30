from django.urls import path

from .views import AsociadosView, CargaMasivaAsociadosView

urlpatterns = [
    path("asociados/", AsociadosView.as_view(), name="asociados"),
    path(
        "carga-masiva/asociados/",
        CargaMasivaAsociadosView.as_view(),
        name="carga-masiva-asociados",
    ),
]
