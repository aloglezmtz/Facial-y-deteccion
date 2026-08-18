"""
Fase A - Análisis Temporal
Rastrea la evolución de señales faciales dentro de una sesión.
Solo guarda métricas numéricas y timestamps — nunca imágenes.
"""

from collections import deque
from datetime import datetime


class AnalizadorTemporal:
    def __init__(self, ventana: int = 30):
        self.historial = deque(maxlen=ventana)
        self._parpadeos = 0
        self._ojo_cerrado_antes = False
        self._emocion_actual = None
        self._inicio_emocion_actual = None

    def registrar(self, senales: dict, emocion_dominante: str, confianza: float):
        ahora = datetime.now()

        # Parpadeo = transición de "cerrado" a "abierto" entre dos mediciones
        cerrado_ahora = senales.get("ojo_probablemente_cerrado", False)
        if self._ojo_cerrado_antes and not cerrado_ahora:
            self._parpadeos += 1
        self._ojo_cerrado_antes = cerrado_ahora

        # Duración de la expresión dominante actual
        if emocion_dominante != self._emocion_actual:
            self._emocion_actual = emocion_dominante
            self._inicio_emocion_actual = ahora
        duracion = (ahora - self._inicio_emocion_actual).total_seconds() if self._inicio_emocion_actual else 0.0

        registro = {
            "timestamp": ahora.strftime("%H:%M:%S"),
            "senales": senales,
            "emocion_dominante": emocion_dominante,
            "confianza": round(confianza, 2),
            "duracion_expresion_actual_seg": round(duracion, 1),
        }
        self.historial.append(registro)
        return registro

    def resumen(self):
        if not self.historial:
            return None

        emociones = [r["emocion_dominante"] for r in self.historial]
        cambios = sum(1 for i in range(1, len(emociones)) if emociones[i] != emociones[i - 1])

        if cambios <= 1:
            estabilidad = "estable"
        elif cambios <= 3:
            estabilidad = "variable"
        else:
            estabilidad = "muy variable"

        return {
            "parpadeos_detectados": self._parpadeos,
            "emocion_actual": self._emocion_actual,
            "duracion_emocion_actual_seg": self.historial[-1]["duracion_expresion_actual_seg"],
            "cambios_de_expresion": cambios,
            "muestras_analizadas": len(self.historial),
            "estabilidad": estabilidad,
        }