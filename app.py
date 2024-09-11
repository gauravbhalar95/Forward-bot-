import os
import telebot
from flask import Flask, request

# Fetch the BOT_TOKEN and APP_URL from environment variables
BOT_TOKEN = os.getenv('BOT_TOKEN')
APP_URL = os.getenv('APP_URL')  # Example: https://your-app.onrender.com

if BOT_TOKEN is None or APP_URL is None:
    raise ValueError("Error: BOT_TOKEN or APP_URL not found in environment variables.")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

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

# Webhook route to process incoming updates
@app.route('/' + BOT_TOKEN, methods=['POST'])
def receive_update():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '!', 200

# Index route to verify that the server is running
@app.route('/')
def index():
    return "Bot is running!"

if __name__ == "__main__":
    # Remove any existing webhooks
    bot.remove_webhook()
    
    # Set webhook with the provided app URL
    bot.set_webhook(url=APP_URL + BOT_TOKEN)
    
    # Run the Flask app to keep the bot running
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
