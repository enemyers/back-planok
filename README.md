# PlanOk API

API de gestión inmobiliaria para PlanOk, desarrollada con Django y Django REST Framework.

## Requisitos

### Para desarrollo local
- Python 3.12+
- PostgreSQL 15
- pip

### Para Docker
- Docker
- Docker Compose

## Configuración del entorno

La aplicación utiliza variables de entorno para su configuración. Estas variables están definidas en el archivo `.env` en la raíz del proyecto.

### Variables de entorno principales

```
DEBUG=True
SECRET_KEY=django-insecure-planok-api-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=planok_db
DB_USER=postgres
DB_PASSWORD=Ene0208.
DB_HOST=172.17.0.2
DB_PORT=5432

# CORS
CORS_ALLOW_ALL_ORIGINS=True
```

## Instalación y ejecución

### Opción 1: Desarrollo local

1. **Clonar el repositorio**

```bash
git clone <url-del-repositorio>
cd planok/back_planok
```

2. **Crear y activar un entorno virtual**

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

4. **Configurar la base de datos PostgreSQL**

Asegúrate de tener PostgreSQL instalado y en ejecución. Luego, crea una base de datos:

```bash
createdb planok_db
```

5. **Configurar variables de entorno**

Ajusta el archivo `.env` según tu configuración local, especialmente las variables de conexión a la base de datos.

6. **Aplicar migraciones**

```bash
python manage.py migrate
```

7. **Crear un superusuario (opcional)**

```bash
python manage.py createsuperuser
```

8. **Ejecutar el servidor de desarrollo**

```bash
python manage.py runserver
```

La API estará disponible en http://localhost:8000/

### Opción 2: Usando Docker

1. **Clonar el repositorio**

```bash
git clone <url-del-repositorio>
cd planok/back_planok
```

2. **Construir y levantar los contenedores**

```bash
docker-compose up --build
```

Este comando construirá las imágenes necesarias y levantará los contenedores para:
- La aplicación Django (disponible en http://localhost:8000/)
- La base de datos PostgreSQL (disponible en localhost:5433)

3. **Crear un superusuario (opcional)**

```bash
docker-compose exec web python manage.py createsuperuser
```

4. **Detener los contenedores**

Para detener los contenedores, presiona `Ctrl+C` en la terminal donde se está ejecutando docker-compose, o ejecuta:

```bash
docker-compose down
```

## Estructura del proyecto

- `planok_api/`: Configuración principal del proyecto Django
- `real_estate/`: Aplicación principal con modelos, vistas y lógica de negocio
- `requirements.txt`: Dependencias del proyecto
- `manage.py`: Script de gestión de Django
- `Dockerfile`: Configuración para construir la imagen Docker de la aplicación
- `docker-compose.yml`: Configuración para orquestar los contenedores de la aplicación y la base de datos

## API Endpoints

La documentación de la API está disponible en:
- Swagger UI: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/

## Pruebas

Para ejecutar las pruebas:

### En desarrollo local

```bash
pytest
```

### En Docker

```bash
docker-compose exec web pytest
```

## Notas adicionales

- La aplicación utiliza JWT para la autenticación
- Las credenciales por defecto para la base de datos en Docker son:
  - Usuario: postgres
  - Contraseña: Ene0208.
  - Base de datos: planok_db
  - Puerto: 5433 (mapeado desde el puerto 5432 interno)
