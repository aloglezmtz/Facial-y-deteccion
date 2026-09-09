"""
Fase 4 (C) - Interfaz de Usuario (Tema: Gatitos Digitales)
Chat persistente (SQLite) reorganizado en pestañas: Chat / Mi ánimo / Detalles técnicos.
El chat queda limpio y protagonista; lo técnico está disponible sin saturar.
"""

import uuid
import hashlib
from datetime import datetime
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
from texto_emocion import AnalizadorEmocionTexto
from fusion import fusionar
from emociones_config import EMOJIS_GATO, COLOR_HERRAMIENTAS, ETIQUETAS_ANIMO
from gatito_widget import generar_gatito_html
import visual_pipeline
from temporal_analysis import AnalizadorTemporal
import database as db
from herramientas import CATEGORIAS, herramientas_por_categoria, obtener_herramienta
import deteccion_crisis
import dialogo_emocional
from ajustes import (TEMAS, TEMA_POR_DEFECTO, AVATARES_BOT, OBJETIVOS, OBJETIVO_A_CATEGORIA,
                      FAQ, AVISO_PRIVACIDAD, TERMINOS)
from contenido_diario import afirmacion_de_hoy


def _ahora() -> str:
    """Timestamp en el mismo formato que guarda la base de datos."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _hora_de(timestamp) -> str:
    """Extrae 'HH:MM' de un timestamp 'YYYY-MM-DD HH:MM:SS'. Cadena vacía si no hay dato."""
    if not timestamp or len(timestamp) < 16:
        return ""
    return timestamp[11:16]


def _fecha_de(timestamp) -> str:
    """Extrae 'YYYY-MM-DD' de un timestamp. Cadena vacía si no hay dato."""
    if not timestamp or len(timestamp) < 10:
        return ""
    return timestamp[:10]


_DIAS_ES = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
_MESES_ES = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio",
             "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def _etiqueta_fecha(fecha_str: str) -> str:
    """'2026-08-27' -> 'Hoy', 'Ayer', o 'Jueves 27 de agosto', para el separador del chat."""
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return ""
    hoy = datetime.now().date()
    if fecha == hoy:
        return "Hoy"
    if (hoy - fecha).days == 1:
        return "Ayer"
    return f"{_DIAS_ES[fecha.weekday()]} {fecha.day} de {_MESES_ES[fecha.month]}"


def _saludo_segun_hora() -> str:
    hora = datetime.now().hour
    if hora < 12:
        return "Buenos días"
    if hora < 19:
        return "Buenas tardes"
    return "Buenas noches"


st.set_page_config(page_title="Gatitos Emocionales", page_icon="🐾", layout="centered")

db.inicializar_db()

# ---------------------------------------------------------
# Identidad anónima por navegador, vía COOKIE (ya no por URL).
# Antes el identificador viajaba pegado al link (?sid=...): si esa URL
# se compartía o se guardaba como favorito, la otra persona heredaba
# la misma sesión y veía los mismos datos. Ahora vive en una cookie
# de sesión del navegador: nunca aparece en el link, y cada navegador/
# dispositivo obtiene la suya propia. Al no ponerle fecha de
# vencimiento, el navegador la borra solo al cerrarse por completo
# (no al recargar la página ni al cambiar de pestaña).
# ---------------------------------------------------------
import extra_streamlit_components as stx


def _obtener_cookie_manager():
    if "cookie_manager" not in st.session_state:
        st.session_state.cookie_manager = stx.CookieManager(key="gora_cookie_manager")
    return st.session_state.cookie_manager


cookie_manager = _obtener_cookie_manager()
cookie_manager._remove_extra_spacing()  # esconde el iframe invisible de las cookies

if "session_id" not in st.session_state:
    # default=None (no {}) para distinguir "todavía no responde el
    # componente" de "ya respondió y de verdad no hay cookie".
    cookies_actuales = cookie_manager.cookie_manager(
        method="getAll", key="gora_get_all_cookies", default=None
    )

    if cookies_actuales is None:
        # El componente de cookies aún no reportó su valor real en este
        # primer render. Streamlit vuelve a correr el script solo en
        # cuanto llegue -- no decidimos nada todavía para no pisar una
        # cookie que ya exista.
        st.stop()

    sid_en_cookie = cookies_actuales.get("gora_sid")
    if sid_en_cookie:
        st.session_state.session_id = sid_en_cookie
    else:
        nuevo_sid = str(uuid.uuid4())
        cookie_manager._remove_extra_spacing()
        cookie_manager.cookie_manager(
            method="set",
            cookie="gora_sid",
            value=nuevo_sid,
            options={"path": "/", "sameSite": "strict"},  # sin "expires" => cookie de sesión
            key="gora_set_sid",
            default=False,
        )
        st.session_state.session_id = nuevo_sid

sid = st.session_state.session_id

# Perfil/ajustes de esta sesión (tema, nombre, PIN, etc.) -- se carga una
# sola vez por sesión de Streamlit; los cambios hechos en la pestaña de
# Ajustes actualizan tanto la BD como esta copia en memoria.
if "perfil" not in st.session_state:
    st.session_state.perfil = db.obtener_perfil(sid) or {}

perfil = st.session_state.perfil

if "tema_elegido" not in st.session_state:
    st.session_state.tema_elegido = perfil.get("tema") or TEMA_POR_DEFECTO

PALETA_UI = TEMAS.get(st.session_state.tema_elegido, TEMAS[TEMA_POR_DEFECTO])

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fredoka:wght@500;600;700&family=Nunito:wght@400;600;700;800&display=swap');

    html, body, [class*="css"] {{ font-family: 'Nunito', sans-serif; }}
    h1, h2, h3 {{ font-family: 'Fredoka', sans-serif !important; letter-spacing: 0.2px; }}

    .stApp {{
        background: linear-gradient(180deg, {PALETA_UI['fondo_inicio']} 0%, {PALETA_UI['fondo_fin']} 100%);
    }}
    h1, h2, h3, p, span, label, .stMarkdown {{ color: {PALETA_UI['texto_principal']} !important; }}
    [data-testid="stCaptionContainer"], .stCaption {{ color: {PALETA_UI['texto_secundario']} !important; }}

    /* Bloquea el ancho para que se vea bien tipo "app" en escritorio y celular */
    .block-container {{ max-width: 640px; padding-top: 0.9rem; padding-bottom: 1.5rem; }}

    /* ---------- Tarjeta del gatito (encabezado) ---------- */
    .tarjeta-gatito {{
        background: {PALETA_UI['tarjeta']};
        border: 1px solid {PALETA_UI['tarjeta_borde']};
        border-radius: 28px;
        padding: 4px 16px 14px 16px;
        box-shadow: 0 8px 24px {PALETA_UI['sombra']};
        margin-bottom: 10px;
        text-align: center;
    }}
    .titulo-app {{
        font-family: 'Fredoka', sans-serif;
        font-size: 1.5rem;
        font-weight: 600;
        margin: 10px 0 0 0;
    }}
    .badge-animo {{
        display: inline-flex; align-items: center; gap: 6px;
        background: {PALETA_UI['acento_suave']};
        color: {PALETA_UI['texto_principal']} !important;
        font-family: 'Fredoka', sans-serif; font-weight: 600; font-size: 0.95rem;
        padding: 6px 18px; border-radius: 999px; margin-top: 4px;
    }}

    /* ---------- Barra de estado compacta (reemplaza el encabezado grande) ---------- */
    .barra-estado {{
        display: flex; align-items: center; gap: 10px;
        background: {PALETA_UI['tarjeta']};
        border: 1px solid {PALETA_UI['tarjeta_borde']};
        border-radius: 999px;
        padding: 8px 10px 8px 8px;
        box-shadow: 0 2px 10px {PALETA_UI['sombra']};
        margin-bottom: 10px;
    }}
    .barra-avatar {{
        font-size: 1.3rem;
        width: 36px; height: 36px; flex-shrink: 0;
        border-radius: 50%;
        background: {PALETA_UI['acento_suave']};
        display: flex; align-items: center; justify-content: center;
    }}
    .barra-texto {{
        font-family: 'Fredoka', sans-serif; font-weight: 600; font-size: 0.92rem;
        flex: 1; min-width: 0;
        overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    }}
    .barra-badge {{
        font-family: 'Fredoka', sans-serif; font-weight: 600; font-size: 0.8rem;
        background: {PALETA_UI['acento_suave']};
        padding: 5px 12px; border-radius: 999px; white-space: nowrap; flex-shrink: 0;
    }}

    /* ---------- Chat (burbujas reales: alineadas por quién habla) ---------- */
    div[data-testid="stChatMessage"] {{
        background-color: {PALETA_UI['burbuja_asistente']};
        border: 1px solid {PALETA_UI['tarjeta_borde']};
        border-radius: 18px 18px 18px 4px;
        padding: 10px 14px;
        box-shadow: 0 2px 10px {PALETA_UI['sombra']};
        animation: aparecer 0.2s ease-out;
        max-width: 78%;
        margin-right: auto;
        margin-left: 0;
    }}
    div[data-testid="stChatMessage"] p {{ color: {PALETA_UI['texto_principal']} !important; margin-bottom: 0; }}
    /* Mensajes del usuario: burbuja a la derecha, con "cola" abajo a la derecha */
    div[data-testid="stChatMessage"]:has(> [data-testid="stChatMessageAvatarUser"]) {{
        background-color: {PALETA_UI['burbuja_usuario']};
        border-color: {PALETA_UI['burbuja_usuario']};
        border-radius: 18px 18px 4px 18px;
        flex-direction: row-reverse;
        margin-left: auto;
        margin-right: 0;
    }}
    div[data-testid="stChatMessage"]:has(> [data-testid="stChatMessageAvatarUser"]) p {{
        color: white !important;
    }}
    [data-testid="stChatMessageAvatarCustom"], [data-testid="stChatMessageAvatarUser"] {{
        border: 2.5px solid {PALETA_UI['acento_suave']} !important;
    }}
    .hora-mensaje {{
        font-size: 0.68rem; margin-top: 3px; opacity: 0.65;
        color: {PALETA_UI['texto_secundario']};
    }}
    div[data-testid="stChatMessage"]:has(> [data-testid="stChatMessageAvatarUser"]) .hora-mensaje {{
        color: #FFFFFFCC; text-align: right;
    }}
    .separador-fecha {{
        text-align: center; color: {PALETA_UI['texto_secundario']};
        font-family: 'Fredoka', sans-serif; font-size: 0.75rem;
        margin: 14px 0 8px 0; opacity: 0.8;
    }}
    @keyframes aparecer {{
        from {{ opacity: 0; transform: translateY(6px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    /* ---------- Caja de Gatitos (grid de herramientas) ---------- */
    .grid-herramientas {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-top: 6px; }}
    .tarjeta-herramienta {{
        border-radius: 20px; padding: 16px 10px; text-align: center;
        box-shadow: 0 2px 8px {PALETA_UI['sombra']};
        font-family: 'Fredoka', sans-serif; font-weight: 600; color: {PALETA_UI['texto_principal']};
        font-size: 0.92rem; line-height: 1.3;
    }}
    .tarjeta-herramienta .icono {{ font-size: 1.8rem; display: block; margin-bottom: 6px; }}

    .etiqueta-teal {{
        color: {PALETA_UI['acento_secundario']} !important; font-family: 'Fredoka', sans-serif;
        font-weight: 600; font-size: 0.9rem;
    }}

    /* ---------- Inicio: dashboard ---------- */
    .saludo-inicio {{
        font-family: 'Fredoka', sans-serif; font-weight: 700; font-size: 1.4rem;
        margin: 4px 0 2px 0;
    }}
    .tarjeta-inicio {{
        background: {PALETA_UI['tarjeta']};
        border: 1px solid {PALETA_UI['tarjeta_borde']};
        border-radius: var(--radio-mediano, 18px);
        padding: 14px 16px;
        box-shadow: 0 2px 10px {PALETA_UI['sombra']};
        margin-bottom: 10px;
    }}
    .tarjeta-inicio-titulo {{
        font-family: 'Fredoka', sans-serif; font-weight: 600; font-size: 0.9rem;
        color: {PALETA_UI['texto_secundario']};
        display: flex; align-items: center; gap: 6px; margin-bottom: 6px;
    }}
    .tarjeta-inicio-cuerpo {{
        font-size: 0.95rem; line-height: 1.4;
    }}

    /* ---------- Controles ---------- */
    .stToggle, .stMetric {{
        background-color: {PALETA_UI['tarjeta']}; border: 1px solid {PALETA_UI['tarjeta_borde']};
        border-radius: 16px; padding: 10px;
    }}
    .stButton > button, .stChatInput {{ border-radius: 999px !important; }}
    .stButton > button {{
        background-color: {PALETA_UI['acento']} !important; color: white !important;
        border: none !important; font-family: 'Fredoka', sans-serif; font-weight: 600;
    }}
    .stButton > button:hover {{ filter: brightness(1.06); }}

    /* ---------- Pestañas tipo píldora ---------- */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px; background: {PALETA_UI['acento_suave']}; padding: 5px; border-radius: 999px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: transparent; border-radius: 999px; padding: 8px 14px;
        font-family: 'Fredoka', sans-serif; font-weight: 600;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {PALETA_UI['tarjeta']} !important;
        box-shadow: 0 2px 6px {PALETA_UI['sombra']};
    }}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def cargar_analizador_texto():
    # No se llama aquí arriba a propósito: pysentimiento carga PyTorch +
    # un modelo transformer completo, y antes esta línea se ejecutaba en
    # cuanto se abría la página, sin importar si el usuario iba a chatear
    # o no. Ahora solo se dispara la primera vez que alguien manda un
    # mensaje (ver más abajo), gracias a @st.cache_resource sigue
    # cargándose una sola vez por proceso.
    return AnalizadorEmocionTexto()

if "historial_chat" not in st.session_state:
    st.session_state.historial_chat = db.cargar_chat(sid)
if "emocion_actual" not in st.session_state:
    ultimos = st.session_state.historial_chat
    st.session_state.emocion_actual = ultimos[-1]["emocion"] if ultimos else "neutral"
if "analizador_temporal" not in st.session_state:
    st.session_state.analizador_temporal = AnalizadorTemporal()
if "ultimo_resultado_visual" not in st.session_state:
    st.session_state.ultimo_resultado_visual = None
if "categoria_activa" not in st.session_state:
    st.session_state.categoria_activa = None
if "herramienta_activa" not in st.session_state:
    st.session_state.herramienta_activa = None
if "dialogo_emocion" not in st.session_state:
    # None = no hay pregunta de seguimiento pendiente. Si no es None, contiene
    # el estado del diálogo (ver dialogo_emocional.py) y el chat debe mostrar
    # la pregunta actual con botones antes de aceptar un mensaje nuevo.
    st.session_state.dialogo_emocion = None

# ---------------------------------------------------------
# Puerta de PIN (si el usuario configuró uno en Ajustes). Es una traba
# básica local -- no una cuenta con contraseña real -- así que se detiene
# aquí todo el resto del script hasta que se ingrese el PIN correcto.
# ---------------------------------------------------------
if perfil.get("pin_hash") and not st.session_state.get("pin_verificado"):
    st.markdown('<div class="tarjeta-gatito" style="margin-top:40px;">', unsafe_allow_html=True)
    st.markdown('<p class="titulo-app">🔒 Ingresa tu PIN</p>', unsafe_allow_html=True)
    st.caption("Es una traba básica para este dispositivo, no una cuenta con contraseña real.")
    pin_ingresado = st.text_input("PIN de 4 dígitos", type="password", max_chars=4,
                                   label_visibility="collapsed", placeholder="••••")
    if st.button("Desbloquear", use_container_width=True):
        if hashlib.sha256(pin_ingresado.encode()).hexdigest() == perfil["pin_hash"]:
            st.session_state.pin_verificado = True
            st.rerun()
        else:
            st.error("PIN incorrecto.")
    st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ---------------------------------------------------------
# Barra de estado compacta -- siempre visible, pero SIN el gatito animado
# grande (eso se movió a "Mi ánimo", donde sí tiene sentido ser
# protagonista). Esto es lo que antes ocupaba ~300px de alto arriba del
# chat en TODAS las pestañas; ahora es una franja de ~56px.
# ---------------------------------------------------------
avatar_bot = perfil.get("avatar_bot") or AVATARES_BOT[0]
saludo = f"Hola, {perfil['nombre']} 👋" if perfil.get("nombre") else "Tu Gatito Emocional"
emocion_mostrada = st.session_state.emocion_actual

st.markdown(
    f'<div class="barra-estado">'
    f'<span class="barra-avatar">{avatar_bot}</span>'
    f'<span class="barra-texto">{saludo}</span>'
    f'<span class="barra-badge">{EMOJIS_GATO.get(emocion_mostrada, "😺")} {emocion_mostrada.capitalize()}</span>'
    f'</div>',
    unsafe_allow_html=True
)

# Acceso permanente a recursos de ayuda -- no solo reactivo ante una alerta.
# Colapsado por defecto para no saturar la pantalla de la mayoría de sesiones,
# pero siempre disponible sin importar la pestaña en la que esté el usuario.
with st.expander("🆘 ¿Necesitas ayuda ahora?"):
    st.markdown(deteccion_crisis.texto_recursos_siempre_visibles())

tab_inicio, tab_chat, tab_animo, tab_caja, tab_tecnico, tab_ajustes = st.tabs(
    ["🏠 Inicio", "💬 Chat", "📊 Mi ánimo", "🧰 Caja de Gatitos", "🔍 Detalles técnicos", "⚙️ Ajustes"])

# ===========================================================
# PESTAÑA 0: INICIO — dashboard con saludo y accesos rápidos
# ===========================================================
with tab_inicio:
    nombre_saludo = perfil.get("nombre") or "humano"
    st.markdown(f'<p class="saludo-inicio">{_saludo_segun_hora()}, {nombre_saludo} 🐾</p>',
                unsafe_allow_html=True)

    # ---- Afirmación de hoy ----
    st.markdown(
        f'<div class="tarjeta-inicio">'
        f'<div class="tarjeta-inicio-titulo">🌻 Afirmación de hoy</div>'
        f'<div class="tarjeta-inicio-cuerpo">{afirmacion_de_hoy()}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    # ---- Diario de gratitud ----
    st.markdown('<div class="tarjeta-inicio">', unsafe_allow_html=True)
    st.markdown('<div class="tarjeta-inicio-titulo">📓 Diario de gratitud</div>', unsafe_allow_html=True)
    gratitud_hoy = db.gratitud_de_hoy(sid)
    if gratitud_hoy:
        st.markdown(f'<div class="tarjeta-inicio-cuerpo">✅ Hoy escribiste: <em>"{gratitud_hoy}"</em></div>',
                    unsafe_allow_html=True)
        with st.expander("Editar lo de hoy"):
            nuevo_texto = st.text_area("¿Por qué otra cosa te sientes agradecido/a hoy?",
                                        value=gratitud_hoy, key="editar_gratitud", height=80)
            if st.button("Actualizar", key="btn_actualizar_gratitud"):
                if nuevo_texto.strip():
                    db.guardar_gratitud(sid, nuevo_texto.strip())
                    st.rerun()
    else:
        texto_gratitud = st.text_area("¿Por una cosa pequeña te sientes agradecido/a hoy?",
                                       key="nueva_gratitud", height=80,
                                       placeholder="Hoy agradezco...")
        if st.button("Guardar", key="btn_guardar_gratitud", use_container_width=True):
            if texto_gratitud.strip():
                db.guardar_gratitud(sid, texto_gratitud.strip())
                st.rerun()
            else:
                st.warning("Escribe algo antes de guardar.")
    racha = db.racha_gratitud(sid)
    if racha > 0:
        st.caption(f"🔥 {racha} día(s) con entrada en los últimos 30 días.")
    st.markdown('</div>', unsafe_allow_html=True)

    # ---- Actividad recomendada (según "Configurar mi rutina" en Ajustes) ----
    categoria_sugerida_inicio = OBJETIVO_A_CATEGORIA.get(perfil.get("objetivo"))
    if categoria_sugerida_inicio and categoria_sugerida_inicio in CATEGORIAS:
        info_cat_inicio = CATEGORIAS[categoria_sugerida_inicio]
        herramientas_sugeridas = herramientas_por_categoria(categoria_sugerida_inicio)
        if herramientas_sugeridas:
            h_sugerida = herramientas_sugeridas[0]
            st.markdown(
                f'<div class="tarjeta-inicio">'
                f'<div class="tarjeta-inicio-titulo">{info_cat_inicio["icono"]} Actividad recomendada</div>'
                f'<div class="tarjeta-inicio-cuerpo"><strong>{h_sugerida["titulo"]}</strong><br>'
                f'<span style="color:{PALETA_UI["texto_secundario"]}; font-size:0.85rem;">'
                f'{h_sugerida["descripcion"]} · {h_sugerida["duracion"]}</span></div>'
                f'</div>',
                unsafe_allow_html=True
            )
            st.caption("👉 Ábrela desde la pestaña 🧰 Caja de Gatitos.")

    # ---- Lugar seguro ----
    with st.expander("🛡️ Lugar seguro"):
        st.markdown(deteccion_crisis.texto_recursos_siempre_visibles())

# ===========================================================
# PESTAÑA 1: CHAT — protagonista, sin ruido técnico
# ===========================================================
with tab_chat:
    # El gatito grande reacciona en vivo a la última emoción detectada/elegida
    # en la conversación (se actualiza solo, porque emocion_mostrada ya se
    # recalcula arriba cada vez que el script vuelve a correr).
    components.html(generar_gatito_html(emocion_mostrada or "neutral"), height=170)

    col1, col2 = st.columns([3, 1])
    with col1:
        camara_disponible = st.toggle(
            "Usar cámara (fusión multimodal)", value=False,
            help="Toma una foto al enviar tu mensaje. El sistema mide señales faciales "
                 "observables y estima una emoción probable con un nivel de confianza."
        )
    with col2:
        st.metric("Modo", "Visual+Texto" if camara_disponible else "Solo Texto")

    foto = None
    if camara_disponible:
        # esta_disponible() carga cv2/mediapipe/deepface la PRIMERA VEZ que
        # alguien activa este toggle -- no antes. Así, si nadie usa la
        # cámara en una sesión, esas librerías (y su memoria) nunca se tocan.
        if visual_pipeline.esta_disponible():
            foto = st.camera_input("Toma una foto de tu rostro", label_visibility="collapsed")
        else:
            motivo = getattr(visual_pipeline, "_MOTIVO_NO_DISPONIBLE", None)
            if motivo:
                st.warning(
                    "El canal visual no está disponible en este servidor (el chat de texto "
                    "sigue funcionando con normalidad).\n\n"
                    f"Detalle técnico: `{motivo}`"
                )
            else:
                st.warning(
                    "El canal visual requiere `opencv-python`, `mediapipe` y `deepface`. Instálalos con:\n\n"
                    "`pip install opencv-python mediapipe deepface tensorflow==2.15.0 tf-keras`"
                )
            camara_disponible = False

    st.divider()

    contenedor_chat = st.container(height=480)
    with contenedor_chat:
        fecha_anterior = None
        for mensaje in st.session_state.historial_chat:
            fecha_msg = _fecha_de(mensaje.get("timestamp"))
            if fecha_msg and fecha_msg != fecha_anterior:
                st.markdown(f'<div class="separador-fecha">— {_etiqueta_fecha(fecha_msg)} —</div>',
                            unsafe_allow_html=True)
                fecha_anterior = fecha_msg

            avatar = EMOJIS_GATO.get(mensaje["emocion"], "😺") if mensaje["rol"] == "user" else avatar_bot
            with st.chat_message(mensaje["rol"], avatar=avatar):
                st.write(mensaje["texto"])
                hora = _hora_de(mensaje.get("timestamp"))
                if hora:
                    st.markdown(f'<div class="hora-mensaje">{hora}</div>', unsafe_allow_html=True)

        # Si hay una pregunta de seguimiento pendiente (rueda de emociones),
        # se muestra aquí con botones -- el usuario puede tocar una opción
        # o, si prefiere, escribirla en el chat de abajo.
        if st.session_state.dialogo_emocion is not None:
            dialogo = st.session_state.dialogo_emocion
            with st.chat_message("assistant", avatar=avatar_bot):
                st.write(dialogo_emocional.texto_pregunta(dialogo))
                if dialogo["paso"] not in ("razon", "seguimiento"):
                    cols = st.columns(len(dialogo["opciones"]))
                    for i, opcion in enumerate(dialogo["opciones"]):
                        with cols[i]:
                            if st.button(opcion.capitalize(), key=f"opt_{dialogo['paso']}_{opcion}",
                                         use_container_width=True):
                                nuevo_dialogo, respuesta_final = dialogo_emocional.avanzar_dialogo(dialogo, opcion)
                                st.session_state.dialogo_emocion = nuevo_dialogo
                                if respuesta_final:
                                    st.session_state.emocion_actual = dialogo["primaria"]
                                    st.session_state.historial_chat.append(
                                        {"rol": "assistant", "texto": respuesta_final, "emocion": dialogo["primaria"], "timestamp": _ahora()})
                                    db.guardar_mensaje(
                                        sid, "assistant", respuesta_final, dialogo["primaria"],
                                        dialogo["confianza"] / 100 if dialogo["confianza"] is not None else None,
                                        False, emocion_especifica=dialogo_emocional.etiqueta_especifica(dialogo))
                                st.rerun()

    # Reacción rápida: tocar un emoji registra el ánimo sin necesidad de
    # escribir. Se oculta mientras hay una pregunta de la rueda pendiente,
    # para no competir con los botones de esa pregunta.
    if st.session_state.dialogo_emocion is None:
        st.caption("O solo toca cómo te sientes:")
        cols_reaccion = st.columns(len(EMOJIS_GATO))
        for col, (emo, emoji) in zip(cols_reaccion, EMOJIS_GATO.items()):
            with col:
                if st.button(emoji, key=f"reaccion_{emo}", use_container_width=True,
                              help=ETIQUETAS_ANIMO.get(emo, emo.capitalize())):
                    etiqueta = ETIQUETAS_ANIMO.get(emo, emo.capitalize())
                    respuesta = (f"Anotado: te sientes **{etiqueta}** {emoji}. "
                                 f"Aquí sigo si quieres contarme más.")

                    st.session_state.emocion_actual = emo
                    st.session_state.historial_chat.append(
                        {"rol": "user", "texto": emoji, "emocion": emo, "timestamp": _ahora()})
                    st.session_state.historial_chat.append(
                        {"rol": "assistant", "texto": respuesta, "emocion": emo, "timestamp": _ahora()})

                    db.guardar_mensaje(sid, "user", emoji, emo)
                    db.guardar_mensaje(sid, "assistant", respuesta, emo)

                    st.rerun()

    texto_usuario = st.chat_input("Cuéntale a tu gatito cómo te sientes...")

    if texto_usuario:
        with st.spinner("El gatito está pensando... 🐾"):
            # ---------------------------------------------------------
            # Capa de seguridad: se evalúa PRIMERO y de forma independiente
            # del análisis de emoción, que no está diseñado para detectar
            # riesgo. Si hay señales de crisis, la respuesta del gatito se
            # reemplaza por contención + recursos reales, sin preguntas que
            # profundicen el momento difícil -- y se cancela cualquier
            # pregunta de seguimiento que estuviera pendiente.
            # ---------------------------------------------------------
            riesgo = deteccion_crisis.evaluar_riesgo(texto_usuario)

            if riesgo["hay_riesgo"]:
                st.session_state.dialogo_emocion = None
                respuesta = deteccion_crisis.mensaje_apoyo_crisis()

                st.session_state.historial_chat.append(
                    {"rol": "user", "texto": texto_usuario, "emocion": st.session_state.emocion_actual, "timestamp": _ahora()})
                st.session_state.historial_chat.append(
                    {"rol": "assistant", "texto": respuesta, "emocion": st.session_state.emocion_actual, "timestamp": _ahora()})

                id_mensaje_usuario = db.guardar_mensaje(sid, "user", texto_usuario, st.session_state.emocion_actual)
                db.guardar_mensaje(sid, "assistant", respuesta, st.session_state.emocion_actual)
                db.registrar_alerta_crisis(sid, id_mensaje_usuario, riesgo["nivel"])

            elif (st.session_state.dialogo_emocion is not None
                  and st.session_state.dialogo_emocion["paso"] == "razon"):
                # El usuario ya vio el desglose de su emoción (rueda) y ahora
                # contó, en texto libre, qué está pasando -- antes de cerrar,
                # se hace UNA pregunta corta de seguimiento (empatía breve).
                dialogo = st.session_state.dialogo_emocion

                st.session_state.historial_chat.append(
                    {"rol": "user", "texto": texto_usuario, "emocion": dialogo["primaria"], "timestamp": _ahora()})
                db.guardar_mensaje(sid, "user", texto_usuario, dialogo["primaria"])

                nuevo_dialogo = dialogo_emocional.avanzar_a_seguimiento(dialogo, texto_usuario)
                respuesta = f"{dialogo_emocional.acuse_corto()} {dialogo_emocional.texto_pregunta(nuevo_dialogo)}"

                st.session_state.dialogo_emocion = nuevo_dialogo
                st.session_state.historial_chat.append(
                    {"rol": "assistant", "texto": respuesta, "emocion": dialogo["primaria"], "timestamp": _ahora()})
                db.guardar_mensaje(sid, "assistant", respuesta, dialogo["primaria"])

            elif (st.session_state.dialogo_emocion is not None
                  and st.session_state.dialogo_emocion["paso"] == "seguimiento"):
                # Respuesta a la pregunta corta de seguimiento -- con esto
                # (más la razón de antes) ya se cierra con aliento + herramienta.
                dialogo = st.session_state.dialogo_emocion

                st.session_state.historial_chat.append(
                    {"rol": "user", "texto": texto_usuario, "emocion": dialogo["primaria"], "timestamp": _ahora()})
                db.guardar_mensaje(sid, "user", texto_usuario, dialogo["primaria"])

                texto_para_analizar = f"{dialogo.get('razon', '')} {texto_usuario}"
                herramienta = dialogo_emocional.sugerir_herramienta(dialogo, texto_para_analizar)
                respuesta = dialogo_emocional.responder_con_apoyo(dialogo, texto_para_analizar, herramienta)

                st.session_state.historial_chat.append(
                    {"rol": "assistant", "texto": respuesta, "emocion": dialogo["primaria"], "timestamp": _ahora()})
                db.guardar_mensaje(
                    sid, "assistant", respuesta, dialogo["primaria"],
                    dialogo["confianza"] / 100 if dialogo["confianza"] is not None else None,
                    False, emocion_especifica=dialogo_emocional.etiqueta_especifica(dialogo))

                if herramienta:
                    db.registrar_uso_herramienta(sid, herramienta["id"], herramienta["categoria"])

                st.session_state.dialogo_emocion = None  # el diálogo ya terminó del todo

            elif st.session_state.dialogo_emocion is not None:
                # El usuario respondió escribiendo en vez de tocar un botón:
                # intentamos encontrar a cuál opción se refería.
                dialogo = st.session_state.dialogo_emocion
                from rueda_emociones import emparejar_texto_con_opcion
                opcion_elegida = emparejar_texto_con_opcion(texto_usuario, dialogo["opciones"])

                st.session_state.historial_chat.append(
                    {"rol": "user", "texto": texto_usuario, "emocion": dialogo["primaria"], "timestamp": _ahora()})
                db.guardar_mensaje(sid, "user", texto_usuario, dialogo["primaria"])

                if opcion_elegida is None:
                    respuesta = dialogo_emocional.responder_intento_fallido(dialogo)
                    st.session_state.historial_chat.append(
                        {"rol": "assistant", "texto": respuesta, "emocion": dialogo["primaria"], "timestamp": _ahora()})
                    # el dialogo se mantiene igual (mismo paso, mismas opciones)
                else:
                    nuevo_dialogo, respuesta_final = dialogo_emocional.avanzar_dialogo(dialogo, opcion_elegida)
                    st.session_state.dialogo_emocion = nuevo_dialogo
                    if respuesta_final:
                        st.session_state.emocion_actual = dialogo["primaria"]
                        st.session_state.historial_chat.append(
                            {"rol": "assistant", "texto": respuesta_final, "emocion": dialogo["primaria"], "timestamp": _ahora()})
                        db.guardar_mensaje(
                            sid, "assistant", respuesta_final, dialogo["primaria"],
                            dialogo["confianza"] / 100 if dialogo["confianza"] is not None else None,
                            False, emocion_especifica=dialogo_emocional.etiqueta_especifica(dialogo))

            else:
                # Mensaje nuevo: se calcula la emoción primaria (fusión visual+
                # texto) como antes, pero en vez de anunciarla con un % de
                # confianza, el gatito PREGUNTA para llegar a algo más preciso.
                emocion_texto, vector_texto = cargar_analizador_texto().analizar(texto_usuario)

                vector_visual = None
                resultado_visual = None
                senales_para_guardar = None
                calidad_para_guardar = None

                if camara_disponible and foto is not None:
                    from PIL import Image
                    imagen_pil = Image.open(foto)
                    frame_bgr = np.array(imagen_pil.convert("RGB"))[:, :, ::-1].copy()
                    resultado_visual = visual_pipeline.analizar_imagen(
                        frame_bgr, analizador_temporal=st.session_state.analizador_temporal
                    )
                    st.session_state.ultimo_resultado_visual = resultado_visual
                    if resultado_visual["rostro_detectado"]:
                        senales_para_guardar = resultado_visual["senales_observables"]
                        calidad_para_guardar = resultado_visual["calidad_deteccion"]
                        if resultado_visual["interpretacion"]["vector_probabilidades"]:
                            vector_visual = resultado_visual["interpretacion"]["vector_probabilidades"]

                usar_camara_en_fusion = camara_disponible and vector_visual is not None

                emocion_final, vector_fusionado, incongruencia = fusionar(
                    vector_texto=vector_texto, vector_visual=vector_visual,
                    camara_disponible=usar_camara_en_fusion
                )
                confianza = vector_fusionado[emocion_final] * 100  # se guarda en BD, no se muestra

                st.session_state.emocion_actual = emocion_final
                st.session_state.historial_chat.append(
                    {"rol": "user", "texto": texto_usuario, "emocion": emocion_final, "timestamp": _ahora()})

                db.guardar_mensaje(
                    sid, "user", texto_usuario, emocion_final, confianza / 100,
                    usar_camara_en_fusion, senales_para_guardar, calidad_para_guardar)

                if camara_disponible and resultado_visual and not resultado_visual["rostro_detectado"]:
                    st.session_state.historial_chat.append({
                        "rol": "assistant",
                        "texto": "😿 *No detecté tu rostro en la foto, así que solo usé el texto para esto.*",
                        "emocion": emocion_final,
                        "timestamp": _ahora(),
                    })

                st.session_state.dialogo_emocion = dialogo_emocional.iniciar_dialogo(
                    emocion_final, texto_usuario, confianza, incongruencia)

        st.rerun()

# ===========================================================
# PESTAÑA 2: MI ÁNIMO — tendencia histórica
# ===========================================================
with tab_animo:
    total_mensajes = db.contar_mensajes_usuario(sid)
    if total_mensajes == 0:
        st.info("Todavía no hay suficientes mensajes para mostrar tendencias. ¡Escríbele algo a tu gatito!")
    else:
        mas_frecuente = db.emocion_mas_frecuente(sid)

        components.html(generar_gatito_html(mas_frecuente or "neutral"), height=170)
        st.markdown(
            f'<p style="text-align:center; font-family:\'Fredoka\',sans-serif; font-weight:600; '
            f'font-size:1.1rem; margin-top:-6px;">{(mas_frecuente or "neutral").capitalize()}</p>',
            unsafe_allow_html=True
        )

        colA, colB = st.columns(2)
        colA.metric("Emoción más frecuente", f"{EMOJIS_GATO.get(mas_frecuente,'😺')} {mas_frecuente}")
        colB.metric("Mensajes registrados", total_mensajes)

        serie = db.serie_para_grafica(sid)
        if len(serie) >= 2:
            st.markdown('<div class="tarjeta-gatito" style="text-align:left;">', unsafe_allow_html=True)
            st.markdown('<span class="etiqueta-teal">📈 Evolución de tu ánimo</span>', unsafe_allow_html=True)
            st.line_chart(serie)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.caption("Escribe algunos mensajes más para ver la gráfica de tendencia.")

        st.divider()
        st.markdown("##### Privacidad")
        st.caption("Tu historial es privado: solo tú puedes verlo, identificado de forma anónima por tu sesión "
                    "de navegador. Se guarda en una base de datos en la nube (Render) para que sobreviva a "
                    "recargas, pero nunca se comparte con otros usuarios.")
        if st.button("🗑️ Borrar todo mi historial", type="secondary"):
            db.borrar_todo(sid)
            st.session_state.historial_chat = []
            st.session_state.emocion_actual = "neutral"
            st.rerun()

# ===========================================================
# PESTAÑA 3: CAJA DE GATITOS — herramientas de bienestar
# ===========================================================
with tab_caja:
    cat_activa = st.session_state.categoria_activa
    herr_activa = st.session_state.herramienta_activa

    # --- Vista 3: detalle de una herramienta (pasos + cierre) ---
    if herr_activa:
        h = obtener_herramienta(herr_activa)
        if st.button("← Volver a la lista"):
            st.session_state.herramienta_activa = None
            st.rerun()

        st.markdown(f"### {h['titulo']}")
        st.caption(f"{h['tipo']} · {h['duracion']}")
        st.write(h["descripcion"])
        st.divider()
        for i, paso in enumerate(h["pasos"], start=1):
            st.markdown(f"**{i}.** {paso}")
        if h["cierre"]:
            st.info(h["cierre"])

        if st.button("✅ Hecho, gracias", type="primary", use_container_width=True):
            db.registrar_uso_herramienta(sid, h["id"], h["categoria"])
            st.success("Guardado. Puedes volver cuando quieras.")

    # --- Vista 2: lista de herramientas de una categoría ---
    elif cat_activa:
        info_cat = CATEGORIAS[cat_activa]
        if st.button("← Volver a categorías"):
            st.session_state.categoria_activa = None
            st.rerun()

        st.markdown(f"### {info_cat['icono']} {info_cat['nombre']}")
        for h in herramientas_por_categoria(cat_activa):
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"**{h['titulo']}**")
                    st.caption(f"{h['descripcion']} · {h['tipo']} · {h['duracion']}")
                with col2:
                    if st.button("Abrir", key=f"abrir_{h['id']}", use_container_width=True):
                        st.session_state.herramienta_activa = h["id"]
                        st.rerun()

    # --- Vista 1: grid de categorías ---
    else:
        st.markdown(
            "<p style='text-align:center; color:#9C8676; margin-bottom:14px;'>"
            "¿En qué quieres trabajar hoy?</p>", unsafe_allow_html=True
        )
        categoria_sugerida = OBJETIVO_A_CATEGORIA.get(perfil.get("objetivo"))
        if categoria_sugerida and categoria_sugerida in CATEGORIAS:
            info_sugerida = CATEGORIAS[categoria_sugerida]
            st.caption(f"💡 Como configuraste tu rutina, te recomendamos empezar por "
                       f"{info_sugerida['icono']} {info_sugerida['nombre']}.")

        claves_categorias = list(CATEGORIAS.keys())
        for fila_inicio in range(0, len(claves_categorias), 2):
            cols = st.columns(2)
            for offset, col in enumerate(cols):
                idx = fila_inicio + offset
                if idx >= len(claves_categorias):
                    continue
                clave = claves_categorias[idx]
                info = CATEGORIAS[clave]
                color = COLOR_HERRAMIENTAS[idx % len(COLOR_HERRAMIENTAS)]
                with col:
                    st.markdown(
                        f'<div class="tarjeta-herramienta" style="background:{color};">'
                        f'<span class="icono">{info["icono"]}</span>{info["nombre"]}</div>',
                        unsafe_allow_html=True
                    )
                    if st.button("Ver", key=f"cat_{clave}", use_container_width=True):
                        st.session_state.categoria_activa = clave
                        st.rerun()

# ===========================================================
# PESTAÑA 3: DETALLES TÉCNICOS — señal vs. interpretación
# ===========================================================
with tab_tecnico:
    r = st.session_state.ultimo_resultado_visual
    if not r:
        st.info("Activa la cámara en la pestaña Chat y envía un mensaje para ver el análisis técnico aquí.")
    elif not r["rostro_detectado"]:
        st.caption(f"No se detectó rostro en la última foto (motivo: {r['calidad_deteccion']}).")
    else:
        s, interp = r["senales_observables"], r["interpretacion"]

        st.markdown("##### Señales medidas (geometría facial)")
        st.caption("Mediciones directas de los landmarks — no son una interpretación emocional.")
        col1, col2, col3 = st.columns(3)
        col1.metric("Apertura de ojos", s["apertura_ojo_promedio"])
        col2.metric("Apertura de boca", s["apertura_boca"])
        col3.metric("Elevación de cejas", s["elevacion_cejas"])
        if s["orientacion_cabeza"]:
            st.caption(f"Orientación estimada de cabeza: {s['orientacion_cabeza']}")

        st.markdown("##### Interpretación estimada")
        st.caption("Estimación con nivel de confianza — no una lectura exacta ni un diagnóstico.")
        colA, colB = st.columns(2)
        colA.metric("Emoción con mayor probabilidad", interp["emocion_dominante"])
        colB.metric("Confianza", f"{interp['confianza']*100:.0f}%")
        st.caption(f"Calidad de la detección: {r['calidad_deteccion']}")

        resumen_temporal = st.session_state.analizador_temporal.resumen()
        if resumen_temporal:
            st.markdown("##### Evolución en esta sesión")
            colX, colY, colZ = st.columns(3)
            colX.metric("Parpadeos detectados", resumen_temporal["parpadeos_detectados"])
            colY.metric("Cambios de expresión", resumen_temporal["cambios_de_expresion"])
            colZ.metric("Estabilidad", resumen_temporal["estabilidad"])

# ===========================================================
# PESTAÑA 5: AJUSTES
# ===========================================================
with tab_ajustes:
    st.markdown("#### General")

    # ---------------- Temas ----------------
    with st.expander("🎨 Temas"):
        claves_tema = list(TEMAS.keys())
        indice_actual = claves_tema.index(st.session_state.tema_elegido) \
            if st.session_state.tema_elegido in claves_tema else 0
        tema_seleccionado = st.radio(
            "Elige un tema", claves_tema, index=indice_actual,
            format_func=lambda clave: TEMAS[clave]["etiqueta"],
            label_visibility="collapsed", key="selector_tema"
        )
        if tema_seleccionado != st.session_state.tema_elegido:
            st.session_state.tema_elegido = tema_seleccionado
            st.session_state.perfil["tema"] = tema_seleccionado
            db.actualizar_perfil(sid, tema=tema_seleccionado)
            st.rerun()

    # ---------------- Personalizar mi chat ----------------
    with st.expander("💬 Personalizar mi chat"):
        nombre_actual = st.text_input("¿Cómo te gustaría que te llame el gatito?",
                                       value=perfil.get("nombre") or "", max_chars=40)
        st.caption("Avatar del gatito en el chat:")
        cols_avatar = st.columns(len(AVATARES_BOT))
        avatar_elegido_temporal = perfil.get("avatar_bot") or AVATARES_BOT[0]
        for col, opcion_avatar in zip(cols_avatar, AVATARES_BOT):
            with col:
                marca = "✅ " if opcion_avatar == avatar_elegido_temporal else ""
                if st.button(f"{marca}{opcion_avatar}", key=f"avatar_{opcion_avatar}", use_container_width=True):
                    avatar_elegido_temporal = opcion_avatar
                    st.session_state.perfil["avatar_bot"] = opcion_avatar
                    db.actualizar_perfil(sid, avatar_bot=opcion_avatar)
                    st.rerun()

        if st.button("Guardar nombre", key="guardar_nombre", use_container_width=True):
            st.session_state.perfil["nombre"] = nombre_actual.strip() or None
            db.actualizar_perfil(sid, nombre=nombre_actual.strip() or None)
            st.success("Guardado.")
            st.rerun()

    # ---------------- Configurar mi rutina ----------------
    with st.expander("🎯 Configurar mi rutina"):
        st.caption("Esto ayuda a sugerirte primero las herramientas más relevantes en la Caja de Gatitos.")
        objetivo_actual = perfil.get("objetivo")
        for obj in OBJETIVOS:
            marca = "✅ " if obj["clave"] == objetivo_actual else ""
            if st.button(f"{marca}{obj['icono']} {obj['nombre']}", key=f"objetivo_{obj['clave']}",
                         use_container_width=True):
                st.session_state.perfil["objetivo"] = obj["clave"]
                db.actualizar_perfil(sid, objetivo=obj["clave"])
                st.rerun()

    # ---------------- Recordatorios ----------------
    with st.expander("🔔 Recordatorios"):
        st.caption("Por ahora esto solo guarda tu preferencia -- los recordatorios por "
                   "notificación todavía no están activos, es la primera versión.")
        recordatorio_activo = st.toggle("Recordarme revisar mi ánimo",
                                         value=bool(perfil.get("recordatorio_activo")))
        hora_valor = perfil.get("recordatorio_hora") or "20:00"
        try:
            hora_default = datetime.strptime(hora_valor, "%H:%M").time()
        except ValueError:
            hora_default = datetime.strptime("20:00", "%H:%M").time()
        hora_recordatorio = st.time_input("Hora preferida", value=hora_default, disabled=not recordatorio_activo)

        if st.button("Guardar recordatorio", key="guardar_recordatorio", use_container_width=True):
            hora_texto = hora_recordatorio.strftime("%H:%M")
            st.session_state.perfil["recordatorio_activo"] = recordatorio_activo
            st.session_state.perfil["recordatorio_hora"] = hora_texto
            db.actualizar_perfil(sid, recordatorio_activo=recordatorio_activo, recordatorio_hora=hora_texto)
            st.success("Guardado.")

    # ---------------- PIN de seguridad ----------------
    with st.expander("🔒 PIN de seguridad"):
        st.caption("Es una traba básica para este dispositivo, no una cuenta con "
                   "contraseña real -- no protege contra alguien con el enlace directo a tu sesión.")
        if perfil.get("pin_hash"):
            st.success("PIN activado.")
            if st.button("Quitar PIN", key="quitar_pin"):
                st.session_state.perfil["pin_hash"] = None
                db.actualizar_perfil(sid, pin_hash=None)
                st.session_state.pin_verificado = False
                st.success("PIN eliminado.")
                st.rerun()
        else:
            nuevo_pin = st.text_input("Nuevo PIN (4 dígitos)", type="password", max_chars=4, key="nuevo_pin")
            confirmar_pin = st.text_input("Confirma el PIN", type="password", max_chars=4, key="confirmar_pin")
            if st.button("Activar PIN", key="activar_pin", use_container_width=True):
                if not (nuevo_pin.isdigit() and len(nuevo_pin) == 4):
                    st.error("El PIN debe ser de exactamente 4 dígitos numéricos.")
                elif nuevo_pin != confirmar_pin:
                    st.error("Los PIN no coinciden.")
                else:
                    pin_hash = hashlib.sha256(nuevo_pin.encode()).hexdigest()
                    st.session_state.perfil["pin_hash"] = pin_hash
                    db.actualizar_perfil(sid, pin_hash=pin_hash)
                    st.session_state.pin_verificado = True
                    st.success("PIN activado.")
                    st.rerun()

    st.markdown("#### Soporte")

    with st.expander("⚠️ Reportar falla técnica"):
        texto_falla = st.text_area("Cuéntanos qué pasó", key="texto_falla", height=100)
        if st.button("Enviar reporte", key="enviar_falla", use_container_width=True):
            if texto_falla.strip():
                db.guardar_reporte(sid, "falla", texto_falla.strip())
                st.success("Gracias, lo revisaremos.")
            else:
                st.warning("Escribe algo antes de enviar.")

    with st.expander("✏️ Enviar retroalimentación"):
        texto_feedback = st.text_area("¿Qué te gustaría que mejoráramos?", key="texto_feedback", height=100)
        if st.button("Enviar retroalimentación", key="enviar_feedback", use_container_width=True):
            if texto_feedback.strip():
                db.guardar_reporte(sid, "feedback", texto_feedback.strip())
                st.success("¡Gracias por tu retroalimentación!")
            else:
                st.warning("Escribe algo antes de enviar.")

    with st.expander("❓ Preguntas frecuentes"):
        for pregunta, respuesta in FAQ:
            st.markdown(f"**{pregunta}**")
            st.write(respuesta)
            st.markdown("---")

    with st.expander("📄 Aviso de Privacidad"):
        st.markdown(AVISO_PRIVACIDAD)

    with st.expander("📜 Términos & Condiciones"):
        st.markdown(TERMINOS)