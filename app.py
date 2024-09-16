import os
from telethon import TelegramClient, events
import json

# Load environment variables
api_id = os.getenv('API_ID')  # Get API ID from environment variable
api_hash = os.getenv('API_HASH')  # Get API Hash from environment variable
bot_token = os.getenv('BOT_TOKEN')  # Get Bot Token from environment variable

# File to store source and destination channel configurations
config_file = 'config.json'

# Create the client and connect
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# Load or initialize config
def load_config():
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'source': None, 'destination': None, 'active': False}

def save_config(config):
    with open(config_file, 'w') as f:
        json.dump(config, f)

config = load_config()

# Command to add source and destination channels
@client.on(events.NewMessage(pattern='/add'))
async def add_channel(event):
    if len(event.message.text.split()) < 3:
        await event.reply('Usage: /add <source_chat_id> <destination_chat_id>')
        return

    _, source, destination = event.message.text.split()
    config['source'] = int(source)
    config['destination'] = int(destination)
    save_config(config)
    await event.reply(f"Source and destination added:\nSource: {source}\nDestination: {destination}")

# Command to remove source and destination
@client.on(events.NewMessage(pattern='/remove'))
async def remove_channel(event):
    config['source'] = None
    config['destination'] = None
    save_config(config)
    await event.reply("Source and destination removed.")

# Command to check current configuration
@client.on(events.NewMessage(pattern='/config'))
async def check_config(event):
    status = "Active" if config['active'] else "Inactive"
    source = config['source'] or "Not Set"
    destination = config['destination'] or "Not Set"
    await event.reply(f"Configuration:\nSource: {source}\nDestination: {destination}\nStatus: {status}")

# Command to activate the bot
@client.on(events.NewMessage(pattern='/activate'))
async def activate_bot(event):
    if config['source'] and config['destination']:
        config['active'] = True
        save_config(config)
        await event.reply("Bot activated. Now forwarding messages.")
    else:
        await event.reply("Please set the source and destination before activating the bot using /add.")

# Command to deactivate the bot
@client.on(events.NewMessage(pattern='/deactivate'))
async def deactivate_bot(event):
    config['active'] = False
    save_config(config)
    await event.reply("Bot deactivated.")

# Forward any new message from source to destination if active
@client.on(events.NewMessage())
async def forward_messages(event):
    if config['active'] and event.chat_id == config['source']:
        await client.send_message(config['destination'], event.message)

print("Bot is running...")
client.run_until_disconnected()
