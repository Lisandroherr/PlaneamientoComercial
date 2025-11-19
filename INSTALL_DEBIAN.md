# 🚗 Instalación en Debian - Sistema Toyota

Guía completa para instalar y ejecutar el sistema en Debian/Ubuntu local.

## 📋 Requisitos Previos

- Debian 11/12 o Ubuntu 20.04/22.04
- Acceso root o sudo
- Conexión a internet
- Al menos 2GB de RAM libre
- 5GB de espacio en disco

## 🚀 Instalación Rápida (Automática)

### Paso 1: Clonar el repositorio

```bash
# Instalar git si no lo tienes
sudo apt-get update
sudo apt-get install -y git

# Clonar el repositorio
git clone https://github.com/TU_USUARIO/Plan.Comercial-main.git
cd Plan.Comercial-main
```

### Paso 2: Ejecutar el script de instalación

```bash
# Dar permisos de ejecución
chmod +x setup_local.sh

# Ejecutar instalación
bash setup_local.sh
```

El script instalará automáticamente:
- Docker y Docker Compose
- Configurará los contenedores
- Iniciará la aplicación

### Paso 3: Acceder a la aplicación

Abre tu navegador y ve a: **http://localhost:5000**

Credenciales por defecto:
- **Usuario:** admin
- **Contraseña:** toyota2024

---

## 🔧 Instalación Manual

Si prefieres instalar manualmente o el script automático falla:

### 1. Instalar Docker

```bash
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
curl -fsSL https://download.docker.com/linux/debian/gpg | \
    sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Agregar repositorio (Debian)
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/debian $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Para Ubuntu, usar este comando en su lugar:
# echo \
#   "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
#   https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
#   sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io \
    docker-buildx-plugin docker-compose-plugin

# Agregar tu usuario al grupo docker
sudo usermod -aG docker $USER

# IMPORTANTE: Cerrar sesión y volver a entrar para aplicar cambios
```

### 2. Verificar instalación de Docker

```bash
# Verificar Docker
docker --version

# Verificar Docker Compose
docker compose version
```

### 3. Clonar el proyecto

```bash
git clone https://github.com/TU_USUARIO/Plan.Comercial-main.git
cd Plan.Comercial-main
```

### 4. Crear directorios necesarios

```bash
mkdir -p uploads Patentamientos
chmod -R 755 uploads Patentamientos
```

### 5. Construir e iniciar

```bash
# Construir imágenes
docker compose build

# Iniciar servicios
docker compose up -d

# Ver logs
docker compose logs -f
```

---

## 📊 Comandos Útiles

### Gestión de servicios

```bash
# Ver estado de contenedores
docker compose ps

# Ver logs en tiempo real
docker compose logs -f

# Ver logs solo de la app
docker compose logs -f app

# Ver logs solo de PostgreSQL
docker compose logs -f postgres

# Detener servicios
docker compose stop

# Iniciar servicios
docker compose start

# Reiniciar servicios
docker compose restart

# Detener y eliminar contenedores (mantiene datos)
docker compose down

# Detener y eliminar TODO (incluye datos)
docker compose down -v
```

### Acceso a contenedores

```bash
# Entrar al contenedor de la aplicación
docker compose exec app bash

# Entrar a PostgreSQL
docker compose exec postgres psql -U toyota_user -d plan_comercial

# Ver base de datos desde psql:
# \dt - listar tablas
# \d nombre_tabla - ver estructura de tabla
# SELECT * FROM users; - consultar usuarios
# \q - salir
```

### Mantenimiento

```bash
# Ver uso de disco por Docker
docker system df

# Limpiar recursos no usados
docker system prune -a

# Backup de base de datos
docker compose exec postgres pg_dump -U toyota_user plan_comercial > backup.sql

# Restaurar backup
cat backup.sql | docker compose exec -T postgres psql -U toyota_user plan_comercial
```

---

## 🔐 Configuración de Seguridad

### Cambiar credenciales de PostgreSQL

Edita `docker-compose.yml`:

```yaml
environment:
  POSTGRES_PASSWORD: TU_PASSWORD_SEGURO
  DB_PASSWORD: TU_PASSWORD_SEGURO
```

### Cambiar SECRET_KEY de Flask

Edita `docker-compose.yml`:

```yaml
environment:
  SECRET_KEY: tu-clave-secreta-larga-y-aleatoria-aqui
```

Luego reinicia:

```bash
docker compose down
docker compose up -d
```

---

## 🌐 Acceso desde Otros Dispositivos en la Red

Para acceder desde otros dispositivos en tu red local:

1. Encuentra la IP de tu servidor Debian:

```bash
ip addr show
# Busca algo como 192.168.1.x
```

2. En otros dispositivos, accede a: `http://IP_DEL_SERVIDOR:5000`

Ejemplo: `http://192.168.1.100:5000`

### Abrir puerto en firewall (si es necesario)

```bash
# UFW (Ubuntu/Debian)
sudo ufw allow 5000/tcp

# iptables
sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
```

---

## 🐛 Solución de Problemas

### Error: "Cannot connect to Docker daemon"

```bash
# Iniciar Docker
sudo systemctl start docker

# Habilitar Docker al inicio
sudo systemctl enable docker

# Verificar estado
sudo systemctl status docker
```

### Error: "Permission denied"

```bash
# Agregar usuario a grupo docker
sudo usermod -aG docker $USER

# Cerrar sesión y volver a entrar
# O ejecutar:
newgrp docker
```

### Puerto 5000 ocupado

Edita `docker-compose.yml` y cambia:

```yaml
ports:
  - "8080:7860"  # Cambiar 5000 por otro puerto (ej: 8080)
```

### PostgreSQL no inicia

```bash
# Ver logs detallados
docker compose logs postgres

# Eliminar volumen y recrear
docker compose down -v
docker compose up -d
```

### La aplicación no carga

```bash
# Ver logs de la app
docker compose logs app

# Reconstruir contenedor
docker compose down
docker compose build --no-cache app
docker compose up -d
```

---

## 📱 Acceso desde Celular/Tablet

1. Asegúrate de que tu servidor y dispositivo están en la misma red WiFi
2. Encuentra la IP del servidor: `ip addr show`
3. En el navegador del móvil: `http://IP_DEL_SERVIDOR:5000`

---

## 🔄 Actualización del Sistema

```bash
# Detener servicios
docker compose down

# Actualizar código
git pull

# Reconstruir e iniciar
docker compose build
docker compose up -d
```

---

## 📞 Soporte

Si encuentras problemas:

1. Revisa los logs: `docker compose logs -f`
2. Verifica el estado: `docker compose ps`
3. Consulta esta documentación
4. Contacta al administrador del sistema

---

## ✅ Checklist de Instalación

- [ ] Docker instalado y funcionando
- [ ] Docker Compose instalado
- [ ] Repositorio clonado
- [ ] Directorios creados (uploads, Patentamientos)
- [ ] Contenedores construidos: `docker compose build`
- [ ] Servicios iniciados: `docker compose up -d`
- [ ] Aplicación accesible en http://localhost:5000
- [ ] Login exitoso con credenciales por defecto
- [ ] (Opcional) SECRET_KEY y passwords cambiados

---

## 🎉 ¡Listo!

El sistema debería estar funcionando correctamente. Si todo está bien, verás la pantalla de login en http://localhost:5000
