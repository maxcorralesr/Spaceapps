#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de pruebas para la base de datos de login
"""

from database_manager import DatabaseManager
import os

def test_database():
    """Ejecuta pruebas básicas de la base de datos"""
    print("🧪 Iniciando pruebas de la base de datos...")
    
    # Crear instancia de la base de datos
    db = DatabaseManager("test_login.db")
    
    # Prueba 1: Registrar usuario válido
    print("\n1. Probando registro de usuario válido...")
    success, message = db.register_user("test@ejemplo.com", "password123")
    print(f"   Resultado: {'✅' if success else '❌'} {message}")
    
    # Prueba 2: Intentar registrar el mismo usuario
    print("\n2. Probando registro de usuario duplicado...")
    success, message = db.register_user("test@ejemplo.com", "otrapassword")
    print(f"   Resultado: {'✅' if success else '❌'} {message}")
    
    # Prueba 3: Login con credenciales correctas
    print("\n3. Probando login con credenciales correctas...")
    success, message, user = db.login_user("test@ejemplo.com", "password123")
    print(f"   Resultado: {'✅' if success else '❌'} {message}")
    
    # Prueba 4: Login con credenciales incorrectas
    print("\n4. Probando login con credenciales incorrectas...")
    success, message, user = db.login_user("test@ejemplo.com", "passwordincorrecta")
    print(f"   Resultado: {'✅' if success else '❌'} {message}")
    
    # Prueba 5: Validación de email
    print("\n5. Probando validación de email...")
    success, message = db.register_user("email-invalido", "password123")
    print(f"   Resultado: {'✅' if success else '❌'} {message}")
    
    # Prueba 6: Validación de contraseña
    print("\n6. Probando validación de contraseña...")
    success, message = db.register_user("test2@ejemplo.com", "123")
    print(f"   Resultado: {'✅' if success else '❌'} {message}")
    
    # Prueba 7: Obtener información de usuario
    print("\n7. Probando obtención de información de usuario...")
    user_info = db.get_user_info("test@ejemplo.com")
    if user_info:
        print(f"   ✅ Usuario encontrado: {user_info['correo']}")
    else:
        print("   ❌ Usuario no encontrado")
    
    # Prueba 8: Listar usuarios
    print("\n8. Probando listado de usuarios...")
    users = db.list_users()
    print(f"   ✅ Se encontraron {len(users)} usuarios")
    
    # Prueba 9: Cambiar contraseña
    print("\n9. Probando cambio de contraseña...")
    success, message = db.change_password("test@ejemplo.com", "password123", "nuevapassword")
    print(f"   Resultado: {'✅' if success else '❌'} {message}")
    
    # Prueba 10: Login con nueva contraseña
    print("\n10. Probando login con nueva contraseña...")
    success, message, user = db.login_user("test@ejemplo.com", "nuevapassword")
    print(f"   Resultado: {'✅' if success else '❌'} {message}")
    
    # Prueba 11: Desactivar usuario
    print("\n11. Probando desactivación de usuario...")
    success, message = db.deactivate_user("test@ejemplo.com")
    print(f"   Resultado: {'✅' if success else '❌'} {message}")
    
    # Prueba 12: Login con usuario desactivado
    print("\n12. Probando login con usuario desactivado...")
    success, message, user = db.login_user("test@ejemplo.com", "nuevapassword")
    print(f"   Resultado: {'✅' if success else '❌'} {message}")
    
    print("\n🎉 Pruebas completadas!")
    
    # Limpiar archivo de prueba
    if os.path.exists("test_login.db"):
        os.remove("test_login.db")
        print("🧹 Archivo de prueba eliminado")

if __name__ == "__main__":
    test_database()
