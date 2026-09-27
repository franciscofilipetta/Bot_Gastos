from bot_gastos.formatting import format_result, money
from bot_gastos.splitter import split


def test_money():
    assert money(1_200_000) == "$12.000"
    assert money(375_050) == "$3.750,50"
    assert money(0) == "$0"


def test_format_ejemplo():
    r = split(["Fran", "Leon", "Octa", "Anto"], {"Fran": 1_200_000, "Anto": 300_000})
    out = format_result(r)
    assert "💰 Total: $15.000 · 👥 4 personas" in out
    assert "🍰 Le toca a cada uno: $3.750" in out
    assert "• Fran: $12.000 (+$8.250)" in out
    assert "• Anto: $3.000 (-$750)" in out
    assert "👉 Leon le paga $3.750 a Fran" in out
    assert "👉 Anto le paga $750 a Fran" in out
    # Quien puso de mas aparece primero.
    assert out.index("• Fran") < out.index("• Anto") < out.index("• Leon")


def test_format_a_mano():
    out = format_result(split(["A", "B"], {"A": 1000, "B": 1000}))
    assert "a mano" in out
    assert "Para saldar" not in out


def test_format_resto_muestra_aproximado():
    out = format_result(split(["A", "B", "C"], {"A": 10_000}))
    assert "Le toca a cada uno: ~$33,33" in out
