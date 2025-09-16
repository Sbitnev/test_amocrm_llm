import os
import sys

# Получаем абсолютный путь к текущему файлу
current_file_path = os.path.abspath(__file__)

# Получаем путь к родительской директории
parent_dir = os.path.dirname(os.path.dirname(current_file_path))

# Добавляем родительскую директорию в sys.path
sys.path.append(parent_dir)


from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from sync_db.sync_logic import sync_all


def get_sheduler():
    scheduler = BackgroundScheduler(timezone="Europe/Moscow")

    scheduler.add_job(
        test_job, trigger='interval', minutes=15, id='sync_all_job_id', replace_existing=True
    )

    return scheduler


def test_job():
    sync_all()
