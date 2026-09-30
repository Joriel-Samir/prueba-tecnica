from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.bulk import process_bulk_upload
from apps.core.serializers import BulkResultSerializer, BulkUploadSerializer

from . import repositories
from .permissions import IsAdministrador
from .serializers import AsociadoSerializer


class AsociadosView(APIView):
    permission_classes = (IsAdministrador,)

    @extend_schema(responses=AsociadoSerializer(many=True))
    def get(self, request):
        serializer = AsociadoSerializer(repositories.listar_asociados(), many=True)
        return Response(serializer.data)

    @extend_schema(request=AsociadoSerializer, responses={201: AsociadoSerializer})
    def post(self, request):
        serializer = AsociadoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CargaMasivaAsociadosView(APIView):
    permission_classes = (IsAdministrador,)
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(
        request=BulkUploadSerializer,
        responses={200: BulkResultSerializer},
        description=(
            "Import CSV or XLSX rows; one invalid row does not abort valid rows."
        ),
    )
    def post(self, request):
        serializer = BulkUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = process_bulk_upload(
            serializer.validated_data["file"], AsociadoSerializer
        )
        return Response(result)
