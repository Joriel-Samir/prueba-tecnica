from rest_framework import serializers

from apps.core.exceptions import APIConflict

from .models import SolicitudRegistro
from .services import (
    EmailYaRegistrado,
    SolicitudPendienteExistente,
    crear_solicitud_registro,
)


class SolicitudRegistroSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8, max_length=128)

    class Meta:
        model = SolicitudRegistro
        fields = ("id", "nombre", "email", "password", "estado", "fecha_solicitud")
        read_only_fields = ("id", "estado", "fecha_solicitud")

    def create(self, validated_data):
        try:
            return crear_solicitud_registro(**validated_data)
        except (EmailYaRegistrado, SolicitudPendienteExistente) as error:
            raise APIConflict(str(error)) from error
