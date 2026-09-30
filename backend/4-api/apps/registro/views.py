from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import SolicitudRegistroSerializer


class SolicitudRegistroView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(
        request=SolicitudRegistroSerializer,
        responses={201: SolicitudRegistroSerializer},
    )
    def post(self, request):
        serializer = SolicitudRegistroSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        solicitud = serializer.save()
        return Response(SolicitudRegistroSerializer(solicitud).data, status=201)
