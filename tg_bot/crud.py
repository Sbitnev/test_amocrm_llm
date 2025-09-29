import os
import sys

# Получаем абсолютный путь к текущему файлу
current_file_path = os.path.abspath(__file__)

# Получаем путь к родительской директории
parent_dir = os.path.dirname(os.path.dirname(current_file_path))

# Добавляем родительскую директорию в sys.path
sys.path.append(parent_dir)

from tenacity import retry, stop_after_attempt, wait_fixed
from telebot.types import Message
from common.models import TgUser
from common.database import get_db


@retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
def register_chat_and_user(message: Message):
    user = message.from_user
    # chat = message.chat
    flag = False

    with next(get_db()) as session:
        tg_user = session.get(TgUser, user.id)

        if not tg_user:
            tg_user = TgUser(
                tg_id=user.id,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
            )
            session.add(tg_user)
            flag = True

        # tg_chat = session.get(TgChat, chat.id)

        # if not tg_chat:
        #     tg_chat = TgChat(
        #         tg_id=chat.id,
        #         title=chat.title,
        #         username=chat.username,
        #         type=chat.type,
        #     )
        #     session.add(tg_chat)
        #     flag = True

        if flag:
            session.commit()
