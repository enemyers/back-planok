#!/bin/bash

# Colores para mensajes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Variables de la base de datos de origen
SOURCE_DB_NAME="planok_db"
SOURCE_DB_USER="postgres"
SOURCE_DB_PASSWORD="Ene0208."
SOURCE_DB_HOST="172.17.0.2"
SOURCE_DB_PORT="5432"

# Variables de la base de datos de destino (Docker)
DOCKER_DB_NAME="planok_db"
DOCKER_DB_USER="postgres"
DOCKER_DB_PASSWORD="Ene0208."
DOCKER_DB_HOST="172.19.0.1"
DOCKER_DB_PORT="5433"

# Nombre del archivo de respaldo
BACKUP_FILE="planok_db_backup.sql"

echo -e "${YELLOW}Iniciando migración de datos de PostgreSQL...${NC}"

# Verificar si pg_dump está instalado
if ! command -v pg_dump &> /dev/null; then
    echo -e "${RED}Error: pg_dump no está instalado. Por favor, instala PostgreSQL client tools.${NC}"
    exit 1
fi

# Verificar si psql está instalado
if ! command -v psql &> /dev/null; then
    echo -e "${RED}Error: psql no está instalado. Por favor, instala PostgreSQL client tools.${NC}"
    exit 1
fi

# Verificar conexión a la base de datos de origen
echo -e "${YELLOW}Verificando conexión a la base de datos de origen...${NC}"
if ! PGPASSWORD=$SOURCE_DB_PASSWORD psql -h $SOURCE_DB_HOST -p $SOURCE_DB_PORT -U $SOURCE_DB_USER -d $SOURCE_DB_NAME -c '\q' 2>/dev/null; then
    echo -e "${RED}Error: No se pudo conectar a la base de datos de origen.${NC}"
    exit 1
fi

# Verificar conexión a la base de datos de destino
echo -e "${YELLOW}Verificando conexión a la base de datos de destino (Docker)...${NC}"
if ! PGPASSWORD=$DOCKER_DB_PASSWORD psql -h $DOCKER_DB_HOST -p $DOCKER_DB_PORT -U $DOCKER_DB_USER -d $DOCKER_DB_NAME -c '\q' 2>/dev/null; then
    echo -e "${RED}Error: No se pudo conectar a la base de datos de destino en Docker.${NC}"
    exit 1
fi

# Exportar datos de la base de datos de origen
echo -e "${YELLOW}Exportando datos de la base de datos de origen...${NC}"
PGPASSWORD=$SOURCE_DB_PASSWORD pg_dump -h $SOURCE_DB_HOST -p $SOURCE_DB_PORT -U $SOURCE_DB_USER -d $SOURCE_DB_NAME -F c -b -v -f $BACKUP_FILE

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Falló la exportación de la base de datos.${NC}"
    exit 1
fi

echo -e "${GREEN}Exportación completada con éxito.${NC}"

# Limpiar la base de datos de destino (opcional)
echo -e "${YELLOW}¿Deseas limpiar la base de datos de destino antes de importar? (s/n)${NC}"
read -r clean_db

if [[ $clean_db =~ ^[Ss]$ ]]; then
    echo -e "${YELLOW}Limpiando la base de datos de destino...${NC}"
    PGPASSWORD=$DOCKER_DB_PASSWORD psql -h $DOCKER_DB_HOST -p $DOCKER_DB_PORT -U $DOCKER_DB_USER -d $DOCKER_DB_NAME -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}Error: Falló la limpieza de la base de datos de destino.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Base de datos de destino limpiada con éxito.${NC}"
fi

# Importar datos a la base de datos de destino
echo -e "${YELLOW}Importando datos a la base de datos de destino (Docker)...${NC}"
PGPASSWORD=$DOCKER_DB_PASSWORD pg_restore -h $DOCKER_DB_HOST -p $DOCKER_DB_PORT -U $DOCKER_DB_USER -d $DOCKER_DB_NAME -v $BACKUP_FILE

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Advertencia: La importación completó con algunos errores. Esto puede ser normal si las tablas ya existían.${NC}"
else
    echo -e "${GREEN}Importación completada con éxito.${NC}"
fi

# Limpiar archivo de respaldo
echo -e "${YELLOW}¿Deseas eliminar el archivo de respaldo? (s/n)${NC}"
read -r clean_backup

if [[ $clean_backup =~ ^[Ss]$ ]]; then
    rm $BACKUP_FILE
    echo -e "${GREEN}Archivo de respaldo eliminado.${NC}"
fi

echo -e "${GREEN}Proceso de migración completado.${NC}"
