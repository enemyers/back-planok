from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class ValidationError:
    """Clase para representar un error de validación"""
    
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
    
    def __str__(self):
        return f"{self.field}: {self.message}"


class BaseValidator(ABC):
    """
    Clase base abstracta para implementar validadores.
    Implementa el principio de Responsabilidad Única (SRP) de SOLID,
    separando la lógica de validación de la lógica de negocio.
    """
    
    def __init__(self):
        self.errors: List[ValidationError] = []
    
    def is_valid(self) -> bool:
        """Verifica si los datos son válidos"""
        self.errors = []
        self._validate()
        return len(self.errors) == 0
    
    def add_error(self, field: str, message: str):
        """Añade un error de validación"""
        self.errors.append(ValidationError(field, message))
    
    def get_errors(self) -> List[ValidationError]:
        """Obtiene los errores de validación"""
        return self.errors
    
    def get_error_dict(self) -> Dict[str, List[str]]:
        """Obtiene los errores de validación como un diccionario"""
        error_dict: Dict[str, List[str]] = {}
        for error in self.errors:
            if error.field not in error_dict:
                error_dict[error.field] = []
            error_dict[error.field].append(error.message)
        return error_dict
    
    @abstractmethod
    def _validate(self):
        """
        Método abstracto que debe ser implementado por las clases hijas.
        Realiza la validación de los datos.
        """
        pass
