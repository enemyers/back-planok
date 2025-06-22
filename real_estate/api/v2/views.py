from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q

from real_estate.models import Usuario
from real_estate.serializers_v2 import UsuarioSerializerV2, UsuarioCreateSerializerV2
from real_estate.services.usuario_service import UsuarioService
from real_estate.validators.usuario_validator import UsuarioValidator


class UsuarioViewSetV2(viewsets.ModelViewSet):
    """
    API v2: ViewSet mejorado para operaciones CRUD en el modelo Usuario.
    Incluye funcionalidades adicionales como estadísticas, búsqueda avanzada
    y serializers específicos para diferentes operaciones.
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializerV2
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active']
    search_fields = ['rut', 'email', 'first_name', 'last_name']
    ordering_fields = ['last_name', 'first_name', 'created_at', 'last_login']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = UsuarioService()
    
    def get_serializer_class(self):
        """
        Retorna diferentes serializers según la acción.
        """
        if self.action == 'create':
            return UsuarioCreateSerializerV2
        return UsuarioSerializerV2
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()
    
    def create(self, request, *args, **kwargs):
        """
        Crea un nuevo usuario con validación mejorada.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        """
        Actualiza un usuario existente con validación mejorada.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """
        Elimina un usuario o lo marca como inactivo según configuración.
        """
        instance = self.get_object()
        
        # Opción de soft delete (marcar como inactivo)
        soft_delete = request.query_params.get('soft_delete', 'true').lower() == 'true'
        
        if soft_delete:
            instance.is_active = False
            instance.save()
            return Response({"detail": "Usuario marcado como inactivo."}, status=status.HTTP_200_OK)
        else:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def clientes(self, request):
        """
        Obtiene todos los usuarios con rol de Cliente.
        """
        clientes = self.service.get_clientes()
        page = self.paginate_queryset(clientes)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(clientes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def administradores(self, request):
        """
        Obtiene todos los usuarios con rol de Administrador.
        """
        administradores = self.service.get_administradores()
        page = self.paginate_queryset(administradores)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(administradores, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Nueva funcionalidad V2: Obtiene estadísticas de usuarios.
        """
        total_usuarios = Usuario.objects.count()
        total_activos = Usuario.objects.filter(is_active=True).count()
        total_clientes = Usuario.objects.filter(role='cliente').count()
        total_administradores = Usuario.objects.filter(role='admin').count()
        
        return Response({
            'total_usuarios': total_usuarios,
            'total_activos': total_activos,
            'total_clientes': total_clientes,
            'total_administradores': total_administradores,
            'porcentaje_activos': (total_activos / total_usuarios * 100) if total_usuarios > 0 else 0
        })
    
    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """
        Nueva funcionalidad V2: Activa un usuario inactivo.
        """
        usuario = self.get_object()
        if usuario.is_active:
            return Response({"detail": "El usuario ya está activo."}, status=status.HTTP_400_BAD_REQUEST)
        
        usuario.is_active = True
        usuario.save()
        serializer = self.get_serializer(usuario)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """
        Nueva funcionalidad V2: Desactiva un usuario activo.
        """
        usuario = self.get_object()
        if not usuario.is_active:
            return Response({"detail": "El usuario ya está inactivo."}, status=status.HTTP_400_BAD_REQUEST)
        
        usuario.is_active = False
        usuario.save()
        serializer = self.get_serializer(usuario)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def busqueda_avanzada(self, request):
        """
        Nueva funcionalidad V2: Búsqueda avanzada de usuarios.
        """
        # Parámetros de búsqueda
        role = request.query_params.get('role')
        is_active = request.query_params.get('is_active')
        created_after = request.query_params.get('created_after')
        created_before = request.query_params.get('created_before')
        search_term = request.query_params.get('q')
        
        # Iniciar con todos los usuarios
        queryset = Usuario.objects.all()
        
        # Aplicar filtros si están presentes
        if role:
            queryset = queryset.filter(role=role)
        
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
        
        if created_after:
            queryset = queryset.filter(created_at__gte=created_after)
        
        if created_before:
            queryset = queryset.filter(created_at__lte=created_before)
        
        if search_term:
            queryset = queryset.filter(
                Q(first_name__icontains=search_term) | 
                Q(last_name__icontains=search_term) | 
                Q(email__icontains=search_term) |
                Q(rut__icontains=search_term)
            )
        
        # Paginar y serializar resultados
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
