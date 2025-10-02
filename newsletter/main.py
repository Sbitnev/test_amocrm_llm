import datetime as dt
import logging
import os
import time

import dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone

from tg_bot_s import bot
from metrics import metrics
from logging_conf import setup_logs

dotenv.load_dotenv()

dev_chat_id = os.getenv("DEV_CHAT_ID")


def job():
    today = dt.datetime.now()

    if today.weekday() == 0:
        start_dt = today.replace(hour=0, minute=0, second=0) - dt.timedelta(days=7)
        end_dt = today.replace(hour=0, minute=0, second=0)
        digest = metrics.get_digest(start_dt, end_dt)

        for user_id in metrics.get_nl_tg_user_ids() + [dev_chat_id]:
            bot.send_digest_message(user_id, digest)

        day_diff = 3
    else:
        day_diff = 1

    start_dt = today.replace(hour=0, minute=0, second=0) - dt.timedelta(days=day_diff)
    end_dt = today.replace(hour=0, minute=0, second=0)
    digest = metrics.get_digest(start_dt, end_dt)

    for user_id in metrics.get_nl_tg_user_ids() + [dev_chat_id]:
        bot.send_digest_message(user_id, digest)


def main():
    # job()

    scheduler = BackgroundScheduler(timezone=timezone("Europe/Moscow"))
    scheduler.add_job(
        job,
        "cron",
        hour=9,
        minute=0,
        day_of_week="mon-fri",
    )
    scheduler.start()
    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == "__main__":
    # logging.basicConfig(level=logging.INFO)
    setup_logs("newsletter.log")
    logger = logging.getLogger(__name__)

    logger.info("Запуск приложения")
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Остановка приложения")
