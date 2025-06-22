from typing import Dict, Any
from django.db.models import QuerySet
import uuid

from ..models import ProyectoInmobiliario
from ..repositories.proyecto_repository import ProyectoRepository
from .base_service import BaseService


class ProyectoService(BaseService[ProyectoInmobiliario]):
    """
    Servicio para operaciones relacionadas con ProyectoInmobiliario.
    Implementa el principio de Abierto/Cerrado (OCP) de SOLID,
    permitiendo extender la funcionalidad sin modificar el código existente.
    """
    
    def __init__(self, repository: ProyectoRepository = None):
        """
        Constructor que inicializa el repositorio.
        Si no se proporciona un repositorio, crea uno nuevo.
        """
        if repository is None:
            repository = ProyectoRepository()
        super().__init__(repository)
        self.repository: ProyectoRepository = repository
    
    def search_advanced(self, **kwargs) -> QuerySet:
        """
        Búsqueda avanzada de proyectos inmobiliarios.
        Delega la implementación al repositorio.
        """
        return self.repository.search_advanced(
            nombre=kwargs.get('nombre'),
            ubicacion=kwargs.get('ubicacion'),
            precio_desde=kwargs.get('precio_desde'),
            precio_hasta=kwargs.get('precio_hasta'),
            codigo=kwargs.get('codigo'),
            id_proyecto=kwargs.get('id_proyecto')
        )
    
    def create(self, **kwargs) -> ProyectoInmobiliario:
        """
        Crea un nuevo proyecto inmobiliario.
        Genera un código único si no se proporciona.
        """
        if 'codigo' not in kwargs:
            # Generar un código único basado en el nombre y un UUID corto
            nombre_base = kwargs.get('nombre', '').split()[0][:3].upper()
            uuid_corto = str(uuid.uuid4())[:8]
            kwargs['codigo'] = f"{nombre_base}-{uuid_corto}"
        
        return super().create(**kwargs)
    
    def get_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de los proyectos inmobiliarios.
        Ejemplo de método que extiende la funcionalidad base.
        """
        proyectos = self.get_all()
        
        # Contar proyectos por estado
        estados = {}
        for proyecto in proyectos:
            if proyecto.estado in estados:
                estados[proyecto.estado] += 1
            else:
                estados[proyecto.estado] = 1
        
        # Calcular otras estadísticas
        total_proyectos = proyectos.count()
        proyectos_activos = proyectos.filter(estado='En Construcción').count()
        
        return {
            'total_proyectos': total_proyectos,
            'proyectos_por_estado': estados,
            'proyectos_activos': proyectos_activos
        }
