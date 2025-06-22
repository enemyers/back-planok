from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .views import ProyectoInmobiliarioViewSet, UnidadPropiedadViewSet, UsuarioViewSet

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response({"success": True, "message": "Token válido", "user": str(request.user)})

router = DefaultRouter()
router.register(r'proyectos', ProyectoInmobiliarioViewSet)
router.register(r'unidades', UnidadPropiedadViewSet)
router.register(r'usuarios', UsuarioViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('test-token/', test_token, name='test_token'),
]
