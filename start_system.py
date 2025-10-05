#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de inicio para el sistema completo de login
"""

import subprocess
import sys
import time
import os
from threading import Thread

def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    try:
        import flask
        import requests
        print("✅ Dependencias verificadas")
        return True
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("📦 Instalando dependencias...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Dependencias instaladas correctamente")
            return True
        except subprocess.CalledProcessError:
            print("❌ Error al instalar dependencias")
            return False

def start_web_server():
    """Inicia el servidor web Flask"""
    print("🌐 Iniciando servidor web...")
    try:
        subprocess.run([sys.executable, "web_server.py"])
    except KeyboardInterrupt:
        print("🛑 Servidor web detenido")

def start_telegram_bot():
    """Inicia el bot de Telegram"""
    print("🤖 Iniciando bot de Telegram...")
    try:
        subprocess.run([sys.executable, "bot_telegram_ngga.py"])
    except KeyboardInterrupt:
        print("🛑 Bot de Telegram detenido")

def main():
    """Función principal"""
    print("🚀 SISTEMA DE LOGIN COMPLETO")
    print("=" * 50)
    
    # Verificar dependencias
    if not check_dependencies():
        print("❌ No se pudieron instalar las dependencias")
        return
    
    print("\n📋 Componentes del sistema:")
    print("1. 🌐 Servidor web Flask (formulario HTML)")
    print("2. 🤖 Bot de Telegram (consulta base de datos)")
    print("3. 🗄️ Base de datos SQLite")
    
    print("\n🔧 Configuración necesaria:")
    print("1. El bot ya está configurado en bot_telegram_ngga.py")
    print("2. Asegúrate de que el servidor web esté funcionando")
    print("3. El bot consultará la API del servidor web")
    
    choice = input("\n¿Qué quieres iniciar? (1=Servidor Web, 2=Bot Telegram, 3=Ambos): ").strip()
    
    if choice == "1":
        start_web_server()
    elif choice == "2":
        start_telegram_bot()
    elif choice == "3":
        print("\n🚀 Iniciando ambos servicios...")
        print("💡 Abre dos terminales:")
        print("   Terminal 1: python web_server.py")
        print("   Terminal 2: python bot_telegram_ngga.py")
        print("\n🌐 Servidor web: http://localhost:5000")
        print("🤖 Bot: Ya configurado en bot_telegram_ngga.py")
    else:
        print("❌ Opción inválida")

if __name__ == "__main__":
    main()

