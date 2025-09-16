import os
import sys

# Получаем абсолютный путь к текущему файлу
current_file_path = os.path.abspath(__file__)

# Получаем путь к родительской директории
parent_dir = os.path.dirname(os.path.dirname(current_file_path))

# Добавляем родительскую директорию в sys.path
sys.path.append(parent_dir)


from typing import Dict
from sqlalchemy import desc

from common.database import get_db
from common.models import Lead, Contact, Company, Pipeline, DataSyncState


def get_date_last_sync(data_type, db=None):
    if db is None:
        db = next(get_db())
    sync_state = db.query(DataSyncState).filter(DataSyncState.data_type == data_type).order_by(desc(DataSyncState.id)).first()
    if not sync_state:
        last_run_timestamp = 0  # Все данные
    else:
        last_run_timestamp = sync_state.last_updated_timestamp
    return last_run_timestamp

def set_date_last_sync(data_type, last_updated_timestamp: int, duration: float, stat: Dict = None, db=None):
    if db is None:
        db = next(get_db())
    row_sync = DataSyncState(
        data_type=data_type,
        last_updated_timestamp=last_updated_timestamp,
        update_log=str(stat),
        execution_duration_seconds=duration
    )
    db.add(row_sync)
    db.commit()

# def get_user(telegram_id, db=None):
#     if db is None:
#         db = next(get_db())
#     return db.query(User_TG).filter(User_TG.telegram_id == telegram_id).first()
#
#
# def get_user_on_topic_id(id_topic, db=None):
#     if db is None:
#         db = next(get_db())
#     return db.query(User_TG).filter(User_TG.id_topic == id_topic).first()
#
#
# def add_thread(user, db):
#     # db = next(get_db())
#     thread = User_Thread(user_id=user.id)
#     db.add(thread)
#     db.commit()
#     return thread
#
#
# def create_user(tg_user, db):
#     # db = next(get_db())
#     user = User_TG(
#         telegram_id=tg_user.id,
#         first_name=tg_user.first_name,
#         last_name=tg_user.last_name,
#         username=tg_user.username,
#     )
#     db.add(user)
#     db.commit()
#     thread = User_Thread(user_id=user.id)
#     db.add(thread)
#     db.commit()
#     user.thread_id = thread.id
#     db.commit()
#     return user
#
#
# def refresh_thread(telegram_id, db):
#     # db = next(get_db())
#     user = get_user(telegram_id, db)
#     thread = User_Thread(user_id=user.id)
#     db.add(thread)
#     db.commit()
#
#     old_id = user.thread_id
#     user.thread_id = thread.id
#     db.add(user)
#     db.commit()
#     return old_id, thread.id
#
#
# def change_debug(telegram_id, db, is_debug):
#     # db = next(get_db())
#     user = get_user(telegram_id, db)
#     user.is_debug = is_debug
#     db.add(user)
#     db.commit()


