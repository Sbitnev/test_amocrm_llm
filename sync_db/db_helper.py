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

