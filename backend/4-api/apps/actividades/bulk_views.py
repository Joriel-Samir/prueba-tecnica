from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.bulk import process_bulk_upload
from apps.core.serializers import BulkResultSerializer, BulkUploadSerializer
from apps.usuarios.permissions import IsAdministrador

from .bulk_serializers import ActividadImportSerializer


class CargaMasivaActividadesView(APIView):
    permission_classes = (IsAdministrador,)
    parser_classes = (MultiPartParser, FormParser)

    @extend_schema(
        request=BulkUploadSerializer,
        responses={200: BulkResultSerializer},
        description=(
            "Import CSV or XLSX activity rows. The asociado column must contain "
            "the associate email. Valid rows are retained if another row fails."
        ),
    )
    def post(self, request):
        serializer = BulkUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = process_bulk_upload(
            serializer.validated_data["file"],
            ActividadImportSerializer,
            context={"request": request},
        )
        return Response(result, status=status.HTTP_200_OK)
