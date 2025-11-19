# 📝 Cambios Importantes para GitHub

## ✅ Cambios Realizados

### 1. **Eliminado PostgreSQL Local del Docker**
- ❌ Ya NO se incluye PostgreSQL en el contenedor Docker
- ✅ Ahora usa base de datos EXTERNA (Neon, Render, etc.)
- 📁 Archivo `docker-compose.yml` actualizado

### 2. **Usuario Hardcodeado de Emergencia**
- ✅ Usuario: `administrador`
- ✅ Contraseña: `LShm.2701`
- ✅ Funciona SIEMPRE, incluso sin base de datos
- 📁 Archivo `auth.py` modificado

### 3. **Solucionado Error de backup_precios.json**
- ✅ Ya NO es obligatorio tener este archivo
- ✅ El sistema funciona sin él
- 📁 Archivo `init_postgres.py` corregido

### 4. **Configuración con .env**
- ✅ Archivo `.env.example` creado como plantilla
- ✅ DATABASE_URL configurable
- ✅ SECRET_KEY personalizable
- ⚠️  **IMPORTANTE**: Crear `.env` antes de usar

### 5. **Documentación Completa**
- ✅ `INSTALL_EXTERNA_DB.md` - Guía para DB externa
- ✅ `INSTALL_DEBIAN.md` - Guía para DB local
- ✅ `BACKUP_DATABASE.md` - Guía de backups
- ✅ `.env.example` - Plantilla de configuración
- ✅ `setup_env.sh` - Script de configuración rápida

### 6. **Git Ignore Actualizado**
- ✅ `.env` NO se sube a GitHub
- ✅ `postgres_data/` NO se sube
- ✅ `backup_precios.json` NO se sube
- ✅ `uploads/` NO se sube

---

## 🚀 Pasos para Subir a GitHub

### 1. Crear archivo .env (NO subir esto)

```bash
# Crear .env con tus credenciales
cp .env.example .env
nano .env
```

Contenido del `.env`:
```env
DATABASE_URL=postgresql://usuario:pass@host.neon.tech/db
SECRET_KEY=tu-clave-secreta-aqui
FLASK_ENV=production
PORT=7860
```

### 2. Verificar que .env no se suba

```bash
# Verificar gitignore
git status

# .env NO debe aparecer en la lista
# Si aparece, ejecutar:
git rm --cached .env
```

### 3. Commit y Push

```bash
# Agregar todos los cambios
git add .

# Commit
git commit -m "✨ Migración a base de datos externa + usuario hardcodeado + documentación"

# Push
git push origin main
```

---

## 📥 Pasos para Hacer Pull en Servidor Debian

### 1. En el servidor, hacer pull

```bash
cd /ruta/a/Plan.Comercial-main
git pull origin main
```

### 2. Crear archivo .env

```bash
# Copiar plantilla
cp .env.example .env

# Editar con tu DATABASE_URL de Neon
nano .env
```

Configurar:
```env
DATABASE_URL=postgresql://neondb_owner:tu_password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
SECRET_KEY=generar-una-clave-aleatoria-larga
FLASK_ENV=production
PORT=7860
```

### 3. Construir e iniciar

```bash
# Detener contenedores anteriores si existen
docker compose down

# Limpiar caché de Docker
docker builder prune -a -f

# Construir desde cero
docker compose build --no-cache

# Iniciar
docker compose up -d

# Ver logs
docker compose logs -f app
```

### 4. Acceder

```bash
# En el navegador:
http://IP_DEL_SERVIDOR:5000

# Login con usuario hardcodeado:
Usuario: administrador
Contraseña: LShm.2701
```

---

## ⚠️ Advertencias Importantes

### 🔒 NUNCA subir a GitHub:
- ❌ `.env` (tiene credenciales)
- ❌ `postgres_data/` (datos de BD local)
- ❌ `backup_precios.json` (puede tener precios confidenciales)
- ❌ Archivos en `uploads/` (documentos subidos por usuarios)

### ✅ SÍ subir a GitHub:
- ✅ `.env.example` (plantilla SIN credenciales)
- ✅ Todos los archivos `.py`
- ✅ `docker-compose.yml`
- ✅ `Dockerfile`
- ✅ `requirements.txt`
- ✅ Archivos de documentación (`.md`)
- ✅ Templates y static files

---

## 🔧 Configuración de Neon

### Obtener DATABASE_URL de Neon:

1. Ve a: https://console.neon.tech/
2. Selecciona tu proyecto
3. Ve a "Connection Details"
4. Copia la "Connection string"
5. Debe verse así:
   ```
   postgresql://neondb_owner:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

### Verificar que Neon esté activo:

```bash
# Desde tu computadora local o servidor
psql "postgresql://neondb_owner:password@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require"

# Debería conectar sin errores
```

---

## 🐛 Solución de Problemas Comunes

### 1. Error: "No such file or directory: 'backup_precios.json'"

✅ **YA SOLUCIONADO** - El código ya no requiere este archivo

### 2. Error: "Error al conectar con PostgreSQL"

Verifica:
- DATABASE_URL en `.env` sea correcto
- Base de datos de Neon esté activa
- Copiar exactamente el connection string de Neon

### 3. No puedo hacer login

Usa el usuario hardcodeado:
- Usuario: `administrador`
- Contraseña: `LShm.2701`

### 4. Puerto 5000 ocupado

Edita `docker-compose.yml`:
```yaml
ports:
  - "8080:7860"  # Cambiar 5000 por 8080
```

---

## 📋 Checklist Final

Antes de hacer push a GitHub:

- [ ] `.env` está en `.gitignore`
- [ ] `.env` NO aparece en `git status`
- [ ] `.env.example` SÍ está incluido
- [ ] Documentación actualizada
- [ ] `docker-compose.yml` configurado para DB externa
- [ ] Usuario hardcodeado funciona
- [ ] Todo compilado sin errores

Después de hacer pull en servidor:

- [ ] Git pull completado
- [ ] Archivo `.env` creado con DATABASE_URL de Neon
- [ ] `docker compose build --no-cache` exitoso
- [ ] `docker compose up -d` corriendo
- [ ] Acceso a http://IP_SERVIDOR:5000 OK
- [ ] Login con usuario hardcodeado funciona
- [ ] Conexión a base de datos Neon OK

---

## ✅ Resumen de Archivos Modificados

```
Archivos MODIFICADOS:
├── auth.py                         (usuario hardcodeado)
├── init_postgres.py                (error backup_precios.json)
├── docker-compose.yml              (eliminado postgres local)
├── .gitignore                      (actualizado)
└── .dockerignore                   (actualizado)

Archivos NUEVOS:
├── .env.example                    (plantilla configuración)
├── INSTALL_EXTERNA_DB.md           (guía instalación)
├── setup_env.sh                    (script configuración)
└── CAMBIOS_IMPORTANTES.md          (este archivo)

Archivos EXISTENTES (no modificados):
├── app.py
├── db_config.py
├── requirements.txt
├── Dockerfile
└── templates/ y static/
```

---

## 🎉 ¡Listo para GitHub!

Ahora puedes hacer:

```bash
git add .
git commit -m "✨ Migración a base de datos externa"
git push origin main
```

Y en el servidor:

```bash
git pull
cp .env.example .env
nano .env  # Configurar DATABASE_URL
docker compose build --no-cache
docker compose up -d
```

**¡Éxito! 🚀**
