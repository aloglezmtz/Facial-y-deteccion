"""
Contenido y datos estáticos para la pestaña de Ajustes.
Se mantiene separado de app_streamlit.py para no saturar el archivo
principal con texto largo (FAQ, avisos, etc.).
"""

TEMA_POR_DEFECTO = "calico"

# Cada tema es un diccionario con la misma forma que PALETA_UI en
# emociones_config.py. "calico" es EXACTAMENTE la paleta original, para que
# nadie note un cambio si nunca toca la pestaña de Ajustes.
TEMAS = {
    "calico": {
        "etiqueta": "🐾 Calicó (clásico)",
        "fondo_inicio": "#FFF3E6",
        "fondo_fin": "#FFE1D6",
        "tarjeta": "#FFFFFF",
        "tarjeta_borde": "#F0E3D8",
        "sombra": "rgba(91, 70, 54, 0.08)",
        "texto_principal": "#5B4636",
        "texto_secundario": "#9C8676",
        "acento": "#F5A94E",
        "acento_suave": "#FFE9D6",
        "acento_secundario": "#7FA88F",
        "burbuja_usuario": "#F5A94E",
        "burbuja_asistente": "#FFFFFF",
    },
    "menta": {
        "etiqueta": "🌿 Menta",
        "fondo_inicio": "#EAF6F1",
        "fondo_fin": "#DCEFE6",
        "tarjeta": "#FFFFFF",
        "tarjeta_borde": "#D3E9DE",
        "sombra": "rgba(47, 92, 74, 0.08)",
        "texto_principal": "#2F5C4A",
        "texto_secundario": "#6E9585",
        "acento": "#4FAE8B",
        "acento_suave": "#DCF2E9",
        "acento_secundario": "#E8A24A",
        "burbuja_usuario": "#4FAE8B",
        "burbuja_asistente": "#FFFFFF",
    },
    "medianoche": {
        "etiqueta": "🌙 Medianoche",
        "fondo_inicio": "#2B2420",
        "fondo_fin": "#1E1917",
        "tarjeta": "#3A322C",
        "tarjeta_borde": "#4A4038",
        "sombra": "rgba(0, 0, 0, 0.35)",
        "texto_principal": "#F5E9DD",
        "texto_secundario": "#C9B8A8",
        "acento": "#F2A65A",
        "acento_suave": "#4A3D30",
        "acento_secundario": "#8FBFA8",
        "burbuja_usuario": "#F2A65A",
        "burbuja_asistente": "#453B33",
    },
}

AVATARES_BOT = ["🐱", "🐈", "😺", "🐈‍⬛"]

# "Mi rutina": en qué le gustaría trabajar al usuario -- se usa para,
# en el futuro, sugerir primero las herramientas más relevantes de la
# Caja de Gatitos. Por ahora solo se guarda la preferencia.
OBJETIVOS = [
    {"clave": "autoestima", "icono": "🌻", "nombre": "Desarrollar mi autoestima"},
    {"clave": "ansiedad", "icono": "☁️", "nombre": "Manejar mi ansiedad"},
    {"clave": "estres", "icono": "⚡", "nombre": "Reducir el estrés o el agotamiento"},
    {"clave": "enojo", "icono": "🔥", "nombre": "Manejar el enojo y otras emociones"},
    {"clave": "relaciones", "icono": "🤝", "nombre": "Construir relaciones más sanas"},
    {"clave": "duelo", "icono": "💔", "nombre": "Superar una pérdida o ruptura"},
]

# A qué categoría de la Caja de Gatitos conviene apuntar primero según el
# objetivo elegido en "Configurar mi rutina" (personalización básica).
OBJETIVO_A_CATEGORIA = {
    "autoestima": "pensamientos",
    "ansiedad": "respiracion",
    "estres": "movimiento",
    "enojo": "respiracion",
    "relaciones": "conexion",
    "duelo": "creatividad",
}

FAQ = [
    ("¿Gora reemplaza a un psicólogo o terapeuta?",
     "No. Gora es una herramienta de autoayuda y acompañamiento emocional, no un servicio "
     "clínico ni un diagnóstico. Si necesitas ayuda profesional, un psicólogo o médico "
     "puede darte algo que esta app no puede: seguimiento real de tu caso."),
    ("¿Quién puede ver lo que escribo?",
     "Solo tú. Tu historial se identifica por un id anónimo de sesión, no por tu nombre "
     "real (a menos que tú lo escribas), y nunca se comparte con otros usuarios."),
    ("¿Cómo funciona la detección de emociones?",
     "Se combina un análisis del texto que escribes con, opcionalmente, un análisis de tu "
     "expresión facial en una foto. El gatito primero identifica una emoción general y "
     "luego te hace una o dos preguntas para llegar a algo más específico -- no es una "
     "lectura perfecta, es una estimación para ayudarte a poner en palabras lo que sientes."),
    ("¿Por qué a veces me pide tomar una foto?",
     "Es opcional. Si activas la cámara, el sistema mide señales faciales objetivas "
     "(apertura de ojos, boca, cejas) para afinar la estimación de emoción -- puedes usar "
     "la app perfectamente bien solo con texto."),
    ("¿Puedo borrar mi información?",
     "Sí, en cualquier momento. En la pestaña 'Mi ánimo' hay un botón para borrar todo tu "
     "historial de esta sesión de forma permanente."),
]

AVISO_PRIVACIDAD = """
**Qué guardamos:** los mensajes que escribes, la emoción estimada de cada uno, y (si usas
la cámara) mediciones geométricas de tu rostro -- nunca la foto en sí. También guardamos
tus preferencias de ajustes (nombre, tema, objetivo) si decides configurarlas.

**Cómo se identifica tu información:** por un id anónimo generado al azar, guardado en la
URL de tu navegador. No pedimos ni requerimos tu nombre real, correo o teléfono.

**Dónde vive:** en una base de datos en la nube (Render), protegida y separada por sesión
-- una sesión nunca puede ver ni borrar los datos de otra.

**Qué NO hacemos:** no vendemos ni compartimos tu información con terceros, no la usamos
para publicidad, y no la revisa una persona salvo que tú reportes un problema técnico o
nos escribas usando el formulario de retroalimentación.

**Tu control:** puedes borrar todo tu historial cuando quieras desde la pestaña "Mi ánimo".

**Excepción de seguridad:** si el sistema detecta señales de riesgo de crisis en un
mensaje, se registra que ocurrió (fecha y nivel), pero no el contenido específico de la
frase que lo activó.
"""

TERMINOS = """
**Qué es Gora:** una aplicación de autoayuda y acompañamiento emocional. No es un
servicio médico, psicológico ni de emergencias.

**Limitaciones:** la detección de emociones es una estimación automática y puede
equivocarse. Las herramientas de la "Caja de Gatitos" son técnicas generales de manejo
emocional, no un tratamiento personalizado.

**En caso de emergencia:** si tú o alguien más está en riesgo inmediato, contacta a los
servicios de emergencia de tu localidad (en México, el 911) o a una línea de crisis --
puedes encontrar una en el apartado "¿Necesitas ayuda ahora?" en la pantalla principal.
Gora no monitorea conversaciones en tiempo real ni puede enviar ayuda física.

**Uso bajo tu propio criterio:** las reflexiones y sugerencias del gatito son un apoyo
para pensar en voz alta, no una indicación profesional a seguir sin criterio propio.

**PIN de seguridad:** si activas un PIN, es una traba básica para que otra persona con
acceso a tu dispositivo no vea tu chat a simple vista -- no es una cuenta con contraseña
real, y no protege contra alguien que tenga el enlace directo a tu sesión.
"""