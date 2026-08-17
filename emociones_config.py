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

# Color del pelaje del gatito héroe (SVG), por emoción — paleta pastel propia
COLOR_GATO = {
    "felicidad": "#F5A94E",   # naranja atigrado
    "tristeza": "#8FA6C7",    # gris azulado
    "enojo": "#D9736A",       # terracota suave
    "miedo": "#B79FD1",       # lila
    "disgusto": "#93A87E",    # verde oliva suave
    "sorpresa": "#F2D06B",    # amarillo pastel
    "neutral": "#B7B0A8",     # gris cálido
}

# Paleta general de la interfaz (fondo cálido tipo Yana)
PALETA_UI = {
    "fondo_inicio": "#FFF3E6",
    "fondo_fin": "#FFE1D6",
    "tarjeta": "#FFFFFF",
    "texto_principal": "#5B4636",
    "acento": "#F5A94E",
}