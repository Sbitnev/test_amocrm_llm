import os
import sys

# Получаем абсолютный путь к текущему файлу
current_file_path = os.path.abspath(__file__)

# Получаем путь к родительской директории
parent_dir = os.path.dirname(os.path.dirname(current_file_path))

# Добавляем родительскую директорию в sys.path
sys.path.append(parent_dir)

import telebot
import dotenv

from tg_bot.route import bot

from tg_bot.logging_conf import logger, logging
from dotenv import load_dotenv
from tenacity import stop_after_attempt, wait_fixed, before_sleep_log, retry

load_dotenv()
@retry(
    #retry=retry_if_exception_type(ConnectionError),
    stop=stop_after_attempt(100),      # можно считать бесконечным
    wait=wait_fixed(10),                   # ждать 3 секунд между попытками
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def start_polling():
    logger.info("🔄 Запуск bot.polling()")
    bot.polling(skip_pending=True, non_stop=True)

if __name__ == "__main__":
    # bot.infinity_polling()
    start_polling()