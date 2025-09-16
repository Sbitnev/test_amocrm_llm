from dotenv import load_dotenv
from tenacity import stop_after_attempt, wait_fixed, before_sleep_log, retry

from tg_bot.logging_conf import logger, logging

load_dotenv()

from common.init_db import init_db
from tg_bot.route import bot
from sync_db.helper_shediler import get_sheduler
from sync_db.sync_logic import sync_all

init_db()


@retry(
    #retry=retry_if_exception_type(ConnectionError),
    stop=stop_after_attempt(100),      # можно считать бесконечным
    wait=wait_fixed(10),                   # ждать 3 секунд между попытками
    before_sleep=before_sleep_log(logger, logging.WARNING)
)
def start_polling():
    logger.info("🔄 Запуск bot.polling()")
    bot.polling(skip_pending=True, non_stop=True)

def start_sheduler():
    scheduler = get_sheduler()
    scheduler.start()

if __name__ == '__main__':

    start_sheduler()
    start_polling()
    # sync_all()
    # bot.polling(skip_pending=True, non_stop=True)