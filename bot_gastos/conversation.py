"""Logica de conversacion pura: dado un texto, decide que mensajes responder."""
from .formatting import format_result
from .parser import parse_natural
from .splitter import split

GREETING = "¡Hola! 👋 ¿Querés dividir gastos?"

FORMAT_HELP = (
    "Mandame los nombres separados por coma, un punto, y después lo que gastó cada uno:\n\n"
    "Ejemplo:\n"
    "Fran, Pepe, Juan. Fran 12000, Juan 3000\n\n"
    "Los que no gastaron nada no hace falta que los pongas en los gastos. "
    "Podés usar montos como 12000, 12.000 o 12.50."
)


def reply_for(text: str) -> list[str]:
    """Devuelve la lista de mensajes a enviar.

    Un texto sin numeros se toma como saludo (o cualquier charla) y se responde con la
    invitacion a dividir gastos; uno con numeros se interpreta como los datos.
    """
    if not any(c.isdigit() for c in text):
        return [GREETING, FORMAT_HELP]
    try:
        participants, paid = parse_natural(text)
        return [format_result(split(participants, paid))]
    except ValueError as e:  # ParseError hereda de ValueError
        return [f"⚠️ {e}", FORMAT_HELP]
