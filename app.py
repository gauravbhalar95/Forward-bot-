import os
import telebot
from telebot.types import Update
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

# Fetch the BOT_TOKEN from environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')

if BOT_TOKEN is None:
    raise ValueError("Error: No BOT_TOKEN found in environment variables.")

bot = telebot.TeleBot(BOT_TOKEN)

# Global variables to store source and destination chat IDs
sources = set()
destinations = set()
forwarding_status = False

# Command to add a source channel
@bot.message_handler(commands=['addsource'])
def add_source(message):
    global sources
    try:
        chat_id = int(message.text.split()[1])
        sources.add(chat_id)
        bot.reply_to(message, f"Source {chat_id} added.")
    except (IndexError, ValueError):
        bot.reply_to(message, "Usage: /addsource <chat_id>")

# Command to add a destination channel
@bot.message_handler(commands=['adddestination'])
def add_destination(message):
    global destinations
    try:
        chat_id = int(message.text.split()[1])
        destinations.add(chat_id)
        bot.reply_to(message, f"Destination {chat_id} added.")
    except (IndexError, ValueError):
        bot.reply_to(message, "Usage: /adddestination <chat_id>")

# Command to remove a source channel
@bot.message_handler(commands=['removesource'])
def remove_source(message):
    global sources
    try:
        chat_id = int(message.text.split()[1])
        if chat_id in sources:
            sources.remove(chat_id)
            bot.reply_to(message, f"Source {chat_id} removed.")
        else:
            bot.reply_to(message, f"Source {chat_id} not found.")
    except (IndexError, ValueError):
        bot.reply_to(message, "Usage: /removesource <chat_id>")

# Command to remove a destination channel
@bot.message_handler(commands=['removedestination'])
def remove_destination(message):
    global destinations
    try:
        chat_id = int(message.text.split()[1])
        if chat_id in destinations:
            destinations.remove(chat_id)
            bot.reply_to(message, f"Destination {chat_id} removed.")
        else:
            bot.reply_to(message, f"Destination {chat_id} not found.")
    except (IndexError, ValueError):
        bot.reply_to(message, "Usage: /removedestination <chat_id>")

# Command to start forwarding messages
@bot.message_handler(commands=['startforward'])
def start_forward(message):
    global forwarding_status
    forwarding_status = True
    bot.reply_to(message, "Message forwarding started.")

# Command to stop forwarding messages
@bot.message_handler(commands=['stopforward'])
def stop_forward(message):
    global forwarding_status
    forwarding_status = False
    bot.reply_to(message, "Message forwarding stopped.")

# Command to check the status
@bot.message_handler(commands=['status'])
def check_status(message):
    status_message = f"Forwarding Status: {'ON' if forwarding_status else 'OFF'}\n"
    status_message += f"Sources: {', '.join(map(str, sources)) if sources else 'None'}\n"
    status_message += f"Destinations: {', '.join(map(str, destinations)) if destinations else 'None'}"
    bot.reply_to(message, status_message)

# Forward messages from source to destination
@bot.message_handler(func=lambda message: forwarding_status and message.chat.id in sources)
def forward_message(message):
    for destination in destinations:
        bot.forward_message(destination, message.chat.id, message.message_id)

# Command to stop the bot
@bot.message_handler(commands=['stop'])
def stop_bot(message):
    bot.reply_to(message, "Bot is stopping...")
    exit()

# Start polling
bot.polling(none_stop=True)
