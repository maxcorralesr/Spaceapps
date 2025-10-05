import logging
import asyncio
from aiogram import Bot, Dispatcher, types, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode

# NUEVO: Importaciones para el servidor web
from aiohttp import web
import requests
import json
import sqlite3
import hashlib

# --- CONFIGURACIÓN ---
API_TOKEN = 'YOUR API KEY'
logging.basicConfig(level=logging.INFO)

# URL del servidor web Flask
WEB_SERVER_URL = "http://localhost:5000"

# Base de datos SQLite
DB_NAME = "login_database.db"

# --- BASE DE DATOS SIMULADA ---
# MODIFICADO: Añadimos un campo 'chat_id' para guardar la "dirección" del usuario
user_db = {
    "sebastiantanori8@gmail.com": {
        "password": "pene",
        "full_name": "Juan Pérez",
        "chat_id": None  # Se llenará cuando el usuario inicie sesión
    }
}

# --- ESTADOS PARA EL LOGIN ---
class LoginStates(StatesGroup):
    waiting_for_email = State()
    waiting_for_password = State()

# --- LÓGICA DEL BOT ---
router = Router()
bot = Bot(token=API_TOKEN)

# --- COMANDOS PARA USUARIOS ---
@router.message(lambda message: message.text and message.text.startswith('/help'))
async def help_command(message: types.Message):
    """Muestra ayuda del bot para usuarios"""
    help_text = """
🤖 <b>Bot de Alertas de Contaminación</b>

<b>Comandos disponibles:</b>
/start - Iniciar sesión para recibir alertas
/help - Mostrar esta ayuda

<b>¿Cómo funciona?</b>
1. Regístrate en el formulario web
2. Usa /start para iniciar sesión con tu email y contraseña
3. Recibirás alertas automáticas sobre la calidad del aire

<b>¿Necesitas ayuda?</b>
Contacta al administrador del sistema.
    """
    await message.answer(help_text, parse_mode=ParseMode.HTML)

# --- FUNCIONES DE VALIDACIÓN ---

def hash_password(password):
    """Genera hash seguro de la contraseña (igual que en database_manager.py)"""
    return hashlib.sha256(password.encode()).hexdigest()

def save_user_chat_id(email: str, chat_id: int):
    """Guarda el chat_id del usuario en la base de datos SQLite"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Verificar si existe una tabla para chat_ids o agregar columna
        cursor.execute("PRAGMA table_info(usuarios)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'chat_id' not in columns:
            # Agregar columna chat_id si no existe
            cursor.execute('ALTER TABLE usuarios ADD COLUMN chat_id INTEGER')
            logging.info("Columna chat_id agregada a la tabla usuarios")
        
        # Actualizar chat_id del usuario
        cursor.execute('''
            UPDATE usuarios SET chat_id = ? WHERE correo = ?
        ''', (chat_id, email))
        
        conn.commit()
        conn.close()
        
        logging.info(f"Chat ID {chat_id} guardado para usuario {email}")
        return True
        
    except Exception as e:
        logging.error(f"Error al guardar chat_id: {e}")
        return False

async def validate_credentials(email: str, password: str):
    """Valida credenciales contra la base de datos SQLite directamente"""
    try:
        # Conectar a la base de datos SQLite
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Buscar usuario en la base de datos
        cursor.execute('''
            SELECT id, correo, contrasena_hash, activo FROM usuarios 
            WHERE correo = ? AND activo = 1
        ''', (email,))
        
        user = cursor.fetchone()
        
        if user:
            user_id, user_email, stored_hash, is_active = user
            
            # Verificar contraseña
            password_hash = hash_password(password)
            if password_hash == stored_hash:
                # Actualizar último acceso
                cursor.execute('''
                    UPDATE usuarios SET ultimo_acceso = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (user_id,))
                conn.commit()
                conn.close()
                
                logging.info(f"Usuario {email} autenticado exitosamente")
                return True, user_email
            else:
                conn.close()
                logging.warning(f"Contraseña incorrecta para {email}")
                return False, None
        else:
            conn.close()
            logging.warning(f"Usuario {email} no encontrado o inactivo")
            return False, None
            
    except Exception as e:
        logging.error(f"Error al validar credenciales: {e}")
        # Fallback a base de datos local como respaldo
        user = user_db.get(email)
        if user and user["password"] == password:
            return True, user["full_name"]
        return False, None

@router.message(CommandStart())
async def start(message: types.Message, state: FSMContext):
    welcome_message = """
🌬️ <b>¡Bienvenido al Sistema de Alertas de Contaminación!</b>

Para recibir alertas automáticas sobre la calidad del aire, necesitas iniciar sesión con tu cuenta.

<b>¿No tienes cuenta?</b>
Regístrate primero en nuestro formulario web.

<b>¿Ya tienes cuenta?</b>
Ingresa tu correo electrónico para continuar:
    """
    await message.answer(welcome_message, parse_mode=ParseMode.HTML)
    await state.set_state(LoginStates.waiting_for_email)

@router.message(LoginStates.waiting_for_email)
async def get_email(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text.strip())
    await message.answer("Ahora ingresa tu contraseña:")
    await state.set_state(LoginStates.waiting_for_password)

@router.message(LoginStates.waiting_for_password)
async def get_password(message: types.Message, state: FSMContext):
    password = message.text.strip()
    user_data = await state.get_data()
    email = user_data.get("email")

    is_valid, full_name = await validate_credentials(email, password)

    if is_valid:
        # Guardar chat_id en la base de datos SQLite
        save_user_chat_id(email, message.chat.id)
        
        # También guardar en base de datos local como respaldo
        if email in user_db:
            user_db[email]["chat_id"] = message.chat.id
        
        success_message = f"""
✅ <b>¡Bienvenido, {full_name}!</b>

🎉 <b>Tu dispositivo ha sido registrado exitosamente.</b>

📱 <b>¿Qué recibirás?</b>
• Alertas automáticas sobre la calidad del aire
• Recomendaciones personalizadas
• Información sobre contaminantes en tu zona

🔔 <b>Las alertas llegarán automáticamente a este chat.</b>

<b>Comandos disponibles:</b>
/help - Ver ayuda
/start - Reiniciar sesión

¡Gracias por usar nuestro sistema de alertas!
        """
        await message.answer(success_message, parse_mode=ParseMode.HTML)
        logging.info(f"Usuario {email} registrado con chat_id: {message.chat.id}")
    else:
        error_message = """
❌ <b>Credenciales incorrectas</b>

El correo o contraseña que ingresaste no es correcto.

<b>¿Qué puedes hacer?</b>
• Verifica que hayas escrito correctamente tu email
• Asegúrate de usar la contraseña correcta
• Si no tienes cuenta, regístrate primero en el formulario web

Usa /start para intentar de nuevo.
        """
        await message.answer(error_message, parse_mode=ParseMode.HTML)
    
    await state.clear()

# --- NUEVO: LÓGICA DEL SERVIDOR WEB ---
async def handle_send_alert(request):
    """
    Este es el endpoint que tu otro programa llamará.
    Espera un JSON con: email, zone, risk_level, contaminants
    """
    try:
        data = await request.json()
        email = data.get("email")
        
        if not email:
            return web.Response(text="Error: Email no proporcionado.", status=400)
        
        # Buscar usuario en la base de datos SQLite
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT chat_id, activo FROM usuarios 
            WHERE correo = ? AND activo = 1
        ''', (email,))
        
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            return web.Response(text=f"Error: Usuario {email} no encontrado o inactivo.", status=404)
        
        chat_id = user[0]
        if not chat_id:
            return web.Response(text=f"Error: El usuario {email} no ha iniciado sesión en el bot.", status=400)

        # Importar y usar recomendacion.py para generar la recomendación
        import recomendacion
        perfil = {
            "email": email,
            "tipo_usuario": data.get("tipo_usuario", "persona"),
            # Puedes agregar más datos del perfil si los tienes
        }
        alteraciones = {
            "zone": data.get("zone", "tu zona"),
            "risk_level": data.get("risk_level", "elevados"),
            "contaminants": data.get("contaminants", "no especificados")
        }
        recomendacion_texto = recomendacion.generar_precauciones(perfil, alteraciones)
        # Enviar la recomendación generada por Gemini
        await bot.send_message(chat_id, recomendacion_texto, parse_mode=ParseMode.HTML)
        logging.info(f"Recomendación enviada a {email} en el chat_id {chat_id}")
        return web.Response(text=f"Recomendación enviada correctamente al usuario {email}.")

    except Exception as e:
        logging.error(f"Error al procesar la alerta: {e}")
        return web.Response(text=f"Error interno del servidor: {e}", status=500)

# --- INICIO DEL BOT Y SERVIDOR ---
async def main():
    dp = Dispatcher()
    dp.include_router(router)
    
    # Creamos la aplicación web
    app = web.Application()
    app.router.add_post('/send_alert', handle_send_alert)
    
    # Iniciamos el servidor web y el bot
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080) # Puedes cambiar el puerto si lo necesitas
    await site.start()
    logging.info("Servidor web iniciado en http://localhost:8080")
    
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot detenido.")