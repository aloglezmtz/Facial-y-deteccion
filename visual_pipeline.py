"""
Fase A - Pipeline Visual (versión responsable)
Separa explícitamente tres capas:
  1. rostro_detectado / calidad_deteccion  -> ¿se pudo medir algo, y qué tan bien?
  2. senales_observables                   -> mediciones geométricas objetivas
  3. interpretacion                        -> clasificación de emoción CON confianza,
                                               presentada como estimación, no como hecho.
Los imports pesados están protegidos: si faltan, DISPONIBLE=False y el resto
de la app sigue funcionando en modo solo-texto.
"""

DISPONIBLE = True
try:
    import cv2
    import mediapipe as mp
    from deepface import DeepFace
except ImportError:
    DISPONIBLE = False

from emociones_config import MAPEO_VISUAL, EMOCIONES
from facial_features import extraer_senales

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


def analizar_imagen(frame_bgr, analizador_temporal=None):
    """
    Recibe un frame BGR y devuelve un diccionario estructurado:
    {
        "rostro_detectado": bool,
        "calidad_deteccion": "buena" | "sin_rostro" | "roi_invalida" | "clasificacion_fallida",
        "senales_observables": {...} | None,
        "interpretacion": {
            "vector_probabilidades": {emocion: prob} | None,
            "emocion_dominante": str | None,
            "confianza": float,
        },
        "analisis_temporal": {...}  (si se pasó un AnalizadorTemporal)
    }
    """
    if not DISPONIBLE:
        return {"rostro_detectado": False, "calidad_deteccion": "librerias_no_instaladas",
                "senales_observables": None, "interpretacion": None}

    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    resultados = _face_mesh.process(rgb)

    if not resultados.multi_face_landmarks:
        return {"rostro_detectado": False, "calidad_deteccion": "sin_rostro",
                "senales_observables": None, "interpretacion": None}

    landmarks = resultados.multi_face_landmarks[0]
    senales = extraer_senales(landmarks, frame_bgr.shape)
    roi = _extraer_roi(frame_bgr, landmarks)

    interpretacion = {"vector_probabilidades": None, "emocion_dominante": None, "confianza": 0.0}
    calidad = "buena"

    if roi.size == 0:
        calidad = "roi_invalida"
    else:
        try:
            resultado = DeepFace.analyze(roi, actions=["emotion"], enforce_detection=False, silent=True)
            if isinstance(resultado, list):
                resultado = resultado[0]
            probs_originales = resultado["emotion"]
            vector = {e: 0.0 for e in EMOCIONES}
            for etiqueta, valor in probs_originales.items():
                comun = MAPEO_VISUAL.get(etiqueta)
                if comun:
                    vector[comun] = valor / 100.0
            emocion_dominante = max(vector, key=vector.get)
            interpretacion = {
                "vector_probabilidades": vector,
                "emocion_dominante": emocion_dominante,
                "confianza": vector[emocion_dominante],
            }
        except Exception:
            calidad = "clasificacion_fallida"

    resultado_final = {
        "rostro_detectado": True,
        "calidad_deteccion": calidad,
        "senales_observables": senales,
        "interpretacion": interpretacion,
    }

    if analizador_temporal is not None and interpretacion["emocion_dominante"]:
        resultado_final["analisis_temporal"] = analizador_temporal.registrar(
            senales, interpretacion["emocion_dominante"], interpretacion["confianza"]
        )

    return resultado_final