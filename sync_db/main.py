import os
import sys
import time

# Получаем абсолютный путь к текущему файлу
current_file_path = os.path.abspath(__file__)

# Получаем путь к родительской директории
parent_dir = os.path.dirname(os.path.dirname(current_file_path))

# Добавляем родительскую директорию в sys.path
sys.path.append(parent_dir)

import logging
from sync_db.helper_shediler import test_job, get_scheduler
from common.logging_conf import setup_logs

def start_scheduler():
    scheduler = get_scheduler()
    scheduler.start()

if __name__ == "__main__":
    setup_logs("sync.log")
    logger = logging.getLogger(__name__)
    test_job()
    start_scheduler()
    while True:
        time.sleep(1)