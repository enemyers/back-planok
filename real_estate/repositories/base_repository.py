from abc import ABC, abstractmethod
from typing import Optional, TypeVar, Generic
from django.db.models import Model, QuerySet

T = TypeVar('T', bound=Model)

class BaseRepository(Generic[T], ABC):
    """
    Clase base abstracta para implementar el patrón Repository.
    Proporciona una interfaz común para todas las operaciones de acceso a datos.
    
    Implementa el principio de Inversión de Dependencias (DIP) de SOLID,
    permitiendo que las clases de alto nivel dependan de abstracciones
    y no de implementaciones concretas.
    """
    
    @abstractmethod
    def get_all(self) -> QuerySet:
        """Obtiene todos los registros"""
        pass
    
    @abstractmethod
    def get_by_id(self, id) -> Optional[T]:
        """Obtiene un registro por su ID"""
        pass
    
    @abstractmethod
    def create(self, **kwargs) -> T:
        """Crea un nuevo registro"""
        pass
    
    @abstractmethod
    def update(self, instance: T, **kwargs) -> T:
        """Actualiza un registro existente"""
        pass
    
    @abstractmethod
    def delete(self, instance: T) -> bool:
        """Elimina un registro"""
        pass
    
    @abstractmethod
    def filter(self, **kwargs) -> QuerySet:
        """Filtra registros según criterios"""
        pass
