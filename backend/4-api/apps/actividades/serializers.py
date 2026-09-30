from rest_framework import serializers

from .models import Actividad
from .services import ActividadSolapada, actualizar_actividad, crear_actividad


class ActividadSerializer(serializers.ModelSerializer):
    creador = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Actividad
        fields = (
            "id",
            "tipo",
            "descripcion",
            "fecha_inicio",
            "fecha_fin",
            "asociado",
            "creador",
        )
        read_only_fields = ("id", "creador")

    def validate(self, attrs):
        fecha_inicio = attrs.get(
            "fecha_inicio", getattr(self.instance, "fecha_inicio", None)
        )
        fecha_fin = attrs.get("fecha_fin", getattr(self.instance, "fecha_fin", None))
        if fecha_inicio is not None and fecha_fin is not None:
            if fecha_fin <= fecha_inicio:
                raise serializers.ValidationError(
                    {"fecha_fin": "Debe ser posterior a fecha_inicio."}
                )
        return attrs

    def create(self, validated_data):
        try:
            return crear_actividad(**validated_data)
        except ActividadSolapada as error:
            raise serializers.ValidationError(
                {"non_field_errors": [str(error)]}
            ) from error
        except ValueError as error:
            raise serializers.ValidationError({"fecha_fin": str(error)}) from error

    def update(self, instance, validated_data):
        try:
            return actualizar_actividad(instance, validated_data)
        except ActividadSolapada as error:
            raise serializers.ValidationError(
                {"non_field_errors": [str(error)]}
            ) from error
        except ValueError as error:
            raise serializers.ValidationError({"fecha_fin": str(error)}) from error
