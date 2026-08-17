"""
Fase 1.B reutilizable - Análisis de emoción sobre una sola imagen (snapshot).
Los imports pesados (opencv, mediapipe, deepface) están protegidos:
si no están instalados, DISPONIBLE queda en False y el resto de la app
sigue funcionando en modo solo-texto, sin romperse.
"""

DISPONIBLE = True
try:
    import cv2
    import mediapipe as mp
    from deepface import DeepFace
except ImportError:
    DISPONIBLE = False

from emociones_config import MAPEO_VISUAL, EMOCIONES

if DISPONIBLE:
    _mp_face_mesh = mp.solutions.face_mesh
    _face_mesh = _mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
    )


def _extraer_roi(frame_bgr, landmarks, padding=20):
    h, w, _ = frame_bgr.shape
    xs = [lm.x * w for lm in landmarks.landmark]
    ys = [lm.y * h for lm in landmarks.landmark]
    x_min = max(int(min(xs)) - padding, 0)
    x_max = min(int(max(xs)) + padding, w)
    y_min = max(int(min(ys)) - padding, 0)
    y_max = min(int(max(ys)) + padding, h)
    return frame_bgr[y_min:y_max, x_min:x_max]


def analizar_imagen(frame_bgr):
    """
    Recibe un frame BGR (numpy array) y devuelve:
    - vector_visual: dict {emocion_comun: prob 0-1}, o None si no se detectó rostro
    - rostro_detectado: bool
    """
    if not DISPONIBLE:
        return None, False

    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    resultados = _face_mesh.process(rgb)

    if not resultados.multi_face_landmarks:
        return None, False

    landmarks = resultados.multi_face_landmarks[0]
    roi = _extraer_roi(frame_bgr, landmarks)

    if roi.size == 0:
        return None, True

    try:
        resultado = DeepFace.analyze(roi, actions=["emotion"], enforce_detection=False, silent=True)
        if isinstance(resultado, list):
            resultado = resultado[0]

        probs_originales = resultado["emotion"]  # claves en inglés, valores 0-100
        vector = {e: 0.0 for e in EMOCIONES}
        for etiqueta, valor in probs_originales.items():
            comun = MAPEO_VISUAL.get(etiqueta)
            if comun:
                vector[comun] = valor / 100.0
        return vector, True

    except Exception:
        return None, True