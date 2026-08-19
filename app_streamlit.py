"""
Fase 4 (C) - Interfaz de Usuario (Tema: Gatitos Digitales)
Chat persistente (SQLite) reorganizado en pestañas: Chat / Mi ánimo / Detalles técnicos.
El chat queda limpio y protagonista; lo técnico está disponible sin saturar.
"""

import uuid
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
from texto_emocion import AnalizadorEmocionTexto
from fusion import fusionar
from emociones_config import EMOJIS_GATO, PALETA_UI, COLOR_HERRAMIENTAS, COLOR_GATO
from gatito_widget import generar_gatito_html
import visual_pipeline
from temporal_analysis import AnalizadorTemporal
import database as db
from herramientas import CATEGORIAS, herramientas_por_categoria, obtener_herramienta
import deteccion_crisis

st.set_page_config(page_title="Gatitos Emocionales", page_icon="🐾", layout="centered")

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
    .block-container {{ max-width: 640px; padding-top: 1.2rem; padding-bottom: 5rem; }}

    /* ---------- Tarjeta del gatito (encabezado) ---------- */
    .tarjeta-gatito {{
        background: {PALETA_UI['tarjeta']};
        border: 1px solid {PALETA_UI['tarjeta_borde']};
        border-radius: 28px;
        padding: 4px 16px 14px 16px;
        box-shadow: 0 8px 24px {PALETA_UI['sombra']};
        margin-bottom: 18px;
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

    /* ---------- Chat (estilo Yana: burbuja + avatar en aro) ---------- */
    div[data-testid="stChatMessage"] {{
        background-color: {PALETA_UI['burbuja_asistente']};
        border: 1px solid {PALETA_UI['tarjeta_borde']};
        border-radius: 20px; padding: 10px 14px;
        box-shadow: 0 2px 10px {PALETA_UI['sombra']};
        animation: aparecer 0.25s ease-out;
    }}
    div[data-testid="stChatMessage"] p {{ color: {PALETA_UI['texto_principal']} !important; }}
    div[data-testid="stChatMessage"]:has(> [data-testid="stChatMessageAvatarUser"]) {{
        background-color: {PALETA_UI['burbuja_usuario']};
        border-color: {PALETA_UI['burbuja_usuario']};
    }}
    div[data-testid="stChatMessage"]:has(> [data-testid="stChatMessageAvatarUser"]) p {{
        color: white !important;
    }}
    [data-testid="stChatMessageAvatarCustom"], [data-testid="stChatMessageAvatarUser"] {{
        border: 2.5px solid {PALETA_UI['acento_suave']} !important;
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

    /* ---------- Ánimo: carita grande ---------- */
    .carita-animo {{
        width: 130px; height: 130px; border-radius: 50%; margin: 8px auto 10px auto;
        display: flex; align-items: center; justify-content: center; font-size: 3.2rem;
        box-shadow: 0 6px 18px {PALETA_UI['sombra']};
    }}
    .etiqueta-teal {{
        color: {PALETA_UI['acento_secundario']} !important; font-family: 'Fredoka', sans-serif;
        font-weight: 600; font-size: 0.9rem;
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

db.inicializar_db()

# ---------------------------------------------------------
# Identidad anónima por navegador: cada usuario obtiene un
# session_id propio, guardado en la URL para sobrevivir a
# recargas de página. Nunca se comparte entre usuarios.
# ---------------------------------------------------------
if "session_id" not in st.session_state:
    sid_en_url = st.query_params.get("sid")
    if not sid_en_url:
        sid_en_url = str(uuid.uuid4())
        st.query_params["sid"] = sid_en_url
    st.session_state.session_id = sid_en_url

sid = st.session_state.session_id


@st.cache_resource
def cargar_analizador_texto():
    return AnalizadorEmocionTexto()


analizador_texto = cargar_analizador_texto()

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

# ---------------------------------------------------------
# Encabezado siempre visible: gatito + estado actual
# ---------------------------------------------------------
st.markdown('<div class="tarjeta-gatito">', unsafe_allow_html=True)
st.markdown('<p class="titulo-app">🐾 Tu Gatito Emocional</p>', unsafe_allow_html=True)
components.html(generar_gatito_html(st.session_state.emocion_actual), height=210)
st.markdown(
    f'<span class="badge-animo">{EMOJIS_GATO.get(st.session_state.emocion_actual, "😺")} '
    f'{st.session_state.emocion_actual.capitalize()}</span>',
    unsafe_allow_html=True
)
st.markdown('</div>', unsafe_allow_html=True)

# Acceso permanente a recursos de ayuda -- no solo reactivo ante una alerta.
# Colapsado por defecto para no saturar la pantalla de la mayoría de sesiones,
# pero siempre disponible sin importar la pestaña en la que esté el usuario.
with st.expander("🆘 ¿Necesitas ayuda ahora?"):
    st.markdown(deteccion_crisis.texto_recursos_siempre_visibles())

tab_chat, tab_animo, tab_caja, tab_tecnico = st.tabs(
    ["💬 Chat", "📊 Mi ánimo", "🧰 Caja de Gatitos", "🔍 Detalles técnicos"])

# ===========================================================
# PESTAÑA 1: CHAT — protagonista, sin ruido técnico
# ===========================================================
with tab_chat:
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
        if visual_pipeline.DISPONIBLE:
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

    contenedor_chat = st.container(height=380)
    with contenedor_chat:
        for mensaje in st.session_state.historial_chat:
            avatar = EMOJIS_GATO.get(mensaje["emocion"], "😺") if mensaje["rol"] == "user" else "🐈‍⬛"
            with st.chat_message(mensaje["rol"], avatar=avatar):
                st.write(mensaje["texto"])

    texto_usuario = st.chat_input("Cuéntale a tu gatito cómo te sientes...")

    if texto_usuario:
        with st.spinner("El gatito está pensando... 🐾"):
            # ---------------------------------------------------------
            # Capa de seguridad: se evalúa PRIMERO y de forma independiente
            # del análisis de emoción, que no está diseñado para detectar
            # riesgo. Si hay señales de crisis, la respuesta del gatito se
            # reemplaza por contención + recursos reales, sin preguntas que
            # profundicen el momento difícil.
            # ---------------------------------------------------------
            riesgo = deteccion_crisis.evaluar_riesgo(texto_usuario)

            emocion_texto, vector_texto = analizador_texto.analizar(texto_usuario)

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

            st.session_state.emocion_actual = emocion_final
            st.session_state.historial_chat.append(
                {"rol": "user", "texto": texto_usuario, "emocion": emocion_final})

            confianza = vector_fusionado[emocion_final] * 100

            if riesgo["hay_riesgo"]:
                # La respuesta normal (confianza, incongruencia, etc.) queda
                # en segundo plano: en un momento de crisis, lo prioritario
                # es contención y recursos, no una lectura de confianza.
                respuesta = deteccion_crisis.mensaje_apoyo_crisis()
            else:
                respuesta = (f"Detecto señales asociadas principalmente a **{emocion_final}** "
                             f"(confianza estimada: {confianza:.0f}%) {EMOJIS_GATO.get(emocion_final,'😺')}")

                if camara_disponible and resultado_visual and not resultado_visual["rostro_detectado"]:
                    respuesta += "\n\n😿 *No se detectó tu rostro en la foto, la estimación usó solo el texto.*"
                if incongruencia:
                    respuesta += ("\n\n😼 *Se detectó una diferencia entre las señales faciales y el texto. "
                                   "Puede deberse a distintas razones.*")

            st.session_state.historial_chat.append(
                {"rol": "assistant", "texto": respuesta, "emocion": emocion_final})

            id_mensaje_usuario = db.guardar_mensaje(
                sid, "user", texto_usuario, emocion_final, confianza / 100,
                usar_camara_en_fusion, senales_para_guardar, calidad_para_guardar)
            db.guardar_mensaje(sid, "assistant", respuesta, emocion_final, confianza / 100, usar_camara_en_fusion)

            if riesgo["hay_riesgo"]:
                db.registrar_alerta_crisis(sid, id_mensaje_usuario, riesgo["nivel"])

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
        color_carita = COLOR_GATO.get(mas_frecuente, COLOR_GATO["neutral"])

        st.markdown(
            f'<div class="carita-animo" style="background:{color_carita}22;">'
            f'{EMOJIS_GATO.get(mas_frecuente, "😺")}</div>'
            f'<p style="text-align:center; font-family:\'Fredoka\',sans-serif; font-weight:600; '
            f'font-size:1.1rem; margin-top:-4px;">{mas_frecuente.capitalize()}</p>',
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