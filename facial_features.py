"""
Fase A - Señales Faciales Observables
Calcula métricas GEOMÉTRICAS directas a partir de los landmarks de MediaPipe.
Estas son mediciones objetivas (distancias, proporciones), NO interpretaciones
emocionales. La interpretación ocurre en una capa separada (visual_pipeline.py).
"""

import numpy as np
import cv2

# Índices de landmarks de MediaPipe Face Mesh (468 puntos base) para EAR estándar
OJO_IZQ = [33, 160, 158, 133, 153, 144]
OJO_DER = [362, 385, 387, 263, 373, 380]
CEJA_IZQ = 105
CEJA_DER = 334
OJO_IZQ_SUP = 159
OJO_DER_SUP = 386

# Modelo 3D genérico de referencia de un rostro promedio (mm) para estimar orientación.
# No es una calibración por persona, es una aproximación estándar en visión por computadora.
MODELO_3D = np.array([
    (0.0, 0.0, 0.0),         # nariz (punta)             -> landmark 1
    (0.0, -63.6, -12.5),     # mentón                     -> landmark 152
    (-43.3, 32.7, -26.0),    # esquina externa ojo izq    -> landmark 33
    (43.3, 32.7, -26.0),     # esquina externa ojo der    -> landmark 263
    (-28.9, -28.9, -24.1),   # esquina boca izq           -> landmark 61
    (28.9, -28.9, -24.1),    # esquina boca der           -> landmark 291
], dtype=np.float64)
INDICES_POSE = [1, 152, 33, 263, 61, 291]


def _distancia(p1, p2):
    return float(np.linalg.norm(np.array(p1) - np.array(p2)))


def _xy(landmarks, idx, w, h):
    lm = landmarks.landmark[idx]
    return (lm.x * w, lm.y * h)


def calcular_ear(landmarks, indices, w, h):
    """Eye Aspect Ratio. ~0.28-0.35 = ojo abierto; <0.18 aprox = ojo cerrado."""
    p = [_xy(landmarks, i, w, h) for i in indices]
    vertical1 = _distancia(p[1], p[5])
    vertical2 = _distancia(p[2], p[4])
    horizontal = _distancia(p[0], p[3])
    return (vertical1 + vertical2) / (2.0 * horizontal) if horizontal else 0.0


def calcular_mar(landmarks, w, h):
    """Mouth Aspect Ratio. Mayor valor = boca más abierta."""
    izq, der = _xy(landmarks, 61, w, h), _xy(landmarks, 291, w, h)
    sup, inf = _xy(landmarks, 13, w, h), _xy(landmarks, 14, w, h)
    horizontal = _distancia(izq, der)
    return _distancia(sup, inf) / horizontal if horizontal else 0.0


def calcular_elevacion_cejas(landmarks, w, h):
    """Distancia ceja-ojo normalizada por el ancho del rostro (mayor = cejas más elevadas)."""
    d_izq = _distancia(_xy(landmarks, CEJA_IZQ, w, h), _xy(landmarks, OJO_IZQ_SUP, w, h))
    d_der = _distancia(_xy(landmarks, CEJA_DER, w, h), _xy(landmarks, OJO_DER_SUP, w, h))
    ancho_rostro = _distancia(_xy(landmarks, 33, w, h), _xy(landmarks, 263, w, h))
    return ((d_izq + d_der) / 2.0) / ancho_rostro if ancho_rostro else 0.0


def estimar_orientacion_cabeza(landmarks, w, h):
    """
    Estima yaw/pitch/roll (grados) mediante solvePnP con un modelo 3D genérico.
    Es una ESTIMACIÓN aproximada (no calibrada a la cámara específica del usuario).
    Devuelve None si el cálculo no converge, para no fingir un dato que no se obtuvo.
    """
    puntos_2d = np.array([_xy(landmarks, i, w, h) for i in INDICES_POSE], dtype=np.float64)
    focal_length = w
    centro = (w / 2, h / 2)
    matriz_camara = np.array([[focal_length, 0, centro[0]],
                               [0, focal_length, centro[1]],
                               [0, 0, 1]], dtype=np.float64)
    dist_coeffs = np.zeros((4, 1))

    exito, rvec, _ = cv2.solvePnP(MODELO_3D, puntos_2d, matriz_camara, dist_coeffs,
                                   flags=cv2.SOLVEPNP_ITERATIVE)
    if not exito:
        return None

    rmat, _ = cv2.Rodrigues(rvec)
    sy = np.sqrt(rmat[0, 0] ** 2 + rmat[1, 0] ** 2)
    if sy < 1e-6:
        return None

    pitch = np.arctan2(-rmat[2, 0], sy)
    yaw = np.arctan2(rmat[1, 0], rmat[0, 0])
    roll = np.arctan2(rmat[2, 1], rmat[2, 2])

    return {
        "yaw_grados": round(float(np.degrees(yaw)), 1),
        "pitch_grados": round(float(np.degrees(pitch)), 1),
        "roll_grados": round(float(np.degrees(roll)), 1),
    }


def extraer_senales(landmarks, frame_shape):
    """
    Punto de entrada: recibe landmarks de un frame y devuelve un diccionario
    de SEÑALES OBSERVABLES. Ningún valor aquí es una emoción — son medidas.
    """
    h, w = frame_shape[:2]

    ear_izq = calcular_ear(landmarks, OJO_IZQ, w, h)
    ear_der = calcular_ear(landmarks, OJO_DER, w, h)
    ear_promedio = (ear_izq + ear_der) / 2.0
    mar = calcular_mar(landmarks, w, h)

    return {
        "apertura_ojo_izq": round(ear_izq, 3),
        "apertura_ojo_der": round(ear_der, 3),
        "apertura_ojo_promedio": round(ear_promedio, 3),
        "ojo_probablemente_cerrado": ear_promedio < 0.18,
        "apertura_boca": round(mar, 3),
        "boca_probablemente_abierta": mar > 0.5,
        "elevacion_cejas": round(calcular_elevacion_cejas(landmarks, w, h), 3),
        "orientacion_cabeza": estimar_orientacion_cabeza(landmarks, w, h),
    }