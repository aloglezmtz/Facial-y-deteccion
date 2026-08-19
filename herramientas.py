"""
Fase 4 (C) - Caja de Gatitos: catálogo de herramientas de bienestar.

17 herramientas breves, organizadas en 6 categorías. Son técnicas generales
de manejo emocional (respiración, movimiento suave, reencuadre de
pensamientos, conexión social, autocuidado y expresión creativa) -- no
son tratamiento clínico ni sustituyen ayuda profesional.

Estructura de cada herramienta:
    id          -> identificador único (string)
    categoria   -> clave de CATEGORIAS a la que pertenece
    titulo      -> nombre corto mostrado en la tarjeta/lista
    tipo        -> etiqueta breve del tipo de ejercicio
    duracion    -> duración aproximada, para que el usuario sepa qué esperar
    descripcion -> una línea, se muestra en la lista antes de abrir
    pasos       -> lista de instrucciones, en orden
    cierre      -> mensaje breve de cierre (opcional, puede ser "")
"""

CATEGORIAS = {
    "respiracion": {"icono": "🌬️", "nombre": "Respiración y calma"},
    "pensamientos": {"icono": "🧠", "nombre": "Pensamientos"},
    "movimiento": {"icono": "🏃", "nombre": "Movimiento"},
    "conexion": {"icono": "🤝", "nombre": "Conexión"},
    "autocuidado": {"icono": "🛁", "nombre": "Autocuidado"},
    "creatividad": {"icono": "🎨", "nombre": "Creatividad y expresión"},
}

HERRAMIENTAS = [
    # ---------------- 🌬️ Respiración y calma ----------------
    {
        "id": "resp_478",
        "categoria": "respiracion",
        "titulo": "Respiración 4-7-8",
        "tipo": "Respiración",
        "duracion": "2-3 min",
        "descripcion": "Un patrón de respiración simple para bajar la activación del cuerpo.",
        "pasos": [
            "Siéntate en una posición cómoda y deja caer los hombros.",
            "Inhala por la nariz contando hasta 4.",
            "Sostén el aire contando hasta 7.",
            "Exhala lento por la boca contando hasta 8.",
            "Repite el ciclo 4 veces, a tu propio ritmo.",
        ],
        "cierre": "Nota cómo se siente tu cuerpo ahora comparado con antes de empezar.",
    },
    {
        "id": "resp_cuadrada",
        "categoria": "respiracion",
        "titulo": "Respiración cuadrada",
        "tipo": "Respiración",
        "duracion": "2 min",
        "descripcion": "Cuatro tiempos iguales, como los lados de un cuadrado, para ordenar la respiración.",
        "pasos": [
            "Inhala contando hasta 4.",
            "Sostén el aire contando hasta 4.",
            "Exhala contando hasta 4.",
            "Sostén los pulmones vacíos contando hasta 4.",
            "Repite el ciclo 5 o 6 veces.",
        ],
        "cierre": "Puedes usar este patrón en cualquier momento del día, no solo en crisis.",
    },
    {
        "id": "anclaje_54321",
        "categoria": "respiracion",
        "titulo": "Anclaje 5-4-3-2-1",
        "tipo": "Grounding",
        "duracion": "3-4 min",
        "descripcion": "Usa tus sentidos para volver al presente cuando la mente va muy rápido.",
        "pasos": [
            "Nombra 5 cosas que puedas ver a tu alrededor.",
            "Nombra 4 cosas que puedas tocar (y tócalas si puedes).",
            "Nombra 3 cosas que puedas escuchar en este momento.",
            "Nombra 2 cosas que puedas oler.",
            "Nombra 1 cosa que puedas saborear, o algo que te guste el sabor.",
        ],
        "cierre": "Este ejercicio ayuda a bajar del 'piloto automático' de la ansiedad al aquí y ahora.",
    },

    # ---------------- 🧠 Pensamientos ----------------
    {
        "id": "registrar_pensamiento",
        "categoria": "pensamientos",
        "titulo": "Registrar el pensamiento",
        "tipo": "Ejercicio cognitivo",
        "duracion": "4-5 min",
        "descripcion": "Poner el pensamiento en palabras para verlo con un poco más de distancia.",
        "pasos": [
            "Escribe (aquí o en papel) el pensamiento que no te deja en paz, tal cual aparece.",
            "Pregúntate: ¿qué evidencia tengo de que esto es cierto?",
            "Pregúntate: ¿qué le diría a un amigo que pensara esto mismo?",
            "Escribe una versión un poco más amable o realista del pensamiento.",
        ],
        "cierre": "No se trata de forzar el optimismo, sino de dejar de creer todo lo que la mente dice sin revisarlo.",
    },
    {
        "id": "reencuadre_amable",
        "categoria": "pensamientos",
        "titulo": "Reencuadre amable",
        "tipo": "Ejercicio cognitivo",
        "duracion": "3 min",
        "descripcion": "Cambiar el tono con el que te hablas a ti mismo/a, sin negar lo que sientes.",
        "pasos": [
            "Identifica una frase dura que te estés diciendo ahora mismo.",
            "Imagina que un amigo cercano te dice exactamente eso sobre sí mismo.",
            "Piensa qué le responderías tú a esa persona.",
            "Dite a ti mismo/a esa misma respuesta, en voz alta o mentalmente.",
        ],
        "cierre": "Hablarte con la misma amabilidad que le darías a alguien más es una práctica, no algo automático.",
    },
    {
        "id": "esto_es_temporal",
        "categoria": "pensamientos",
        "titulo": "Esto es temporal",
        "tipo": "Ejercicio cognitivo",
        "duracion": "2 min",
        "descripcion": "Un recordatorio breve de que los estados emocionales intensos cambian con el tiempo.",
        "pasos": [
            "Nombra la emoción que sientes ahora mismo, sin juzgarla.",
            "Recuerda un momento pasado en el que sentiste algo igual de intenso y que, con el tiempo, cambió.",
            "Repite para ti: 'esto que siento ahora no es permanente, es una ola que va a pasar'.",
        ],
        "cierre": "",
    },

    # ---------------- 🏃 Movimiento ----------------
    {
        "id": "estiramiento_2min",
        "categoria": "movimiento",
        "titulo": "Estiramiento de 2 minutos",
        "tipo": "Movimiento",
        "duracion": "2 min",
        "descripcion": "Liberar tensión física acumulada, sobre todo en cuello y hombros.",
        "pasos": [
            "Ponte de pie o siéntate derecho/a.",
            "Sube los hombros hacia las orejas, sostén 3 segundos y suelta.",
            "Gira el cuello lentamente hacia un lado y luego hacia el otro.",
            "Estira los brazos hacia arriba y respira profundo dos veces.",
        ],
        "cierre": "El cuerpo y la mente están conectados: soltar tensión física también ayuda a la mente.",
    },
    {
        "id": "caminar_atencion_plena",
        "categoria": "movimiento",
        "titulo": "Caminar con atención plena",
        "tipo": "Movimiento",
        "duracion": "5 min",
        "descripcion": "Una caminata corta, prestando atención a las sensaciones en vez de a los pensamientos.",
        "pasos": [
            "Camina a un ritmo natural, dentro o fuera de casa.",
            "Nota cómo se siente cada pie al tocar el suelo.",
            "Si la mente se va a otro lugar, tráela de vuelta a la sensación de caminar, sin frustrarte.",
            "Continúa así por unos 5 minutos.",
        ],
        "cierre": "",
    },
    {
        "id": "sacudir_tension",
        "categoria": "movimiento",
        "titulo": "Sacudir la tensión",
        "tipo": "Movimiento",
        "duracion": "1-2 min",
        "descripcion": "Un movimiento rápido para soltar energía acumulada por estrés o enojo.",
        "pasos": [
            "Ponte de pie con espacio a tu alrededor.",
            "Sacude las manos y los brazos como si te quitaras agua de encima.",
            "Sacude también las piernas, una y luego la otra.",
            "Termina con una respiración profunda y los hombros relajados.",
        ],
        "cierre": "Muchos animales sacuden el cuerpo después de un susto -- es una forma natural de soltar tensión.",
    },

    # ---------------- 🤝 Conexión ----------------
    {
        "id": "mensaje_confianza",
        "categoria": "conexion",
        "titulo": "Mensaje a alguien de confianza",
        "tipo": "Social",
        "duracion": "3-5 min",
        "descripcion": "A veces basta con avisarle a alguien que no la estás pasando bien.",
        "pasos": [
            "Piensa en una persona con la que te sientas cómodo/a siendo honesto/a.",
            "No hace falta explicar todo: un simple '¿tienes un momento? no la estoy pasando muy bien' es suficiente.",
            "Envía el mensaje, o si no estás listo/a, guárdalo escrito para cuando sí lo estés.",
        ],
        "cierre": "Pedir compañía no es una molestia para las personas que te quieren.",
    },
    {
        "id": "escribir_sin_enviar",
        "categoria": "conexion",
        "titulo": "Escribir lo que sientes",
        "tipo": "Social",
        "duracion": "5 min",
        "descripcion": "Poner en palabras lo que pasa, aunque decidas no compartirlo todavía.",
        "pasos": [
            "Abre una nota o toma papel y lápiz.",
            "Escribe libremente lo que sientes, sin corregir ni organizar.",
            "Cuando termines, decide: ¿lo compartes con alguien, o lo guardas para ti por ahora?",
        ],
        "cierre": "Ambas opciones son válidas -- el ejercicio ya cumplió su función al ponerlo en palabras.",
    },
    {
        "id": "pedir_compania",
        "categoria": "conexion",
        "titulo": "Pedir un abrazo o compañía",
        "tipo": "Social",
        "duracion": "Variable",
        "descripcion": "El contacto humano y la presencia de otra persona regulan el sistema nervioso.",
        "pasos": [
            "Piensa en alguien cerca de ti (en persona o por llamada) con quien te sientas seguro/a.",
            "Pide directamente lo que necesitas: un abrazo, una llamada, o solo que te acompañen un rato.",
            "Si no hay nadie disponible ahora, anota a quién le pedirás esto en cuanto puedas.",
        ],
        "cierre": "",
    },

    # ---------------- 🛁 Autocuidado ----------------
    {
        "id": "vaso_agua_pausa",
        "categoria": "autocuidado",
        "titulo": "Vaso de agua y pausa",
        "tipo": "Autocuidado",
        "duracion": "1-2 min",
        "descripcion": "Una pausa mínima pero real, para interrumpir el piloto automático.",
        "pasos": [
            "Levántate y sirve un vaso de agua.",
            "Bébelo despacio, prestando atención a la temperatura y el sabor.",
            "Antes de volver a lo que hacías, respira profundo una vez.",
        ],
        "cierre": "",
    },
    {
        "id": "lavado_cara_consciente",
        "categoria": "autocuidado",
        "titulo": "Lavado de cara consciente",
        "tipo": "Autocuidado",
        "duracion": "2 min",
        "descripcion": "El agua fresca en la cara puede ayudar a bajar la intensidad de una emoción fuerte.",
        "pasos": [
            "Ve al baño y moja tu cara con agua fresca (no helada).",
            "Sécate con calma, sin apurarte.",
            "Mírate al espejo un momento y respira profundo dos veces.",
        ],
        "cierre": "",
    },
    {
        "id": "playlist_calma",
        "categoria": "autocuidado",
        "titulo": "Playlist de calma",
        "tipo": "Autocuidado",
        "duracion": "5-10 min",
        "descripcion": "Usar música elegida a propósito para acompañar cómo te sientes o para cambiar el ánimo.",
        "pasos": [
            "Elige 2 o 3 canciones que te den calma o te hagan sentir acompañado/a.",
            "Ponte cómodo/a y escúchalas sin hacer otra cosa al mismo tiempo, si puedes.",
            "Nota si tu ánimo cambió algo al terminar, sin exigirte que cambie del todo.",
        ],
        "cierre": "",
    },

    # ---------------- 🎨 Creatividad y expresión ----------------
    {
        "id": "dibujo_libre_emocion",
        "categoria": "creatividad",
        "titulo": "Dibujo libre de la emoción",
        "tipo": "Creativo",
        "duracion": "5-10 min",
        "descripcion": "Dar forma, color o trazo a lo que sientes, sin intentar que se vea 'bien'.",
        "pasos": [
            "Consigue papel y algo para dibujar (o usa una app de dibujo).",
            "Piensa en la emoción que tienes ahora y qué forma o color le pondrías.",
            "Dibuja libremente por unos minutos, sin buscar que sea una obra de arte.",
        ],
        "cierre": "El objetivo no es el resultado, es darle una salida a lo que sientes.",
    },
    {
        "id": "carta_futuro",
        "categoria": "creatividad",
        "titulo": "Carta a ti mismo/a del futuro",
        "tipo": "Creativo",
        "duracion": "5-8 min",
        "descripcion": "Escribirle a la versión de ti que ya salió de este momento difícil.",
        "pasos": [
            "Imagina a la versión de ti mismo/a dentro de unas semanas, cuando este momento ya haya pasado.",
            "Escríbele una carta corta contándole cómo te sientes hoy.",
            "Termina la carta con algo que te gustaría recordar o que esa versión de ti te diría.",
        ],
        "cierre": "Guarda la carta si quieres releerla más adelante.",
    },
]


def herramientas_por_categoria(clave_categoria):
    """Devuelve la lista de herramientas de una categoría, en el orden del catálogo."""
    return [h for h in HERRAMIENTAS if h["categoria"] == clave_categoria]


def obtener_herramienta(id_herramienta):
    """Devuelve una herramienta por su id, o None si no existe."""
    for h in HERRAMIENTAS:
        if h["id"] == id_herramienta:
            return h
    return None