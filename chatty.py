from telegram import ChatAction, Update
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater, CallbackContext
import logging
import markovify
import schedule
from os import environ, path
from random import randrange
import atexit

CHATTY_BOT_TOKEN = environ['CHATTY_BOT_TOKEN']
CHATTY_CHAT_ID = environ['CHATTY_CHAT_ID']

MODEL_NAME = "text_model.json"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

## HELPER FUNCTIONS ##

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
    output = f"The current size of the model is {path.getsize(MODEL_NAME)}"
    setup_schedule()
    return output

def check_chat(update: Update) -> bool:
    return str(update.message.chat_id) == str(CHATTY_CHAT_ID)

def train(message: str) -> None:
    schedule.run_pending()

    new_text = markovify.Text(f"{message}{'.' if not (message.endswith('.') or message.endswith('!') or message.endswith('?')) else ''}", well_formed = False, state_size=4)

    global text_model

    if text_model:
        text_model = markovify.combine([text_model, new_text], [1, 1.5])
    else:
        text_model = new_text

## FUNCTIONS CALLED BY DISPATCHER ##

def start(update: Update, context: CallbackContext) -> None:
    if check_chat(update):
        update.message.reply_text("Hello")

def train_and_reply(update: Update, context: CallbackContext) -> None:
    if check_chat(update):
        train(update.message.text)

        if randrange(0, 100) < 5:
            context.bot.send_chat_action(chat_id = update.effective_message.chat_id, action = ChatAction.TYPING)
            full_message = ""
                              
            for i in range(randrange(1, 5)):
                new_sentence = text_model.make_sentence(tries=100)
                if new_sentence:
                    full_message += f"{new_sentence} "

            update.message.reply_text(full_message)

def get_size(update: Update, context: CallbackContext) -> None:
    if check_chat(update):
        context.bot.send_chat_action(chat_id = update.effective_message.chat_id, action = ChatAction.TYPING)
        update.message.reply_text(generate_get_size_message())

if __name__ == "__main__":
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


