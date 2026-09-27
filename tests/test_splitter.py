import pytest

from bot_gastos.splitter import Payment, split


def test_ejemplo_del_enunciado():
    r = split(["Fran", "Leon", "Octa", "Anto"], {"Fran": 1_200_000, "Anto": 300_000})
    assert r.total_cents == 1_500_000
    assert set(r.payments) == {
        Payment("Leon", "Fran", 375_000),
        Payment("Octa", "Fran", 375_000),
        Payment("Anto", "Fran", 75_000),
    }


def test_todos_a_mano():
    assert split(["A", "B"], {"A": 1000, "B": 1000}).payments == []


def test_nadie_gasto():
    assert split(["A", "B"], {}).payments == []


def test_un_solo_participante():
    assert split(["A"], {"A": 500}).payments == []


def test_resto_de_centavos_suma_exacto():
    r = split(["A", "B", "C"], {"A": 10_000})
    assert sum(r.share.values()) == 10_000
    assert sum(p.cents for p in r.payments) == r.paid["A"] - r.share["A"]


def test_pagos_conservan_saldos():
    parts = ["A", "B", "C", "D", "E"]
    r = split(parts, {"A": 5000, "B": 1234, "D": 999})
    net = {p: r.paid[p] - r.share[p] for p in parts}
    for pay in r.payments:
        net[pay.payer] += pay.cents
        net[pay.receiver] -= pay.cents
    assert all(v == 0 for v in net.values())
    assert len(r.payments) <= len(parts) - 1


def test_gastador_desconocido():
    with pytest.raises(ValueError):
        split(["A"], {"Z": 1})
