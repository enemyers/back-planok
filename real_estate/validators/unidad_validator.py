from typing import Dict, Any

from .base_validator import BaseValidator


class UnidadValidator(BaseValidator):
    """
    Validador para el modelo UnidadPropiedad.
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
        Realiza la validación de los datos de la unidad de propiedad.
        """
        self._validate_proyecto()
        self._validate_numero_unidad()
        self._validate_tipo_unidad()
        self._validate_metraje()
        self._validate_precio()
        self._validate_estado()
    
    def _validate_proyecto(self):
        """Valida el proyecto asociado a la unidad"""
        proyecto_id = self.data.get('proyecto_id')
        
        if not proyecto_id:
            self.add_error('proyecto_id', 'El proyecto es obligatorio')
    
    def _validate_numero_unidad(self):
        """Valida el número de unidad"""
        numero_unidad = self.data.get('numero_unidad')
        
        if not numero_unidad:
            self.add_error('numero_unidad', 'El número de unidad es obligatorio')
        elif len(numero_unidad) > 20:
            self.add_error('numero_unidad', 'El número de unidad no puede tener más de 20 caracteres')
    
    def _validate_tipo_unidad(self):
        """Valida el tipo de unidad"""
        tipo_unidad = self.data.get('tipo_unidad')
        tipos_validos = ['Departamento', 'Casa', 'Oficina', 'Local Comercial', 'Terreno', 'Bodega', 'Estacionamiento']
        
        if not tipo_unidad:
            self.add_error('tipo_unidad', 'El tipo de unidad es obligatorio')
        elif tipo_unidad not in tipos_validos:
            self.add_error('tipo_unidad', f'El tipo de unidad debe ser uno de: {", ".join(tipos_validos)}')
    
    def _validate_metraje(self):
        """Valida el metraje cuadrado"""
        metraje = self.data.get('metraje_cuadrado')
        
        if metraje is None:
            self.add_error('metraje_cuadrado', 'El metraje cuadrado es obligatorio')
        elif metraje <= 0:
            self.add_error('metraje_cuadrado', 'El metraje cuadrado debe ser mayor que cero')
    
    def _validate_precio(self):
        """Valida el precio de venta"""
        precio = self.data.get('precio_venta')
        
        if precio is None:
            self.add_error('precio_venta', 'El precio de venta es obligatorio')
        elif precio <= 0:
            self.add_error('precio_venta', 'El precio de venta debe ser mayor que cero')
    
    def _validate_estado(self):
        """Valida el estado de la unidad"""
        estado = self.data.get('estado')
        estados_validos = ['Disponible', 'Reservado', 'Vendido', 'No Disponible']
        
        if not estado:
            self.add_error('estado', 'El estado es obligatorio')
        elif estado not in estados_validos:
            self.add_error('estado', f'El estado debe ser uno de: {", ".join(estados_validos)}')
