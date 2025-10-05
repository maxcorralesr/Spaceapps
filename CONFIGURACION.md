# 🔧 Guía de Configuración del Sistema de Login

## 📋 Resumen del Sistema

Tu sistema completo incluye:
- **Formulario HTML** (`templates/index.html`) - Para registro de usuarios
- **Servidor web Flask** (`web_server.py`) - Maneja el formulario y API
- **Base de datos SQLite** (`database_manager.py`) - Almacena usuarios
- **Bot de Telegram** (`telegram_bot.py`) - Consulta la base de datos

## 🚀 Instalación y Configuración

### 1. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 2. Bot de Telegram

El bot ya está configurado en `bot_telegram_ngga.py` con tu token. No necesitas configuración adicional.

### 3. Iniciar el Sistema

#### Opción A: Inicio Automático
```bash
python start_system.py
```

#### Opción B: Inicio Manual
**Terminal 1 - Servidor Web:**
```bash
python web_server.py
```

**Terminal 2 - Bot de Telegram:**
```bash
python bot_telegram_ngga.py
```

## 🌐 Uso del Sistema

### 1. Formulario Web
- Abre http://localhost:5000 en tu navegador
- Completa el formulario de registro
- Los datos se guardan en la base de datos SQLite

### 2. Bot de Telegram
El bot permite a los usuarios autenticarse y recibir alertas:

**Comandos para usuarios:**
- `/start` - Iniciar sesión en el bot
- `/help` - Mostrar ayuda

**Flujo de usuario:**
1. Usuario se registra en el formulario web
2. Usuario inicia sesión en el bot con `/start`
3. Usuario recibe alertas automáticas sobre contaminación

## 📁 Estructura de Archivos

```
Base de Datos/
├── database_manager.py      # Clase de base de datos
├── web_server.py          # Servidor Flask
├── telegram_bot.py        # Bot de Telegram
├── templates/
│   └── index.html         # Formulario HTML
├── login_database.db      # Base de datos SQLite
├── requirements.txt       # Dependencias
├── start_system.py        # Script de inicio
└── CONFIGURACION.md       # Esta guía
```

## 🔄 Flujo del Sistema

### 1. Registro de Usuarios
- **Formulario HTML** → **Base de datos SQLite**
- Usuarios se registran con email y contraseña
- Datos se almacenan encriptados en SQLite

### 2. Autenticación en Bot
- **Bot de Telegram** → **Consulta base de datos SQLite**
- Usuario inicia sesión con `/start`
- Bot verifica credenciales contra la base de datos
- Bot guarda chat_id del usuario

### 3. Envío de Alertas
- **Sistema externo** → **Bot de Telegram**
- Bot consulta chat_id desde la base de datos
- Envía alertas automáticas al usuario

## 🗄️ Base de Datos

### Tabla: usuarios
| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER | ID único |
| correo | TEXT | Email del usuario |
| contrasena_hash | TEXT | Hash de la contraseña |
| fecha_creacion | TIMESTAMP | Fecha de registro |
| ultimo_acceso | TIMESTAMP | Último login |
| activo | BOOLEAN | Estado del usuario |
| chat_id | INTEGER | ID del chat de Telegram (se agrega automáticamente) |

## 🔒 Seguridad

- Contraseñas hasheadas con SHA-256
- Validación de formato de email
- Prevención de inyección SQL
- API endpoints protegidos

## 🐛 Solución de Problemas

### Error: "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Error: "Bot token not configured"
- Configura tu token en `telegram_bot.py`
- Obtén el token de @BotFather

### Error: "Connection refused"
- Asegúrate de que el servidor web esté ejecutándose
- Verifica que el puerto 5000 esté libre

### El bot no responde
- Verifica que el token sea correcto
- Asegúrate de que el servidor web esté funcionando
- Revisa los logs del bot

## 📞 Soporte

Si tienes problemas:
1. Verifica que todas las dependencias estén instaladas
2. Revisa que el servidor web esté funcionando
3. Confirma que el token del bot sea correcto
4. Revisa los logs de error en la consola

## 🚀 Próximos Pasos

Para mejorar el sistema:
- Agregar autenticación JWT
- Implementar logs de auditoría
- Agregar notificaciones automáticas
- Crear panel de administración web

