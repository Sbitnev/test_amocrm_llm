import requests
import json
import os
from typing import Optional, List, Union
from tenacity import retry, stop_after_attempt, wait_fixed

import dotenv

from schemas import Digest


dotenv.load_dotenv()


class TelegramBot:
    def __init__(self, token: str):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
    def send_message(
        self,
        chat_id: Union[int, str],
        text: str,
        parse_mode: Optional[str] = None,
        reply_markup: Optional[dict] = None,
    ) -> dict:
        """
        Отправка текстового сообщения

        Args:
            chat_id: ID чата или username
            text: Текст сообщения
            parse_mode: Форматирование (HTML, Markdown)
            reply_markup: Клавиатура или inline-кнопки
        """
        url = f"{self.base_url}/sendMessage"
        payload = {"chat_id": chat_id, "text": text}

        if parse_mode:
            payload["parse_mode"] = parse_mode
        if reply_markup:
            payload["reply_markup"] = json.dumps(reply_markup)

        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    def send_digest_message(self, chat_id: Union[int, str], digest: Digest) -> dict:
        """
        Отправка дайджеста в форматированном виде
        """
        # Форматируем сообщение
        message = self._format_digest_message(digest)

        return self.send_message(chat_id=chat_id, text=message, parse_mode="HTML")

    def _format_digest_message(self, digest: Digest) -> str:
        """
        Форматирование дайджеста в HTML
        """
        message = (
            f"""
<b>📊 Дайджест продаж</b>
Период: {digest.start_dt.strftime('%d.%m.%Y')} - {digest.end_dt.strftime('%d.%m.%Y')}

<u>Основные метрики:</u>
• Создано сделок: <b>{digest.created_leads}</b>
• Закрыто сделок: <b>{digest.closed_leads}</b>
• Общая сумма: <b>{digest.total_price:,.0f}₽</b>
• Средний чек: <b>{digest.avg_price:,.0f}₽</b>
• Конверсия: <b>{digest.conversion:.1%}</b>
        """
            + f"""
<u>Ключевые метрики по команде:</u>
🥇 Лидер продаж: <b>{digest.best_seller.name}</b> — {digest.best_seller.total_price:,.0f}₽
📊 Самый низкий результат: <b>{digest.worst_seller.name}</b> — {digest.worst_seller.total_price:,.0f}₽
Общая активность команды: <b>{digest.created_leads}</b> новых сделок
            """
        )

        # Добавляем алерты если есть
        message += "\n<u>⚠️ Предупреждения:</u>\n"
        if digest.alerts:
            for alert in digest.alerts:
                message += f"• {alert}\n"
        else:
            message += "Падения по метрикам за период нет"

        return message

    def send_message_with_keyboard(
        self, chat_id: Union[int, str], text: str, buttons: List[List[dict]]
    ) -> dict:
        """
        Отправка сообщения с клавиатурой

        Args:
            buttons: [[{text: "Кнопка 1", callback_data: "data1"}], ...]
        """
        keyboard = {"inline_keyboard": buttons}

        return self.send_message(
            chat_id=chat_id, text=text, parse_mode="HTML", reply_markup=keyboard
        )


bot = TelegramBot(os.getenv("TELEGRAM_TOKEN"))
