"""
Fase 4 (C) - Interfaz de Usuario (Tema: Gatitos Digitales)
Chat persistente (SQLite) reorganizado en pestañas: Chat / Mi ánimo / Detalles técnicos.
El chat queda limpio y protagonista; lo técnico está disponible sin saturar.
"""

import numpy as np
import streamlit as st
import streamlit.components.v1 as components
from texto_emocion import AnalizadorEmocionTexto
from fusion import fusionar
from emociones_config import EMOJIS_GATO, PALETA_UI
from gatito_widget import generar_gatito_html
import visual_pipeline
from temporal_analysis import AnalizadorTemporal
import database as db

st.set_page_config(page_title="Gatitos Emocionales", page_icon="🐾", layout="centered")

st.markdown(f"""
<style>
    .stApp {{ background: linear-gradient(180deg, {PALETA_UI['fondo_inicio']} 0%, {PALETA_UI['fondo_fin']} 100%); }}
    h1, h2, h3, p, span, label {{ color: {PALETA_UI['texto_principal']} !important; }}
    div[data-testid="stChatMessage"] {{
        background-color: {PALETA_UI['tarjeta']}; border-radius: 18px; padding: 6px 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }}
    .stToggle, .stMetric {{ background-color: {PALETA_UI['tarjeta']}; border-radius: 14px; padding: 8px; }}
    .stTabs [data-baseweb="tab-list"] {{ gap: 4px; }}
    .stTabs [data-baseweb="tab"] {{
        background-color: {PALETA_UI['tarjeta']}; border-radius: 12px 12px 0 0; padding: 8px 16px;
    }}
</style>
""", unsafe_allow_html=True)

db.inicializar_db()


@st.cache_resource
def cargar_analizador_texto():
    return AnalizadorEmocionTexto()


analizador_texto = cargar_analizador_texto()

if "historial_chat" not in st.session_state:
    st.session_state.historial_chat = db.cargar_chat()
if "emocion_actual" not in st.session_state:
    ultimos = st.session_state.historial_chat
    st.session_state.emocion_actual = ultimos[-1]["emocion"] if ultimos else "neutral"
if "analizador_temporal" not in st.session_state:
    st.session_state.analizador_temporal = AnalizadorTemporal()
if "ultimo_resultado_visual" not in st.session_state:
    st.session_state.ultimo_resultado_visual = None

# ---------------------------------------------------------
# Encabezado siempre visible: gatito + estado actual
# ---------------------------------------------------------
st.markdown("<h1 style='text-align:center;'>🐾 Tu Gatito Emocional</h1>", unsafe_allow_html=True)
components.html(generar_gatito_html(st.session_state.emocion_actual), height=220)
st.markdown(
    f"<p style='text-align:center; font-size:18px; font-weight:600;'>"
    f"{EMOJIS_GATO.get(st.session_state.emocion_actual, '😺')}  {st.session_state.emocion_actual.capitalize()}</p>",
    unsafe_allow_html=True
)

tab_chat, tab_animo, tab_tecnico = st.tabs(["💬 Chat", "📊 Mi ánimo", "🔍 Detalles técnicos"])

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
            respuesta = (f"Detecto señales asociadas principalmente a **{emocion_final}** "
                         f"(confianza estimada: {confianza:.0f}%) {EMOJIS_GATO.get(emocion_final,'😺')}")

            if camara_disponible and resultado_visual and not resultado_visual["rostro_detectado"]:
                respuesta += "\n\n😿 *No se detectó tu rostro en la foto, la estimación usó solo el texto.*"
            if incongruencia:
                respuesta += ("\n\n😼 *Se detectó una diferencia entre las señales faciales y el texto. "
                               "Puede deberse a distintas razones.*")

            st.session_state.historial_chat.append(
                {"rol": "assistant", "texto": respuesta, "emocion": emocion_final})

            db.guardar_mensaje("user", texto_usuario, emocion_final, confianza / 100,
                                usar_camara_en_fusion, senales_para_guardar, calidad_para_guardar)
            db.guardar_mensaje("assistant", respuesta, emocion_final, confianza / 100, usar_camara_en_fusion)

        st.rerun()

# ===========================================================
# PESTAÑA 2: MI ÁNIMO — tendencia histórica
# ===========================================================
with tab_animo:
    total_mensajes = db.contar_mensajes_usuario()
    if total_mensajes == 0:
        st.info("Todavía no hay suficientes mensajes para mostrar tendencias. ¡Escríbele algo a tu gatito!")
    else:
        mas_frecuente = db.emocion_mas_frecuente()
        colA, colB = st.columns(2)
        colA.metric("Emoción más frecuente", f"{EMOJIS_GATO.get(mas_frecuente,'😺')} {mas_frecuente}")
        colB.metric("Mensajes registrados", total_mensajes)

        serie = db.serie_para_grafica()
        if len(serie) >= 2:
            st.markdown("**Evolución de tu ánimo:**")
            st.line_chart(serie)
        else:
            st.caption("Escribe algunos mensajes más para ver la gráfica de tendencia.")

        st.divider()
        st.markdown("##### Privacidad")
        st.caption("Tus datos se guardan localmente en tu computadora (`gora_local.db`). Nunca se envían a un servidor externo.")
        if st.button("🗑️ Borrar todo mi historial", type="secondary"):
            db.borrar_todo()
            st.session_state.historial_chat = []
            st.session_state.emocion_actual = "neutral"
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