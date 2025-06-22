import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo electrónico es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'Administrador')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    ROLE_CHOICES = (
        ('Administrador', 'Administrador'),
        ('Cliente', 'Cliente'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rut = models.CharField(max_length=12, unique=True)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='Cliente')
    phone = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=150, unique=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['rut', 'first_name', 'last_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class ProyectoInmobiliario(models.Model):
    STATUS_CHOICES = (
        ('En construcción', 'En construcción'),
        ('Terminado', 'Terminado'),
        ('Planificación', 'Planificación'),
        ('Cancelado', 'Cancelado'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    ubicacion = models.CharField(max_length=255)
    fecha_inicio = models.DateField()
    fecha_finalizacion = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Planificación')
    created_at = models.DateTimeField(auto_now_add=True)
    codigo = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return self.nombre
    
    class Meta:
        verbose_name = "Proyecto Inmobiliario"
        verbose_name_plural = "Proyectos Inmobiliarios"
        ordering = ['-created_at']


class UnidadPropiedad(models.Model):
    STATUS_CHOICES = (
        ('Disponible', 'Disponible'),
        ('Vendido', 'Vendido'),
        ('Reservado', 'Reservado'),
    )
    
    TIPO_CHOICES = (
        ('Departamento', 'Departamento'),
        ('Casa', 'Casa'),
        ('Oficina', 'Oficina'),
        ('Local', 'Local Comercial'),
        ('Terreno', 'Terreno'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    proyecto = models.ForeignKey(ProyectoInmobiliario, on_delete=models.CASCADE, related_name='unidades')
    numero_unidad = models.CharField(max_length=20)
    tipo_unidad = models.CharField(max_length=20, choices=TIPO_CHOICES)
    metraje_cuadrado = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=12, decimal_places=2)
    estado = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Disponible')
    cliente = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, related_name='propiedades')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.proyecto.nombre} - Unidad {self.numero_unidad}"
    
    class Meta:
        verbose_name = "Unidad de Propiedad"
        verbose_name_plural = "Unidades de Propiedad"
        unique_together = ('proyecto', 'numero_unidad')
        ordering = ['numero_unidad']
