import sqlite3
import hashlib
import os
from datetime import datetime
import re

class DatabaseManager:
    def __init__(self, db_name="login_database.db"):
        """Inicializa la conexión a la base de datos"""
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        """Crea la tabla de usuarios si no existe"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                correo TEXT UNIQUE NOT NULL,
                contrasena_hash TEXT NOT NULL,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultimo_acceso TIMESTAMP,
                activo BOOLEAN DEFAULT 1
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """Genera hash seguro de la contraseña"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def validate_email(self, email):
        """Valida formato de correo electrónico"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password):
        """Valida fortaleza de la contraseña"""
        if len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"
        return True, "Contraseña válida"
    
    def register_user(self, email, password):
        """Registra un nuevo usuario"""
        if not self.validate_email(email):
            return False, "Formato de correo inválido"
        
        is_valid, message = self.validate_password(password)
        if not is_valid:
            return False, message
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            # Verificar si el correo ya existe
            cursor.execute("SELECT id FROM usuarios WHERE correo = ?", (email,))
            if cursor.fetchone():
                conn.close()
                return False, "El correo ya está registrado"
            
            # Crear nuevo usuario
            password_hash = self.hash_password(password)
            cursor.execute('''
                INSERT INTO usuarios (correo, contrasena_hash)
                VALUES (?, ?)
            ''', (email, password_hash))
            
            conn.commit()
            conn.close()
            return True, "Usuario registrado exitosamente"
            
        except Exception as e:
            return False, f"Error al registrar usuario: {str(e)}"
    
    def login_user(self, email, password):
        """Autentica un usuario"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            cursor.execute('''
                SELECT id, correo, activo FROM usuarios 
                WHERE correo = ? AND contrasena_hash = ? AND activo = 1
            ''', (email, password_hash))
            
            user = cursor.fetchone()
            
            if user:
                # Actualizar último acceso
                cursor.execute('''
                    UPDATE usuarios SET ultimo_acceso = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (user[0],))
                conn.commit()
                conn.close()
                return True, "Login exitoso", user[1]
            else:
                conn.close()
                return False, "Credenciales inválidas", None
                
        except Exception as e:
            return False, f"Error en login: {str(e)}", None
    
    def get_user_info(self, email):
        """Obtiene información de un usuario"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, correo, fecha_creacion, ultimo_acceso, activo 
                FROM usuarios WHERE correo = ?
            ''', (email,))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return {
                    'id': user[0],
                    'correo': user[1],
                    'fecha_creacion': user[2],
                    'ultimo_acceso': user[3],
                    'activo': user[4]
                }
            return None
            
        except Exception as e:
            print(f"Error al obtener información del usuario: {str(e)}")
            return None
    
    def list_users(self):
        """Lista todos los usuarios (solo para administración)"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, correo, fecha_creacion, ultimo_acceso, activo 
                FROM usuarios ORDER BY fecha_creacion DESC
            ''')
            
            users = cursor.fetchall()
            conn.close()
            
            return users
            
        except Exception as e:
            print(f"Error al listar usuarios: {str(e)}")
            return []
    
    def deactivate_user(self, email):
        """Desactiva un usuario"""
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE usuarios SET activo = 0 WHERE correo = ?
            ''', (email,))
            
            if cursor.rowcount > 0:
                conn.commit()
                conn.close()
                return True, "Usuario desactivado"
            else:
                conn.close()
                return False, "Usuario no encontrado"
                
        except Exception as e:
            return False, f"Error al desactivar usuario: {str(e)}"
    
    def change_password(self, email, old_password, new_password):
        """Cambia la contraseña de un usuario"""
        # Verificar credenciales actuales
        success, message, _ = self.login_user(email, old_password)
        if not success:
            return False, "Contraseña actual incorrecta"
        
        # Validar nueva contraseña
        is_valid, message = self.validate_password(new_password)
        if not is_valid:
            return False, message
        
        try:
            conn = sqlite3.connect(self.db_name)
            cursor = conn.cursor()
            
            new_password_hash = self.hash_password(new_password)
            cursor.execute('''
                UPDATE usuarios SET contrasena_hash = ? WHERE correo = ?
            ''', (new_password_hash, email))
            
            conn.commit()
            conn.close()
            return True, "Contraseña cambiada exitosamente"
            
        except Exception as e:
            return False, f"Error al cambiar contraseña: {str(e)}"
