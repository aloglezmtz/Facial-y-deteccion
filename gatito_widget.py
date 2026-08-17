"""
Generador del "gatito héroe" animado con profundidad.
Dibuja un gato en SVG puro y lo anima con CSS.
La forma de ojos/boca/extras cambia según la emoción,
y las animaciones reaccionan a la INTENSIDAD de la fusión.
"""

from emociones_config import COLOR_GATO

# Diccionario completo de formas faciales (¡No lo borres!)
EXPRESIONES = {
    "felicidad": {
        "ojos": '<path d="M 65,98 Q 75,86 85,98" stroke="#3a2e26" stroke-width="4" fill="none" stroke-linecap="round"/>'
                '<path d="M 115,98 Q 125,86 135,98" stroke="#3a2e26" stroke-width="4" fill="none" stroke-linecap="round"/>',
        "boca": '<path d="M 78,132 Q 100,155 122,132" stroke="#3a2e26" stroke-width="4" fill="none" stroke-linecap="round"/>',
        "extra": "",
    },
    "tristeza": {
        "ojos": '<ellipse cx="75" cy="100" rx="6" ry="9" fill="#3a2e26"/>'
                '<ellipse cx="125" cy="100" rx="6" ry="9" fill="#3a2e26"/>',
        "boca": '<path d="M 80,142 Q 100,124 120,142" stroke="#3a2e26" stroke-width="4" fill="none" stroke-linecap="round"/>',
        "extra": '<path d="M 70,112 Q 66,124 70,132 Q 76,124 70,112 Z" fill="#7FB3E8" class="lagrima"/>'
                 '<path d="M 130,112 Q 126,124 130,132 Q 136,124 130,112 Z" fill="#7FB3E8" class="lagrima"/>',
    },
    "enojo": {
        "ojos": '<circle cx="75" cy="102" r="6" fill="#3a2e26"/>'
                '<circle cx="125" cy="102" r="6" fill="#3a2e26"/>'
                '<line x1="60" y1="82" x2="86" y2="94" stroke="#3a2e26" stroke-width="4" stroke-linecap="round"/>'
                '<line x1="140" y1="82" x2="114" y2="94" stroke="#3a2e26" stroke-width="4" stroke-linecap="round"/>',
        "boca": '<path d="M 82,138 L 118,138" stroke="#3a2e26" stroke-width="4" stroke-linecap="round"/>',
        "extra": '<line x1="35" y1="70" x2="45" y2="80" stroke="#D9736A" stroke-width="3" stroke-linecap="round" class="vena"/>'
                 '<line x1="35" y1="80" x2="45" y2="70" stroke="#D9736A" stroke-width="3" stroke-linecap="round" class="vena"/>',
    },
    "miedo": {
        "ojos": '<circle cx="75" cy="100" r="11" fill="white" stroke="#3a2e26" stroke-width="3"/>'
                '<circle cx="125" cy="100" r="11" fill="white" stroke="#3a2e26" stroke-width="3"/>'
                '<circle cx="75" cy="100" r="4" fill="#3a2e26"/>'
                '<circle cx="125" cy="100" r="4" fill="#3a2e26"/>',
        "boca": '<ellipse cx="100" cy="140" rx="7" ry="10" fill="#3a2e26"/>',
        "extra": '<path d="M 145,90 Q 150,100 145,108 Q 140,100 145,90 Z" fill="#7FB3E8" class="sudor"/>',
    },
    "disgusto": {
        "ojos": '<path d="M 66,100 L 84,100" stroke="#3a2e26" stroke-width="4" stroke-linecap="round"/>'
                '<circle cx="125" cy="100" r="6" fill="#3a2e26"/>',
        "boca": '<path d="M 80,138 Q 90,130 100,138 Q 110,146 120,138" stroke="#3a2e26" stroke-width="4" fill="none" stroke-linecap="round"/>',
        "extra": "",
    },
    "sorpresa": {
        "ojos": '<circle cx="75" cy="100" r="10" fill="white" stroke="#3a2e26" stroke-width="3"/>'
                '<circle cx="125" cy="100" r="10" fill="white" stroke="#3a2e26" stroke-width="3"/>'
                '<circle cx="75" cy="100" r="4" fill="#3a2e26"/>'
                '<circle cx="125" cy="100" r="4" fill="#3a2e26"/>',
        "boca": '<ellipse cx="100" cy="140" rx="9" ry="13" fill="#3a2e26"/>',
        "extra": "",
    },
    "neutral": {
        "ojos": '<circle cx="75" cy="100" r="6" fill="#3a2e26"/>'
                '<circle cx="125" cy="100" r="6" fill="#3a2e26"/>',
        "boca": '<path d="M 85,138 L 115,138" stroke="#3a2e26" stroke-width="4" stroke-linecap="round"/>',
        "extra": "",
    },
}


def generar_gatito_html(emocion: str, confianza: float = 0.5, tamano: int = 220) -> str:
    """
    Devuelve un documento HTML autocontenido.
    confianza: float entre 0.0 y 1.0 (obtenido de vector_fusionado)
    """
    expresion = EXPRESIONES.get(emocion, EXPRESIONES["neutral"])
    color = COLOR_GATO.get(emocion, COLOR_GATO["neutral"])

    # --- CÁLCULO DINÁMICO DE INTENSIDAD (PROFUNDIDAD) ---
    if confianza > 0.75:      # Intensidad Alta
        vel_flotar = "1.0s"
        vel_cola = "0.6s"
        escala_extra = "scale(1.5)"
        shaking = "animation: temblar 0.3s infinite;" if emocion in ["enojo", "miedo"] else ""
    elif confianza > 0.45:    # Intensidad Media
        vel_flotar = "2.4s"
        vel_cola = "1.6s"
        escala_extra = "scale(1.0)"
        shaking = ""
    else:                     # Intensidad Baja
        vel_flotar = "4.0s"
        vel_cola = "3.0s"
        escala_extra = "scale(0.6)"
        shaking = ""

    return f"""
    <html>
    <head>
    <style>
        body {{ margin: 0; display: flex; justify-content: center; align-items: center; background: transparent; }}
        .gato-wrap {{ 
            animation: flotar {vel_flotar} ease-in-out infinite;
            {shaking}
        }}
        @keyframes flotar {{
            0%, 100% {{ transform: translateY(0px); }}
            50% {{ transform: translateY(-12px); }}
        }}
        @keyframes temblar {{
            0% {{ transform: translate(1px, 1px) rotate(0deg); }}
            10% {{ transform: translate(-1px, -1px) rotate(-1deg); }}
            20% {{ transform: translate(-2px, 0px) rotate(1deg); }}
            30% {{ transform: translate(1px, 2px) rotate(0deg); }}
            40% {{ transform: translate(-1px, 1px) rotate(1deg); }}
            50% {{ transform: translate(-2px, -1px) rotate(-1deg); }}
        }}
        .oreja-izq {{ transform-origin: 55px 60px; animation: mover_oreja 3s ease-in-out infinite; }}
        .oreja-der {{ transform-origin: 145px 60px; animation: mover_oreja 3s ease-in-out infinite reverse; }}
        @keyframes mover_oreja {{
            0%, 100% {{ transform: rotate(0deg); }}
            50% {{ transform: rotate(-6deg); }}
        }}
        .cola {{ transform-origin: 170px 170px; animation: mover_cola {vel_cola} ease-in-out infinite; }}
        @keyframes mover_cola {{
            0%, 100% {{ transform: rotate(0deg); }}
            50% {{ transform: rotate(12deg); }}
        }}
        .lagrima, .vena, .sudor {{ 
            transform-origin: center;
            transform: {escala_extra};
            transition: transform 0.5s ease;
        }}
    </style>
    </head>
    <body>
    <div class="gato-wrap">
        <svg width="{tamano}" height="{tamano}" viewBox="0 0 200 200">
            <path class="cola" d="M 165,170 Q 195,150 180,120" stroke="{color}" stroke-width="14" fill="none" stroke-linecap="round"/>
            <path class="oreja-izq" d="M 50,70 L 35,25 L 80,55 Z" fill="{color}"/>
            <path class="oreja-der" d="M 150,70 L 165,25 L 120,55 Z" fill="{color}"/>
            <path d="M 55,60 L 42,35 L 68,52 Z" fill="#FFE1D6"/>
            <path d="M 145,60 L 158,35 L 132,52 Z" fill="#FFE1D6"/>
            <circle cx="100" cy="110" r="70" fill="{color}"/>
            {expresion['ojos']}
            {expresion['boca']}
            <line x1="40" y1="118" x2="70" y2="115" stroke="#3a2e26" stroke-width="2" stroke-linecap="round"/>
            <line x1="40" y1="128" x2="70" y2="128" stroke="#3a2e26" stroke-width="2" stroke-linecap="round"/>
            <line x1="130" y1="115" x2="160" y2="118" stroke="#3a2e26" stroke-width="2" stroke-linecap="round"/>
            <line x1="130" y1="128" x2="160" y2="128" stroke="#3a2e26" stroke-width="2" stroke-linecap="round"/>
            {expresion['extra']}
        </svg>
    </div>
    </body>
    </html>
    """
