from telegram import ChatAction, Update
from telegram.ext import CommandHandler, MessageHandler, Filters, Updater, CallbackContext
import logging
import markovify
import schedule
from os import environ
from random import randrange
import atexit

CHATTY_BOT_TOKEN = environ['CHATTY_BOT_TOKEN']
CHATTY_CHAT_ID = environ['CHATTY_CHAT_ID']

MODEL_NAME = "text_model.json"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

def save_model() -> None:
    if text_model:
        with open(MODEL_NAME, "w") as f:
            f.write(text_model.to_json())

def load_model() -> markovify.Text:
    with open(MODEL_NAME, "r") as f:
        return markovify.Text.from_json(f.read())

def train(message: str) -> None:
    schedule.run_pending()

    new_text = markovify.Text(f"{message}{'.' if not (message.endswith('.') or message.endswith('!') or message.endswith('?')) else ''}", well_formed = False, state_size=4)

    global text_model

    if text_model:
        text_model = markovify.combine([text_model, new_text], [1, 1.5])
    else:
        text_model = new_text
    
def train_and_reply(update: Update, context: CallbackContext) -> None:
    if str(update.message.chat_id) == str(CHATTY_CHAT_ID):
        train(update.message.text)

        # TODO: make this conditional less sloppy
        if randrange(0, 100) < 5:
            context.bot.send_chat_action(chat_id = update.effective_message.chat_id, action = ChatAction.TYPING)
            full_message = ""
                              
            for i in range(randrange(1, 5)):
                new_sentence = text_model.make_sentence(tries=100)
                if new_sentence:
                    full_message += f"{new_sentence} "

            update.message.reply_text(full_message)
    
def start(update: Update, context: CallbackContext) -> None:
    if str(update.message.chat_id) == str(CHATTY_CHAT_ID):
        update.message.reply_text("Hello")



if __name__ == "__main__":
    try:
        text_model = load_model()
    except:
        text_model = None
    
    schedule.every(5).minutes.do(save_model)

    atexit.register(save_model)

    updater = Updater(CHATTY_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    train_and_reply_handler = MessageHandler(Filters.text & (~Filters.command), train_and_reply)
    dispatcher.add_handler(train_and_reply_handler)
    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)

    updater.start_polling()
    updater.idle()


