"""
Rueda de emociones (inspirada en la que compartiste, no una transcripción
literal de ninguna imagen en particular) para llevar la detección más allá
de las 7 emociones básicas del modelo. A partir de la emoción PRIMARIA que
ya detecta la fusión visual+texto, esta rueda ofrece emociones SECUNDARIAS
y TERCIARIAS más específicas -- el gatito pregunta para llegar a ellas,
en vez de adivinar o mostrar un porcentaje de confianza.
"""

RUEDA_EMOCIONES = {
    "enojo": {
        "humillado": ["ridiculizado", "irrespetado", "menospreciado"],
        "traicionado": ["decepcionado", "resentido", "usado"],
        "frustrado": ["impotente", "bloqueado", "harto"],
        "amenazado": ["atacado", "a la defensiva", "provocado"],
        "celoso": ["envidioso", "posesivo", "inseguro"],
    },
    "miedo": {
        "inseguro": ["vulnerable", "indefenso", "expuesto"],
        "ansioso": ["preocupado", "agobiado", "nervioso"],
        "aterrado": ["asustado", "en pánico", "paralizado"],
        "rechazado": ["excluido", "abandonado", "marginado"],
    },
    "disgusto": {
        "repugnado": ["asqueado", "indignado", "ofendido"],
        "desconfiado": ["escéptico", "receloso", "suspicaz"],
        "critico": ["desdeñoso", "despectivo", "sarcástico"],
    },
    "tristeza": {
        "solo": ["aislado", "desamparado", "desconectado"],
        "desesperanzado": ["derrotado", "sin salida", "agotado"],
        "culpable": ["avergonzado", "arrepentido", "responsable"],
        "vacio": ["apático", "desmotivado", "melancólico"],
        "herido": ["lastimado", "decepcionado", "traicionado"],
    },
    "sorpresa": {
        "confundido": ["desconcertado", "perplejo", "desorientado"],
        "conmocionado": ["impactado", "en shock", "abrumado"],
        "asombrado": ["maravillado", "impresionado", "emocionado"],
    },
    "felicidad": {
        "orgulloso": ["seguro", "capaz", "satisfecho"],
        "agradecido": ["afortunado", "en paz", "pleno"],
        "esperanzado": ["optimista", "motivado", "ilusionado"],
        "conectado": ["querido", "acompañado", "en confianza"],
        "euforico": ["entusiasmado", "con energía", "vivo"],
    },
    "neutral": {
        "tranquilo": ["en calma", "estable", "centrado"],
        "indiferente": ["desconectado", "distraído", "de bajón"],
    },
}


def opciones_secundarias(emocion_primaria: str) -> list:
    """Lista de emociones secundarias para preguntar, dada la emoción primaria."""
    rama = RUEDA_EMOCIONES.get(emocion_primaria, RUEDA_EMOCIONES["neutral"])
    return list(rama.keys())


def opciones_terciarias(emocion_primaria: str, emocion_secundaria: str) -> list:
    """Lista de emociones terciarias (más específicas), dada la secundaria elegida."""
    rama = RUEDA_EMOCIONES.get(emocion_primaria, RUEDA_EMOCIONES["neutral"])
    return rama.get(emocion_secundaria, [])


def _normalizar(texto: str) -> str:
    import unicodedata
    texto = texto.lower().strip()
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def emparejar_texto_con_opcion(texto: str, opciones: list):
    """Si el usuario escribe en vez de tocar un botón, intenta encontrar cuál
    opción mencionó (sin distinguir mayúsculas ni acentos). Devuelve la
    opción original (con acentos) o None si no encontró coincidencia."""
    if not texto:
        return None
    texto_norm = _normalizar(texto)
    for opcion in opciones:
        if _normalizar(opcion) in texto_norm:
            return opcion
    return None