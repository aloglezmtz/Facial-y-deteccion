"""
Fase A - Pipeline Visual (versión responsable)
Separa explícitamente tres capas:
  1. rostro_detectado / calidad_deteccion  -> ¿se pudo medir algo, y qué tan bien?
  2. senales_observables                   -> mediciones geométricas objetivas
  3. interpretacion                        -> clasificación de emoción CON confianza,
                                               presentada como estimación, no como hecho.
Los imports pesados y la inicialización de MediaPipe están protegidos con un
try/except AMPLIO (no solo ImportError): si CUALQUIER cosa falla al cargar
-- falta la librería, o está instalada pero rota/incompatible con la versión
de Python del servidor, como el AttributeError conocido de `mp.solutions` en
mediapipe 0.10.3x -- DISPONIBLE queda en False y el resto de la app (chat de
texto, detección de crisis) sigue funcionando con normalidad. Una falla en
el canal visual OPCIONAL nunca debe tumbar la app completa.
"""

# CARGA PEREZOSA: cv2/mediapipe/deepface (y TensorFlow, que deepface arrastra)
# ya NO se importan aquí arriba. Antes se cargaban en cuanto algo hacía
# `import visual_pipeline` -- es decir, apenas arrancaba la app, sin
# importar si alguien usaba la cámara o no. Eso consumía cientos de MB de
# RAM desde el primer segundo. Ahora solo se cargan la primera vez que
# esta_disponible() o analizar_imagen() se llaman de verdad.
DISPONIBLE = None  # None = todavía no se intentó cargar
_MOTIVO_NO_DISPONIBLE = None
cv2 = None
DeepFace = None
_face_mesh = None


def _asegurar_cargado():
    """Importa e inicializa cv2/mediapipe/deepface la primera vez que se necesitan.
    Llamadas posteriores no hacen nada (ya quedó cargado o ya falló antes)."""
    global DISPONIBLE, _MOTIVO_NO_DISPONIBLE, cv2, DeepFace, _face_mesh
    if DISPONIBLE is not None:
        return

    try:
        import cv2 as _cv2
        import mediapipe as mp
        from deepface import DeepFace as _DeepFace

        cv2 = _cv2
        DeepFace = _DeepFace
        _mp_face_mesh = mp.solutions.face_mesh
        _face_mesh = _mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        DISPONIBLE = True
    except Exception as _error_inicializacion:
        DISPONIBLE = False
        _MOTIVO_NO_DISPONIBLE = str(_error_inicializacion)


def esta_disponible():
    """Úsalo en vez de leer DISPONIBLE directamente: dispara la carga
    perezosa la primera vez y devuelve True/False de forma confiable."""
    _asegurar_cargado()
    return DISPONIBLE


from emociones_config import MAPEO_VISUAL, EMOCIONES
from facial_features import extraer_senales, describir_gesto


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
    _asegurar_cargado()
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

    interpretacion = {"vector_probabilidades": None, "emocion_dominante": None, "confianza": 0.0,
                       "gesto_principal": None, "lectura_estable": None}
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

            # Qué tan clara fue la lectura: si la emoción con más probabilidad
            # y la segunda están muy cerca, es una lectura ambigua -- mejor
            # decirlo que fingir una certeza que no hay.
            probs_ordenadas = sorted(vector.values(), reverse=True)
            margen = probs_ordenadas[0] - probs_ordenadas[1] if len(probs_ordenadas) > 1 else 1.0

            interpretacion = {
                "vector_probabilidades": vector,
                "emocion_dominante": emocion_dominante,
                "confianza": vector[emocion_dominante],
                "gesto_principal": describir_gesto(senales),
                "lectura_estable": margen >= 0.15,
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