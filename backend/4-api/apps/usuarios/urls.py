from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import IhungoTokenObtainPairSerializer


class IhungoTokenObtainPairView(TokenObtainPairView):
    serializer_class = IhungoTokenObtainPairSerializer

urlpatterns = [
    path('token/', IhungoTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
