import os
import sys

# Получаем абсолютный путь к текущему файлу
current_file_path = os.path.abspath(__file__)

# Получаем путь к родительской директории
parent_dir = os.path.dirname(os.path.dirname(current_file_path))

# Добавляем родительскую директорию в sys.path
sys.path.append(parent_dir)

import dotenv
from tenacity import retry, stop_after_attempt, wait_fixed

from telebot import TeleBot, util

from tg_bot.agent_api_llm import Bot_LLM
from tg_bot.logging_conf import logger

dotenv.load_dotenv()

API_TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = TeleBot(API_TOKEN)

llm_bot = Bot_LLM(
    bot=bot,
    logger=logger,
)
llm_bot.run()


@retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
def send_message(chat_id, text, id_topic=None, reply_markup=None):
    if not text:
        return
    parts = util.smart_split(text, chars_per_string=4096)
    for part in parts:
        bot.send_message(
            chat_id=chat_id,
            text=part,
            message_thread_id=id_topic,
            reply_markup=reply_markup,
            parse_mode="HTML",
        )


@retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
def send_attache(chat_id, file, id_topic=None):
    if not file:
        return
    with open(file, "rb") as fileraw:
        if file.split(".")[-1] in ("png", "jpg", "jpeg"):
            bot.send_photo(chat_id, fileraw)
        else:
            bot.send_document(
                chat_id=chat_id, document=fileraw, message_thread_id=id_topic
            )


@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.reply_to(message, "Добро пожаловать обратно! Чем я могу вам помочь?")


@bot.message_handler(
    func=lambda message: message.text
    not in ["Сбросить диалог", "Выключить дебаг", "Включить дебаг"]
)
def handle_message(message):
    send_message(message.chat.id, "Обрабатываю запрос...")
    list_messages = llm_bot.steam(
        message_tg=message, user_tg_id=message.from_user.id, is_debug=True
    )
