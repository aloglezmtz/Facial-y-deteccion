"""
Módulo de análisis de emoción visual (imagen estática).
Reutilizable desde: la UI (foto subida) y, más adelante, el pipeline de
webcam en vivo (Fase 1.B), para no duplicar la lógica de DeepFace.
"""

from deepface import DeepFace
from emociones_config import MAPEO_VISUAL, EMOCIONES


def analizar_emocion_imagen(imagen):
    """
    imagen: array numpy en formato BGR (como lo entrega OpenCV/Streamlit) o ruta de archivo.

    Devuelve:
    - emocion_dominante (str, taxonomía común, o None si falló)
    - vector_probabilidades (dict, taxonomía común -> 0.0-1.0)
    """
    vector_vacio = {e: 0.0 for e in EMOCIONES}

    try:
        resultado = DeepFace.analyze(
            imagen,
            actions=["emotion"],
            enforce_detection=False,
            silent=True
        )
        if isinstance(resultado, list):
            resultado = resultado[0]

        probabilidades_deepface = resultado["emotion"]  # vienen en escala 0-100

        vector = {e: 0.0 for e in EMOCIONES}
        for etiqueta_original, prob in probabilidades_deepface.items():
            etiqueta_comun = MAPEO_VISUAL.get(etiqueta_original)
            if etiqueta_comun:
                vector[etiqueta_comun] = prob / 100.0  # normalizar a 0-1, igual que el canal de texto

        emocion_dominante = max(vector, key=vector.get)
        return emocion_dominante, vector

    except Exception as e:
        print(f"Advertencia: fallo en análisis visual -> {e}")
        return None, vector_vacio