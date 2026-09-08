"""
Fase 1.A - Módulo Visual (Modo Archivo de Video)
Captura de video + detección de rostro con MediaPipe Face Mesh
Sistema Multimodal de Análisis de Emociones
"""

import cv2
import mediapipe as mp
import time
import os

# ---------------------------------------------------------
# CONFIGURACIÓN: nombre del archivo de video
# ---------------------------------------------------------
NOMBRE_VIDEO = "videoplayback.mp4"   # <-- cambia esto por el nombre exacto de tu archivo

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


def main():
    # -------------------------------------------------------------
    # Construir ruta absoluta: el video debe estar en la misma
    # carpeta que este script, sin importar desde dónde lo ejecutes
    # -------------------------------------------------------------
    carpeta_script = os.path.dirname(os.path.abspath(__file__))
    ruta_video = os.path.join(carpeta_script, NOMBRE_VIDEO)

    if not os.path.exists(ruta_video):
        print(f"ERROR: No se encontró el archivo '{NOMBRE_VIDEO}' en:")
        print(f"  {carpeta_script}")
        print("Verifica que el video esté en la misma carpeta que este script")
        print("y que el nombre (incluyendo la extensión) esté escrito exactamente igual.")
        return

    cap = cv2.VideoCapture(ruta_video)

    if not cap.isOpened():
        print(f"ERROR: El archivo '{NOMBRE_VIDEO}' existe pero no se pudo abrir.")
        print("Puede estar corrupto o en un formato/codec no soportado por OpenCV.")
        return

    # Info útil del video para debug
    fps_video = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    print(f"Video cargado: {NOMBRE_VIDEO}")
    print(f"FPS originales: {fps_video:.1f} | Total de frames: {total_frames}")
    print("Presiona 'q' en la ventana de video para salir antes de que termine.\n")

    prev_time = 0
    frame_count = 0
    frames_con_rostro = 0

    while cap.isOpened():
        success, frame = cap.read()

        if not success:
            print(f"\nVideo terminado. Frames procesados: {frame_count}")
            print(f"Frames con rostro detectado: {frames_con_rostro} "
                  f"({(frames_con_rostro / max(frame_count, 1)) * 100:.1f}%)")
            break

        frame_count += 1

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False

        resultados = face_mesh.process(rgb_frame)

        rgb_frame.flags.writeable = True

        if resultados.multi_face_landmarks:
            frames_con_rostro += 1
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
                cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)

                cv2.putText(frame, "Rostro detectado", (x_min, y_min - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        else:
            cv2.putText(frame, "No se detecta rostro", (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        # FPS reales de procesamiento (velocidad de tu pipeline, no del video)
        curr_time = time.time()
        fps_procesamiento = 1 / (curr_time - prev_time) if prev_time else 0
        prev_time = curr_time
        cv2.putText(frame, f"Procesando a: {int(fps_procesamiento)} FPS", (20, frame.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        cv2.putText(frame, f"Frame {frame_count}/{total_frames}", (20, frame.shape[0] - 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

        cv2.imshow("Modulo Visual - Deteccion de Rostro (Modo Video)", frame)

        # 30ms ~ reproduce a velocidad cercana al video original.
        # Bájalo (ej. 1) si quieres procesar lo más rápido posible sin importar
        # la velocidad de reproducción visual.
        if cv2.waitKey(30) & 0xFF == ord('q'):
            print("\nSalida manual solicitada por el usuario.")
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()