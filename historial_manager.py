"""
Historial de emociones: persistencia simple en JSON local.
Alimenta el panel de "Estado de ánimo" (tendencia + emoción más frecuente).
"""

import json
import os
from datetime import datetime
from collections import Counter

RUTA_HISTORIAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "historial_emociones.json")

# Escala numérica simple para graficar tendencia (ánimo negativo -> positivo)
ESCALA_ANIMO = {
    "tristeza": 1, "miedo": 2, "disgusto": 2, "enojo": 2,
    "neutral": 3, "sorpresa": 4, "felicidad": 5,
}


def cargar_historial():
    if not os.path.exists(RUTA_HISTORIAL):
        return []
    try:
        with open(RUTA_HISTORIAL, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def guardar_registro(emocion: str, confianza: float, texto: str, camara_usada: bool):
    historial = cargar_historial()
    historial.append({
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "emocion": emocion,
        "confianza": round(confianza, 1),
        "texto": texto[:200],   # se recorta por tamaño; no es un log de auditoría
        "camara_usada": camara_usada,
    })
    with open(RUTA_HISTORIAL, "w", encoding="utf-8") as f:
        json.dump(historial, f, ensure_ascii=False, indent=2)
    return historial


def emocion_mas_frecuente(historial):
    if not historial:
        return None
    conteo = Counter(r["emocion"] for r in historial)
    return conteo.most_common(1)[0][0]


def serie_para_grafica(historial, ultimos_n=20):
    """
    Devuelve un dict {hora: valor_animo} listo para st.line_chart,
    usando solo los últimos N registros.
    """
    recientes = historial[-ultimos_n:]
    return {r["fecha"][-8:]: ESCALA_ANIMO.get(r["emocion"], 3) for r in recientes}


def borrar_historial():
    if os.path.exists(RUTA_HISTORIAL):
        os.remove(RUTA_HISTORIAL)