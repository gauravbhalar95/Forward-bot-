import os
from telethon import TelegramClient, events
from flask import Flask

# Initialize Flask app (for HTTP service on Render)
app = Flask(__name__)

# Fetch API credentials from environment variables
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
BOT_TOKEN = os.getenv('BOT_TOKEN')

# Initialize Telegram bot client
bot = TelegramClient('bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Initialize configuration storage
source_dest_config = {
    'sources': set(),
    'destinations': set(),
    'active': False
}

@app.route('/')
def home():
    return 'Telegram Bot is running!'

@bot.on(events.NewMessage)
async def handler(event):
    if source_dest_config['active']:
        if event.chat_id in source_dest_config['sources']:
            for dest_chat_id in source_dest_config['destinations']:
                try:
                    # Forward message to all destination chat IDs
                    await bot.send_message(dest_chat_id, event.message)
                except Exception as e:
                    print(f"Error forwarding message: {e}")

@bot.on(events.NewMessage(pattern='/addsource'))
async def add_source(event):
    try:
        chat_id = event.message.text.split(maxsplit=1)[1]
        if chat_id.isdigit():
            source_dest_config['sources'].add(int(chat_id))
            await event.respond(f'Source chat ID {chat_id} added.')
        else:
            await event.respond('Invalid chat ID.')
    except Exception as e:
        await event.respond(f"Error: {e}")

@bot.on(events.NewMessage(pattern='/removesource'))
async def remove_source(event):
    try:
        chat_id = event.message.text.split(maxsplit=1)[1]
        if chat_id.isdigit():
            source_dest_config['sources'].discard(int(chat_id))
            await event.respond(f'Source chat ID {chat_id} removed.')
        else:
            await event.respond('Invalid chat ID.')
    except Exception as e:
        await event.respond(f"Error: {e}")

@bot.on(events.NewMessage(pattern='/adddestination'))
async def add_destination(event):
    try:
        chat_id = event.message.text.split(maxsplit=1)[1]
        if chat_id.isdigit():
            source_dest_config['destinations'].add(int(chat_id))
            await event.respond(f'Destination chat ID {chat_id} added.')
        else:
            await event.respond('Invalid chat ID.')
    except Exception as e:
        await event.respond(f"Error: {e}")

@bot.on(events.NewMessage(pattern='/removedestination'))
async def remove_destination(event):
    try:
        chat_id = event.message.text.split(maxsplit=1)[1]
        if chat_id.isdigit():
            source_dest_config['destinations'].discard(int(chat_id))
            await event.respond(f'Destination chat ID {chat_id} removed.')
        else:
            await event.respond('Invalid chat ID.')
    except Exception as e:
        await event.respond(f"Error: {e}")

@bot.on(events.NewMessage(pattern='/activate'))
async def activate(event):
    source_dest_config['active'] = True
    await event.respond('Message forwarding activated.')

@bot.on(events.NewMessage(pattern='/deactivate'))
async def deactivate(event):
    source_dest_config['active'] = False
    await event.respond('Message forwarding deactivated.')

if __name__ == '__main__':
    # Run the bot and Flask app
    bot.start()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
