"""
Motor de diálogo para llegar de una emoción primaria a una más específica
mediante preguntas, en vez de solo declarar la emoción con un % de
confianza. Lógica pura (sin Streamlit) para poder probarla de forma aislada.

Flujo:
    iniciar_dialogo()      -> arma el estado y las primeras opciones (secundarias)
    texto_pregunta()       -> texto de la pregunta a mostrar para el paso actual
    avanzar_dialogo()      -> procesa la opción elegida (clic o texto emparejado)
                               y decide si hay que preguntar un nivel más, si hay
                               que pasar a preguntar la razón (paso "razon"), o si
                               ya se puede cerrar con una respuesta final
    responder_intento_fallido() -> mensaje cuando el texto libre del usuario no
                               coincidió con ninguna opción
    responder_con_apoyo()  -> una vez que el usuario cuenta la razón (texto libre),
                               arma una palabra de aliento + una herramienta sugerida
"""

import random

from rueda_emociones import opciones_secundarias, opciones_terciarias
from emociones_config import EMOJIS_GATO
from herramientas import herramientas_por_categoria


def iniciar_dialogo(primaria: str, contexto: str, confianza: float, incongruencia: bool) -> dict:
    return {
        "paso": "secundaria",
        "primaria": primaria,
        "contexto": contexto,
        "confianza": confianza,       # se guarda para la BD, NUNCA se muestra al usuario
        "incongruencia": incongruencia,
        "opciones": opciones_secundarias(primaria),
        "secundaria": None,
        "terciaria": None,
    }


def _formatear_opciones(opciones: list) -> str:
    opciones = [o.capitalize() if i == 0 else o for i, o in enumerate(opciones)]
    if len(opciones) == 1:
        return opciones[0]
    return ", ".join(opciones[:-1]) + f" o {opciones[-1]}"


def texto_pregunta(dialogo: dict) -> str:
    if dialogo["paso"] == "razon":
        return _PREGUNTA_RAZON
    if dialogo["paso"] == "seguimiento":
        return dialogo.get("pregunta_seguimiento", "")
    opciones_fmt = _formatear_opciones(dialogo["opciones"])
    if dialogo["paso"] == "secundaria":
        return f"Cuéntame un poco más -- ¿dirías que te sentiste más **{opciones_fmt}**?"
    return f"Y de eso, ¿fue más bien **{opciones_fmt}**?"


_PREGUNTA_RAZON = "¿Me cuentas un poco qué está pasando, o qué crees que hizo que te sintieras así? 💭"

_PREGUNTAS_SEGUIMIENTO = [
    "¿Dirías que esto es de hoy nada más, o ya llevas un rato con esto?",
    "¿Ya intentaste algo para sentirte mejor, o apenas te está cayendo el veinte?",
    "¿Cómo te gustaría sentirte en vez de esto?",
    "¿Hay alguien con quien puedas platicar esto además de a mí?",
]

_ACUSE_CORTO = [
    "Te escucho.",
    "Gracias por contarlo.",
    "Ok, entiendo.",
    "Vale, gracias por compartir eso.",
]


def acuse_corto() -> str:
    return random.choice(_ACUSE_CORTO)


def avanzar_a_seguimiento(dialogo: dict, razon_texto: str) -> dict:
    """Guarda la razón que dio el usuario y arma UNA pregunta corta y
    genérica de seguimiento, antes de cerrar con aliento + herramienta."""
    dialogo = dict(dialogo)
    dialogo["paso"] = "seguimiento"
    dialogo["razon"] = razon_texto
    dialogo["pregunta_seguimiento"] = random.choice(_PREGUNTAS_SEGUIMIENTO)
    dialogo["opciones"] = []
    return dialogo


def avanzar_dialogo(dialogo: dict, opcion_elegida: str):
    """
    Avanza el diálogo un paso.
    Devuelve (dialogo_actualizado_o_None, respuesta_final_o_None):
    - Si el diálogo debe seguir (falta el paso terciario, o falta preguntar
      la razón), devuelve (dialogo_actualizado, respuesta_o_None).
    - Si el diálogo terminó del todo (ya se dio el mensaje de apoyo),
      devuelve (None, None) -- pero eso ahora lo decide responder_con_apoyo(),
      no esta función.
    """
    if dialogo["paso"] == "secundaria":
        dialogo = dict(dialogo)
        dialogo["secundaria"] = opcion_elegida
        terciarias = opciones_terciarias(dialogo["primaria"], opcion_elegida)
        if terciarias:
            dialogo["paso"] = "terciaria"
            dialogo["opciones"] = terciarias
            return dialogo, None
        return _pasar_a_razon(dialogo)

    dialogo = dict(dialogo)
    dialogo["terciaria"] = opcion_elegida
    return _pasar_a_razon(dialogo)


def _pasar_a_razon(dialogo: dict):
    """Cierra el desglose de la emoción y deja el diálogo listo para
    preguntar la razón -- el diálogo NO termina aquí todavía."""
    respuesta = _construir_respuesta_final(dialogo)
    dialogo = dict(dialogo)
    dialogo["paso"] = "razon"
    dialogo["opciones"] = []
    return dialogo, respuesta


def _construir_respuesta_final(dialogo: dict) -> str:
    primaria = dialogo["primaria"]
    secundaria = dialogo.get("secundaria")
    terciaria = dialogo.get("terciaria")

    if secundaria and terciaria:
        nucleo = f"**{primaria}**, más específicamente **{secundaria}** -- en particular, **{terciaria}**"
    elif secundaria:
        nucleo = f"**{primaria}**, sintiéndote sobre todo **{secundaria}**"
    else:
        nucleo = f"**{primaria}**"

    respuesta = f"💛 Por lo que platicamos, esto es lo que percibo: {nucleo}. {EMOJIS_GATO.get(primaria, '😺')}"

    if dialogo.get("incongruencia"):
        respuesta += ("\n\n😼 *Noté una diferencia entre lo que mostró tu rostro y lo que escribiste. "
                       "Puede deberse a distintas razones.*")

    return respuesta


def responder_intento_fallido(dialogo: dict) -> str:
    opciones_fmt = " / ".join(o.capitalize() if i == 0 else o for i, o in enumerate(dialogo["opciones"]))
    return f"No logré identificar cuál se parece más a lo tuyo. ¿Alguna de estas: {opciones_fmt}?"


def etiqueta_especifica(dialogo: dict):
    """La emoción más específica disponible en el diálogo (terciaria > secundaria > primaria)."""
    return dialogo.get("terciaria") or dialogo.get("secundaria") or dialogo.get("primaria")


# ---------------------------------------------------------------
# Paso final: el usuario ya contó la razón (texto libre) -- se arma
# una palabra de aliento + se sugiere UNA herramienta de la Caja de
# Gatitos relacionada, según palabras clave en lo que escribió o,
# si no hay ninguna pista clara, según la emoción primaria detectada.
# ---------------------------------------------------------------

_PALABRAS_A_CATEGORIA = {
    "trabajo": "pensamientos", "escuela": "pensamientos", "examen": "pensamientos",
    "tarea": "pensamientos", "jefe": "pensamientos", "estudio": "pensamientos",
    "presion": "respiracion", "presión": "respiracion", "estres": "respiracion",
    "estrés": "respiracion", "ansiedad": "respiracion", "ansioso": "respiracion",
    "ansiosa": "respiracion", "nervios": "respiracion",
    "pelea": "conexion", "discuti": "conexion", "discutí": "conexion",
    "amigo": "conexion", "amiga": "conexion", "pareja": "conexion", "novio": "conexion",
    "novia": "conexion", "familia": "conexion", "solo": "conexion", "sola": "conexion",
    "nadie": "conexion", "extraño": "conexion", "extraña": "conexion",
    "cansad": "autocuidado", "dormir": "autocuidado", "duermo": "autocuidado",
    "descanso": "autocuidado", "agotad": "autocuidado",
    "culpa": "pensamientos", "pienso": "pensamientos", "vueltas": "pensamientos",
    "encerrad": "movimiento", "quieto": "movimiento", "quieta": "movimiento",
    "sedentari": "movimiento",
}

_CATEGORIA_POR_EMOCION = {
    "enojo": "movimiento",
    "disgusto": "pensamientos",
    "miedo": "respiracion",
    "tristeza": "conexion",
    "sorpresa": "pensamientos",
    "neutral": "pensamientos",
    "felicidad": "creatividad",
}

_ALIENTO = {
    "enojo": [
        "Tiene sentido sentirte así con lo que me cuentas -- el enojo casi siempre avisa que algo importante para ti se sintió atropellado.",
        "Gracias por contarme. Enojarte por eso es una reacción válida, no algo de lo que avergonzarte.",
    ],
    "disgusto": [
        "Entiendo por qué te cayó mal. Confiar en esa incomodidad también es cuidarte.",
    ],
    "miedo": [
        "Suena como algo que de verdad pesa. El miedo se siente enorme, pero eso no significa que estés en peligro real ahora mismo.",
        "Gracias por confiar eso. Es normal que el cuerpo se ponga en alerta con una situación así.",
    ],
    "tristeza": [
        "Siento que estés pasando por eso. No tienes que cargarlo solo/a.",
        "Gracias por compartirlo -- la tristeza pide espacio, no que la resuelvas de inmediato.",
    ],
    "sorpresa": [
        "Con razón te agarró desprevenido/a. Está bien tomarte un momento para procesarlo.",
    ],
    "neutral": [
        "Gracias por contarme un poco más de tu día.",
    ],
    "felicidad": [
        "¡Qué bueno leer esto! Vale la pena quedarte un momento disfrutando cómo se siente.",
        "Me alegra mucho -- momentos así son buenos para atesorar.",
    ],
}


def _inferir_categoria(primaria: str, razon_texto: str) -> str:
    texto = (razon_texto or "").lower()
    for palabra, categoria in _PALABRAS_A_CATEGORIA.items():
        if palabra in texto:
            return categoria
    return _CATEGORIA_POR_EMOCION.get(primaria, "pensamientos")


def sugerir_herramienta(dialogo: dict, texto_para_analizar: str):
    """Devuelve una herramienta (dict de herramientas.py) relacionada con
    lo que escribió el usuario (razón + seguimiento, ya combinados por quien
    llama), o None si la emoción es felicidad (ahí no se sugiere una
    'herramienta para sentirse mejor')."""
    if dialogo["primaria"] == "felicidad":
        return None
    categoria = _inferir_categoria(dialogo["primaria"], texto_para_analizar)
    candidatas = herramientas_por_categoria(categoria)
    return random.choice(candidatas) if candidatas else None


def responder_con_apoyo(dialogo: dict, razon_texto: str, herramienta) -> str:
    """Palabra de aliento + (si aplica) una herramienta sugerida."""
    primaria = dialogo["primaria"]
    aliento = random.choice(_ALIENTO.get(primaria, _ALIENTO["neutral"]))

    if not herramienta:
        return f"{aliento} 🐾"

    return (
        f"{aliento}\n\n"
        f"Si quieres, esto puede ayudar ahora mismo: **{herramienta['titulo']}** "
        f"({herramienta['duracion']}) -- {herramienta['descripcion']} "
        f"La encuentras completa en la Caja de Gatitos. 🐾"
    )