from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters
import os
import json
import logging
import requests

# Set up FastAPI and logging
app = FastAPI()
logging.basicConfig(level=logging.INFO)

# Load tokens from environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Build Telegram app
telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()

# Command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm alive.")

# Message handler
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    prompt = f"""Extract the expense from this message, dont convert the currency, default is IDR:
    "{user_message}"

    Respond only with JSON like:
    {{
        "item": "<item>",
        "amount": <number>,
        "currency": "USD"
    }}"""

    headers = {"Content-Type": "application/json"}
    body = {"contents": [{"parts": [{"text": prompt}]}]}
    gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"

    try:
        response = requests.post(gemini_url, headers=headers, json=body)
        result = response.json()

        logging.info("Gemini response: %s", result)

        parsed = result["candidates"][0]["content"]["parts"][0]["text"]
        parsed_clean = parsed.strip().strip('`')
        if parsed_clean.startswith("json"):
            parsed_clean = parsed_clean[4:].strip()

        # Attempt to parse JSON
        try:
            expense = json.loads(parsed_clean)
        except json.JSONDecodeError:
            logging.warning("Gemini response was not valid JSON.")
            await update.message.reply_text(
                "🤖 I couldn't find an expense in that message. Try something like:\n\n`coffee $5`",
                parse_mode="Markdown"
            )
            return

        await update.message.reply_text(
            f"✅ Parsed:\nItem: {expense['item']}\nAmount: {expense['amount']} {expense['currency']}"
        )

    except Exception as e:
        logging.error("❌ Unexpected error in echo handler: %s", e, exc_info=True)
        await update.message.reply_text(
            "⚠️ Something went wrong. Try again in a moment."
        )


# Register handlers
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))


# webhook endpoint
@app.post("/")
async def webhook(req: Request):
    try:
        data = await req.json()
        logging.info("Incoming Telegram update: %s", data)

        update = Update.de_json(data, telegram_app.bot)

        if not telegram_app._initialized:
            await telegram_app.initialize()  # ✅ Manually initialize it

        await telegram_app.process_update(update)

    except Exception as e:
        logging.error("❌ Webhook processing error: %s", e, exc_info=True)
        return {"ok": False, "error": str(e)}

    return {"ok": True}
