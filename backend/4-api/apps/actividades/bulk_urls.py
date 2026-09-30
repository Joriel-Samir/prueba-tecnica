from django.urls import path

from .bulk_views import CargaMasivaActividadesView

urlpatterns = [
    path("", CargaMasivaActividadesView.as_view(), name="carga-masiva-actividades"),
]
