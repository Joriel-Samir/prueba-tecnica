from django.urls import path

from .views import SolicitudRegistroView

urlpatterns = [
    path("", SolicitudRegistroView.as_view(), name="solicitud-registro"),
]
