# main.py — Asosiy kirish nuqtasi
# Render da "python main.py" buyrug'i bilan ishga tushadi
import logging
import threading

from flask import Flask
from bot import on_new_video, run_bot
from monitor import start_monitor

# ── Logging ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# ── Flask (keep-alive uchun) ──
app = Flask(__name__)

@app.route("/")
def health():
    return "✅ Bot ishlayapti!", 200

@app.route("/ping")
def ping():
    return "pong", 200


if __name__ == "__main__":
    import os

    logger.info("=== Bot va monitor ishga tushmoqda ===")

    # 1. YouTube monitorni background threadda ishga tushir
    start_monitor(on_new_video)

    # 2. Telegram bot polling ni alohida threadda ishga tushir
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()

    # 3. Flask serverni ishga tushir (Render PORT ni talab qiladi)
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Flask server port {port} da ishga tushmoqda...")
    app.run(host="0.0.0.0", port=port)
