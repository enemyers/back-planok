from typing import Optional, Dict, Any
from django.db.models import QuerySet, Avg, Min, Max, Count

from ..models import UnidadPropiedad
from ..repositories.unidad_repository import UnidadRepository
from .base_service import BaseService


class UnidadService(BaseService[UnidadPropiedad]):
    """
    Servicio para operaciones relacionadas con UnidadPropiedad.
    Implementa el principio de Abierto/Cerrado (OCP) de SOLID,
    permitiendo extender la funcionalidad sin modificar el código existente.
    """
    
    def __init__(self, repository: UnidadRepository = None):
        """
        Constructor que inicializa el repositorio.
        Si no se proporciona un repositorio, crea uno nuevo.
        """
        if repository is None:
            repository = UnidadRepository()
        super().__init__(repository)
        self.repository: UnidadRepository = repository
    
    def get_by_proyecto(self, proyecto_id) -> QuerySet:
        """Obtiene todas las unidades de un proyecto específico"""
        return self.repository.get_by_proyecto(proyecto_id)
    
    def get_disponibles(self) -> QuerySet:
        """Obtiene todas las unidades disponibles"""
        return self.repository.get_disponibles()
    
    def get_by_tipo(self, tipo_unidad) -> QuerySet:
        """Obtiene todas las unidades de un tipo específico"""
        return self.repository.get_by_tipo(tipo_unidad)
    
    def get_by_rango_precio(self, precio_desde, precio_hasta) -> QuerySet:
        """Obtiene todas las unidades dentro de un rango de precios"""
        return self.repository.get_by_rango_precio(precio_desde, precio_hasta)
    
    def asignar_cliente(self, unidad_id, cliente_id) -> Optional[UnidadPropiedad]:
        """
        Asigna un cliente a una unidad y cambia su estado a 'Reservado'.
        Ejemplo de lógica de negocio en el servicio.
        
        Raises:
            UnidadNoDisponibleError: Si la unidad no está disponible
        """
        from ..exceptions import UnidadNoDisponibleError
        
        unidad = self.get_by_id(unidad_id)
        if not unidad or unidad.estado != 'Disponible':
            raise UnidadNoDisponibleError()
        
        return self.update(unidad_id, cliente_id=cliente_id, estado='Reservado')
    
    def marcar_como_vendida(self, unidad_id) -> Optional[UnidadPropiedad]:
        """
        Marca una unidad como vendida.
        Ejemplo de lógica de negocio en el servicio.
        
        Raises:
            UnidadNoDisponibleError: Si la unidad no está reservada
            ClienteNoValidoError: Si la unidad no tiene cliente asignado
        """
        from ..exceptions import UnidadNoDisponibleError, ClienteNoValidoError
        
        unidad = self.get_by_id(unidad_id)
        if not unidad:
            raise UnidadNoDisponibleError()
        if unidad.estado != 'Reservado':
            raise UnidadNoDisponibleError()
        if not unidad.cliente_id:
            raise ClienteNoValidoError()
        
        return self.update(unidad_id, estado='Vendido')
    
    def get_estadisticas_por_proyecto(self, proyecto_id) -> Dict[str, Any]:
        """
        Obtiene estadísticas de las unidades de un proyecto.
        Ejemplo de método que extiende la funcionalidad base.
        """
        unidades = self.get_by_proyecto(proyecto_id)
        
        # Estadísticas de precios
        stats = unidades.aggregate(
            precio_promedio=Avg('precio_venta'),
            precio_minimo=Min('precio_venta'),
            precio_maximo=Max('precio_venta'),
            total_unidades=Count('id')
        )
        
        # Contar unidades por estado
        estados = {}
        for unidad in unidades:
            if unidad.estado in estados:
                estados[unidad.estado] += 1
            else:
                estados[unidad.estado] = 1
        
        # Contar unidades por tipo
        tipos = {}
        for unidad in unidades:
            if unidad.tipo_unidad in tipos:
                tipos[unidad.tipo_unidad] += 1
            else:
                tipos[unidad.tipo_unidad] = 1
        
        stats['unidades_por_estado'] = estados
        stats['unidades_por_tipo'] = tipos
        
        return stats
