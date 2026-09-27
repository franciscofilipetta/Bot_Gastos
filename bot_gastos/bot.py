"""Bot de Telegram para dividir gastos. Sin estado, sin base de datos. Solo chat privado.

Corre en dos modos, sin ninguna configuracion manual:
- Polling (local, para desarrollo): si no hay una URL publica configurada.
- Webhook (deploy en Render u otro hosting): si RENDER_EXTERNAL_URL o WEBHOOK_URL
  estan definidas. Render las provee sola; en otro hosting hay que setear WEBHOOK_URL.
"""
import hashlib
import logging
import os
import time
from collections import defaultdict, deque

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from .conversation import reply_for

log = logging.getLogger("bot_gastos")

_RATE_LIMIT = 10      # mensajes
_RATE_WINDOW = 60.0   # por ventana de segundos
_recent: dict[int, deque[float]] = defaultdict(deque)


def _allowed_ids() -> set[int]:
    raw = os.getenv("ALLOWED_USER_IDS", "")
    return {int(x) for x in raw.replace(" ", "").split(",") if x}


def _authorized(update: Update) -> bool:
    allowed = _allowed_ids()
    user = update.effective_user
    return not allowed or (user is not None and user.id in allowed)


def _rate_limited(user_id: int) -> bool:
    """Ventana deslizante en memoria por usuario."""
    now = time.monotonic()
    q = _recent[user_id]
    while q and now - q[0] > _RATE_WINDOW:
        q.popleft()
    if not q:
        _recent.pop(user_id, None)
        q = _recent[user_id]
    if len(q) >= _RATE_LIMIT:
        return True
    q.append(now)
    return False


async def _answer(update: Update, text: str) -> None:
    if not _authorized(update):
        await update.message.reply_text("No tenés permiso para usar este bot.")
        return
    if _rate_limited(update.effective_user.id):
        await update.message.reply_text("⏳ Demasiados mensajes seguidos, probá de nuevo en un minuto.")
        return
    for msg in reply_for(text):
        await update.message.reply_text(msg)


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cualquier mensaje de texto en privado: saludo o datos de gastos."""
    await _answer(update, update.message.text or "")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await _answer(update, "hola")


async def dividir(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Compatibilidad: /dividir <datos>. Sin datos, muestra el formato."""
    pieces = (update.message.text or "").split(None, 1)
    await _answer(update, pieces[1] if len(pieces) > 1 else "hola")


async def show_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Sin restriccion: hace falta para poder configurar la lista de permitidos.
    await update.message.reply_text(f"Tu ID de Telegram es: {update.effective_user.id}")


def main() -> None:
    load_dotenv()
    logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO)
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token or token == "pegar_token_aqui":
        raise SystemExit("Falta TELEGRAM_BOT_TOKEN. Copia .env.example a .env y completalo.")
    if not _allowed_ids():
        log.warning("ALLOWED_USER_IDS vacio: cualquiera puede usar el bot.")

    private = filters.ChatType.PRIVATE
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler(["start", "ayuda", "help"], start, filters=private))
    app.add_handler(CommandHandler("id", show_id, filters=private))
    app.add_handler(CommandHandler("dividir", dividir, filters=private))
    app.add_handler(MessageHandler(private & filters.TEXT & ~filters.COMMAND, on_text))

    external_url = os.getenv("RENDER_EXTERNAL_URL") or os.getenv("WEBHOOK_URL")
    if external_url:
        # El token en la URL y un secret_token adicional evitan que otros manden
        # updates falsos a este endpoint.
        port = int(os.getenv("PORT", "10000"))
        secret_token = hashlib.sha256(token.encode()).hexdigest()
        webhook_url = f"{external_url.rstrip('/')}/{token}"
        log.info("Bot iniciado (webhook) en %s", webhook_url)
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=token,
            webhook_url=webhook_url,
            secret_token=secret_token,
            drop_pending_updates=True,
        )
    else:
        log.info("Bot iniciado (polling).")
        app.run_polling()


if __name__ == "__main__":
    main()
