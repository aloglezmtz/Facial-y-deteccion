"""
Fase 2 - Módulo NLP
Clasificación de emoción en texto en español usando pysentimiento
(RoBERTuito ajustado para análisis de emoción, no solo sentimiento).
"""

from pysentimiento import create_analyzer
from emociones_config import MAPEO_TEXTO, EMOCIONES


class AnalizadorEmocionTexto:
    def __init__(self):
        print("Cargando modelo de emoción en texto (RoBERTuito)... primera vez puede tardar.")
        self.analyzer = create_analyzer(task="emotion", lang="es")
        print("Modelo de texto listo.")

    def analizar(self, texto: str):
        """
        Devuelve:
        - emocion_dominante (str, en la taxonomía común, ej. 'felicidad')
        - vector_probabilidades (dict, taxonomía común -> probabilidad 0-1)
        """
        if not texto or not texto.strip():
            return "neutral", {e: 0.0 for e in EMOCIONES}

        resultado = self.analyzer.predict(texto)

        # Traducir el vector completo de probabilidades a la taxonomía común
        vector = {e: 0.0 for e in EMOCIONES}
        for etiqueta_original, prob in resultado.probas.items():
            etiqueta_comun = MAPEO_TEXTO.get(etiqueta_original)
            if etiqueta_comun:
                vector[etiqueta_comun] = prob

        emocion_dominante = max(vector, key=vector.get)
        return emocion_dominante, vector


# ---------------------------------------------------------
# Prueba rápida standalone: python texto_emocion.py
# ---------------------------------------------------------
if __name__ == "__main__":
    analizador = AnalizadorEmocionTexto()

    frases_prueba = [
        "Estoy muy feliz de haber terminado este proyecto",
        "No puedo creer que me hayan hecho esto, qué rabia",
        "Tengo mucho miedo de lo que pueda pasar mañana",
        "jaja claro, todo perfecto como siempre... genial",  # posible sarcasmo
    ]

    for frase in frases_prueba:
        emocion, vector = analizador.analizar(frase)
        print(f"\nTexto: {frase}")
        print(f"Emoción dominante: {emocion}")
        print(f"Vector: { {k: round(v, 2) for k, v in vector.items()} }")