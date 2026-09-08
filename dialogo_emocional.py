"""
Motor de diálogo para llegar de una emoción primaria a una más específica
mediante preguntas, en vez de solo declarar la emoción con un % de
confianza. Lógica pura (sin Streamlit) para poder probarla de forma aislada.

Flujo:
    iniciar_dialogo()      -> arma el estado y las primeras opciones (secundarias)
    texto_pregunta()       -> texto de la pregunta a mostrar para el paso actual
    avanzar_dialogo()      -> procesa la opción elegida (clic o texto emparejado)
                               y decide si hay que preguntar un nivel más, o si
                               ya se puede cerrar con una respuesta final
    responder_intento_fallido() -> mensaje cuando el texto libre del usuario no
                               coincidió con ninguna opción
"""

from rueda_emociones import opciones_secundarias, opciones_terciarias
from emociones_config import EMOJIS_GATO


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
    opciones_fmt = _formatear_opciones(dialogo["opciones"])
    if dialogo["paso"] == "secundaria":
        return f"Cuéntame un poco más -- ¿dirías que te sentiste más **{opciones_fmt}**?"
    return f"Y de eso, ¿fue más bien **{opciones_fmt}**?"


def avanzar_dialogo(dialogo: dict, opcion_elegida: str):
    """
    Avanza el diálogo un paso.
    Devuelve (dialogo_actualizado_o_None, respuesta_final_o_None):
    - Si el diálogo debe seguir (falta el paso terciario), devuelve
      (dialogo_actualizado, None).
    - Si el diálogo terminó, devuelve (None, respuesta_final_en_texto).
    """
    if dialogo["paso"] == "secundaria":
        dialogo = dict(dialogo)
        dialogo["secundaria"] = opcion_elegida
        terciarias = opciones_terciarias(dialogo["primaria"], opcion_elegida)
        if terciarias:
            dialogo["paso"] = "terciaria"
            dialogo["opciones"] = terciarias
            return dialogo, None
        return None, _construir_respuesta_final(dialogo)

    dialogo = dict(dialogo)
    dialogo["terciaria"] = opcion_elegida
    return None, _construir_respuesta_final(dialogo)


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