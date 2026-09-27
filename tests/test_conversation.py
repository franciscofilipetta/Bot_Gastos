import pytest

from bot_gastos.conversation import FORMAT_HELP, GREETING, reply_for
from bot_gastos.parser import parse_natural


@pytest.mark.parametrize("text", ["hola", "Hola bot", "buenas", "como va", "che", "👋"])
def test_saludos(text):
    assert reply_for(text) == [GREETING, FORMAT_HELP]


def test_formato_natural():
    out = reply_for("Fran, Leon, Octa, Anto. Fran 12000, Anto 3000")
    assert len(out) == 1
    assert "👉 Leon le paga $3.750 a Fran" in out[0]
    assert "👉 Anto le paga $750 a Fran" in out[0]


def test_error_muestra_formato():
    out = reply_for("Fran, Leon. Octa 100")
    assert out[0].startswith("⚠️") and out[1] == FORMAT_HELP


def test_sin_punto():
    out = reply_for("Fran, Leon Fran 100")
    assert out[0].startswith("⚠️")


@pytest.mark.parametrize("text", [
    "Fran, Leon, Octa, Anto. Fran 12000, Anto 3000",
    "Fran, Leon, Octa, Anto. Fran 12000, Anto 3000.",
    "Fran, Leon, Octa y Anto. Fran 12000 y Anto 3000",
    "fran, leon, octa, anto\nfran 12.000\nanto 3.000",
    "Fran, Leon, Octa, Anto | Fran 12000, Anto 3000",
])
def test_variantes_equivalentes(text):
    names, paid = parse_natural(text)
    assert names == ["fran", "leon", "octa", "anto"] or names == ["Fran", "Leon", "Octa", "Anto"]
    assert sorted(paid.values()) == [300_000, 1_200_000]


def test_monto_decimal_con_punto_no_rompe_separador():
    _, paid = parse_natural("A, B. A 12.50")
    assert paid == {"A": 1250}
