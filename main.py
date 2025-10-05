#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema de Login - Base de Datos
Script principal para interactuar con la base de datos de usuarios
"""

from database_manager import DatabaseManager
import getpass
import sys

def print_menu():
    """Muestra el menú principal"""
    print("\n" + "="*50)
    print("    SISTEMA DE LOGIN - BASE DE DATOS")
    print("="*50)
    print("1. Registrar nuevo usuario")
    print("2. Iniciar sesión")
    print("3. Ver información de usuario")
    print("4. Cambiar contraseña")
    print("5. Listar usuarios (Admin)")
    print("6. Desactivar usuario (Admin)")
    print("7. Salir")
    print("="*50)

def register_user(db):
    """Registra un nuevo usuario"""
    print("\n--- REGISTRO DE USUARIO ---")
    email = input("Ingrese su correo electrónico: ").strip()
    password = getpass.getpass("Ingrese su contraseña: ")
    confirm_password = getpass.getpass("Confirme su contraseña: ")
    
    if password != confirm_password:
        print("❌ Error: Las contraseñas no coinciden")
        return
    
    success, message = db.register_user(email, password)
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")

def login_user(db):
    """Inicia sesión de usuario"""
    print("\n--- INICIO DE SESIÓN ---")
    email = input("Ingrese su correo: ").strip()
    password = getpass.getpass("Ingrese su contraseña: ")
    
    success, message, user_email = db.login_user(email, password)
    if success:
        print(f"✅ {message}")
        print(f"Bienvenido, {user_email}")
    else:
        print(f"❌ {message}")

def show_user_info(db):
    """Muestra información del usuario"""
    print("\n--- INFORMACIÓN DE USUARIO ---")
    email = input("Ingrese el correo del usuario: ").strip()
    
    user_info = db.get_user_info(email)
    if user_info:
        print(f"\n📧 Correo: {user_info['correo']}")
        print(f"🆔 ID: {user_info['id']}")
        print(f"📅 Fecha de creación: {user_info['fecha_creacion']}")
        print(f"🕒 Último acceso: {user_info['ultimo_acceso'] or 'Nunca'}")
        print(f"🟢 Estado: {'Activo' if user_info['activo'] else 'Inactivo'}")
    else:
        print("❌ Usuario no encontrado")

def change_password(db):
    """Cambia la contraseña del usuario"""
    print("\n--- CAMBIAR CONTRASEÑA ---")
    email = input("Ingrese su correo: ").strip()
    old_password = getpass.getpass("Ingrese su contraseña actual: ")
    new_password = getpass.getpass("Ingrese su nueva contraseña: ")
    confirm_password = getpass.getpass("Confirme su nueva contraseña: ")
    
    if new_password != confirm_password:
        print("❌ Error: Las contraseñas no coinciden")
        return
    
    success, message = db.change_password(email, old_password, new_password)
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")

def list_users(db):
    """Lista todos los usuarios (función administrativa)"""
    print("\n--- LISTA DE USUARIOS ---")
    users = db.list_users()
    
    if users:
        print(f"{'ID':<5} {'Correo':<30} {'Creado':<20} {'Último Acceso':<20} {'Estado'}")
        print("-" * 80)
        for user in users:
            status = "Activo" if user[4] else "Inactivo"
            last_access = user[3] or "Nunca"
            print(f"{user[0]:<5} {user[1]:<30} {user[2]:<20} {last_access:<20} {status}")
    else:
        print("No hay usuarios registrados")

def deactivate_user(db):
    """Desactiva un usuario"""
    print("\n--- DESACTIVAR USUARIO ---")
    email = input("Ingrese el correo del usuario a desactivar: ").strip()
    
    success, message = db.deactivate_user(email)
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")

def main():
    """Función principal"""
    # Inicializar la base de datos
    db = DatabaseManager()
    
    while True:
        print_menu()
        choice = input("\nSeleccione una opción (1-7): ").strip()
        
        if choice == "1":
            register_user(db)
        elif choice == "2":
            login_user(db)
        elif choice == "3":
            show_user_info(db)
        elif choice == "4":
            change_password(db)
        elif choice == "5":
            list_users(db)
        elif choice == "6":
            deactivate_user(db)
        elif choice == "7":
            print("\n👋 ¡Hasta luego!")
            sys.exit(0)
        else:
            print("❌ Opción inválida. Por favor, seleccione 1-7.")
        
        input("\nPresione Enter para continuar...")

if __name__ == "__main__":
    main()
