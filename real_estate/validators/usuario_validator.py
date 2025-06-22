import re
from typing import Dict, Any

from .base_validator import BaseValidator


class UsuarioValidator(BaseValidator):
    """
    Validador para el modelo Usuario.
    Implementa el principio de Responsabilidad Única (SRP) de SOLID,
    separando la lógica de validación de la lógica de negocio.
    """
    
    def __init__(self, data: Dict[str, Any], instance=None):
        """
        Constructor que recibe los datos a validar y opcionalmente una instancia existente.
        """
        super().__init__()
        self.data = data
        self.instance = instance
    
    def _validate(self):
        """
        Realiza la validación de los datos del usuario.
        """
        self._validate_rut()
        self._validate_email()
        self._validate_nombres()
        self._validate_password()
        self._validate_role()
        self._validate_phone()
    
    def _validate_rut(self):
        """Valida el RUT del usuario"""
        rut = self.data.get('rut')
        
        if not rut:
            self.add_error('rut', 'El RUT es obligatorio')
        elif not self._is_valid_rut_format(rut):
            self.add_error('rut', 'El formato del RUT no es válido (debe ser 12345678-9)')
    
    def _is_valid_rut_format(self, rut: str) -> bool:
        """Verifica si el formato del RUT es válido"""
        # Formato básico: 12345678-9
        pattern = r'^\d{1,8}-[\dkK]$'
        return bool(re.match(pattern, rut))
    
    def _validate_email(self):
        """Valida el email del usuario"""
        email = self.data.get('email')
        
        if not email:
            self.add_error('email', 'El email es obligatorio')
        elif not self._is_valid_email(email):
            self.add_error('email', 'El formato del email no es válido')
    
    def _is_valid_email(self, email: str) -> bool:
        """Verifica si el formato del email es válido"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _validate_nombres(self):
        """Valida el nombre y apellido del usuario"""
        first_name = self.data.get('first_name')
        last_name = self.data.get('last_name')
        
        if not first_name:
            self.add_error('first_name', 'El nombre es obligatorio')
        elif len(first_name) < 2:
            self.add_error('first_name', 'El nombre debe tener al menos 2 caracteres')
        
        if not last_name:
            self.add_error('last_name', 'El apellido es obligatorio')
        elif len(last_name) < 2:
            self.add_error('last_name', 'El apellido debe tener al menos 2 caracteres')
    
    def _validate_password(self):
        """Valida la contraseña del usuario"""
        password = self.data.get('password')
        
        # Solo validar la contraseña si se está creando un usuario o si se está actualizando la contraseña
        if password:
            if len(password) < 8:
                self.add_error('password', 'La contraseña debe tener al menos 8 caracteres')
            elif not self._is_strong_password(password):
                self.add_error('password', 'La contraseña debe contener al menos una letra mayúscula, una minúscula y un número')
    
    def _is_strong_password(self, password: str) -> bool:
        """Verifica si la contraseña es segura"""
        # Debe contener al menos una letra mayúscula, una minúscula y un número
        return (
            any(c.isupper() for c in password) and
            any(c.islower() for c in password) and
            any(c.isdigit() for c in password)
        )
    
    def _validate_role(self):
        """Valida el rol del usuario"""
        role = self.data.get('role')
        roles_validos = ['Administrador', 'Cliente']
        
        if role and role not in roles_validos:
            self.add_error('role', f'El rol debe ser uno de: {", ".join(roles_validos)}')
    
    def _validate_phone(self):
        """Valida el teléfono del usuario"""
        phone = self.data.get('phone')
        
        if phone and not self._is_valid_phone(phone):
            self.add_error('phone', 'El formato del teléfono no es válido')
    
    def _is_valid_phone(self, phone: str) -> bool:
        """Verifica si el formato del teléfono es válido"""
        # Formato básico: +56912345678 o 912345678
        pattern = r'^(\+\d{1,3})?[0-9]{8,12}$'
        return bool(re.match(pattern, phone))
