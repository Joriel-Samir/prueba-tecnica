from rest_framework import serializers

from apps.core.exceptions import APIConflict

from .models import Asociado
from .services import AsociadoDuplicado, crear_asociado


class AsociadoSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Asociado
        extra_kwargs = {
            "email": {"validators": []},
            "identificacion": {"validators": []},
        }
        fields = (
            "id",
            "identificacion",
            "nombre",
            "apellidos",
            "email",
            "ciudad",
            "password",
        )
        read_only_fields = ("id",)

    def create(self, validated_data):
        try:
            return crear_asociado(**validated_data)
        except AsociadoDuplicado as error:
            raise APIConflict(str(error)) from error
