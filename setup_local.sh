#!/bin/bash

# Script de instalación para Debian/Ubuntu
# Ejecutar con: bash setup_local.sh

echo "=========================================="
echo "🚗 Sistema Toyota - Instalación Local"
echo "=========================================="
echo ""

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar si Docker está instalado
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker no está instalado${NC}"
    echo ""
    echo "Instalando Docker..."
    
    # Actualizar paquetes
    sudo apt-get update
    
    # Instalar dependencias
    sudo apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # Agregar GPG key de Docker
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # Agregar repositorio de Docker
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Instalar Docker Engine
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Agregar usuario al grupo docker
    sudo usermod -aG docker $USER
    
    echo -e "${GREEN}✅ Docker instalado correctamente${NC}"
    echo -e "${YELLOW}⚠️  Necesitas cerrar sesión y volver a iniciarla para usar Docker sin sudo${NC}"
fi

# Verificar si Docker Compose está instalado
if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose no está instalado${NC}"
    echo "Docker Compose debería haberse instalado con Docker. Verifica la instalación."
    exit 1
fi

echo -e "${GREEN}✅ Docker y Docker Compose están instalados${NC}"
echo ""

# Verificar si Git está instalado
if ! command -v git &> /dev/null; then
    echo -e "${YELLOW}📦 Instalando Git...${NC}"
    sudo apt-get update
    sudo apt-get install -y git
fi

echo -e "${GREEN}✅ Git está instalado${NC}"
echo ""

# Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p uploads
mkdir -p Patentamientos
mkdir -p postgres_data

# Configurar permisos
chmod -R 755 uploads
chmod -R 755 Patentamientos
chmod -R 777 postgres_data  # PostgreSQL necesita permisos de escritura

echo -e "${GREEN}✅ Directorios creados${NC}"
echo ""

# Construir e iniciar contenedores
echo "🔨 Construyendo contenedores Docker..."
docker compose build

echo ""
echo "🚀 Iniciando aplicación..."
docker compose up -d

echo ""
echo "⏳ Esperando a que los servicios estén listos..."
sleep 10

# Verificar estado de los contenedores
echo ""
echo "📊 Estado de los servicios:"
docker compose ps

echo ""
echo "=========================================="
echo -e "${GREEN}✅ Instalación completada${NC}"
echo "=========================================="
echo ""
echo "🌐 La aplicación está corriendo en:"
echo -e "   ${GREEN}http://localhost:5000${NC}"
echo ""
echo "📋 Comandos útiles:"
echo "   Ver logs:           docker compose logs -f"
echo "   Ver logs de app:    docker compose logs -f app"
echo "   Ver logs de DB:     docker compose logs -f postgres"
echo "   Detener:            docker compose stop"
echo "   Iniciar:            docker compose start"
echo "   Reiniciar:          docker compose restart"
echo "   Detener y eliminar: docker compose down"
echo "   Entrar a bash app:  docker compose exec app bash"
echo "   Entrar a psql:      docker compose exec postgres psql -U toyota_user -d plan_comercial"
echo ""
echo "🔐 Credenciales por defecto:"
echo "   Usuario: admin"
echo "   Contraseña: toyota2024"
echo ""
