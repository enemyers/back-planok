from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import UsuarioViewSetV2

# API v2
router_v2 = DefaultRouter()
router_v2.register(r'usuarios', UsuarioViewSetV2)

urlpatterns = [
    path('', include(router_v2.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair_v2'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh_v2'),
]
