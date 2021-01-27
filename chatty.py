from telegram import ChatAction, Update
from telegram
from telegram import ChatAction, Update
from telegram.ext import CommandHandler, Updater, CallbackContext
import logging
import markovify
import schedule

MODEL_NAME = "model.json"

def save_model(corpus) -> None:
    with open(MODEL_NAME, "w") as f:
        f.write(markovify.Text(corpus).to_json())

def load_model() -> markovify.Text:
    with open(MODEL_NAME, "r") as f:
        return markovify.Text.from_json(f.read())
    

if __name__ == "__main__":
    corpus = None
    schedule.every(10).minutes.do(save_model(corpus))
    
    # this will be invoked when a new text is added to the corpus
    #schedule.run_pending() 