"""
Fase 1.B - Módulo Visual: Detección de Rostro + Clasificación de Emoción
MediaPipe (tracking rápido) + DeepFace (clasificación FER, cada N frames)
Sistema Multimodal de Análisis de Emociones
"""

import cv2
import mediapipe as mp
import time
import os
from deepface import DeepFace

# ---------------------------------------------------------
# CONFIGURACIÓN
# ---------------------------------------------------------
NOMBRE_VIDEO = "cuaso.mp4"   # <-- cambia por el nombre exacto de tu archivo
FRAMES_ENTRE_INFERENCIAS = 10  # cada cuántos frames corremos DeepFace (ajustable)

# ---------------------------------------------------------
# Configuración de MediaPipe Face Mesh
# ---------------------------------------------------------
mp_face_mesh = mp.solutions.face_mesh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Traducción de emociones para mostrar en español (DeepFace devuelve en inglés)
TRADUCCION_EMOCIONES = {
    "angry": "Enojo",
    "disgust": "Disgusto",
    "fear": "Miedo",
    "happy": "Felicidad",
    "sad": "Tristeza",
    "surprise": "Sorpresa",
    "neutral": "Neutral"
}

# Colores por emoción (BGR) para dar feedback visual rápido
COLOR_EMOCIONES = {
    "angry": (0, 0, 255),
    "disgust": (0, 128, 0),
    "fear": (128, 0, 128),
    "happy": (0, 255, 255),
    "sad": (255, 0, 0),
    "surprise": (0, 165, 255),
    "neutral": (200, 200, 200)
}


def extraer_roi_rostro(frame, landmarks, padding=20):
    """
    Calcula el bounding box del rostro a partir de los landmarks
    y devuelve la región recortada (ROI) lista para el modelo FER.
    """
    h, w, _ = frame.shape
    xs = [lm.x * w for lm in landmarks.landmark]
    ys = [lm.y * h for lm in landmarks.landmark]

    x_min = max(int(min(xs)) - padding, 0)
    x_max = min(int(max(xs)) + padding, w)
    y_min = max(int(min(ys)) - padding, 0)
    y_max = min(int(max(ys)) + padding, h)

    roi = frame[y_min:y_max, x_min:x_max]
    return roi, (x_min, y_min, x_max, y_max)


def clasificar_emocion(roi):
    """
    Corre DeepFace sobre el ROI del rostro y devuelve:
    - emocion_dominante (str, en inglés, clave de TRADUCCION_EMOCIONES)
    - confianza (float, 0-100)
    - todas las probabilidades (dict) por si luego se quieren usar en la Fase 3 (fusión)
    Devuelve (None, 0, {}) si no se pudo clasificar.
    """
    try:
        resultado = DeepFace.analyze(
            roi,
            actions=["emotion"],
            enforce_detection=False,  # ya sabemos que hay rostro (nos lo dijo MediaPipe)
            silent=True
        )
        # DeepFace puede devolver una lista si detecta varios rostros
        if isinstance(resultado, list):
            resultado = resultado[0]

        emocion_dominante = resultado["dominant_emotion"]
        probabilidades = resultado["emotion"]
        confianza = probabilidades[emocion_dominante]
        return emocion_dominante, confianza, probabilidades

    except Exception as e:
        import traceback
        print("Advertencia: fallo en clasificación de emoción:")
        traceback.print_exc()
        return None, 0, {}


def main():
    carpeta_script = os.path.dirname(os.path.abspath(__file__))
    ruta_video = os.path.join(carpeta_script, NOMBRE_VIDEO)

    if not os.path.exists(ruta_video):
        print(f"ERROR: No se encontró el archivo '{NOMBRE_VIDEO}' en:")
        print(f"  {carpeta_script}")
        return

    cap = cv2.VideoCapture(ruta_video)

    if not cap.isOpened():
        print(f"ERROR: El archivo '{NOMBRE_VIDEO}' existe pero no se pudo abrir.")
        return

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Video cargado: {NOMBRE_VIDEO} | Total de frames: {total_frames}")
    print(f"Clasificando emoción cada {FRAMES_ENTRE_INFERENCIAS} frames.")
    print("Presiona 'q' en la ventana de video para salir antes de que termine.\n")

    prev_time = 0
    frame_count = 0

    # Estado "persistente" de la última emoción detectada
    # (se muestra en pantalla hasta la siguiente actualización)
    ultima_emocion = None
    ultima_confianza = 0

    # Historial simple para reportar estadísticas al final (útil para tu informe)
    historial_emociones = []

    while cap.isOpened():
        success, frame = cap.read()

        if not success:
            print(f"\nVideo terminado. Frames procesados: {frame_count}")
            if historial_emociones:
                from collections import Counter
                conteo = Counter(historial_emociones)
                print("Distribución de emociones detectadas:")
                for emo, cnt in conteo.most_common():
                    pct = (cnt / len(historial_emociones)) * 100
                    print(f"  {TRADUCCION_EMOCIONES.get(emo, emo):12s}: {cnt:4d} veces ({pct:.1f}%)")
            break

        frame_count += 1

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False
        resultados = face_mesh.process(rgb_frame)
        rgb_frame.flags.writeable = True

        if resultados.multi_face_landmarks:
            for landmarks in resultados.multi_face_landmarks:
                mp_drawing.draw_landmarks(
                    image=frame,
                    landmark_list=landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=None,
                    connection_drawing_spec=mp_drawing_styles.get_default_face_mesh_tesselation_style()
                )

                roi, bbox = extraer_roi_rostro(frame, landmarks)
                x_min, y_min, x_max, y_max = bbox

                # --- Solo corremos DeepFace cada N frames ---
                if frame_count % FRAMES_ENTRE_INFERENCIAS == 0 and roi.size > 0:
                    emocion, confianza, _ = clasificar_emocion(roi)
                    if emocion is not None:
                        ultima_emocion = emocion
                        ultima_confianza = confianza
                        historial_emociones.append(emocion)

                # Color del bbox según la emoción detectada
                color_bbox = COLOR_EMOCIONES.get(ultima_emocion, (0, 255, 0))
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), color_bbox, 2)

                if ultima_emocion is not None:
                    texto_emocion = f"{TRADUCCION_EMOCIONES.get(ultima_emocion, ultima_emocion)} ({ultima_confianza:.0f}%)"
                else:
                    texto_emocion = "Analizando..."

                cv2.putText(frame, texto_emocion, (x_min, y_min - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color_bbox, 2)
        else:
            cv2.putText(frame, "No se detecta rostro", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        curr_time = time.time()
        fps_procesamiento = 1 / (curr_time - prev_time) if prev_time else 0
        prev_time = curr_time
        cv2.putText(frame, f"Procesando a: {int(fps_procesamiento)} FPS", (20, frame.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
        cv2.putText(frame, f"Frame {frame_count}/{total_frames}", (20, frame.shape[0] - 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        cv2.imshow("Modulo Visual - Deteccion de Emocion (Fase 1.B)", frame)

        if cv2.waitKey(30) & 0xFF == ord('q'):
            print("\nSalida manual solicitada por el usuario.")
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()