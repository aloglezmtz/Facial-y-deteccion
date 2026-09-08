"""
Contenido rotativo para la pantalla de Inicio: se elige de forma
determinista según el día del año, así que es el mismo todo el día y
cambia automáticamente al siguiente sin necesitar guardar nada en la BD.
"""

from datetime import date

AFIRMACIONES = [
    "Merezco tratarme con la misma paciencia que le doy a quienes quiero.",
    "No tengo que tenerlo todo resuelto hoy para estar bien.",
    "Mis emociones son información, no un defecto que corregir.",
    "Puedo pedir ayuda sin que eso signifique que fallé.",
    "Hoy hice lo que pude con lo que tenía -- y eso cuenta.",
    "Descansar también es una forma de cuidarme.",
    "No necesito ser productivo/a todo el tiempo para tener valor.",
    "Puedo sentirme mal un rato sin que eso defina todo mi día.",
    "Está bien avanzar despacio, mientras avance.",
    "Soy más de lo que pienso de mí mismo/a en mis peores momentos.",
    "Cada pequeño paso hacia sentirme mejor cuenta, aunque no se note todavía.",
    "Puedo poner límites sin sentirme culpable por hacerlo.",
    "No tengo que cargar todo sola/o -- pedir compañía es válido.",
    "Mi ritmo es el correcto para mí, no tiene que compararse con el de nadie más.",
    "Equivocarme no me hace menos capaz de intentarlo de nuevo.",
    "Puedo estar orgulloso/a de mí incluso en un día difícil.",
    "Mereces el mismo cuidado que le das a los demás.",
    "No pasa nada por no tener ganas hoy -- mañana puede ser distinto.",
    "Soy capaz de sostenerme, y también está bien apoyarme en otros.",
    "Cuidar de mí no es egoísmo, es necesario.",
]


def afirmacion_de_hoy() -> str:
    
    indice = date.today().timetuple().tm_yday % len(AFIRMACIONES)
    return AFIRMACIONES[indice]