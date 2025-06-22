from typing import Optional, Dict, Any, List
from django.db.models import QuerySet

from ..models import Usuario
from ..repositories.usuario_repository import UsuarioRepository
from .base_service import BaseService


class UsuarioService(BaseService[Usuario]):
    """
    Servicio para operaciones relacionadas con Usuario.
    Implementa el principio de Abierto/Cerrado (OCP) de SOLID,
    permitiendo extender la funcionalidad sin modificar el código existente.
    """
    
    def __init__(self, repository: UsuarioRepository = None):
        """
        Constructor que inicializa el repositorio.
        Si no se proporciona un repositorio, crea uno nuevo.
        """
        if repository is None:
            repository = UsuarioRepository()
        super().__init__(repository)
        self.repository: UsuarioRepository = repository
    
    def get_by_email(self, email) -> Optional[Usuario]:
        """Obtiene un usuario por su email"""
        return self.repository.get_by_email(email)
    
    def get_by_rut(self, rut) -> Optional[Usuario]:
        """Obtiene un usuario por su RUT"""
        return self.repository.get_by_rut(rut)
    
    def create(self, **kwargs) -> Usuario:
        """
        Crea un nuevo usuario.
        Implementa validaciones de negocio antes de la creación.
        """
        # Validar que el email no exista
        email = kwargs.get('email')
        if email and self.get_by_email(email):
            raise ValueError(f"Ya existe un usuario con el email {email}")
        
        # Validar que el RUT no exista
        rut = kwargs.get('rut')
        if rut and self.get_by_rut(rut):
            raise ValueError(f"Ya existe un usuario con el RUT {rut}")
        
        # Validar el rol
        role = kwargs.get('role')
        if role and role not in ['Administrador', 'Cliente']:
            raise ValueError(f"El rol {role} no es válido. Debe ser 'Administrador' o 'Cliente'")
        
        return self.repository.create(**kwargs)
    
    def update(self, id, **kwargs) -> Optional[Usuario]:
        """
        Actualiza un usuario existente.
        Implementa validaciones de negocio antes de la actualización.
        """
        # Obtener la instancia actual
        instance = self.get_by_id(id)
        if not instance:
            return None
        
        # Validar que el email no exista (si se está cambiando)
        email = kwargs.get('email')
        if email and email != instance.email:
            existing = self.get_by_email(email)
            if existing and existing.id != id:
                raise ValueError(f"Ya existe un usuario con el email {email}")
        
        # Validar que el RUT no exista (si se está cambiando)
        rut = kwargs.get('rut')
        if rut and rut != instance.rut:
            existing = self.get_by_rut(rut)
            if existing and existing.id != id:
                raise ValueError(f"Ya existe un usuario con el RUT {rut}")
        
        # Validar el rol
        role = kwargs.get('role')
        if role and role not in ['Administrador', 'Cliente']:
            raise ValueError(f"El rol {role} no es válido. Debe ser 'Administrador' o 'Cliente'")
        
        return self.repository.update(instance, **kwargs)
    
    def get_by_role(self, role) -> QuerySet:
        """Obtiene todos los usuarios con un rol específico"""
        return self.repository.get_by_role(role)
    
    def get_clientes(self) -> QuerySet:
        """Obtiene todos los usuarios con rol de Cliente"""
        return self.repository.get_clientes()
    
    def get_administradores(self) -> QuerySet:
        """Obtiene todos los usuarios con rol de Administrador"""
        return self.repository.get_administradores()
    
    def cambiar_password(self, user_id, password_actual, password_nuevo) -> bool:
        """
        Cambia la contraseña de un usuario.
        Ejemplo de lógica de negocio en el servicio.
        """
        usuario = self.get_by_id(user_id)
        if not usuario:
            return False
        
        # Verificar que la contraseña actual sea correcta
        if not usuario.check_password(password_actual):
            return False
        
        # Actualizar la contraseña
        usuario.set_password(password_nuevo)
        usuario.save()
        return True
