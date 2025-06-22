from typing import Optional
from django.db.models import QuerySet

from ..models import Usuario
from .base_repository import BaseRepository


class UsuarioRepository(BaseRepository[Usuario]):
    """
    Repositorio para operaciones relacionadas con Usuario.
    Implementa el patrón Repository y el principio de Responsabilidad Única (SRP).
    """
    
    def get_all(self) -> QuerySet:
        """Obtiene todos los usuarios"""
        return Usuario.objects.all()
    
    def get_by_id(self, id) -> Optional[Usuario]:
        """Obtiene un usuario por su ID"""
        try:
            return Usuario.objects.get(id=id)
        except Usuario.DoesNotExist:
            return None
    
    def get_by_email(self, email) -> Optional[Usuario]:
        """Obtiene un usuario por su email"""
        try:
            return Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return None
    
    def get_by_rut(self, rut) -> Optional[Usuario]:
        """Obtiene un usuario por su RUT"""
        try:
            return Usuario.objects.get(rut=rut)
        except Usuario.DoesNotExist:
            return None
    
    def create(self, **kwargs) -> Usuario:
        """
        Crea un nuevo usuario.
        Utiliza el UserManager personalizado para la creación segura de usuarios.
        """
        # Si se proporciona una contraseña, usamos create_user para el hash seguro
        password = kwargs.pop('password', None)
        if password:
            return Usuario.objects.create_user(password=password, **kwargs)
        return Usuario.objects.create(**kwargs)
    
    def update(self, instance: Usuario, **kwargs) -> Usuario:
        """
        Actualiza un usuario existente.
        Maneja la contraseña de forma segura si se proporciona.
        """
        password = kwargs.pop('password', None)
        
        for key, value in kwargs.items():
            setattr(instance, key, value)
        
        if password:
            instance.set_password(password)
            
        instance.save()
        return instance
    
    def delete(self, instance: Usuario) -> bool:
        """Elimina un usuario"""
        instance.delete()
        return True
    
    def filter(self, **kwargs) -> QuerySet:
        """Filtra usuarios según criterios"""
        return Usuario.objects.filter(**kwargs)
    
    def get_by_role(self, role) -> QuerySet:
        """Obtiene todos los usuarios con un rol específico"""
        return self.filter(role=role)
    
    def get_clientes(self) -> QuerySet:
        """Obtiene todos los usuarios con rol de Cliente"""
        return self.get_by_role('Cliente')
    
    def get_administradores(self) -> QuerySet:
        """Obtiene todos los usuarios con rol de Administrador"""
        return self.get_by_role('Administrador')
