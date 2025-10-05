#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de demostración rápida del sistema de login
"""

from database_manager import DatabaseManager

def demo():
    """Demostración rápida del sistema"""
    print("🎯 DEMOSTRACIÓN DEL SISTEMA DE LOGIN")
    print("="*50)
    
    # Crear base de datos
    db = DatabaseManager("demo_login.db")
    print("✅ Base de datos inicializada")
    
    # Registrar algunos usuarios de ejemplo
    usuarios_demo = [
        ("admin@empresa.com", "admin123"),
        ("usuario1@empresa.com", "password123"),
        ("usuario2@empresa.com", "mipassword456")
    ]
    
    print("\n📝 Registrando usuarios de demostración...")
    for email, password in usuarios_demo:
        success, message = db.register_user(email, password)
        print(f"   {email}: {'✅' if success else '❌'} {message}")
    
    # Mostrar lista de usuarios
    print("\n👥 Lista de usuarios registrados:")
    users = db.list_users()
    for user in users:
        status = "🟢 Activo" if user[4] else "🔴 Inactivo"
        print(f"   ID: {user[0]} | {user[1]} | {status}")
    
    # Probar login
    print("\n🔐 Probando login...")
    success, message, user_email = db.login_user("admin@empresa.com", "admin123")
    print(f"   Login admin: {'✅' if success else '❌'} {message}")
    
    # Mostrar información de usuario
    print("\n📊 Información del usuario admin:")
    user_info = db.get_user_info("admin@empresa.com")
    if user_info:
        print(f"   📧 Email: {user_info['correo']}")
        print(f"   🆔 ID: {user_info['id']}")
        print(f"   📅 Creado: {user_info['fecha_creacion']}")
        print(f"   🕒 Último acceso: {user_info['ultimo_acceso'] or 'Nunca'}")
    
    # Cambiar contraseña
    print("\n🔑 Cambiando contraseña...")
    success, message = db.change_password("admin@empresa.com", "admin123", "nuevapassword")
    print(f"   Cambio de contraseña: {'✅' if success else '❌'} {message}")
    
    # Probar login con nueva contraseña
    print("\n🔐 Probando login con nueva contraseña...")
    success, message, user_email = db.login_user("admin@empresa.com", "nuevapassword")
    print(f"   Login con nueva contraseña: {'✅' if success else '❌'} {message}")
    
    print("\n🎉 ¡Demostración completada!")
    print("💡 Para usar el sistema completo, ejecuta: python main.py")
    
    # Limpiar archivo de demostración
    import os
    if os.path.exists("demo_login.db"):
        os.remove("demo_login.db")
        print("🧹 Archivo de demostración eliminado")

if __name__ == "__main__":
    demo()
