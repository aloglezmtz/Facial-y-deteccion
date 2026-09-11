"""
Fase B - Persistencia en PostgreSQL (Render Cloud)
Reemplaza la base de datos local SQLite por una base de datos segura en la nube.
Sobrevive a reinicios del servidor de Streamlit y centraliza los datos en internet.

Cada usuario tiene un `session_id` anónimo (generado en app_streamlit.py y guardado
en la URL para sobrevivir a recargas de página). TODAS las consultas se filtran por
ese id, así que un usuario nunca ve ni borra el historial de otro.

La URL de conexión NUNCA va escrita en este archivo: se lee desde
st.secrets, que Streamlit Cloud provee de forma segura (Settings > Secrets
en el dashboard de tu app) y que en local vive en .streamlit/secrets.toml
(archivo que debe estar en tu .gitignore, para que nunca se suba a git).
"""

import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime
from contextlib import contextmanager


def _obtener_database_url():
    try:
        return st.secrets["DATABASE_URL"]
    except (KeyError, FileNotFoundError):
        raise RuntimeError(
            "No se encontró DATABASE_URL en st.secrets. "
            "En Streamlit Cloud: Settings > Secrets, agrega:\n"
            'DATABASE_URL = "postgresql://usuario:password@host/db"\n'
            "En local: crea .streamlit/secrets.toml con la misma línea "
            "(y agrega esa carpeta a tu .gitignore)."
        )


@contextmanager
def _conexion():
    conn = psycopg2.connect(_obtener_database_url())
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def inicializar_db():
    with _conexion() as conn:
        with conn.cursor() as cur:
            # 1. Tabla de mensajes
            cur.execute("""
                CREATE TABLE IF NOT EXISTS mensajes (
                    id SERIAL PRIMARY KEY,
                    session_id TEXT,                   -- identifica a qué usuario/navegador pertenece
                    rol TEXT NOT NULL,                 -- 'user' | 'assistant'
                    texto TEXT NOT NULL,
                    emocion_estimada TEXT,
                    confianza REAL,
                    camara_usada INTEGER DEFAULT 0,
                    timestamp TEXT NOT NULL
                )
            """)
            # Por si la tabla ya existía de antes de este cambio (producción):
            # agrega la columna sin tronar si ya está.
            cur.execute("ALTER TABLE mensajes ADD COLUMN IF NOT EXISTS session_id TEXT")
            cur.execute("ALTER TABLE mensajes ADD COLUMN IF NOT EXISTS emocion_especifica TEXT")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_mensajes_session ON mensajes(session_id)")

            # 2. Tabla de señales faciales
            cur.execute("""
                CREATE TABLE IF NOT EXISTS senales_faciales (
                    id SERIAL PRIMARY KEY,
                    mensaje_id INTEGER NOT NULL,
                    apertura_ojo REAL,
                    apertura_boca REAL,
                    elevacion_cejas REAL,
                    orientacion_json TEXT,
                    calidad_deteccion TEXT,
                    FOREIGN KEY (mensaje_id) REFERENCES mensajes(id) ON DELETE CASCADE
                )
            """)

            # 3. Tabla de uso de herramientas (Caja de Gatitos)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS uso_herramientas (
                    id SERIAL PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    herramienta_id TEXT NOT NULL,
                    categoria TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_uso_session ON uso_herramientas(session_id)")

            # 4. Tabla de alertas de crisis (detección de riesgo en texto)
            # Solo guarda nivel y timestamp -- el texto del mensaje ya vive
            # en `mensajes`, y aquí no se duplica ni se anota qué frase
            # disparó la alerta.
            cur.execute("""
                CREATE TABLE IF NOT EXISTS alertas_crisis (
                    id SERIAL PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    mensaje_id INTEGER,
                    nivel TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY (mensaje_id) REFERENCES mensajes(id) ON DELETE SET NULL
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_alertas_session ON alertas_crisis(session_id)")

            # 5. Perfil/ajustes del usuario (una fila por session_id). Todo
            # opcional -- si no existe fila, se usan valores por defecto en
            # el código de la app.
            cur.execute("""
                CREATE TABLE IF NOT EXISTS perfiles (
                    session_id TEXT PRIMARY KEY,
                    nombre TEXT,
                    objetivo TEXT,
                    tema TEXT,
                    avatar_bot TEXT,
                    recordatorio_activo BOOLEAN DEFAULT FALSE,
                    recordatorio_hora TEXT,
                    pin_hash TEXT,
                    creado_en TEXT
                )
            """)

            # 6. Reportes de soporte (falla técnica / retroalimentación)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS reportes (
                    id SERIAL PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    tipo TEXT NOT NULL,     -- 'falla' | 'feedback'
                    mensaje TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)

            # 7. Diario de gratitud (pantalla de Inicio)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS diario_gratitud (
                    id SERIAL PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    texto TEXT NOT NULL,
                    fecha TEXT NOT NULL,        -- 'YYYY-MM-DD', una entrada por día
                    timestamp TEXT NOT NULL
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_gratitud_session ON diario_gratitud(session_id)")

            # 8. Diario del día (nuevo, separado del de gratitud -- espacio
            # libre para escribir cómo estuvo el día, no solo una gratitud)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS diario_dia (
                    id SERIAL PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    texto TEXT NOT NULL,
                    fecha TEXT NOT NULL,        -- 'YYYY-MM-DD', una entrada por día
                    timestamp TEXT NOT NULL
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_diario_dia_session ON diario_dia(session_id)")


def guardar_mensaje(session_id, rol, texto, emocion_estimada=None, confianza=None,
                     camara_usada=False, senales_observables=None, calidad_deteccion=None,
                     emocion_especifica=None):
    with _conexion() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO mensajes (session_id, rol, texto, emocion_estimada, confianza,
                                          camara_usada, timestamp, emocion_especifica)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                (session_id, rol, texto[:2000], emocion_estimada, confianza, int(camara_usada),
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"), emocion_especifica)
            )
            mensaje_id = cur.fetchone()[0]

            if senales_observables:
                cur.execute(
                    """INSERT INTO senales_faciales (mensaje_id, apertura_ojo, apertura_boca,
                                                      elevacion_cejas, orientacion_json, calidad_deteccion)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (mensaje_id,
                     senales_observables.get("apertura_ojo_promedio"),
                     senales_observables.get("apertura_boca"),
                     senales_observables.get("elevacion_cejas"),
                     json.dumps(senales_observables.get("orientacion_cabeza")),
                     calidad_deteccion)
                )
            return mensaje_id


def cargar_chat(session_id, limite=100):
    """Devuelve los últimos N mensajes DE ESTA SESIÓN en orden cronológico."""
    with _conexion() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """SELECT rol, texto, emocion_estimada, timestamp FROM mensajes
                   WHERE session_id = %s ORDER BY id DESC LIMIT %s""",
                (session_id, limite)
            )
            filas = cur.fetchall()
            return [{"rol": f["rol"], "texto": f["texto"], "emocion": f["emocion_estimada"] or "neutral",
                      "timestamp": f["timestamp"]}
                    for f in reversed(filas)]


def emocion_mas_frecuente(session_id):
    with _conexion() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """SELECT emocion_estimada, COUNT(*) as total FROM mensajes
                   WHERE rol='user' AND emocion_estimada IS NOT NULL AND session_id = %s
                   GROUP BY emocion_estimada ORDER BY total DESC LIMIT 1""",
                (session_id,)
            )
            fila = cur.fetchone()
            return fila["emocion_estimada"] if fila else None


def serie_para_grafica(session_id, ultimos_n=20):
    escala = {"tristeza": 1, "miedo": 2, "disgusto": 2, "enojo": 2, "neutral": 3, "sorpresa": 4, "felicidad": 5}
    with _conexion() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """SELECT timestamp, emocion_estimada FROM mensajes
                   WHERE rol='user' AND emocion_estimada IS NOT NULL AND session_id = %s
                   ORDER BY id DESC LIMIT %s""",
                (session_id, ultimos_n)
            )
            filas = cur.fetchall()
            return {f["timestamp"][-8:]: escala.get(f["emocion_estimada"], 3) for f in reversed(filas)}


def contar_mensajes_usuario(session_id):
    with _conexion() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT COUNT(*) as total FROM mensajes WHERE rol='user' AND session_id = %s",
                (session_id,)
            )
            return cur.fetchone()["total"]


def registrar_uso_herramienta(session_id, herramienta_id, categoria):
    with _conexion() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO uso_herramientas (session_id, herramienta_id, categoria, timestamp)
                   VALUES (%s, %s, %s, %s)""",
                (session_id, herramienta_id, categoria,
                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )


def usos_por_categoria(session_id):
    """Cuántas veces se usó cada categoría — sirve de contexto para el chat más adelante."""
    with _conexion() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """SELECT categoria, COUNT(*) as total FROM uso_herramientas
                   WHERE session_id = %s GROUP BY categoria ORDER BY total DESC""",
                (session_id,)
            )
            return {f["categoria"]: f["total"] for f in cur.fetchall()}


def registrar_alerta_crisis(session_id, mensaje_id, nivel="crisis"):
    """Registra que se disparó el mensaje de apoyo por riesgo de crisis.
    No guarda el texto ni la frase detectada -- solo nivel y momento."""
    with _conexion() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """INSERT INTO alertas_crisis (session_id, mensaje_id, nivel, timestamp)
                   VALUES (%s, %s, %s, %s)""",
                (session_id, mensaje_id, nivel, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )


def contar_alertas_crisis(session_id):
    """Cuántas veces se activó la capa de crisis en esta sesión (uso interno/futuro)."""
    with _conexion() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT COUNT(*) as total FROM alertas_crisis WHERE session_id = %s",
                (session_id,)
            )
            return cur.fetchone()["total"]


# ---------------------------------------------------------------------
# Perfil / ajustes del usuario
# ---------------------------------------------------------------------

_COLUMNAS_PERFIL_PERMITIDAS = {
    "nombre", "objetivo", "tema", "avatar_bot",
    "recordatorio_activo", "recordatorio_hora", "pin_hash",
}


def obtener_perfil(session_id):
    """Devuelve el perfil como dict, o None si el usuario nunca ha guardado ajustes."""
    with _conexion() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM perfiles WHERE session_id = %s", (session_id,))
            fila = cur.fetchone()
            return dict(fila) if fila else None


def actualizar_perfil(session_id, **campos):
    """
    Crea o actualiza el perfil de esta sesión. Solo se tocan las columnas
    pasadas como argumento (las demás quedan igual). Los nombres de columna
    vienen siempre de nuestro propio código (nunca de texto libre del
    usuario), así que no hay riesgo de inyección al interpolarlos.
    """
    campos = {k: v for k, v in campos.items() if k in _COLUMNAS_PERFIL_PERMITIDAS}
    if not campos:
        return

    with _conexion() as conn:
        with conn.cursor() as cur:
            # Asegura que exista una fila para este session_id.
            cur.execute(
                "INSERT INTO perfiles (session_id, creado_en) VALUES (%s, %s) "
                "ON CONFLICT (session_id) DO NOTHING",
                (session_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )
            set_clause = ", ".join(f"{columna} = %s" for columna in campos)
            valores = list(campos.values()) + [session_id]
            cur.execute(f"UPDATE perfiles SET {set_clause} WHERE session_id = %s", valores)


def guardar_reporte(session_id, tipo, mensaje):
    """tipo: 'falla' | 'feedback'."""
    with _conexion() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO reportes (session_id, tipo, mensaje, timestamp) VALUES (%s, %s, %s, %s)",
                (session_id, tipo, mensaje[:2000], datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            )


# ---------------------------------------------------------------------
# Diario de gratitud
# ---------------------------------------------------------------------

def guardar_gratitud(session_id, texto):
    """Una entrada por día: si ya escribiste hoy, la reemplaza en vez de duplicarla."""
    hoy = datetime.now().strftime("%Y-%m-%d")
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with _conexion() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM diario_gratitud WHERE session_id = %s AND fecha = %s",
                (session_id, hoy)
            )
            cur.execute(
                "INSERT INTO diario_gratitud (session_id, texto, fecha, timestamp) VALUES (%s, %s, %s, %s)",
                (session_id, texto[:500], hoy, ahora)
            )


def gratitud_de_hoy(session_id):
    """Devuelve el texto guardado hoy, o None si todavía no ha escrito nada."""
    hoy = datetime.now().strftime("%Y-%m-%d")
    with _conexion() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT texto FROM diario_gratitud WHERE session_id = %s AND fecha = %s",
                (session_id, hoy)
            )
            fila = cur.fetchone()
            return fila["texto"] if fila else None


def racha_gratitud(session_id, dias=30):
    """Cuántos días distintos (de los últimos `dias`) tienen una entrada de gratitud."""
    with _conexion() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """SELECT COUNT(DISTINCT fecha) as total FROM diario_gratitud
                   WHERE session_id = %s
                   AND fecha >= TO_CHAR(CURRENT_DATE - %s::int, 'YYYY-MM-DD')""",
                (session_id, dias)
            )
            return cur.fetchone()["total"]


def guardar_diario_dia(session_id, texto):
    """Diario del día (texto libre) -- una entrada por día, la reemplaza si ya escribiste hoy."""
    hoy = datetime.now().strftime("%Y-%m-%d")
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with _conexion() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM diario_dia WHERE session_id = %s AND fecha = %s",
                (session_id, hoy)
            )
            cur.execute(
                "INSERT INTO diario_dia (session_id, texto, fecha, timestamp) VALUES (%s, %s, %s, %s)",
                (session_id, texto[:3000], hoy, ahora)
            )


def diario_dia_de_hoy(session_id):
    """Devuelve el texto del diario de hoy, o None si todavía no ha escrito nada."""
    hoy = datetime.now().strftime("%Y-%m-%d")
    with _conexion() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT texto FROM diario_dia WHERE session_id = %s AND fecha = %s",
                (session_id, hoy)
            )
            fila = cur.fetchone()
            return fila["texto"] if fila else None


def historial_diario_dia(session_id, limite=30):
    """Últimas entradas del diario del día, más reciente primero."""
    with _conexion() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """SELECT fecha, texto FROM diario_dia WHERE session_id = %s
                   ORDER BY fecha DESC LIMIT %s""",
                (session_id, limite)
            )
            return cur.fetchall()


def borrar_todo(session_id):
    """Borra SOLO los datos de esta sesión (derecho de privacidad del usuario sobre sus propios datos)."""
    with _conexion() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """DELETE FROM senales_faciales WHERE mensaje_id IN
                   (SELECT id FROM mensajes WHERE session_id = %s)""",
                (session_id,)
            )
            cur.execute("DELETE FROM mensajes WHERE session_id = %s", (session_id,))
            cur.execute("DELETE FROM uso_herramientas WHERE session_id = %s", (session_id,))
            cur.execute("DELETE FROM alertas_crisis WHERE session_id = %s", (session_id,))
            cur.execute("DELETE FROM diario_gratitud WHERE session_id = %s", (session_id,))
            cur.execute("DELETE FROM diario_dia WHERE session_id = %s", (session_id,))