"""
Fase C - Detección de señales de crisis (seguridad del usuario)

Capa de RESGUARDO, independiente del clasificador de emociones (texto_emocion.py
no fue entrenado para esto y no debe ser el único filtro de seguridad).

Es un sistema basado en reglas -- NO es un diagnóstico ni sustituye ayuda
profesional. Su único trabajo es: si el texto del usuario contiene señales
de riesgo (ideación suicida, autolesión, desesperanza con intención de
morir), ofrecer recursos de ayuda reales de inmediato, sin esperar a que
el usuario los pida.

Principios de diseño:
- Frases completas, no palabras sueltas: "cortar" solo dispara si aparece
  en un contexto de autolesión, para no marcar cosas como "cortar cebolla".
- Prioriza NO dejar pasar un caso real (falsos negativos) sobre evitar
  falsos positivos: ante la duda, se muestra el mensaje de apoyo. Mostrarlo
  de más no hace daño; no mostrarlo cuando hacía falta, sí.
- No se decodifica ni se expone al usuario qué frase disparó la alerta.
"""

import re

RECURSOS_CRISIS_MX = {
    "linea_vida": {
        "nombre": "Línea de la Vida",
        "telefono": "800 911 2000",
        "detalle": "Gratuita, 24/7, todo México. Orientación en salud mental, adicciones y crisis emocional.",
    },
    "emergencia": {
        "nombre": "Emergencias",
        "telefono": "911",
        "detalle": "Si hay un riesgo inmediato para tu vida o la de alguien más.",
    },
}

RECURSO_INTERNACIONAL_URL = "https://findahelpline.com"

# ---------------------------------------------------------------------
# Patrones de riesgo: ideación suicida, autolesión, plan o deseo de morir.
# Se agrupan como frases (no palabras sueltas) para reducir falsos positivos
# frente a lenguaje figurado o coloquial ("me muero de hambre", etc.).
# ---------------------------------------------------------------------
_PATRONES_CRISIS = [
    r"quiero\s+(morir(me)?|matarme|suicidarme)",
    r"(ya\s+)?no\s+quiero\s+(seguir\s+)?vivi(r|endo)",
    r"(pensando|pienso|he\s+pensado)\s+en\s+(matarme|suicidarme|quitarme\s+la\s+vida)",
    r"quitarme\s+la\s+vida",
    r"acabar\s+con\s+(mi\s+vida|todo\s+esto)\b",
    r"no\s+(aguanto|soporto)\s+m[aá]s\s+(vivir|esta\s+vida|seguir\s+as[ií])",
    r"mejor\s+(estar[ií]a|estoy\s+mejor)\s+muert[oa]",
    r"me\s+quiero\s+(morir|matar)",
    r"quiero\s+dejar\s+de\s+existir",
    r"no\s+(quiero\s+|voy\s+a\s+|creo\s+que\s+(voy\s+a\s+)?)(despertar|llegar\s+a\s+ma[ñn]ana)",
    r"(quiero|voy\s+a)\s+hacerme\s+da[ñn]o",
    r"\bme\s+(estoy\s+)?cort(o|ando)\b",
    r"ganas\s+de\s+cortarme",
    r"ya\s+no\s+(tiene|le\s+veo)\s+sentido\s+(a\s+)?(la\s+vida|vivir|seguir(\s+aqu[ií])?)",
]

_REGEX_CRISIS = re.compile("|".join(_PATRONES_CRISIS), re.IGNORECASE)


def evaluar_riesgo(texto: str) -> dict:
    """
    Analiza el texto del usuario en busca de señales de riesgo de crisis.
    NO es un diagnóstico: es una capa de resguardo basada en reglas.

    Devuelve: {"hay_riesgo": bool, "nivel": "crisis" | "ninguno"}
    """
    if not texto or not texto.strip():
        return {"hay_riesgo": False, "nivel": "ninguno"}

    if _REGEX_CRISIS.search(texto):
        return {"hay_riesgo": True, "nivel": "crisis"}

    return {"hay_riesgo": False, "nivel": "ninguno"}


def mensaje_apoyo_crisis() -> str:
    """
    Mensaje de contención mostrado INMEDIATAMENTE cuando se detecta riesgo,
    en lugar de la respuesta normal del gatito. No hace preguntas que
    profundicen la crisis; ofrece ayuda concreta y estable.
    """
    lv = RECURSOS_CRISIS_MX["linea_vida"]
    em = RECURSOS_CRISIS_MX["emergencia"]
    return (
        "💙 Antes que nada: lo que sientes importa, y no tienes que pasar por esto solo/a.\n\n"
        f"**📞 {lv['nombre']}: {lv['telefono']}**\n"
        f"{lv['detalle']}\n\n"
        f"**🚨 {em['nombre']}: {em['telefono']}**\n"
        f"{em['detalle']}\n\n"
        f"Si estás fuera de México, puedes encontrar una línea de ayuda en tu país en "
        f"[findahelpline.com]({RECURSO_INTERNACIONAL_URL}).\n\n"
        "Sigo aquí para escucharte cuando quieras seguir hablando."
    )


def texto_recursos_siempre_visibles() -> str:
    """Versión breve para mostrar de forma permanente en la app (no solo reactiva)."""
    lv = RECURSOS_CRISIS_MX["linea_vida"]
    em = RECURSOS_CRISIS_MX["emergencia"]
    return (
        f"**{lv['nombre']}: {lv['telefono']}** · Gratuita, 24/7, México\n\n"
        f"**{em['nombre']}: {em['telefono']}** · Riesgo inmediato\n\n"
        f"Fuera de México: [findahelpline.com]({RECURSO_INTERNACIONAL_URL})"
    )