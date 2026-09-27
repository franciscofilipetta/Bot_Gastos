"""Formato del mensaje de respuesta."""
from .splitter import Result


def money(cents: int) -> str:
    """Formato es-AR: $12.000 o $3.750,50."""
    whole, frac = divmod(cents, 100)
    s = f"{whole:,}".replace(",", ".")
    return f"${s},{frac:02d}" if frac else f"${s}"


def _signed(cents: int) -> str:
    return f"+{money(cents)}" if cents > 0 else f"-{money(-cents)}" if cents < 0 else "a mano"


def format_result(result: Result) -> str:
    people = list(result.share)
    shares = set(result.share.values())
    share_txt = money(shares.pop()) if len(shares) == 1 else f"~{money(min(result.share.values()))}"

    # Primero quienes pusieron de mas, luego los que deben; el orden original desempata.
    balance = {p: result.paid[p] - result.share[p] for p in people}
    ordered = sorted(people, key=lambda p: -balance[p])

    lines = [
        "🧾 Cuentas claras",
        "",
        f"💰 Total: {money(result.total_cents)} · 👥 {len(people)} personas",
        f"🍰 Le toca a cada uno: {share_txt}",
        "",
        "📊 Quién puso qué",
    ]
    for p in ordered:
        lines.append(f"• {p}: {money(result.paid[p])} ({_signed(balance[p])})")
    lines.append("")

    if not result.payments:
        lines.append("✅ ¡Están todos a mano, nadie debe nada!")
    else:
        lines.append("💸 Para saldar")
        for pay in result.payments:
            lines.append(f"👉 {pay.payer} le paga {money(pay.cents)} a {pay.receiver}")
        lines.append("")
        lines.append("✅ ¡Listo, cuentas saldadas!")
    return "\n".join(lines)
