from telegram import ChatAction, Update
from telegram
from telegram import ChatAction, Update
from telegram.ext import CommandHandler, Updater, CallbackContext
import logging
import markovify
import schedule

def save_model(corpus) -> None:
    with open("model.json", "w") as f:
        f.write(markovify.Text(corpus).to_json())

if __name__ == "__main__":
    corpus = None
    schedule.every(10).minutes.do(save_model(corpus))