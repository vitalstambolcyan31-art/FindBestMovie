import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def search_movie(description):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={requests.utils.quote(description)}&language=ru-RU"
    r = requests.get(url, timeout=10)
    data = r.json() if r.ok else {}
    if not data.get("results"):
        url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={requests.utils.quote(description)}&language=en-US"
        r = requests.get(url, timeout=10)
        data = r.json() if r.ok else {}
    results = data.get("results", [])
    if not results:
        return None
    movie = results[0]
    title = movie.get("title") or movie.get("original_title")
    overview = movie.get("overview", "Описание отсутствует.")
    poster_path = movie.get("poster_path")
    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
    return title, overview, poster_url

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Опиши фильм — я попробую найти его.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.message.text
    await update.message.chat.send_action(action="typing")
    res = search_movie(q)
    if not res:
        await update.message.reply_text("😕 Ничего не нашёл. Попробуй описать по-другому.")
        return
    title, overview, poster = res
    msg = f"🎬 *{title}*

{overview}"
    await update.message.reply_text(msg, parse_mode="Markdown")
    if poster:
        await update.message.reply_photo(poster)

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot started")
    app.run_polling()

if __name__ == "__main__":
    main()
