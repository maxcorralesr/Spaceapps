#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Servidor web Flask para manejar el formulario de registro
"""

from flask import Flask, render_template, request, redirect, url_for, jsonify
from database_manager import DatabaseManager
import os
from datetime import datetime
import pandas as pd
from typing import Optional, List

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'  # Cambia esto en producción

# Inicializar la base de datos
db = DatabaseManager()

# Almacén simple en memoria para la última serie temporal cargada
timeseries_store = {'data': []}


def _find_date_column(df: pd.DataFrame) -> Optional[str]:
    candidates = ['date', 'fecha', 'dia', 'fecha_hora', 'timestamp', 'time']
    lower_map = {c.lower().strip(): c for c in df.columns}
    for k in candidates:
        if k in lower_map:
            return lower_map[k]
    # fallback: try infer by dtype
    for c in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[c]):
            return c
    # fallback: detect textual date patterns like '23/08/02' or '2023-08-02'
    sample = df.head(200)
    for c in df.columns:
        if pd.api.types.is_string_dtype(df[c]):
            vals = sample[c].astype(str).str.strip().dropna()
            if vals.str.contains(r"\b\d{2}/\d{2}/\d{2}\b").any() or vals.str.contains(r"\b\d{4}-\d{2}-\d{2}\b").any():
                return c
    return None


def _find_value_column(df: pd.DataFrame, keywords: List[str]) -> Optional[str]:
    lower_map = {c.lower().strip(): c for c in df.columns}
    for k in keywords + ['value']:
        for key in list(lower_map.keys()):
            if k in key:
                return lower_map[key]
    # fallback: first numeric column excluding date
    for c in df.columns:
        if pd.api.types.is_numeric_dtype(df[c]):
            return c
    return None


def _normalize_single(df: pd.DataFrame, kind: str) -> pd.DataFrame:
    """
    kind: 'no2' or 'hch'
    Returns a dataframe with columns ['date', kind]
    """
    date_col = _find_date_column(df)
    if date_col is None:
        raise ValueError('No se encontró columna de fecha')
    if kind == 'no2':
        val_col = _find_value_column(df, ['no2'])
    else:
        val_col = _find_value_column(df, ['hch', 'hcho', 'formaldeh'])
    if val_col is None:
        raise ValueError(f'No se encontró columna de valor para {kind}')

    out = df[[date_col, val_col]].copy()
    # Try multiple date formats, including YY/MM/DD
    out[date_col] = pd.to_datetime(out[date_col], errors='coerce', infer_datetime_format=True)
    # If still NaT, attempt specific formats
    mask_nat = out[date_col].isna()
    if mask_nat.any():
        try:
            out.loc[mask_nat, date_col] = pd.to_datetime(out.loc[mask_nat, date_col].astype(str), format='%y/%m/%d', errors='coerce')
        except Exception:
            pass
    out = out.dropna(subset=[date_col])
    out[val_col] = pd.to_numeric(out[val_col], errors='coerce')
    out = out.dropna(subset=[val_col])
    out = out.rename(columns={date_col: 'date', val_col: kind})
    out['date'] = out['date'].dt.normalize()
    out = out.groupby('date', as_index=False)[kind].mean()
    return out


def _scan_for_files() -> (Optional[str], Optional[str]):
    files = [f for f in os.listdir('.') if f.lower().endswith('.csv')]
    no2_file = None
    hch_file = None
    for f in files:
        name = f.lower()
        if 'no2' in name and no2_file is None:
            no2_file = f
        if (('hch' in name) or ('hcho' in name) or ('formaldeh' in name)) and hch_file is None:
            hch_file = f
    return no2_file, hch_file


def load_local_timeseries() -> List[dict]:
    no2_path, hch_path = _scan_for_files()
    if not no2_path or not hch_path:
        return []
    try:
        no2_df_raw = pd.read_csv(no2_path)
        hch_df_raw = pd.read_csv(hch_path)
        no2_df = _normalize_single(no2_df_raw, 'no2')
        hch_df = _normalize_single(hch_df_raw, 'hch')
        merged = pd.merge(no2_df, hch_df, on='date', how='inner')
        # Filter to requested range if present
        try:
            start = pd.Timestamp('2023-08-02')
            end = pd.Timestamp('2025-09-01')
            merged = merged[(merged['date'] >= start) & (merged['date'] <= end)]
        except Exception:
            pass
        merged = merged.sort_values('date')
        data = [{
            'date': d.strftime('%Y-%m-%d'),
            'no2': float(n),
            'hch': float(h)
        } for d, n, h in zip(merged['date'], merged['no2'], merged['hch'])]
        return data
    except Exception:
        return []

@app.route('/')
def index():
    """Página principal con el formulario de registro"""
    return render_template('metatempo.html')

@app.route('/register_personal', methods=['POST'])
def register_personal():
    """Maneja el registro de usuarios personales"""
    try:
        # Obtener datos del formulario personal
        # Obtener IP del usuario
        user_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        # Usar una API pública para geolocalización por IP
        import requests as pyrequests
        region = ''
        try:
            geo_resp = pyrequests.get(f'https://ipapi.co/{user_ip}/json/')
            if geo_resp.status_code == 200:
                geo_data = geo_resp.json()
                region = geo_data.get('region', '')
                if not region:
                    region = geo_data.get('country_name', '')
        except Exception:
            region = ''
        data = {
            'nombre': request.form.get('p-nombre', '').strip(),
            'email': request.form.get('p-email', '').strip(),
            'password': request.form.get('p-password', ''),
            'edad': request.form.get('p-edad', ''),
            'region': region,
            'telefono': request.form.get('p-telefono', '').strip(),
            'sexo': request.form.get('p-sexo', ''),
            'oficio': request.form.get('p-oficio', ''),
            'otro_oficio': request.form.get('p-otro-oficio', '').strip(),
            'vulnerable': request.form.get('vulnerable', 'no'),
            'grupo_vulnerable': request.form.get('vulnerable-group', '')
        }
        
        # Validar datos obligatorios
        if not data['email'] or not data['password']:
            return jsonify({'success': False, 'message': 'Email y contraseña son obligatorios'})
        
        # Registrar usuario en la base de datos
        success, message = db.register_user(data['email'], data['password'])
        
        if success:
            # Guardar datos adicionales en un archivo de log o base de datos extendida
            log_user_data('PERSONAL', data)
            return jsonify({'success': True, 'message': f'Usuario registrado exitosamente: {data["nombre"]}'})
        else:
            return jsonify({'success': False, 'message': f'Error al registrar: {message}'})
                
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'})

@app.route('/register_institutional', methods=['POST'])
def register_institutional():
    """Maneja el registro de usuarios institucionales"""
    try:
        # Obtener datos del formulario institucional
        data = {
            'nombre_institucion': request.form.get('i-nombre', '').strip(),
            'email': request.form.get('i-email', '').strip(),
            'password': request.form.get('i-password', ''),
            'telefono': request.form.get('i-telefono', '').strip(),
            'region': request.form.get('i-region', ''),
            'sector': request.form.get('i-sector', ''),
            'otro_sector': request.form.get('i-otro-sector', '').strip(),
            'actividad': request.form.get('i-actividad', '').strip()
        }
        
        # Validar datos obligatorios
        if not data['email'] or not data['password']:
            return jsonify({'success': False, 'message': 'Email y contraseña son obligatorios'})
        
        # Registrar usuario en la base de datos
        success, message = db.register_user(data['email'], data['password'])
        
        if success:
            # Guardar datos adicionales
            log_user_data('INSTITUCIONAL', data)
            return jsonify({'success': True, 'message': f'Institución registrada exitosamente: {data["nombre_institucion"]}'})
        else:
            return jsonify({'success': False, 'message': f'Error al registrar: {message}'})
                
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'})

@app.route('/api/users')
def api_users():
    """API endpoint para obtener lista de usuarios (para el bot de Telegram)"""
    try:
        users = db.list_users()
        users_data = []
        for user in users:
            users_data.append({
                'id': user[0],
                'email': user[1],
                'created_at': user[2],
                'last_access': user[3],
                'active': bool(user[4])
            })
        return jsonify({'success': True, 'users': users_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/user/<email>')
def api_user_info(email):
    """API endpoint para obtener información de un usuario específico"""
    try:
        user_info = db.get_user_info(email)
        if user_info:
            return jsonify({'success': True, 'user': user_info})
        else:
            return jsonify({'success': False, 'error': 'Usuario no encontrado'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/check_user/<email>')
def api_check_user(email):
    """API endpoint para verificar si un usuario existe"""
    try:
        user_info = db.get_user_info(email)
        if user_info:
            return jsonify({
                'success': True, 
                'exists': True, 
                'active': bool(user_info['activo']),
                'created_at': user_info['fecha_creacion'],
                'last_access': user_info['ultimo_acceso']
            })
        else:
            return jsonify({'success': True, 'exists': False})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/login', methods=['POST'])
def api_login():
    """API endpoint para login de usuarios (para el bot de Telegram)"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'success': False, 'error': 'Email y contraseña son obligatorios'})
        
        # Usar la función de login de la base de datos
        success, message, user_email = db.login_user(email, password)
        
        if success:
            return jsonify({'success': True, 'message': message, 'user': user_email})
        else:
            return jsonify({'success': False, 'error': message})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def log_user_data(user_type, data):
    """Registra datos adicionales del usuario en un archivo"""
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {user_type} - {data}\n"
        
        with open('user_details.log', 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Error al escribir log: {e}")


@app.route('/api/upload_timeseries', methods=['POST'])
def api_upload_timeseries():
    """
    Sube un CSV con columnas: date, no2, hch (o equivalentes),
    normaliza y almacena en memoria para graficar.
    """
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'Envíe un archivo en el campo "file"'}), 400
        f = request.files['file']
        if not f.filename:
            return jsonify({'success': False, 'error': 'Archivo vacío'}), 400

        df = pd.read_csv(f)

        # Normalizar nombres y mapear columnas
        cols = {c.lower().strip(): c for c in df.columns}
        date_col = next((cols[k] for k in cols if k in ('date', 'fecha', 'dia', 'fecha_hora')), None)
        no2_col = next((cols[k] for k in cols if k in ('no2',)), None)
        hch_col = next((cols[k] for k in cols if k in ('hch', 'hcho', 'formaldehido', 'formaldehído', 'formaldehyde')), None)
        if not date_col or not no2_col or not hch_col:
            return jsonify({'success': False, 'error': 'Se requieren columnas: date, no2, hch (o equivalentes)'}), 400

        df = df[[date_col, no2_col, hch_col]].copy()
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df[no2_col] = pd.to_numeric(df[no2_col], errors='coerce')
        df[hch_col] = pd.to_numeric(df[hch_col], errors='coerce')
        df = df.dropna().sort_values(by=date_col)

        data = [{
            'date': d.strftime('%Y-%m-%d'),
            'no2': float(n),
            'hch': float(h)
        } for d, n, h in zip(df[date_col], df[no2_col], df[hch_col])]

        timeseries_store['data'] = data
        return jsonify({'success': True, 'count': len(data), 'data': data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/timeseries', methods=['GET'])
def api_timeseries():
    """Devuelve la serie histórica combinada de archivos locales (NO2 + HCHO)."""
    data = load_local_timeseries()
    if data:
        timeseries_store['data'] = data
    return jsonify({'success': True, 'data': timeseries_store['data']})

if __name__ == '__main__':
    # Crear directorio de templates si no existe
    os.makedirs('templates', exist_ok=True)
    # Pre-cargar datos locales si están disponibles
    timeseries_store['data'] = load_local_timeseries()
    
    print("🚀 Iniciando servidor web...")
    print("📝 Formulario disponible en: http://localhost:5000")
    print("🔌 API endpoints disponibles:")
    print("   - GET /api/users - Lista todos los usuarios")
    print("   - GET /api/user/<email> - Información de usuario específico")
    print("   - GET /api/check_user/<email> - Verificar si usuario existe")
    print("\n💡 Para detener el servidor presiona Ctrl+C")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

