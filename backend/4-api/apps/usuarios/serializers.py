from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.core.exceptions import APIConflict

from .models import Asociado
from .services import AsociadoDuplicado, crear_asociado


class IhungoTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = (
            'admin' if getattr(user, 'es_administrador', False) else 'associate'
        )
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = (
            'admin'
            if getattr(self.user, 'es_administrador', False)
            else 'associate'
        )
        return data


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
