"""Logica pura de division de gastos. Todo se calcula en centavos enteros."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Payment:
    payer: str
    receiver: str
    cents: int


@dataclass(frozen=True)
class Result:
    total_cents: int
    paid: dict[str, int]      # centavos que puso cada uno
    share: dict[str, int]     # centavos que le corresponde a cada uno
    payments: list[Payment]   # transferencias para saldar


def split(participants: list[str], paid: dict[str, int]) -> Result:
    """Divide el total en partes iguales y calcula los pagos minimos.

    `participants` conserva el orden dado; `paid` puede omitir a quienes no pusieron nada.
    El resto de centavos (si el total no divide exacto) se reparte de a 1 centavo
    entre los primeros de la lista.
    """
    if not participants:
        raise ValueError("Debe haber al menos un participante.")
    unknown = set(paid) - set(participants)
    if unknown:
        raise ValueError(f"Gastadores fuera de la lista: {', '.join(sorted(unknown))}")

    all_paid = {p: paid.get(p, 0) for p in participants}
    total = sum(all_paid.values())
    base, remainder = divmod(total, len(participants))
    share = {p: base + (1 if i < remainder else 0) for i, p in enumerate(participants)}

    balance = {p: all_paid[p] - share[p] for p in participants}
    return Result(total, all_paid, share, _settle(participants, balance))


def _settle(order: list[str], balance: dict[str, int]) -> list[Payment]:
    """Empareja al mayor deudor con el mayor acreedor hasta saldar todo."""
    idx = {p: i for i, p in enumerate(order)}
    creditors = [[b, p] for p, b in balance.items() if b > 0]
    debtors = [[-b, p] for p, b in balance.items() if b < 0]

    def key(x):
        return (-x[0], idx[x[1]])

    payments: list[Payment] = []
    while creditors and debtors:
        creditors.sort(key=key)
        debtors.sort(key=key)
        c, d = creditors[0], debtors[0]
        amount = min(c[0], d[0])
        payments.append(Payment(d[1], c[1], amount))
        c[0] -= amount
        d[0] -= amount
        if c[0] == 0:
            creditors.pop(0)
        if d[0] == 0:
            debtors.pop(0)
    return payments
