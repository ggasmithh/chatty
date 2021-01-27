from telegram import ChatAction, Update
from telegram
from telegram import ChatAction, Update
from telegram.ext import MessageHandler, Filters, Updater, CallbackContext
import logging
import markovify
import schedule
from os import environ

CHATTY_BOT_TOKEN = environ['CHATTY_BOT_TOKEN']
CHATTY_CHAT_ID = environ['CHATTY_CHAT_ID']

MODEL_NAME = "model.json"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

# TODO: needs type hinting
def save_model(corpus) -> None:
    with open(MODEL_NAME, "w") as f:
        f.write(markovify.Text(corpus).to_json())

def load_model() -> markovify.Text:
    with open(MODEL_NAME, "r") as f:
        return markovify.Text.from_json(f.read())

# TODO: needs type hinting
def train(message: String, corpus) -> None:
    schedule.run_pending()
    return 0

def reply(update: Update, context: CallbackContext) -> None:
    if str(update.message.chat_id) == str(CHATTY_CHAT_ID):
        context.bot.send_chat_action(chat_id = update.effective_message.chat, action=ChatAction.TYPING)





if __name__ == "__main__":
    corpus = None
    schedule.every(10).minutes.do(save_model(corpus))

    updater = Updater(CHATTY_BOT_TOKEN, use_context=True)
    dispacher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.text), train_and_reply)