from typing import Optional
from django.db.models import QuerySet, Q

from ..models import ProyectoInmobiliario
from .base_repository import BaseRepository


class ProyectoRepository(BaseRepository[ProyectoInmobiliario]):
    """
    Repositorio para operaciones relacionadas con ProyectoInmobiliario.
    Implementa el patrón Repository y el principio de Responsabilidad Única (SRP).
    """
    
    def get_all(self) -> QuerySet:
        """Obtiene todos los proyectos inmobiliarios"""
        return ProyectoInmobiliario.objects.all()
    
    def get_by_id(self, id) -> Optional[ProyectoInmobiliario]:
        """Obtiene un proyecto inmobiliario por su ID"""
        try:
            return ProyectoInmobiliario.objects.get(id=id)
        except ProyectoInmobiliario.DoesNotExist:
            return None
    
    def create(self, **kwargs) -> ProyectoInmobiliario:
        """Crea un nuevo proyecto inmobiliario"""
        return ProyectoInmobiliario.objects.create(**kwargs)
    
    def update(self, instance: ProyectoInmobiliario, **kwargs) -> ProyectoInmobiliario:
        """Actualiza un proyecto inmobiliario existente"""
        for key, value in kwargs.items():
            setattr(instance, key, value)
        instance.save()
        return instance
    
    def delete(self, instance: ProyectoInmobiliario) -> bool:
        """Elimina un proyecto inmobiliario"""
        instance.delete()
        return True
    
    def filter(self, **kwargs) -> QuerySet:
        """Filtra proyectos inmobiliarios según criterios"""
        return ProyectoInmobiliario.objects.filter(**kwargs)
    
    def search_advanced(self, nombre=None, ubicacion=None, precio_desde=None, 
                        precio_hasta=None, codigo=None, id_proyecto=None) -> QuerySet:
        """
        Búsqueda avanzada de proyectos inmobiliarios.
        Implementa una búsqueda compleja con múltiples criterios.
        """
        queryset = self.get_all()
        
        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)
        
        if ubicacion:
            queryset = queryset.filter(ubicacion__icontains=ubicacion)
        
        if codigo:
            queryset = queryset.filter(codigo__iexact=codigo)
        
        if id_proyecto:
            queryset = queryset.filter(id=id_proyecto)
        
        # Filtrar por precio (requiere un join con UnidadPropiedad)
        if precio_desde or precio_hasta:
            precio_filter = Q()
            if precio_desde:
                precio_filter &= Q(unidades__precio_venta__gte=precio_desde)
            if precio_hasta:
                precio_filter &= Q(unidades__precio_venta__lte=precio_hasta)
            
            queryset = queryset.filter(precio_filter).distinct()
            
        return queryset
