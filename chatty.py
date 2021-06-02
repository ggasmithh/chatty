from telegram import ChatAction, Update
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater, CallbackContext
import logging
import markovify
import schedule
from os import environ, path
from random import randrange
import atexit
import humanfriendly

CHATTY_BOT_TOKEN = environ['CHATTY_BOT_TOKEN']
CHATTY_CHAT_ID = environ['CHATTY_CHAT_ID']

MODEL_NAME = "text_model.json"

# If anyone tries to circumvent these limits I'm moving it to an environment var
# This the maximum length of a telegram message. If someone sends more than one
# max length messages at a time, the bot will reject the input. This is to 
# circumvent attempts to poison the bot with things like movie scripts.
SAME_USER_CHAR_LIMIT = 4096

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

####################
# INTERNAL FUNCTIONS
####################

def save_model() -> None:
    if text_model:
        with open(MODEL_NAME, "w") as f:
            f.write(text_model.to_json())

def load_model() -> markovify.Text:
    with open(MODEL_NAME, "r") as f:
        return markovify.Text.from_json(f.read())

def setup_schedule() -> None:
    schedule.every(5).minutes.do(save_model)

def generate_get_size_message() -> str:
    schedule.run_all()
    schedule.clear()
    output = f"The current size of the model is {humanfriendly.format_size(path.getsize(MODEL_NAME), binary=True)}!"
    setup_schedule()
    return output

def check_chat_id(update: Update) -> bool:
    return str(update.message.chat_id) == str(CHATTY_CHAT_ID)

# TODO: add type hinting
def unban_user(user):
    banned_users.remove(user)
    return schedule.CancelJob

def is_spam(update: Update) -> bool:
    if update.message.from_user in banned_users:
        return True

    if update.message.from_user == messages_from_same_user['last_user']:
        messages_from_same_user['character_count'] += len(update.message.text)

        if messages_from_same_user['character_count'] > SAME_USER_CHAR_LIMIT:
            banned_users.append(messages_from_same_user['last_user'])
            schedule.every(randrange(30, 60)).minutes.do(unban_user, user=messages_from_same_user['last_user'])
            return True
    
    else:
        messages_from_same_user['last_user'] = update.message.from_user
        messages_from_same_user['character_count'] = 0
        return False

def train(message: str) -> None:
    schedule.run_pending()

    new_text = markovify.Text(f"{message}{'.' if not (message.endswith('.') or message.endswith('!') or message.endswith('?')) else ''}", well_formed = False, state_size=4)

    global text_model

    if text_model:
        text_model = markovify.combine([text_model, new_text], [1, 1.5])
    else:
        text_model = new_text

################################### 
# CHAT FUNCTIONS
###################################

def start(update: Update, context: CallbackContext) -> None:
    if check_chat_id(update):
        update.message.reply_text("Hello")

def train_and_reply(update: Update, context: CallbackContext) -> None:
    if check_chat_id(update) and not is_spam(update):
        train(update.message.text)

        direct_reply = False
        
        if update.message.reply_to_message != None:
            direct_reply = update.message.reply_to_message.from_user.id == context.bot.get_me().id

        if randrange(0, 100) < 5 or direct_reply:
            context.bot.send_chat_action(chat_id = update.effective_message.chat_id, action = ChatAction.TYPING)
            full_message = ""
                              
            for i in range(randrange(1, 5)):
                new_sentence = text_model.make_sentence(tries=100)
                if new_sentence:
                    full_message += f"{new_sentence} "
            
            if full_message:
                update.message.reply_text(full_message)

def get_size(update: Update, context: CallbackContext) -> None:
    if check_chat_id(update):
        context.bot.send_chat_action(chat_id = update.effective_message.chat_id, action = ChatAction.TYPING)
        update.message.reply_text(generate_get_size_message())

##############
# MAIN PROGRAM
##############
messages_from_same_user = {'last_user': None, 'character_count': 0}
banned_users = []

try:
    text_model = load_model()
except:
    text_model = None

setup_schedule()
atexit.register(save_model)

updater = Updater(CHATTY_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

train_and_reply_handler = MessageHandler(Filters.text & (~Filters.command), train_and_reply)
dispatcher.add_handler(train_and_reply_handler)

get_size_handler = CommandHandler('get_size', get_size)
dispatcher.add_handler(get_size_handler)

updater.start_polling()
updater.idle()
