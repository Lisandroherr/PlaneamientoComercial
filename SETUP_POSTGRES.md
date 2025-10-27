# 🚀 Configuración de Base de Datos PostgreSQL en Hugging Face

## Paso 1: Crear base de datos en Neon.tech

1. Ve a https://neon.tech
2. Regístrate gratis (con GitHub o email)
3. Crea un nuevo proyecto llamado "PlaneamientoComercial"
4. Copia la **Connection String** (se ve así):
   ```
   postgresql://user:password@ep-xxx.region.aws.neon.tech/dbname?sslmode=require
   ```

## Paso 2: Configurar variable de entorno en Hugging Face

1. Ve a tu Space: https://huggingface.co/spaces/YacopiniAPPS/PlaneamientoComercial
2. Click en **Settings** (⚙️)
3. Scroll hasta **Repository secrets**
4. Click en **New secret**
5. Name: `DATABASE_URL`
6. Value: Pega tu connection string de Neon
7. Click **Add**

## Paso 3: Reiniciar el Space

1. Ve a la pestaña principal del Space
2. Click en el menú **⋮** (tres puntos)
3. Click en **Factory reboot**
4. Espera a que se reconstruya (3-5 minutos)

## ✅ Verificar que funciona

Una vez que el Space esté **Running**:

1. Los modelos y precios deberían cargarse automáticamente
2. Prueba editar un precio y guardar
3. Refresca la página → el cambio debería persistir ✅
4. Reinicia el Space → el cambio aún debería estar ✅

## 🎯 Beneficios

- ✅ **Persistencia real**: Los cambios se guardan permanentemente
- ✅ **Sin límites de tamaño**: La BD puede crecer sin problemas
- ✅ **Backups automáticos**: Neon hace backups por ti
- ✅ **Gratis**: Plan gratuito de Neon es suficiente
