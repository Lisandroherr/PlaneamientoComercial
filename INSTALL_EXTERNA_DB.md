# 🚀 Guía de Instalación con Base de Datos Externa

Esta guía te ayudará a configurar el sistema usando tu base de datos PostgreSQL externa (Neon, Render, etc.) en lugar de una base de datos local.

## 📋 Requisitos Previos

- Docker y Docker Compose instalados
- Base de datos PostgreSQL externa (Neon, Render, etc.) con su URL de conexión
- Git instalado

---

## 🔧 Configuración Rápida

### Paso 1: Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/Plan.Comercial-main.git
cd Plan.Comercial-main
```

### Paso 2: Configurar variables de entorno

#### Opción A: Script automático (Linux/Mac)

```bash
chmod +x setup_env.sh
./setup_env.sh
```

#### Opción B: Manual

Crea un archivo `.env` en la raíz del proyecto:

```bash
# Copiar el ejemplo
cp .env.example .env

# Editar con tu editor favorito
nano .env   # o vim, code, etc.
```

Contenido del archivo `.env`:

```env
# URL de tu base de datos PostgreSQL externa
DATABASE_URL=postgresql://usuario:password@host.neon.tech/database?sslmode=require

# Clave secreta (generar una aleatoria y larga)
SECRET_KEY=tu-clave-secreta-muy-larga-y-aleatoria-aqui

# Entorno
FLASK_ENV=production

# Puerto
PORT=7860
```

### Paso 3: Construir e iniciar

```bash
# Construir imagen Docker
docker compose build

# Iniciar aplicación
docker compose up -d

# Ver logs
docker compose logs -f app
```

### Paso 4: Acceder

Abre tu navegador en: **http://localhost:5000**

Credenciales de emergencia:
- **Usuario:** administrador
- **Contraseña:** LShm.2701

---

## 🔑 Obtener DATABASE_URL de Neon

1. Ve a tu dashboard de Neon: https://console.neon.tech/
2. Selecciona tu proyecto
3. Ve a la pestaña "Connection Details"
4. Copia la cadena de conexión que dice "Connection string"
5. Debe verse así:
   ```
   postgresql://usuario:password@ep-xxx-xxx.us-east-2.aws.neon.tech/database?sslmode=require
   ```

---

## 📊 Estructura del Proyecto

```
Plan.Comercial-main/
├── .env                    ← Configuración (NO subir a Git)
├── .env.example            ← Plantilla de configuración
├── docker-compose.yml      ← Configuración Docker
├── Dockerfile              ← Imagen Docker
├── app.py                  ← Aplicación principal
├── auth.py                 ← Sistema de autenticación
├── db_config.py            ← Configuración de base de datos
├── init_postgres.py        ← Inicialización de tablas
├── requirements.txt        ← Dependencias Python
├── uploads/                ← Archivos subidos (no se sube a Git)
├── Patentamientos/         ← CSV de patentamientos
└── templates/              ← Templates HTML
```

---

## 🐛 Solución de Problemas

### Error: "No such file or directory: 'backup_precios.json'"

✅ **Solucionado** - El sistema ahora funciona sin este archivo. Los precios se cargarán desde la base de datos externa.

### Error: "Error al inicializar la base de datos"

Verifica:
1. Que tu `DATABASE_URL` en `.env` sea correcto
2. Que tu base de datos en Neon esté activa
3. Que el usuario tenga permisos de crear tablas

```bash
# Ver logs detallados
docker compose logs app

# Probar conexión manualmente
docker compose exec app python -c "from db_config import init_connection_pool; init_connection_pool(); print('✅ Conexión exitosa')"
```

### No puedo hacer login

Si la base de datos está vacía o tiene problemas, usa el usuario hardcodeado:
- **Usuario:** administrador
- **Contraseña:** LShm.2701

Este usuario funciona SIEMPRE, incluso si la base de datos falla.

### Puerto 5000 ocupado

Edita `docker-compose.yml`:

```yaml
ports:
  - "8080:7860"  # Cambia 5000 por otro puerto disponible
```

---

## 🔄 Actualizar el Sistema

```bash
# Detener contenedores
docker compose down

# Actualizar código desde Git
git pull

# Reconstruir e iniciar
docker compose build --no-cache
docker compose up -d
```

---

## 📦 Comandos Útiles

```bash
# Ver logs en tiempo real
docker compose logs -f app

# Reiniciar aplicación
docker compose restart app

# Detener todo
docker compose down

# Ver estado
docker compose ps

# Acceder al contenedor
docker compose exec app bash

# Limpiar todo y empezar de cero
docker compose down -v
docker compose build --no-cache
docker compose up -d
```

---

## 🔐 Seguridad

### Cambiar SECRET_KEY

Genera una clave aleatoria:

```bash
# Linux/Mac
openssl rand -base64 32

# Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copia el resultado en tu `.env`:

```env
SECRET_KEY=tu-nueva-clave-aqui
```

### Nunca subir .env a Git

El archivo `.gitignore` ya está configurado para excluir `.env`, pero verifica:

```bash
# Verificar que .env no esté trackeado
git status

# Si aparece .env, eliminarlo del tracking
git rm --cached .env
```

---

## 🌐 Acceso desde Otros Dispositivos

Para acceder desde otros dispositivos en tu red local:

```bash
# Encontrar IP del servidor
ip addr show   # Linux
ifconfig       # Mac

# Acceder desde otro dispositivo
http://IP_DEL_SERVIDOR:5000
```

Ejemplo: `http://192.168.1.100:5000`

---

## 📝 Checklist de Instalación

- [ ] Docker instalado y corriendo
- [ ] Base de datos externa (Neon) creada y activa
- [ ] Repositorio clonado
- [ ] Archivo `.env` configurado con DATABASE_URL correcto
- [ ] SECRET_KEY generado y configurado
- [ ] `docker compose build` ejecutado sin errores
- [ ] `docker compose up -d` iniciado correctamente
- [ ] Acceso a http://localhost:5000 funcionando
- [ ] Login exitoso con usuario hardcodeado
- [ ] Carpetas `uploads/` y `Patentamientos/` creadas

---

## ✅ Diferencias con Instalación Local

| Característica | Base de Datos Local | Base de Datos Externa (Neon) |
|----------------|---------------------|------------------------------|
| PostgreSQL en Docker | ✅ Incluido | ❌ No necesario |
| Persistencia de datos | Carpeta local | ☁️ Nube (Neon) |
| Backup | Manual (carpeta) | Automático (Neon) |
| Acceso remoto | Solo red local | 🌐 Desde cualquier lugar |
| Configuración | Automática | Requiere DATABASE_URL |
| Velocidad | 🚀 Muy rápida | 🌐 Depende de internet |

---

## 🎉 ¡Listo!

Si todo funcionó correctamente, deberías poder:
1. Acceder a la aplicación en http://localhost:5000
2. Hacer login con el usuario hardcodeado
3. Ver que la aplicación se conecta a tu base de datos externa
4. Los datos persisten en Neon (no se pierden al reiniciar)

---

## 📞 Soporte

Si encuentras problemas:
1. Revisa los logs: `docker compose logs -f app`
2. Verifica tu DATABASE_URL en `.env`
3. Confirma que Neon esté activo
4. Usa el usuario hardcodeado: `administrador` / `LShm.2701`
