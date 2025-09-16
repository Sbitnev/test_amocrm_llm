import os
import sys

# Получаем абсолютный путь к текущему файлу
current_file_path = os.path.abspath(__file__)

# Получаем путь к родительской директории
parent_dir = os.path.dirname(os.path.dirname(current_file_path))

# Добавляем родительскую директорию в sys.path
sys.path.append(parent_dir)

from tg_bot.settings import ROOT_DIR


def get_personalization(user_tg_id):
    path = os.path.join(ROOT_DIR, f"personalization/{user_tg_id}.txt")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        return text
    else:
        return None

def get_mtime_personalization(path):
    if os.path.exists(path):
        mtime = os.path.getmtime(path)
        return mtime
    else:
        return None


def set_personalization(text, user_tg_id):
    path = os.path.join(ROOT_DIR, f"personalization/{user_tg_id}.txt")
    with open(path, "w", encoding="utf-8") as file:
        file.write(text)



def delete_personalization(user_tg_id):
    pass
