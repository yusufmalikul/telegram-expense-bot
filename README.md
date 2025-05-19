# Telegram Expense Bot

A Telegram bot that helps you track expenses by automatically parsing expense messages using Google's Gemini AI. The bot extracts expense details from natural language messages and formats them into a structured format.

## Features

- 🤖 Telegram bot integration
- 💰 Automatic expense parsing from natural language
- 🧠 Powered by Google's Gemini AI
- 🌐 FastAPI backend
- 🚀 Deployable on Vercel

## How It Works

1. Send a message to the bot with your expense (e.g., "coffee $5" or "lunch 150000 IDR")
2. The bot uses Gemini AI to parse the message and extract:
   - Item name
   - Amount
   - Currency
3. The bot responds with the parsed expense details in a structured format

## Prerequisites

- Python 3.7+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Google Gemini API Key

## Environment Variables

Create a `.env` file with the following variables:

```env
TELEGRAM_TOKEN=your_telegram_bot_token
GEMINI_API_KEY=your_gemini_api_key
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yusufmalikul/telegram-expense-bot
cd telegram-expense-bot
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running Locally

1. Start the FastAPI server:
```bash
uvicorn main:app --reload
```

2. Set up a webhook for your Telegram bot (you can use ngrok for local development):
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://your-vercel-webhook-domain.com/"
```

## Deployment

The project is configured for deployment on Vercel. The `vercel.json` file contains the necessary configuration.

## Usage

1. Start a chat with your bot on Telegram
2. Send `/start` to verify the bot is working
3. Send expense messages in natural language, for example:
   - "coffee $5"
   - "lunch 150000 IDR"
   - "groceries 75 USD"

## Dependencies

- python-telegram-bot==20.3
- fastapi
- uvicorn
- requests

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.