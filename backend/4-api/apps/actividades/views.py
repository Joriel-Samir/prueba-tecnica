from django.utils.dateparse import parse_date
from rest_framework import serializers, viewsets
from rest_framework.exceptions import PermissionDenied

from . import repositories
from .permissions import ActividadPermission
from .serializers import ActividadSerializer


class ActividadViewSet(viewsets.ModelViewSet):
    serializer_class = ActividadSerializer
    permission_classes = (ActividadPermission,)

    def get_queryset(self):
        user = self.request.user
        queryset = repositories.actividades_visibles_para(user).select_related(
            "asociado", "creador"
        )
        desde = self.request.query_params.get("desde")
        hasta = self.request.query_params.get("hasta")
        fecha_desde = self._parsear_fecha("desde", desde)
        fecha_hasta = self._parsear_fecha("hasta", hasta)
        if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
            raise serializers.ValidationError(
                {"hasta": "Debe ser igual o posterior a desde."}
            )
        if fecha_desde:
            queryset = queryset.filter(fecha_inicio__date__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_inicio__date__lte=fecha_hasta)
        return queryset

    @staticmethod
    def _parsear_fecha(parametro, valor):
        if valor is None:
            return None
        fecha = parse_date(valor)
        if fecha is None:
            raise serializers.ValidationError(
                {parametro: "Usa el formato ISO YYYY-MM-DD."}
            )
        return fecha

    def perform_create(self, serializer):
        user = self.request.user
        asociado = serializer.validated_data["asociado"]
        if not getattr(user, "es_administrador", False) and asociado.pk != user.pk:
            raise PermissionDenied(
                "Un asociado solo puede crear actividades para sí mismo."
            )
        serializer.save(creador=user)
