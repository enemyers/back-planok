from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import UsuarioViewSet

# Crear router para la API v1
router_v1 = DefaultRouter()
router_v1.register(r'usuarios', UsuarioViewSet)

urlpatterns = [
    path('', include(router_v1.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair_v1'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh_v1'),
]
