#!/bin/bash

# Script de configuración rápida para base de datos externa

echo "=========================================="
echo "🚗 Sistema Toyota - Configuración Rápida"
echo "=========================================="
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Verificar si existe .env
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Ya existe un archivo .env${NC}"
    read -p "¿Deseas sobrescribirlo? (s/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        echo "Configuración cancelada"
        exit 1
    fi
fi

# Solicitar DATABASE_URL
echo ""
echo -e "${GREEN}📋 Configuración de Base de Datos${NC}"
echo ""
echo "Ingresa tu DATABASE_URL de Neon (o cualquier PostgreSQL externo)"
echo "Ejemplo: postgresql://usuario:password@host.neon.tech/database?sslmode=require"
echo ""
read -p "DATABASE_URL: " DATABASE_URL

# Generar SECRET_KEY aleatorio
SECRET_KEY=$(openssl rand -base64 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_urlsafe(32))")

# Crear archivo .env
cat > .env << EOF
# ========================================
# CONFIGURACIÓN DE BASE DE DATOS
# ========================================

# URL de PostgreSQL (Neon, Render, etc.)
DATABASE_URL=$DATABASE_URL

# Configuración de Flask
SECRET_KEY=$SECRET_KEY
FLASK_ENV=production

# Puerto de la aplicación
PORT=7860
EOF

echo ""
echo -e "${GREEN}✅ Archivo .env creado correctamente${NC}"
echo ""
echo "Configuración guardada:"
echo "  DATABASE_URL: ✓ (configurado)"
echo "  SECRET_KEY: ✓ (generado automáticamente)"
echo ""
echo -e "${YELLOW}📝 Próximos pasos:${NC}"
echo "  1. Verifica que tu base de datos en Neon esté activa"
echo "  2. Ejecuta: docker compose build"
echo "  3. Ejecuta: docker compose up -d"
echo ""
echo -e "${GREEN}🎉 ¡Listo para usar!${NC}"
