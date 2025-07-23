import asyncio
from telegram import Bot

# Load your token and chat ID from your saved text file
with open("bot_credentials.txt", "r") as f:
    lines = f.read().splitlines()
    BOT_TOKEN = lines[0].strip()
    CHAT_ID = lines[1].strip()

async def send_telegram_message_async(message):
    bot = Bot(token=BOT_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=message)

def send_telegram_message(message):
    asyncio.run(send_telegram_message_async(message))

if __name__ == "__main__":
    send_telegram_message("🚨 Test message: Your Agentic AI Cyber Security Bot is working!")
