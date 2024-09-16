import os
from telethon import TelegramClient, events
from flask import Flask

# Set up Flask app (required for Render deployment)
app = Flask(__name__)

# Fetch API credentials from environment variables
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Initialize Telegram bot client
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Route to confirm the bot is running (optional, for HTTP service)
@app.route('/')
def home():
    return 'Telegram Bot is running!'

# Example forwarder logic (adjust according to your needs)
SOURCE_CHAT_ID = int(os.getenv('SOURCE_CHAT_ID'))  # Source chat ID (to forward from)
DESTINATION_CHAT_ID = int(os.getenv('DESTINATION_CHAT_ID'))  # Destination chat ID (to forward to)

# Set up event handler to listen for new messages in the source chat
@bot.on(events.NewMessage(chats=SOURCE_CHAT_ID))
async def handler(event):
    # Forward message to destination chat
    await bot.send_message(DESTINATION_CHAT_ID, event.message)

# Run Flask app and Telegram client
if __name__ == '__main__':
    # Start the bot in the background
    bot.start()

    # Flask will listen on the dynamic port provided by Render
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
