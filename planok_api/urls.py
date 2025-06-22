"""
URL configuration for planok_api project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.generic import RedirectView

# Swagger documentation
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="PlanOk API",
        default_version='v1',
        description="API para la gestión de proyectos inmobiliarios",
        terms_of_service="https://www.planok.com/terms/",
        contact=openapi.Contact(email="contact@planok.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Importar decorador para eximir de autenticación
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny

# Crear vistas personalizadas para Swagger que no requieran autenticación
@authentication_classes([])
@permission_classes([AllowAny])
def swagger_ui(request, *args, **kwargs):
    return schema_view.with_ui('swagger', cache_timeout=0)(request, *args, **kwargs)

@authentication_classes([])
@permission_classes([AllowAny])
def redoc_ui(request, *args, **kwargs):
    return schema_view.with_ui('redoc', cache_timeout=0)(request, *args, **kwargs)

@authentication_classes([])
@permission_classes([AllowAny])
def schema_json(request, *args, **kwargs):
    return schema_view.without_ui(cache_timeout=0)(request, *args, **kwargs)

urlpatterns = [
    # Redirección desde la raíz a Swagger
    path('', RedirectView.as_view(url='/swagger/', permanent=False), name='index'),
    
    path("admin/", admin.site.urls),
    
    # API v1 (original - mantener para compatibilidad)
    path("api/v1/", include('real_estate.urls')),
    
    # API v1 para usuarios (versionada - misma estructura que la original)
    path("api/v1/", include('real_estate.api.v1.urls')),
    
    # API v2 para usuarios (nueva versión - misma estructura pero en v2)
    path("api/v2/", include('real_estate.api.v2.urls')),
    
    # Swagger documentation URLs con vistas personalizadas sin autenticación
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_json, name='schema-json'),
    path('swagger/', swagger_ui, name='schema-swagger-ui'),
    path('redoc/', redoc_ui, name='schema-redoc'),
]
