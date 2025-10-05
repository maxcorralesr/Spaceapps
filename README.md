# MetaTempo – Plataforma Web con Login, API y Visualización (NO₂ y HCHO)

Proyecto que combina:
- Sistema de usuarios (SQLite) con login y API.
- Servidor web (Flask) con página pública `templates/metatempo.html`.
- Visualización de “Tendencias históricas” comparando NO₂ y HCHO a partir de archivos CSV locales (TEMPO).
- Bot de Telegram (opcional) para interacción con usuarios.

## 📁 Estructura del proyecto

```
Base de Datos/
├── web_server.py            # Servidor Flask y endpoints HTTP
├── templates/
│   └── metatempo.html      # Página principal (Tailwind + Chart.js)
├── database_manager.py     # Capa de acceso a datos (SQLite)
├── main.py                 # CLI para administración de usuarios
├── recomendacion.py        # Generación de recomendaciones (Gemini)
├── bot_telegram.py         # Bot de Telegram (opcional)
├── requirements.txt        # Dependencias
├── README.md               # Documentación (este archivo)
├── login_database.db       # SQLite (autogenerada)
├── user_details.log        # Log de registros
└── datos_tempo_*.csv       # CSV locales (NO2/HCHO) usados por la gráfica
```

## 🛠️ Instalación

Requisitos: Python 3.10+ recomendado.

1) Crear entorno (opcional) e instalar dependencias:
```bash
pip install -r requirements.txt
```

2) Coloca en la raíz del proyecto dos CSV grandes (de TEMPO u otros):
- Un archivo cuyo nombre contenga `no2` (ej. `datos_tempo_no2_completo.csv`).
- Un archivo cuyo nombre contenga `hch`, `hcho` o `formaldeh` (ej. `datos_tempo_hcho_completo.csv`).

Formato esperado (flexible):
- Columna de fecha/hora: `time` (acepta también `date/fecha/dia/fecha_hora/timestamp`).
- Columna de valor: `value` (si no existe, se buscará por nombre que contenga la palabra clave del gas).
- Otras columnas (lat/lon/qa/units…) se ignoran para la gráfica.
- Fechas como `23/08/02` (AA/MM/DD) o `2023-08-02` se detectan automáticamente.

## ▶️ Ejecución

Servidor web:
```bash
python web_server.py
```
Abre `http://localhost:5000` y ve a la tarjeta “Tendencias históricas (NO₂ y HCHO)”.

Qué verás:
- La página consulta `GET /api/timeseries` y grafica automáticamente NO₂ vs HCHO.
- El servidor mergea y promedia por fecha, filtra el rango 2023-08-02 → 2025-09-01 y devuelve la serie ordenada.

CLI administrativa de usuarios (opcional):
```bash
python main.py
```

## 🌐 Endpoints HTTP (Flask)

- `GET /` → Render de `metatempo.html`.
- `POST /register_personal` → Registra usuario personal (JSON de estado).
- `POST /register_institutional` → Registra usuario institucional (JSON de estado).
- `GET /api/users` → Lista usuarios (para integraciones).
- `GET /api/user/<email>` → Detalle de un usuario.
- `GET /api/check_user/<email>` → Verifica existencia/actividad.
- `POST /api/login` → Login simple contra SQLite.
- `GET /api/timeseries` → Devuelve serie histórica combinada de NO₂ y HCHO a partir de CSV locales.
  - Detección de archivos por nombre: contiene `no2` y `hch|hcho|formaldeh`.
  - Detección de columnas: fecha `time` (o equivalentes) y valor `value` (o equivalentes).
  - Limpieza: conversión a datetime, coerción a numérico y promedio por fecha.
  - Filtro de rango: 2023-08-02 a 2025-09-01.

Nota: también existe `POST /api/upload_timeseries` (ingestión manual de CSV) pero la UI actual ya no lo usa.

## 🗄️ Base de datos de usuarios (SQLite)

Archivo: `login_database.db` (autogenerado por `database_manager.py`).

Tabla `usuarios`:
| Campo | Tipo | Descripción |
|---|---|---|
| id | INTEGER | Clave primaria AUTOINCREMENT |
| correo | TEXT | Único, requerido |
| contrasena_hash | TEXT | SHA-256 de la contraseña |
| fecha_creacion | TIMESTAMP | Alta |
| ultimo_acceso | TIMESTAMP | Último login exitoso |
| activo | BOOLEAN | 1=activo, 0=inactivo |

Operaciones clave expuestas por `DatabaseManager`:
- `register_user(email, password)`
- `login_user(email, password)`
- `get_user_info(email)`
- `list_users()`
- `deactivate_user(email)`
- `change_password(email, old_password, new_password)`

## 📊 Visualización “Tendencias históricas”

Front-end (`templates/metatempo.html`):
- TailwindCSS para estilos.
- Chart.js para líneas comparativas NO₂ vs HCHO.
- JS que hace `fetch('/api/timeseries')` y dibuja automáticamente.

Back-end (`web_server.py`):
- Escanea CSV locales, detecta columnas `time`/`value`, agrega por fecha, une series y limita al rango 2023-08-02 a 2025-09-01.
- Devuelve JSON: `[{ date: 'YYYY-MM-DD', no2: float, hch: float }, ...]`.

Cambios comunes solicitables:
- Agregación por semana/mes (en lugar de por día).
- Escala logarítmica o ejes duales.
- Filtros por región si se proveen columnas.

## 🤖 Bot de Telegram (opcional)

Archivo: `bot_telegram.py`.
- Usa `aiogram` para manejar comandos y puede consultar el API/usuarios.
- Requiere token de bot en entorno si se habilita.

## 🔐 Seguridad

- Passwords con SHA-256. Considera cambiar a `bcrypt` en producción.
- Validación básica de email y longitud de contraseña.
- Endpoints devuelven mensajes sanitizados; evita imprimir trazas en producción.

## 🧪 Pruebas rápidas

```bash
python test_database.py
```

## 🧯 Solución de problemas

- “La gráfica muestra 0/1 puntos”: verifica que existan dos CSV con nombres que contengan `no2` y `hch|hcho|formaldeh`, y que tengan `time` y `value` (o columnas equivalentes reconocibles). El rango por defecto filtra 2023-08-02 → 2025-09-01.
- Error al convertir fechas: revisa que `time` sea texto con formato `AA/MM/DD`, `YYYY-MM-DD` o timestamps convertibles.
- Dependencias: ejecuta `pip install -r requirements.txt`.

## 📝 Licencia

Uso educativo y comercial permitido. Ajusta según tus necesidades.
