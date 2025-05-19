import os
import json
import requests
from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, ContextTypes

from telegram.ext import CommandHandler, MessageHandler, filters

app = FastAPI()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

telegram_app = Application.builder().token(TELEGRAM_TOKEN).build()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm alive.")


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

        parsed = result["candidates"][0]["content"]["parts"][0]["text"]
        parsed_clean = parsed.strip().strip('`')
        if parsed_clean.startswith("json"):
            parsed_clean = parsed_clean[4:].strip()

        expense = json.loads(parsed_clean)

        await update.message.reply_text(
            f"✅ Parsed:\nItem: {expense['item']}\nAmount: {expense['amount']} {expense['currency']}"
        )

    except Exception as e:
        print("Error:", e)
        await update.message.reply_text(
            "❌ Couldn't understand that. Try something like: 'coffee $5'"
        )


telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))


@app.post("/")
async def webhook(req: Request):
    data = await req.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"ok": True}
