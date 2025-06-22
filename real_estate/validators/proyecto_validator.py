from datetime import date
from typing import Dict, Any

from .base_validator import BaseValidator


class ProyectoValidator(BaseValidator):
    """
    Validador para el modelo ProyectoInmobiliario.
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
        Realiza la validación de los datos del proyecto inmobiliario.
        """
        self._validate_nombre()
        self._validate_ubicacion()
        self._validate_fechas()
        self._validate_estado()
        self._validate_codigo()
    
    def _validate_nombre(self):
        """Valida el nombre del proyecto"""
        nombre = self.data.get('nombre')
        
        if not nombre:
            self.add_error('nombre', 'El nombre es obligatorio')
        elif len(nombre) < 3:
            self.add_error('nombre', 'El nombre debe tener al menos 3 caracteres')
        elif len(nombre) > 100:
            self.add_error('nombre', 'El nombre no puede tener más de 100 caracteres')
    
    def _validate_ubicacion(self):
        """Valida la ubicación del proyecto"""
        ubicacion = self.data.get('ubicacion')
        
        if not ubicacion:
            self.add_error('ubicacion', 'La ubicación es obligatoria')
        elif len(ubicacion) < 5:
            self.add_error('ubicacion', 'La ubicación debe tener al menos 5 caracteres')
        elif len(ubicacion) > 200:
            self.add_error('ubicacion', 'La ubicación no puede tener más de 200 caracteres')
    
    def _validate_fechas(self):
        """Valida las fechas del proyecto"""
        fecha_inicio = self.data.get('fecha_inicio')
        fecha_finalizacion = self.data.get('fecha_finalizacion')
        
        if fecha_inicio and fecha_finalizacion:
            if isinstance(fecha_inicio, str):
                try:
                    fecha_inicio = date.fromisoformat(fecha_inicio)
                except ValueError:
                    self.add_error('fecha_inicio', 'Formato de fecha inválido')
                    return
            
            if isinstance(fecha_finalizacion, str):
                try:
                    fecha_finalizacion = date.fromisoformat(fecha_finalizacion)
                except ValueError:
                    self.add_error('fecha_finalizacion', 'Formato de fecha inválido')
                    return
            
            if fecha_inicio > fecha_finalizacion:
                self.add_error('fecha_finalizacion', 'La fecha de finalización debe ser posterior a la fecha de inicio')
    
    def _validate_estado(self):
        """Valida el estado del proyecto"""
        estado = self.data.get('estado')
        estados_validos = ['Planificación', 'En Construcción', 'Terminado', 'Cancelado']
        
        if estado and estado not in estados_validos:
            self.add_error('estado', f'El estado debe ser uno de: {", ".join(estados_validos)}')
    
    def _validate_codigo(self):
        """Valida el código del proyecto"""
        codigo = self.data.get('codigo')
        
        if codigo:
            if len(codigo) < 5:
                self.add_error('codigo', 'El código debe tener al menos 5 caracteres')
            elif len(codigo) > 20:
                self.add_error('codigo', 'El código no puede tener más de 20 caracteres')
