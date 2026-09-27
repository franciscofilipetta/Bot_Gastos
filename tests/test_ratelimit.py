from bot_gastos import bot


def test_rate_limit():
    bot._recent.clear()
    assert not any(bot._rate_limited(1) for _ in range(bot._RATE_LIMIT))
    assert bot._rate_limited(1)
    assert not bot._rate_limited(2)  # otro usuario no se ve afectado
