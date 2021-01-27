from telegram import ChatAction, Update
from telegram
from telegram import ChatAction, Update
from telegram.ext import MessageHandler, Filters, Updater, CallbackContext
import logging
import markovify
import schedule
from os import environ
from random import randrange

CHATTY_BOT_TOKEN = environ['CHATTY_BOT_TOKEN']
CHATTY_CHAT_ID = environ['CHATTY_CHAT_ID']

MODEL_NAME = "text_model.json"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

def save_model() -> None:
    with open(MODEL_NAME, "w") as f:
        f.write(markovify.Text(text_model).to_json())

def load_model() -> markovify.Text:
    with open(MODEL_NAME, "r") as f:
        return markovify.Text.from_json(f.read())

def train(message: String) -> None:
    schedule.run_pending()

    new_text = markovify.Text(message)

    if not text_model:
        global text_model = new_text
    else:
        global text_model = markovify.combine([text_model, new_text], [1, 1.025])

 
def reply(update: Update, context: CallbackContext) -> None:
    if str(update.message.chat_id) == str(CHATTY_CHAT_ID):
        context.bot.send_chat_action(chat_id = update.effective_message.chat, action = ChatAction.TYPING)
        train(context.message.text)

        full_message = ""
        for i in randrange(5):
            full_message += f"{text_model.make_sentence()} "

        update.message.reply_text(full_message)


if __name__ == "__main__":
    try:
        text_model = load_model()
    except:
        text_model = None
    
    schedule.every(10).minutes.do(save_model(text_model))

    updater = Updater(CHATTY_BOT_TOKEN, use_context=True)
    dispacher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.text), reply)

    updater.start_polling()
    updater.idle()