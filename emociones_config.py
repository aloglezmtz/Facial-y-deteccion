"""
Configuración central de emociones y pesos de fusión.
Todos los módulos (visual, texto, fusión, UI) importan de aquí
para garantizar que hablan la misma taxonomía.
"""

# Taxonomía común (7 emociones básicas de Ekman + neutral)
EMOCIONES = ["enojo", "disgusto", "miedo", "felicidad", "tristeza", "sorpresa", "neutral"]

# Mapeo: etiquetas de DeepFace (inglés) -> taxonomía común
MAPEO_VISUAL = {
    "angry": "enojo",
    "disgust": "disgusto",
    "fear": "miedo",
    "happy": "felicidad",
    "sad": "tristeza",
    "surprise": "sorpresa",
    "neutral": "neutral",
}

# Mapeo: etiquetas de pysentimiento (modelo de emoción en español) -> taxonomía común
MAPEO_TEXTO = {
    "anger": "enojo",
    "disgust": "disgusto",
    "fear": "miedo",
    "joy": "felicidad",
    "sadness": "tristeza",
    "surprise": "sorpresa",
    "others": "neutral",
}

# Emojis para la interfaz (listos; los stickers de gato se añaden después
# reemplazando estos valores por rutas de imagen, ver nota en app_streamlit.py)
EMOJIS = {
    "enojo": "😠",
    "disgusto": "🤢",
    "miedo": "😨",
    "felicidad": "😄",
    "tristeza": "😢",
    "sorpresa": "😲",
    "neutral": "😐",
}

# Pesos de fusión según disponibilidad de cámara
PESOS = {
    "con_camara": {"visual": 0.6, "texto": 0.4},
    "sin_camara": {"visual": 0.0, "texto": 0.8},  # 20% queda como incertidumbre estructural
}

# ---------------------------------------------------------
# Tema "gatitos digitales" — usado por app_streamlit.py
# ---------------------------------------------------------

# Emojis nativos de gato (Unicode) para avatares de chat — sin imágenes externas
EMOJIS_GATO = {
    "felicidad": "😻",
    "tristeza": "😿",
    "enojo": "😾",
    "miedo": "🙀",
    "disgusto": "😼",
    "sorpresa": "😹",
    "neutral": "😺",
}

# Color de acento por emoción -- usado para fondos/insignias tintados según
# el ánimo detectado (NO es el color del pelaje del gatito, que ahora es
# calicó fijo; ver COLOR_CALICO más abajo).
COLOR_GATO = {
    "felicidad": "#F5A94E",   # naranja atigrado
    "tristeza": "#8FA6C7",    # gris azulado
    "enojo": "#D9736A",       # terracota suave
    "miedo": "#B79FD1",       # lila
    "disgusto": "#93A87E",    # verde oliva suave
    "sorpresa": "#F2D06B",    # amarillo pastel
    "neutral": "#B7B0A8",     # gris cálido
}

# Etiqueta corta y amigable por emoción, para el check-in de ánimo
# (equivalente a mostrar "Great" en vez de solo el nombre técnico).
ETIQUETAS_ANIMO = {
    "felicidad": "¡Genial!",
    "tristeza": "Bajo",
    "enojo": "Tenso",
    "miedo": "Inquieto",
    "disgusto": "Incómodo",
    "sorpresa": "Sorprendido",
    "neutral": "Tranquilo",
}

# ---------------------------------------------------------
# Pelaje del gatito héroe: calicó fijo (blanco + naranja + carey oscuro).
# A diferencia de COLOR_GATO, esto NO cambia con la emoción -- el color de
# un gato no cambia según su ánimo, solo su expresión. Mantenerlo fijo
# también refuerza que el gatito es "el mismo personaje" siempre.
# ---------------------------------------------------------
COLOR_CALICO = {
    "base": "#FFF8EE",          # blanco cálido / crema, color de fondo del pelaje
    "mancha_naranja": "#EE9B4D",  # parche naranja clásico calicó
    "mancha_carey": "#5B4636",    # parche oscuro tipo carey (marrón cálido, no negro puro)
    "nariz": "#E88D8D",
}

# Colores para las tarjetas de la Caja de Gatitos (uso cíclico, uno por tarjeta)
COLOR_HERRAMIENTAS = [
    "#FFE9D6",  # durazno suave
    "#E3EFE0",  # verde salvia claro
    "#F7E0E3",  # rosa polvo
    "#E4E9F7",  # azul lavanda claro
    "#FFF3D6",  # amarillo crema
    "#EAE1F0",  # lila claro
]

# Paleta general de la interfaz (fondo cálido tipo Yana)
PALETA_UI = {
    "fondo_inicio": "#FFF3E6",
    "fondo_fin": "#FFE1D6",
    "tarjeta": "#FFFFFF",
    "tarjeta_borde": "#F0E3D8",
    "sombra": "rgba(91, 70, 54, 0.08)",
    "texto_principal": "#5B4636",
    "texto_secundario": "#9C8676",
    "acento": "#F5A94E",
    "acento_suave": "#FFE9D6",
    "acento_secundario": "#7FA88F",
    "burbuja_usuario": "#F5A94E",
    "burbuja_asistente": "#FFFFFF",
}