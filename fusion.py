"""
Fase 3 - Fusión Multimodal (Late Fusion ponderada)
Combina el vector de probabilidades del canal visual y del canal textual.
Si no hay cámara disponible, cae automáticamente a modo texto-dominante.
"""

from emociones_config import EMOCIONES, PESOS


def fusionar(vector_texto: dict, vector_visual: dict = None, camara_disponible: bool = False):
    """
    vector_texto: dict {emocion: prob} del módulo NLP (obligatorio)
    vector_visual: dict {emocion: prob} del módulo visual (opcional)
    camara_disponible: bool, determina qué set de pesos usar

    Devuelve:
    - emocion_final (str)
    - vector_fusionado (dict)
    - incongruencia (bool): True si visual y texto discrepan fuertemente
      (posible sarcasmo, frustración contenida o represión emocional)
    """
    pesos = PESOS["con_camara"] if camara_disponible else PESOS["sin_camara"]
    peso_visual = pesos["visual"]
    peso_texto = pesos["texto"]

    if vector_visual is None:
        vector_visual = {e: 0.0 for e in EMOCIONES}

    vector_fusionado = {}
    for emocion in EMOCIONES:
        v = vector_visual.get(emocion, 0.0)
        t = vector_texto.get(emocion, 0.0)
        vector_fusionado[emocion] = (peso_visual * v) + (peso_texto * t)

    emocion_final = max(vector_fusionado, key=vector_fusionado.get)

    # Detección simple de incongruencia: la emoción dominante de cada canal
    # es distinta Y ambas tienen confianza razonable (no es solo ruido)
    incongruencia = False
    if camara_disponible and vector_visual:
        emocion_visual_dominante = max(vector_visual, key=vector_visual.get)
        emocion_texto_dominante = max(vector_texto, key=vector_texto.get)
        if (emocion_visual_dominante != emocion_texto_dominante
                and vector_visual[emocion_visual_dominante] > 0.4
                and vector_texto[emocion_texto_dominante] > 0.4):
            incongruencia = True

    return emocion_final, vector_fusionado, incongruencia