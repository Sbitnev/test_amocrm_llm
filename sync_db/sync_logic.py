import os
import sys

# Получаем абсолютный путь к текущему файлу
current_file_path = os.path.abspath(__file__)

# Получаем путь к родительской директории
parent_dir = os.path.dirname(os.path.dirname(current_file_path))

# Добавляем родительскую директорию в sys.path
sys.path.append(parent_dir)


from datetime import datetime
import time

from sync_db.amo_connector import get_objects
from sync_db.db_helper import get_date_last_sync, set_date_last_sync
from common.database import get_db
from common.models import Lead, Contact, Company, Pipeline, Status

def sync_all():

    sync_objects_Pipeline(Pipeline)
    sync_objects(Contact)
    sync_leads(Lead)
    sync_objects(Company)

def sync_objects_Pipeline(class_model, if_force_rewrite = False):
    start_time = time.time()
    db = next(get_db())
    last_date = get_date_last_sync(data_type=class_model.LABEL, db=db)
    last_run_timestamp = int(time.time())
    entries = get_objects(class_model.LABEL, last_date)
    count_new = 0
    count_updated = 0
    for entry in entries:
        entry_in_base = db.query(class_model).filter(class_model.id == entry['id']).first()
        if not entry_in_base:
            # Добавляем новый лид
            entry_in_base = class_model()
            entry_in_base.fill(entry)
            count_new += 1
        elif entry_in_base.need_update(entry, if_force_rewrite):
            entry_in_base.fill(entry)
            count_updated += 1
        else:
            continue
        db.add(entry_in_base)
        db.commit()
        entries_status = get_objects(LABEL=class_model.LABEL, params = {'pipeline_id': entry['id']})
        for entry_status in entries_status:
            entry_status_in_base = db.query(Status).filter(Status.id == entry_status['id'] and Status.pipeline_id == entry['id']).first()
            if not entry_status_in_base:
                # Добавляем новый лид
                entry_status_in_base = Status()
                entry_status_in_base.fill(entry_status)
                count_new += 1
            else:
                continue
            # elif entry_status_in_base.need_update(entry_status, if_force_rewrite):
            #     entry_status_in_base.fill(entry_status)
            #     count_updated += 1
            if entry_status_in_base.pipeline_id == 0:
                continue
            db.add(entry_status_in_base)
            db.commit()
    if count_new or count_updated:
        db.commit()
    stat = {}
    stat['new_' + class_model.LABEL] = count_new
    stat['updated_' + class_model.LABEL] = count_updated
    duration = time.time() - start_time
    set_date_last_sync(class_model.LABEL, last_run_timestamp, duration, stat, db)
    print(f'Sync for {class_model.LABEL} completed in {duration} seconds, stat {stat}')

def sync_objects(class_model, if_force_rewrite = False):
    start_time = time.time()
    db = next(get_db())
    last_date = get_date_last_sync(data_type=class_model.LABEL, db=db)
    last_run_timestamp = int(time.time())
    entries = get_objects(class_model.LABEL, last_date)
    count_new = 0
    count_updated = 0
    for entry in entries:
        entry_in_base = db.query(class_model).filter(class_model.id == entry['id']).first()
        if not entry_in_base:
            # Добавляем новый лид
            entry_in_base = class_model()
            entry_in_base.fill(entry)
            count_new += 1
        elif entry_in_base.need_update(entry, if_force_rewrite):
            entry_in_base.fill(entry)
            count_updated += 1
        else:
            continue
        db.add(entry_in_base)
    if count_new or count_updated:
        db.commit()
    stat = {}
    stat['new_' + class_model.LABEL] = count_new
    stat['updated_' + class_model.LABEL] = count_updated
    duration = time.time() - start_time
    set_date_last_sync(class_model.LABEL, last_run_timestamp, duration, stat, db)
    print(f'Sync for {class_model.LABEL} completed in {duration} seconds, stat {stat}')

def sync_leads(class_model, if_force_rewrite = False):
    start_time = time.time()
    db = next(get_db())
    last_date = get_date_last_sync(data_type=class_model.LABEL, db=db)
    last_run_timestamp = int(time.time())
    entries = []
    entries_sort = get_objects(class_model.LABEL, last_date)
    # entries_unsort = get_objects('unsorted', last_date)
    entries.extend(entries_sort)
    # entries.extend(entries_unsort)
    count_new = 0
    count_updated = 0
    for entry in entries:
        entry_in_base = db.query(class_model).filter(class_model.id == entry['id']).first()
        if not entry_in_base:
            # Добавляем новый лид
            entry_in_base = class_model()
            entry_in_base.fill(entry)
            count_new += 1
        elif entry_in_base.need_update(entry, if_force_rewrite):
            entry_in_base.fill(entry)
            count_updated += 1
        else:
            continue
        db.add(entry_in_base)
    if count_new or count_updated:
        db.commit()
    stat = {}
    stat['new_' + class_model.LABEL] = count_new
    stat['updated_' + class_model.LABEL] = count_updated
    duration = time.time() - start_time
    set_date_last_sync(class_model.LABEL, last_run_timestamp, duration, stat, db)
    print(f'Sync {class_model.LABEL} completed in {duration} seconds, stat {stat}')


