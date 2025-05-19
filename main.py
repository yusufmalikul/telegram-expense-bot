import os
import json
import requests
from fastapi import FastAPI, Request
from telegram import Update, Bot
from telegram.constants import ParseMode

TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

bot = Bot(token=TOKEN)
app = FastAPI()

@app.post("/")
async def telegram_webhook(req: Request):
    body = await req.json()
    update = Update.de_json(body, bot)

    if update.message and update.message.text:
        text = update.message.text
        chat_id = update.message.chat_id

        if text.startswith("/start"):
            await bot.send_message(chat_id=chat_id, text="Hello! I'm alive.")
            return {"ok": True}

        prompt = f"""Extract the expense from this message, dont convert the currency, default is IDR:
        "{text}"

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
            print("Gemini raw response:", result)

            parsed = result["candidates"][0]["content"]["parts"][0]["text"]
            parsed_clean = parsed.strip().strip('`')
            if parsed_clean.startswith("json"):
                parsed_clean = parsed_clean[4:].strip()

            expense = json.loads(parsed_clean)

            await bot.send_message(
                chat_id=chat_id,
                text=f"✅ Parsed:\nItem: {expense['item']}\nAmount: {expense['amount']} {expense['currency']}"
            )

        except Exception as e:
            print("Error:", e)
            await bot.send_message(
                chat_id=chat_id,
                text="❌ Couldn't understand that. Try something like: 'coffee $5'"
            )

    return {"ok": True}
