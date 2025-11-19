# 💾 Gestión de Backups de Base de Datos

Guía completa para realizar backups y restauraciones de la base de datos PostgreSQL.

## 📍 Ubicación de los Datos

Los datos de PostgreSQL se almacenan en:
```
./postgres_data/
```

Esta carpeta contiene TODA la base de datos y persiste incluso si eliminas los contenedores Docker.

---

## 🔄 Backup Automático (Recomendado)

### Backup completo de la carpeta

```bash
# Backup simple (copiar carpeta)
sudo cp -r postgres_data postgres_data_backup_$(date +%Y%m%d_%H%M%S)

# Backup comprimido
sudo tar -czf postgres_backup_$(date +%Y%m%d_%H%M%S).tar.gz postgres_data/
```

### Script de backup automático

Crea un archivo `backup_db.sh`:

```bash
#!/bin/bash
# Backup automático de base de datos

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Crear directorio de backups
mkdir -p $BACKUP_DIR

# Backup SQL
docker compose exec -T postgres pg_dump -U toyota_user plan_comercial > $BACKUP_DIR/backup_$DATE.sql

# Backup de carpeta completa (comprimido)
sudo tar -czf $BACKUP_DIR/postgres_data_$DATE.tar.gz postgres_data/

# Mantener solo los últimos 7 backups
find $BACKUP_DIR -name "backup_*.sql" -mtime +7 -delete
find $BACKUP_DIR -name "postgres_data_*.tar.gz" -mtime +7 -delete

echo "✅ Backup completado: $BACKUP_DIR/backup_$DATE.sql"
```

Ejecutar:
```bash
chmod +x backup_db.sh
./backup_db.sh
```

### Automatizar con cron

```bash
# Editar crontab
crontab -e

# Agregar backup diario a las 2 AM
0 2 * * * cd /ruta/a/Plan.Comercial-main && ./backup_db.sh
```

---

## 📥 Backup Manual (SQL)

### Backup completo

```bash
# Generar archivo SQL
docker compose exec postgres pg_dump -U toyota_user plan_comercial > backup.sql

# Con compresión
docker compose exec postgres pg_dump -U toyota_user plan_comercial | gzip > backup_$(date +%Y%m%d).sql.gz
```

### Backup de tabla específica

```bash
# Solo una tabla
docker compose exec postgres pg_dump -U toyota_user -t disponibles plan_comercial > disponibles_backup.sql

# Múltiples tablas
docker compose exec postgres pg_dump -U toyota_user -t precios -t disponibles plan_comercial > tablas_backup.sql
```

### Backup solo de datos (sin estructura)

```bash
docker compose exec postgres pg_dump -U toyota_user --data-only plan_comercial > datos_backup.sql
```

### Backup solo de estructura (sin datos)

```bash
docker compose exec postgres pg_dump -U toyota_user --schema-only plan_comercial > estructura_backup.sql
```

---

## 📤 Restaurar Base de Datos

### Restaurar desde archivo SQL

```bash
# Restaurar backup completo
cat backup.sql | docker compose exec -T postgres psql -U toyota_user plan_comercial

# Restaurar desde archivo comprimido
gunzip -c backup.sql.gz | docker compose exec -T postgres psql -U toyota_user plan_comercial
```

### Restaurar tabla específica

```bash
cat disponibles_backup.sql | docker compose exec -T postgres psql -U toyota_user plan_comercial
```

### Restaurar desde carpeta postgres_data

```bash
# 1. Detener servicios
docker compose down

# 2. Eliminar datos actuales
sudo rm -rf postgres_data/*

# 3. Restaurar desde backup
sudo tar -xzf postgres_backup_FECHA.tar.gz

# 4. Iniciar servicios
docker compose up -d
```

---

## 🔄 Migrar Base de Datos a Otro Servidor

### En el servidor origen:

```bash
# 1. Crear backup
docker compose exec postgres pg_dump -U toyota_user plan_comercial | gzip > migracion.sql.gz

# 2. Copiar archivo a servidor destino
scp migracion.sql.gz usuario@servidor-destino:/ruta/destino/
```

### En el servidor destino:

```bash
# 1. Restaurar
gunzip -c migracion.sql.gz | docker compose exec -T postgres psql -U toyota_user plan_comercial

# 2. Verificar
docker compose exec postgres psql -U toyota_user -d plan_comercial -c "\dt"
```

---

## 🧪 Clonar Base de Datos para Testing

```bash
# 1. Backup de producción
docker compose exec postgres pg_dump -U toyota_user plan_comercial > prod_backup.sql

# 2. Crear base de datos de test
docker compose exec postgres psql -U toyota_user -c "CREATE DATABASE plan_comercial_test;"

# 3. Restaurar en test
cat prod_backup.sql | docker compose exec -T postgres psql -U toyota_user plan_comercial_test
```

---

## 📊 Verificar Tamaño de Base de Datos

```bash
# Tamaño de la base de datos
docker compose exec postgres psql -U toyota_user -d plan_comercial -c "SELECT pg_size_pretty(pg_database_size('plan_comercial'));"

# Tamaño por tabla
docker compose exec postgres psql -U toyota_user -d plan_comercial -c "
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"

# Tamaño de la carpeta postgres_data
du -sh postgres_data/
```

---

## 🗄️ Backup en Diferentes Formatos

### Formato custom (más rápido, comprimido)

```bash
# Backup
docker compose exec postgres pg_dump -U toyota_user -Fc plan_comercial > backup.dump

# Restaurar
docker compose exec -T postgres pg_restore -U toyota_user -d plan_comercial -c < backup.dump
```

### Formato directory (paralelo, muy rápido)

```bash
# Backup
docker compose exec postgres pg_dump -U toyota_user -Fd -j 4 plan_comercial -f /tmp/backup_dir
docker compose cp postgres:/tmp/backup_dir ./backup_dir

# Restaurar
docker compose cp ./backup_dir postgres:/tmp/backup_dir
docker compose exec postgres pg_restore -U toyota_user -Fd -j 4 -d plan_comercial /tmp/backup_dir
```

---

## 🚨 Recuperación de Emergencia

### Si perdiste la carpeta postgres_data:

```bash
# 1. Detener servicios
docker compose down

# 2. Crear nueva carpeta
mkdir -p postgres_data
chmod 777 postgres_data

# 3. Iniciar PostgreSQL limpio
docker compose up -d postgres

# 4. Esperar que inicie
sleep 10

# 5. Restaurar desde backup SQL
cat backup.sql | docker compose exec -T postgres psql -U toyota_user plan_comercial

# 6. Iniciar aplicación
docker compose up -d app
```

### Si el contenedor está corrupto:

```bash
# 1. Detener todo
docker compose down

# 2. Eliminar contenedor e imagen
docker rm -f toyota_postgres
docker rmi postgres:15-alpine

# 3. Volver a crear (postgres_data se mantiene intacto)
docker compose up -d
```

---

## 📅 Estrategia de Backup Recomendada

### Para producción:

1. **Backup diario automático** (SQL + carpeta comprimida)
2. **Mantener últimos 7 días** en disco local
3. **Backup semanal** a almacenamiento externo/nube
4. **Backup mensual** archivado (6 meses)

### Script completo de backup con rotación:

```bash
#!/bin/bash
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
DAY=$(date +%A)

mkdir -p $BACKUP_DIR/{daily,weekly,monthly}

# Backup diario
docker compose exec -T postgres pg_dump -U toyota_user plan_comercial | \
    gzip > $BACKUP_DIR/daily/backup_$DATE.sql.gz

# Backup semanal (domingos)
if [ "$DAY" = "Sunday" ]; then
    sudo tar -czf $BACKUP_DIR/weekly/postgres_$DATE.tar.gz postgres_data/
fi

# Backup mensual (día 1)
if [ $(date +%d) = "01" ]; then
    sudo tar -czf $BACKUP_DIR/monthly/postgres_$DATE.tar.gz postgres_data/
fi

# Limpiar backups antiguos
find $BACKUP_DIR/daily -name "*.sql.gz" -mtime +7 -delete
find $BACKUP_DIR/weekly -name "*.tar.gz" -mtime +30 -delete
find $BACKUP_DIR/monthly -name "*.tar.gz" -mtime +180 -delete

echo "✅ Backup completado"
```

---

## 🔐 Backup Encriptado

```bash
# Backup encriptado con GPG
docker compose exec -T postgres pg_dump -U toyota_user plan_comercial | \
    gzip | \
    gpg --symmetric --cipher-algo AES256 > backup_encrypted.sql.gz.gpg

# Restaurar backup encriptado
gpg --decrypt backup_encrypted.sql.gz.gpg | \
    gunzip | \
    docker compose exec -T postgres psql -U toyota_user plan_comercial
```

---

## ✅ Checklist de Backup

- [ ] Backup automático configurado (cron)
- [ ] Script de backup testeado
- [ ] Carpeta `postgres_data/` incluida en backup de sistema
- [ ] Backup externo/nube configurado
- [ ] Proceso de restauración probado
- [ ] Documentación actualizada
- [ ] Permisos de carpetas verificados

---

## 📞 Comandos Rápidos de Referencia

```bash
# Backup rápido
docker compose exec postgres pg_dump -U toyota_user plan_comercial > backup.sql

# Restaurar rápido
cat backup.sql | docker compose exec -T postgres psql -U toyota_user plan_comercial

# Ver tablas
docker compose exec postgres psql -U toyota_user -d plan_comercial -c "\dt"

# Ver tamaño DB
docker compose exec postgres psql -U toyota_user -d plan_comercial -c "SELECT pg_size_pretty(pg_database_size('plan_comercial'));"

# Backup carpeta
sudo tar -czf backup.tar.gz postgres_data/

# Restaurar carpeta
docker compose down
sudo tar -xzf backup.tar.gz
docker compose up -d
```
