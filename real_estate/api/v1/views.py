from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from real_estate.models import Usuario
from real_estate.serializers import UsuarioSerializer
from real_estate.services.usuario_service import UsuarioService
from real_estate.validators.usuario_validator import UsuarioValidator


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    API v1: ViewSet para operaciones CRUD en el modelo Usuario.
    Implementa el patrón de diseño Facade, proporcionando una interfaz simplificada
    para interactuar con el servicio y validador de Usuario.
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active']
    search_fields = ['rut', 'email', 'first_name', 'last_name']
    ordering_fields = ['last_name', 'first_name', 'created_at']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inyección de dependencias: principio de Inversión de Dependencias (DIP)
        self.service = UsuarioService()
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()
    
    def create(self, request, *args, **kwargs):
        """
        Crea un nuevo usuario utilizando el servicio y validador.
        Implementa el principio de Responsabilidad Única (SRP).
        """
        # Validar datos de entrada
        validator = UsuarioValidator(request.data)
        if not validator.is_valid():
            return Response(validator.get_error_dict(), status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Crear usuario utilizando el servicio
            usuario = self.service.create(**request.data)
            serializer = self.get_serializer(usuario)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """
        Actualiza un usuario existente utilizando el servicio y validador.
        Implementa el principio de Responsabilidad Única (SRP).
        """
        # Validar datos de entrada
        instance = self.get_object()
        validator = UsuarioValidator(request.data, instance=instance)
        if not validator.is_valid():
            return Response(validator.get_error_dict(), status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Actualizar usuario utilizando el servicio
            usuario = self.service.update(kwargs.get('pk'), **request.data)
            serializer = self.get_serializer(usuario)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """
        Elimina un usuario utilizando el servicio.
        Implementa el principio de Responsabilidad Única (SRP).
        """
        try:
            # Eliminar usuario utilizando el servicio
            self.service.delete(kwargs.get('pk'))
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def clientes(self, request):
        """
        Obtiene todos los usuarios con rol de Cliente.
        Ejemplo de método que extiende la funcionalidad base.
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
        Ejemplo de método que extiende la funcionalidad base.
        """
        administradores = self.service.get_administradores()
        page = self.paginate_queryset(administradores)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(administradores, many=True)
        return Response(serializer.data)
