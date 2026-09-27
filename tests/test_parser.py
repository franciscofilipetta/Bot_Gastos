import pytest

from bot_gastos.parser import ParseError, parse_amount, parse_command


@pytest.mark.parametrize("text,cents", [
    ("12000", 1_200_000), ("12.000", 1_200_000), ("$1.500", 150_000),
    ("12.5", 1250), ("12.50", 1250), ("1.234.567", 123_456_700),
])
def test_parse_amount(text, cents):
    assert parse_amount(text) == cents


@pytest.mark.parametrize("bad", ["abc", "", "12,5x", "-5"])
def test_parse_amount_invalido(bad):
    with pytest.raises(ParseError):
        parse_amount(bad)


def test_comando_ejemplo():
    names, paid = parse_command("Fran, Leon, Octa, Anto | Fran 12000, Anto 3000")
    assert names == ["Fran", "Leon", "Octa", "Anto"]
    assert paid == {"Fran": 1_200_000, "Anto": 300_000}


def test_mayusculas_y_gastos_repetidos_se_suman():
    _, paid = parse_command("Fran, Leon | fran 100, FRAN 50")
    assert paid == {"Fran": 15_000}


def test_saltos_de_linea():
    names, paid = parse_command("Fran, Leon | Fran 100\nLeon 50")
    assert paid == {"Fran": 10_000, "Leon": 5_000}


@pytest.mark.parametrize("text", [
    "Fran, Leon Fran 100",
    " | Fran 100",
    "Fran, Leon | ",
    "Fran, fran | Fran 100",
    "Fran, Leon | Octa 100",
    "Fran, Leon | Fran",
    "Fran, Leon | Fran 0",
])
def test_comando_invalido(text):
    with pytest.raises(ParseError):
        parse_command(text)


def test_tope_de_participantes():
    names = ", ".join(f"P{i}" for i in range(31))
    with pytest.raises(ParseError):
        parse_command(f"{names} | P0 100")


def test_nombre_muy_largo():
    with pytest.raises(ParseError):
        parse_command(f"{'x' * 31}, B | B 100")


def test_monto_absurdo():
    with pytest.raises(ParseError):
        parse_command("A, B | A 99999999999999")
