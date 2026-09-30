from rest_framework import serializers

from apps.core.exceptions import APIConflict
from apps.usuarios.models import Asociado

from .services import ActividadSolapada, crear_actividad


class ActividadImportSerializer(serializers.Serializer):
    tipo = serializers.CharField(max_length=100)
    descripcion = serializers.CharField(required=False, allow_blank=True)
    fecha_inicio = serializers.DateTimeField()
    fecha_fin = serializers.DateTimeField()
    asociado = serializers.CharField()

    def validate_asociado(self, value):
        try:
            return Asociado.objects.get(email__iexact=value.strip())
        except Asociado.DoesNotExist as error:
            raise serializers.ValidationError(
                "No associate exists with this email."
            ) from error

    def validate(self, attrs):
        if attrs["fecha_fin"] <= attrs["fecha_inicio"]:
            raise serializers.ValidationError(
                {"fecha_fin": "Must be later than fecha_inicio."}
            )
        return attrs

    def create(self, validated_data):
        validated_data["creador"] = self.context["request"].user
        try:
            return crear_actividad(**validated_data)
        except ActividadSolapada as error:
            raise APIConflict(str(error)) from error
