from typing import Optional
from django.db.models import QuerySet

from ..models import UnidadPropiedad
from .base_repository import BaseRepository


class UnidadRepository(BaseRepository[UnidadPropiedad]):
    """
    Repositorio para operaciones relacionadas con UnidadPropiedad.
    Implementa el patrón Repository y el principio de Responsabilidad Única (SRP).
    """
    
    def get_all(self) -> QuerySet:
        """Obtiene todas las unidades de propiedad"""
        return UnidadPropiedad.objects.all()
    
    def get_by_id(self, id) -> Optional[UnidadPropiedad]:
        """Obtiene una unidad de propiedad por su ID"""
        try:
            return UnidadPropiedad.objects.get(id=id)
        except UnidadPropiedad.DoesNotExist:
            return None
    
    def create(self, **kwargs) -> UnidadPropiedad:
        """Crea una nueva unidad de propiedad"""
        return UnidadPropiedad.objects.create(**kwargs)
    
    def update(self, instance: UnidadPropiedad, **kwargs) -> UnidadPropiedad:
        """Actualiza una unidad de propiedad existente"""
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save()
        return instance
    
    def delete(self, instance: UnidadPropiedad) -> bool:
        """Elimina una unidad de propiedad"""
        instance.delete()
        return True
    
    def filter(self, **kwargs) -> QuerySet:
        """Filtra unidades de propiedad según criterios"""
        return UnidadPropiedad.objects.filter(**kwargs)
    
    def get_by_proyecto(self, proyecto_id) -> QuerySet:
        """Obtiene todas las unidades de un proyecto específico"""
        return self.filter(proyecto_id=proyecto_id)
    
    def get_disponibles(self) -> QuerySet:
        """Obtiene todas las unidades disponibles"""
        return self.filter(estado='Disponible')
    
    def get_by_tipo(self, tipo_unidad) -> QuerySet:
        """Obtiene todas las unidades de un tipo específico"""
        return self.filter(tipo_unidad=tipo_unidad)
    
    def get_by_rango_precio(self, precio_desde, precio_hasta) -> QuerySet:
        """Obtiene todas las unidades dentro de un rango de precios"""
        queryset = self.get_all()
        
        if precio_desde:
            queryset = queryset.filter(precio_venta__gte=precio_desde)
        
        if precio_hasta:
            queryset = queryset.filter(precio_venta__lte=precio_hasta)
            
        return queryset
