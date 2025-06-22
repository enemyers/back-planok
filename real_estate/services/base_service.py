from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional, List
from django.db.models import Model, QuerySet

from ..repositories.base_repository import BaseRepository

T = TypeVar('T', bound=Model)

class BaseService(Generic[T], ABC):
    """
    Clase base abstracta para implementar servicios.
    Proporciona una interfaz común para todas las operaciones de negocio.
    
    Implementa el principio de Segregación de Interfaces (ISP) de SOLID,
    permitiendo que los clientes no dependan de interfaces que no utilizan.
    """
    
    def __init__(self, repository: BaseRepository[T]):
        """
        Constructor que recibe un repositorio como dependencia.
        Implementa el principio de Inversión de Dependencias (DIP) de SOLID.
        """
        self.repository = repository
    
    def get_all(self) -> QuerySet:
        """Obtiene todos los registros"""
        return self.repository.get_all()
    
    def get_by_id(self, id) -> Optional[T]:
        """Obtiene un registro por su ID"""
        return self.repository.get_by_id(id)
    
    def create(self, **kwargs) -> T:
        """
        Crea un nuevo registro.
        Antes de crear, se pueden realizar validaciones o lógica de negocio.
        """
        # Aquí se pueden realizar validaciones antes de crear
        return self.repository.create(**kwargs)
    
    def update(self, id, **kwargs) -> Optional[T]:
        """
        Actualiza un registro existente.
        Antes de actualizar, se pueden realizar validaciones o lógica de negocio.
        """
        instance = self.get_by_id(id)
        if not instance:
            return None
        
        # Aquí se pueden realizar validaciones antes de actualizar
        return self.repository.update(instance, **kwargs)
    
    def delete(self, id) -> bool:
        """
        Elimina un registro.
        Antes de eliminar, se pueden realizar validaciones o lógica de negocio.
        """
        instance = self.get_by_id(id)
        if not instance:
            return False
        
        # Aquí se pueden realizar validaciones antes de eliminar
        return self.repository.delete(instance)
    
    def filter(self, **kwargs) -> QuerySet:
        """Filtra registros según criterios"""
        return self.repository.filter(**kwargs)
