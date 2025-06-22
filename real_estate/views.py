from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from django_filters.rest_framework import DjangoFilterBackend

# Importar modelos
from .models import Usuario, ProyectoInmobiliario, UnidadPropiedad

# Importar serializers
from .serializers import (
    UsuarioSerializer,
    ProyectoInmobiliarioSerializer,
    ProyectoInmobiliarioDetailSerializer,
    UnidadPropiedadSerializer,
    UnidadPropiedadDetailSerializer
)

# Importar servicios
from .services.usuario_service import UsuarioService
from .services.proyecto_service import ProyectoService
from .services.unidad_service import UnidadService

# Importar validadores
from .validators.usuario_validator import UsuarioValidator
from .validators.proyecto_validator import ProyectoValidator
from .validators.unidad_validator import UnidadValidator


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD en el modelo Usuario.
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


class ProyectoInmobiliarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD en el modelo ProyectoInmobiliario.
    Implementa el patrón de diseño Facade, proporcionando una interfaz simplificada
    para interactuar con el servicio y validador de ProyectoInmobiliario.
    """
    queryset = ProyectoInmobiliario.objects.all()
    serializer_class = ProyectoInmobiliarioSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['estado']
    search_fields = ['nombre', 'ubicacion', 'codigo']
    ordering_fields = ['nombre', 'fecha_inicio', 'created_at']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inyección de dependencias: principio de Inversión de Dependencias (DIP)
        self.service = ProyectoService()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProyectoInmobiliarioDetailSerializer
        return self.serializer_class
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()
    
    def create(self, request, *args, **kwargs):
        """
        Crea un nuevo proyecto inmobiliario utilizando el servicio y validador.
        Implementa el principio de Responsabilidad Única (SRP).
        """
        # Validar datos de entrada
        validator = ProyectoValidator(request.data)
        if not validator.is_valid():
            return Response(validator.get_error_dict(), status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Crear proyecto utilizando el servicio
            proyecto = self.service.create(**request.data)
            serializer = self.get_serializer(proyecto)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """
        Actualiza un proyecto inmobiliario existente utilizando el servicio y validador.
        Implementa el principio de Responsabilidad Única (SRP).
        """
        # Validar datos de entrada
        instance = self.get_object()
        validator = ProyectoValidator(request.data, instance=instance)
        if not validator.is_valid():
            return Response(validator.get_error_dict(), status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Actualizar proyecto utilizando el servicio
            proyecto = self.service.update(kwargs.get('pk'), **request.data)
            serializer = self.get_serializer(proyecto)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """
        Elimina un proyecto inmobiliario utilizando el servicio.
        Implementa el principio de Responsabilidad Única (SRP).
        """
        try:
            # Eliminar proyecto utilizando el servicio
            self.service.delete(kwargs.get('pk'))
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """
        Búsqueda avanzada de proyectos inmobiliarios.
        Utiliza el servicio para realizar la búsqueda, aplicando el principio de Delegación.
        """
        # Extraer parámetros de búsqueda
        search_params = {
            'nombre': request.query_params.get('nombre'),
            'ubicacion': request.query_params.get('ubicacion'),
            'precio_desde': request.query_params.get('precio_desde'),
            'precio_hasta': request.query_params.get('precio_hasta'),
            'codigo': request.query_params.get('codigo'),
            'id_proyecto': request.query_params.get('id')
        }
        
        # Delegar la búsqueda al servicio
        queryset = self.service.search_advanced(**search_params)
        
        # Paginar y serializar resultados
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Obtiene estadísticas de los proyectos inmobiliarios.
        Ejemplo de método que extiende la funcionalidad base.
        """
        # Delegar al servicio
        stats = self.service.get_estadisticas()
        return Response(stats)


class UnidadPropiedadViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD en el modelo UnidadPropiedad.
    Implementa el patrón de diseño Facade, proporcionando una interfaz simplificada
    para interactuar con el servicio y validador de UnidadPropiedad.
    """
    queryset = UnidadPropiedad.objects.all()
    serializer_class = UnidadPropiedadSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['proyecto', 'tipo_unidad', 'estado']
    search_fields = ['numero_unidad']
    ordering_fields = ['precio_venta', 'metraje_cuadrado', 'numero_unidad']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inyección de dependencias: principio de Inversión de Dependencias (DIP)
        self.service = UnidadService()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UnidadPropiedadDetailSerializer
        return self.serializer_class
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return super().get_permissions()
    
    def create(self, request, *args, **kwargs):
        """
        Crea una nueva unidad de propiedad utilizando el servicio y validador.
        Implementa el principio de Responsabilidad Única (SRP).
        """
        # Validar datos de entrada
        validator = UnidadValidator(request.data)
        if not validator.is_valid():
            return Response(validator.get_error_dict(), status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Crear unidad utilizando el servicio
            unidad = self.service.create(**request.data)
            serializer = self.get_serializer(unidad)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        """
        Actualiza una unidad de propiedad existente utilizando el servicio y validador.
        Implementa el principio de Responsabilidad Única (SRP).
        """
        # Validar datos de entrada
        instance = self.get_object()
        validator = UnidadValidator(request.data, instance=instance)
        if not validator.is_valid():
            return Response(validator.get_error_dict(), status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Actualizar unidad utilizando el servicio
            unidad = self.service.update(kwargs.get('pk'), **request.data)
            serializer = self.get_serializer(unidad)
            return Response(serializer.data)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        """
        Elimina una unidad de propiedad utilizando el servicio.
        Implementa el principio de Responsabilidad Única (SRP).
        """
        try:
            # Eliminar unidad utilizando el servicio
            self.service.delete(kwargs.get('pk'))
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def por_proyecto(self, request):
        """
        Obtiene todas las unidades de un proyecto específico.
        Utiliza el servicio para realizar la búsqueda, aplicando el principio de Delegación.
        """
        proyecto_id = request.query_params.get('proyecto_id')
        if not proyecto_id:
            return Response({"error": "Se requiere el ID del proyecto"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Delegar al servicio
        unidades = self.service.get_by_proyecto(proyecto_id)
        
        # Paginar y serializar resultados
        page = self.paginate_queryset(unidades)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(unidades, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        """
        Obtiene todas las unidades disponibles.
        Ejemplo de método que extiende la funcionalidad base.
        """
        # Delegar al servicio
        unidades = self.service.get_disponibles()
        
        # Paginar y serializar resultados
        page = self.paginate_queryset(unidades)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(unidades, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_tipo(self, request):
        """
        Obtiene todas las unidades de un tipo específico.
        Ejemplo de método que extiende la funcionalidad base.
        """
        tipo_unidad = request.query_params.get('tipo')
        if not tipo_unidad:
            return Response({"error": "Se requiere el tipo de unidad"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Delegar al servicio
        unidades = self.service.get_by_tipo(tipo_unidad)
        
        # Paginar y serializar resultados
        page = self.paginate_queryset(unidades)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(unidades, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def por_rango_precio(self, request):
        """
        Obtiene todas las unidades dentro de un rango de precios.
        Ejemplo de método que extiende la funcionalidad base.
        """
        precio_desde = request.query_params.get('desde')
        precio_hasta = request.query_params.get('hasta')
        
        if not precio_desde and not precio_hasta:
            return Response({"error": "Se requiere al menos un límite de precio"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Delegar al servicio
        unidades = self.service.get_by_rango_precio(precio_desde, precio_hasta)
        
        # Paginar y serializar resultados
        page = self.paginate_queryset(unidades)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(unidades, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def asignar_cliente(self, request, pk=None):
        """
        Asigna un cliente a una unidad y cambia su estado a 'Reservado'.
        Ejemplo de lógica de negocio en el controlador.
        """
        cliente_id = request.data.get('cliente_id')
        if not cliente_id:
            return Response({"error": "Se requiere el ID del cliente"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Delegar al servicio
        try:
            unidad = self.service.asignar_cliente(pk, cliente_id)
            if not unidad:
                return Response({"error": "No se pudo asignar el cliente a la unidad"}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = self.get_serializer(unidad)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def marcar_como_vendida(self, request, pk=None):
        """
        Marca una unidad como vendida.
        Ejemplo de lógica de negocio en el controlador.
        """
        # Delegar al servicio
        try:
            unidad = self.service.marcar_como_vendida(pk)
            if not unidad:
                return Response({"error": "No se pudo marcar la unidad como vendida"}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer = self.get_serializer(unidad)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def estadisticas_por_proyecto(self, request):
        """
        Obtiene estadísticas de las unidades de un proyecto.
        Ejemplo de método que extiende la funcionalidad base.
        """
        proyecto_id = request.query_params.get('proyecto_id')
        if not proyecto_id:
            return Response({"error": "Se requiere el ID del proyecto"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Delegar al servicio
        stats = self.service.get_estadisticas_por_proyecto(proyecto_id)
        return Response(stats)
