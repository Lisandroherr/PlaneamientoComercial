# 🚀 Inicio Rápido - Sistema de Autenticación

## 1️⃣ Instalar dependencias

```powershell
pip install -r requirements.txt
```

## 2️⃣ Configurar variables de entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
DATABASE_URL=postgresql://usuario:password@host.neon.tech:5432/dbname
SECRET_KEY=clave-secreta-aleatoria-aqui
ADMIN_USERNAME=admin
ADMIN_PASSWORD=TuContraseñaSegura123
ADMIN_EMAIL=admin@tuempresa.com
```

**Generar SECRET_KEY:**
```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

## 3️⃣ Inicializar la base de datos

### Opción A: Script automático (recomendado)
```powershell
python setup_auth.py
```

### Opción B: Manual
```powershell
python init_users.py
```

## 4️⃣ Ejecutar la aplicación

```powershell
python app.py
```

## 5️⃣ Acceder

- **Login**: http://localhost:7860/login
- **Usuario**: El configurado en `ADMIN_USERNAME`
- **Contraseña**: La configurada en `ADMIN_PASSWORD`

---

## 📚 Documentación Completa

Lee `AUTHENTICATION_SETUP.md` para información detallada sobre:
- Funcionalidades implementadas
- Panel de administración
- Gestión de usuarios
- Despliegue en producción
- Seguridad

---

## 🔑 Acceso al Panel de Administración

Una vez autenticado como admin:
- Ve a: http://localhost:7860/admin/users
- Gestiona usuarios (crear, editar, eliminar)
- Cambia tu contraseña inicial

---

## ⚠️ Importante

1. **Cambia la contraseña del admin** después del primer login
2. **Nunca subas el archivo `.env`** al repositorio
3. Usa una **SECRET_KEY única y segura** en producción

---

## ❓ Problemas?

Si algo no funciona:
1. Verifica que el archivo `.env` existe y tiene todas las variables
2. Comprueba que ejecutaste `python init_users.py`
3. Revisa la consola para ver mensajes de error

---

**¡Listo para usar! 🎉**
