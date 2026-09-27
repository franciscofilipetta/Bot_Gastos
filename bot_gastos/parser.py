"""Parser del comando: `Fran, Leon, Octa, Anto | Fran 12000, Anto 3000`."""
import re


class ParseError(ValueError):
    """Error de formato con mensaje apto para mostrar al usuario."""


MAX_PARTICIPANTS = 30
MAX_NAME_LEN = 30
MAX_CENTS = 10**12  # tope razonable para evitar montos absurdos

_THOUSANDS =re.compile(r"^\d{1,3}(?:\.\d{3})+$")
_DECIMAL = re.compile(r"^(\d+)(?:\.(\d{1,2}))?$")


def parse_amount(text: str) -> int:
    """Convierte '12000', '12.000', '$1.500' o '12.50' a centavos.

    Un punto seguido de exactamente 3 digitos se interpreta como separador de miles.
    """
    t = text.strip().lstrip("$").strip()
    if _THOUSANDS.match(t):
        return int(t.replace(".", "")) * 100
    m = _DECIMAL.match(t)
    if not m:
        raise ParseError(f"Monto invalido: '{text.strip()}'")
    return int(m.group(1)) * 100 + int((m.group(2) or "").ljust(2, "0"))


_NATURAL_SPLIT = re.compile(r"\.\s+|\n+")
_LIST_SEP = re.compile(r"[,;\n]|\s+y\s+", re.IGNORECASE)


def parse_natural(text: str) -> tuple[list[str], dict[str, int]]:
    """Formato natural: 'Fran, Leon, Octa. Fran 12000, Anto 3000'.

    Los participantes y los gastos se separan con un punto (seguido de espacio) o un
    salto de linea. Tambien acepta el formato con '|'.
    """
    text = text.strip()
    if "|" in text:
        return parse_command(text)
    parts = _NATURAL_SPLIT.split(text.rstrip("."), maxsplit=1)
    if len(parts) != 2 or not parts[1].strip():
        raise ParseError("Falta separar los nombres de los gastos con un punto.")
    return parse_command(f"{parts[0]}|{parts[1]}")


def parse_command(text: str) -> tuple[list[str], dict[str, int]]:
    """Devuelve (participantes, gastos en centavos por persona)."""
    if "|" not in text:
        raise ParseError("Falta el separador '|' entre participantes y gastos.")
    left, right = text.split("|", 1)

    names = [n.strip() for n in _LIST_SEP.split(left) if n.strip()]
    if not names:
        raise ParseError("No indicaste participantes.")
    if len(names) > MAX_PARTICIPANTS:
        raise ParseError(f"Máximo {MAX_PARTICIPANTS} participantes.")
    canon: dict[str, str] = {}
    for n in names:
        if len(n) > MAX_NAME_LEN:
            raise ParseError(f"Nombre demasiado largo (máximo {MAX_NAME_LEN} caracteres).")
        key = n.casefold()
        if key in canon:
            raise ParseError(f"Nombre repetido: '{n}'")
        canon[key] = n

    entries = [e.strip() for e in _LIST_SEP.split(right) if e.strip()]
    if not entries:
        raise ParseError("No indicaste ningun gasto.")

    paid: dict[str, int] = {}
    for entry in entries:
        parts = entry.rsplit(None, 1)
        if len(parts) != 2:
            raise ParseError(f"Gasto invalido: '{entry}' (usa 'Nombre monto')")
        name, amount_text = parts[0].strip(), parts[1]
        key = name.casefold()
        if key not in canon:
            raise ParseError(f"'{name}' gasto pero no esta en la lista de participantes.")
        cents = parse_amount(amount_text)
        if cents <= 0:
            raise ParseError(f"El monto de '{name}' debe ser mayor a 0.")
        if cents > MAX_CENTS:
            raise ParseError(f"El monto de '{name}' es demasiado grande.")
        paid[canon[key]] = paid.get(canon[key], 0) + cents
    return names, paid
