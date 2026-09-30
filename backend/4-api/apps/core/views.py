from drf_spectacular.utils import extend_schema
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response

from .serializers import HealthResponseSerializer
from .services import check_database


@extend_schema(responses=HealthResponseSerializer)
@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def health(request):
    db_ok = check_database()
    body = {
        "status": "ok" if db_ok else "error",
        "database": "ok" if db_ok else "error",
    }
    return Response(body, status=200 if db_ok else 503)
