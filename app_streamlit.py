"""
Fase 4 - Interfaz de Usuario (Tema: Gatitos Digitales)
Chat con análisis de emoción en tiempo real + panel de tendencia de ánimo +
canal visual opcional vía snapshot de cámara (Fase 1.B integrada).
"""

import numpy as np
import streamlit as st
import streamlit.components.v1 as components
from texto_emocion import AnalizadorEmocionTexto
from fusion import fusionar
from emociones_config import EMOJIS_GATO, PALETA_UI, EMOCIONES
from gatito_widget import generar_gatito_html
import visual_pipeline
import historial_manager as hm

st.set_page_config(page_title="Gatitos Emocionales", page_icon="🐾", layout="centered")

st.markdown(f"""
<style>
    .stApp {{
        background: linear-gradient(180deg, {PALETA_UI['fondo_inicio']} 0%, {PALETA_UI['fondo_fin']} 100%);
    }}
    h1, h2, h3, p, span, label {{ color: {PALETA_UI['texto_principal']} !important; }}
    div[data-testid="stChatMessage"] {{
        background-color: {PALETA_UI['tarjeta']};
        border-radius: 18px; padding: 6px 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }}
    .stToggle, .stMetric {{ background-color: {PALETA_UI['tarjeta']}; border-radius: 14px; padding: 8px; }}
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def cargar_analizador():
    return AnalizadorEmocionTexto()


analizador = cargar_analizador()

if "historial_chat" not in st.session_state:
    st.session_state.historial_chat = []
if "emocion_actual" not in st.session_state:
    st.session_state.emocion_actual = "neutral"

st.markdown("<h1 style='text-align:center;'>🐾 Tu Gatito Emocional</h1>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Control de modo (cámara)
# ---------------------------------------------------------
col1, col2 = st.columns([3, 1])
with col1:
    camara_disponible = st.toggle(
        "Usar cámara (fusión multimodal)",
        value=False,
        help="Toma una foto al enviar tu mensaje y combina el canal visual (60%) "
             "con el canal textual (40%). Si las librerías de visión no están "
             "instaladas, la app avisa y sigue en modo solo-texto."
    )
with col2:
    st.metric("Modo", "Visual+Texto" if camara_disponible else "Solo Texto")

foto = None
if camara_disponible:
    if visual_pipeline.DISPONIBLE:
        foto = st.camera_input("Toma una foto de tu rostro (se analiza al enviar tu mensaje)")
    else:
        st.warning(
            "El canal visual requiere `opencv-python`, `mediapipe` y `deepface`. "
            "Instálalos con:\n\n`pip install opencv-python mediapipe deepface tensorflow==2.15.0 tf-keras`\n\n"
            "Mientras tanto, seguimos en modo solo-texto."
        )
        camara_disponible = False

# ---------------------------------------------------------
# Gatito héroe animado
# ---------------------------------------------------------
components.html(generar_gatito_html(st.session_state.emocion_actual), height=260)
st.markdown(
    f"<p style='text-align:center; font-size:20px; font-weight:600;'>"
    f"{EMOJIS_GATO.get(st.session_state.emocion_actual, '😺')}  {st.session_state.emocion_actual.capitalize()}</p>",
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# Panel de estado de ánimo (historial persistente)
# ---------------------------------------------------------
import pandas as pd
import altair as alt
from emociones_config import COLOR_GATO, PALETA_UI, EMOCIONES

# Aseguramos el mapeo numérico inverso usando la taxonomía de emociones-config
# EMOCIONES = ["enojo", "disgusto", "miedo", "felicidad", "tristeza", "sorpresa", "neutral"]
# Esto significa que 0=enojo, 1=disgusto, 2=miedo, 3=felicidad, 4=tristeza, 5=sorpresa, 6=neutral, etc.
# Si tu orden interno en el backend es distinto, ajusta las posiciones de la lista abajo.
ORDEN_EMOCIONES = ["enojo", "disgusto", "miedo", "tristeza", "neutral", "sorpresa", "felicidad"]

historial_guardado = hm.cargar_historial()
if historial_guardado:
    with st.expander("📊 Tu estado de ánimo reciente", expanded=False):
        mas_frecuente = hm.emocion_mas_frecuente(historial_guardado)
        
        # Si el método devuelve un número, lo traducimos a texto para el mensaje
        if isinstance(mas_frecuente, int) and mas_frecuente < len(EMOCIONES):
            mas_frecuente_txt = EMOCIONES[mas_frecuente]
        else:
            mas_frecuente_txt = str(mas_frecuente)

        colA, colB = st.columns(2)
        with colA:
            st.markdown(f"**Ánimo más frecuente:** {EMOJIS_GATO.get(mas_frecuente_txt,'😺')} {mas_frecuente_txt.capitalize()}")
        with colB:
            st.markdown(f"**Registros totales:** {len(historial_guardado)}")

        serie = hm.serie_para_grafica(historial_guardado)
        
        if len(serie) >= 2:
            df_lista = []
            for momento, emocion_id in serie.items():
                # TRADUCCIÓN: Si es número, saca el texto de la lista de EMOCIONES
                try:
                    idx = int(emocion_id)
                    emocion_limpia = EMOCIONES[idx] if idx < len(EMOCIONES) else "neutral"
                except (ValueError, TypeError):
                    emocion_limpia = str(emocion_id).lower().strip()
                
                df_lista.append({
                    "Momento": momento,
                    "Emoción": emocion_limpia.capitalize(),  # Para una presentación estética
                    "Color": COLOR_GATO.get(emocion_limpia, "#B7B0A8")
                })
            
            df_plot = pd.DataFrame(df_lista)

                        # --- OPCIÓN 1: TABLA VISUAL ESTILIZADA ---
            st.markdown("<p style='font-weight:600; margin-bottom:5px;'>📋 Historial de lecturas:</p>", unsafe_allow_html=True)
            
            # Formateamos los colores en la tabla usando .map()
            def colorear_celda(val):
                if isinstance(val, str) and val.startswith("#"):
                    return f'background-color: {val}; color: #5B4636; font-weight: bold; border-radius: 6px;'
                return ''
                
            # AQUÍ ESTÁ EL CAMBIO PRINCIPAL: .map en lugar de .applymap
            df_estilizado = df_plot.style.map(colorear_celda, subset=['Color'])
            st.dataframe(df_estilizado, use_container_width=True, hide_index=True)

            # --- OPCIÓN 2: GRÁFICA ALTAIR INTEGRADA ---
            st.markdown("<p style='font-weight:600; margin-top:15px; margin-bottom:5px;'>📉 Línea de tendencia temporal:</p>", unsafe_allow_html=True)
            
            # Adaptamos el orden psicológico con mayúsculas para emparejar con los datos capitalizados
            orden_capitalizado = [e.capitalize() for e in ORDEN_EMOCIONES]

            base_chart = alt.Chart(df_plot).encode(
                x=alt.X("Momento:O", axis=alt.Axis(labelAngle=-45, titleColor=PALETA_UI['texto_principal'], grid=False)),
                y=alt.Y("Emoción:O", sort=orden_capitalizado, axis=alt.Axis(titleColor=PALETA_UI['texto_principal'], grid=True))
            )

            lineas = base_chart.mark_line(
                stroke=PALETA_UI['texto_principal'],
                strokeWidth=4,
                interpolate="monotone"
            )

            puntos = base_chart.mark_point(
                size=120, 
                filled=True, 
                stroke="white", 
                strokeWidth=2
            ).encode(
                color=alt.Color("Emoción:N", scale=alt.Scale(
                    domain=[e.capitalize() for e in COLOR_GATO.keys()],
                    range=list(COLOR_GATO.values())
                ), legend=None)
            )

            grafica_final = (lineas + puntos).properties(
                height=250
            ).configure_view(
                strokeWidth=0
            ).configure_axis(
                domain=False,
                labelColor=PALETA_UI['texto_principal'],
                titleColor=PALETA_UI['texto_principal']
            )

            st.altair_chart(grafica_final, use_container_width=True)

        else:
            st.caption("Escribe algunos mensajes más para ver la tendencia de tu ánimo.")

        if st.button("🗑️ Borrar historial"):
            hm.borrar_historial()
            st.rerun()

st.divider()

# ---------------------------------------------------------
# Historial de chat (avatares de gato por emoción)
# ---------------------------------------------------------
for mensaje in st.session_state.historial_chat:
    avatar = EMOJIS_GATO.get(mensaje["emocion"], "😺") if mensaje["rol"] == "user" else "🐈‍⬛"
    with st.chat_message(mensaje["rol"], avatar=avatar):
        st.write(mensaje["texto"])

# ---------------------------------------------------------
# Input de chat
# ---------------------------------------------------------
texto_usuario = st.chat_input("Cuéntale a tu gatito cómo te sientes...")

if texto_usuario:
    emocion_texto, vector_texto = analizador.analizar(texto_usuario)

    vector_visual = None
    rostro_detectado = False
    if camara_disponible and foto is not None:
        from PIL import Image
        imagen_pil = Image.open(foto)
        frame_rgb = np.array(imagen_pil.convert("RGB"))
        frame_bgr = frame_rgb[:, :, ::-1].copy()  # RGB -> BGR para el pipeline visual
        vector_visual, rostro_detectado = visual_pipeline.analizar_imagen(frame_bgr)

    usar_camara_en_fusion = camara_disponible and vector_visual is not None

    emocion_final, vector_fusionado, incongruencia = fusionar(
        vector_texto=vector_texto,
        vector_visual=vector_visual,
        camara_disponible=usar_camara_en_fusion
    )

    st.session_state.emocion_actual = emocion_final
    st.session_state.historial_chat.append({"rol": "user", "texto": texto_usuario, "emocion": emocion_final})

    confianza = vector_fusionado[emocion_final] * 100
    respuesta = f"Ronroneo... detecto **{emocion_final}** (confianza: {confianza:.0f}%) {EMOJIS_GATO.get(emocion_final,'😺')}"

    if camara_disponible and not rostro_detectado:
        respuesta += "\n\n😿 *No pude ver tu rostro en la foto, así que usé solo el texto esta vez.*"
    if incongruencia:
        respuesta += "\n\n😼 *Psst... tu cara y tus palabras no dicen lo mismo. ¿Sarcasmo tal vez?*"

    st.session_state.historial_chat.append({"rol": "assistant", "texto": respuesta, "emocion": emocion_final})

    hm.guardar_registro(emocion_final, confianza, texto_usuario, usar_camara_en_fusion)

    st.rerun()

st.caption("🐱 El gatito cambia de expresión según la emoción detectada en tu mensaje.")