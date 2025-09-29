import os
import sys

# Получаем абсолютный путь к текущему файлу
current_file_path = os.path.abspath(__file__)

# Получаем путь к родительской директории
parent_dir = os.path.dirname(os.path.dirname(current_file_path))

# Добавляем родительскую директорию в sys.path
sys.path.append(parent_dir)

import logging
import os
import getpass
import tempfile
import traceback
from datetime import datetime
from pathlib import Path

import httpx
import requests
import json
from langchain_core.messages import (
    HumanMessage,
    AIMessage,
    ToolMessage,
    SystemMessage,
    RemoveMessage,
)
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.graph.state import CompiledStateGraph
from telebot import util
from tenacity import retry, stop_after_attempt, wait_fixed
import yaml

from langchain_core.callbacks import BaseCallbackHandler

from langgraph.prebuilt import create_react_agent
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver
from langchain import hub
import requests
import re
from urllib.parse import unquote
from tg_bot.settings import ROOT_DIR

from tg_bot.logging_conf import logger

# from agent_dev.tools_desc import Osv_FinalSchema
from common.database import engine
from common.prompt_manager import prompt_manager

from dotenv import load_dotenv

load_dotenv()

files_dir = "files"
os.makedirs(files_dir, exist_ok=True)
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
# logger = logging.getLogger("langsmith")
# logger.setLevel(logging.DEBUG)
# logger.setLevel(logging.INFO)
# logger.addHandler(logging.FileHandler(os.path.join(log_dir, "langsmith.log")))
# logger.addHandler(logging.StreamHandler())

BASEDIR = Path(__file__).parent.parent
CA_CERT_PATH = BASEDIR / "ca.crt"
CA_CERT_PATH = str(CA_CERT_PATH.resolve())


class GuardHandler(BaseCallbackHandler):
    def on_tool_start(self, serialized, *_, **__):
        if serialized.get("name") == "requests_get" and "get_order_invoice" in __.get(
            "inputs"
        ):
            raise RuntimeError(
                "get_order_invoice заблокирован. Используй инструмент get_file_from_url."
            )


class Bot_LLM:
    def __init__(
        self, bot, model_id="gpt-4.1-mini", max_history_message_tokens=1000, logger=None
    ):
        self.bot = bot
        self.model_id = model_id
        self.max_history_message_tokens = max_history_message_tokens
        self.logger = logger
        self.model = ChatOpenAI(
            api_key=os.environ.get("API_KEY_MINI_LLM"),
            model=model_id,
            base_url=os.environ.get("BASE_URL_MINI_LLM"),
            http_client=httpx.Client(verify=CA_CERT_PATH),
        )
        self.agent_executor: CompiledStateGraph = CompiledStateGraph

    def run(self):
        self._init_smb_assist()

    def _init_smb_assist(self):

        def system_prompt(state, config):
            prompt_text = prompt_manager.get_system_prompt()
            return [SystemMessage(content=prompt_text)] + state["messages"]
            # return SystemMessage(content=prompt_text)

        db = SQLDatabase(engine=engine)
        toolkit = SQLDatabaseToolkit(db=db, llm=self.model)
        self.agent_executor: CompiledStateGraph = create_react_agent(
            self.model,
            toolkit.get_tools(),
            prompt=system_prompt,
            checkpointer=MemorySaver(),
        )
        self.agent_executor = self.agent_executor.with_config(
            callbacks=[GuardHandler()]
        )

    def steam(self, message_tg, user_tg_id, thread_id=None, is_debug=False):
        # config = {"configurable": {"thread_id": thread_id, "user_id": user_tg_id}}
        config = {"configurable": {"thread_id": user_tg_id}}
        message = message_tg.text
        logger.info(f"Обработка сообщения от пользователя user_tg_id: {message}")
        current_state = self.agent_executor.get_state(config)
        messages = current_state.values.get("messages", [])
        logger.info(f"Поток: {user_tg_id}, сообщений: {len(messages)}")

        if not messages or len(messages) == 0:
            input_messages = {
                "messages": [HumanMessage(message)],
            }
        else:
            last_message = messages[-1]
            if (
                isinstance(last_message, AIMessage)
                and getattr(last_message, "tool_calls", None)
                and last_message.tool_calls[0]["name"] == "ask_human"
            ):
                input_messages = Command(resume=message)
            else:
                input_messages = {
                    "messages": [HumanMessage(message)],
                }
        if is_debug:
            result = self.process_call_in_debug_mode(message_tg, input_messages, config)
        else:
            result = self.process_call_in_standart_mode(input_messages, config)

        current_state = self.agent_executor.get_state(config)
        messages = current_state.values.get("messages", [])
        if len(messages) > 30:
            logger.info(
                f"Суммаризация для потока {user_tg_id}, сообщений: {len(messages)}"
            )
            summary_prompt = (
                "Суммаризируй приведённые выше сообщения чата в одно краткое сообщение."
                "Включи как можно больше конкретных деталей."
                "Если последнее сообщение от ИИ содержит вопрос, обязательно сохрани его."
            )
            summary_message = self.model.invoke(
                messages + [HumanMessage(content=summary_prompt)]
            )
            content = "Сокращенная история сообщений:\n\n" + summary_message.content
            new_messages = [SystemMessage(content=content)]
            delete_messages = [RemoveMessage(id=m.id) for m in messages]
            # self.agent_executor.checkpointer.delete_thread(thread_id=user_tg_id)
            self.agent_executor.update_state(
                config, {"messages": new_messages + delete_messages}
            )
            # messages = new_messages

        return result

    def invoke(self, message_tg, user_tg_id, thread_id=None, is_debug=False):
        message = message_tg.text
        input_messages = {
            "messages": [HumanMessage(message)],
        }
        response = self.agent_executor.invoke({"input": message})
        result = []
        result.append({"type": "text", "content": response["output"]})
        return result

    def process_call_in_standart_mode(self, input_messages, config):
        events = self.agent_executor.stream(
            input_messages, stream_mode="updates", config=config
        )
        result = []
        last_index = None
        for event in events:
            if event.get("tools"):
                for message in event["tools"]["messages"]:
                    # message.pretty_print()
                    if message.name == "get_file_from_url":
                        result.append({"type": "file", "content": message.content})
                    continue
            if event.get("agent"):
                for message in event["agent"]["messages"]:
                    # message.pretty_print()
                    # if isinstance(last_message, (HumanMessage, ToolMessage)):
                    #     continue
                    if not message.content:
                        continue
                    result.append({"type": "text", "content": message.pretty_repr()})
            if event.get("__interrupt__"):
                for interrupt in event["__interrupt__"]:
                    result.append({"type": "text", "content": interrupt.value})
        return result

    def process_call_in_debug_mode(self, message_tg, input_messages, config):
        events = self.agent_executor.stream(
            input_messages, stream_mode="values", config=config
        )
        result = []
        last_index = None
        for event in events:
            if last_index is None:
                last_index = len(event["messages"]) - 1
            # else:
            #     last_index += 1
            for i in range(last_index, len(event["messages"])):
                last_message = event["messages"][i]
                # last_message.pretty_print()
                self.send_message(
                    message_tg.chat.id,
                    last_message.pretty_repr(),
                )
                result.append({"type": "text", "content": last_message.pretty_repr()})
                if (
                    isinstance(last_message, ToolMessage)
                    and last_message.name == "get_file_from_url"
                    and last_message.content
                ):
                    self.send_attache(
                        message_tg.chat.id,
                        last_message.content,
                    )
                    result.append({"type": "file", "content": last_message.content})
                last_index += 1
        return result

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
    def send_message(self, chat_id, text, id_topic=None, reply_markup=None):
        if not text:
            return
        try:
            parts = util.smart_split(text, chars_per_string=4096)
            for part in parts:
                self.bot.send_message(
                    chat_id=chat_id,
                    text=part,
                    message_thread_id=id_topic,
                    reply_markup=reply_markup,
                    parse_mode="HTML",
                )
        except Exception as e:
            if self.logger:
                self.logger.warning(f"[send_message] Ошибка при отправке текста: {e}")
                self.logger.debug(traceback.format_exc())

            # Сохраняем текст во временный файл
            with tempfile.NamedTemporaryFile(
                mode="w+", delete=False, suffix=".txt", encoding="utf-8"
            ) as tmp:
                tmp.write(text)
                tmp_path = tmp.name

            # Пытаемся отправить как файл
            try:
                with open(tmp_path, "rb") as file_doc:
                    self.bot.send_document(
                        chat_id=chat_id,
                        document=file_doc,
                        caption="Сообщение не удалось отправить как текст, поэтому прикреплено файлом.",
                        message_thread_id=id_topic,
                    )
            except Exception as e2:
                if self.logger:
                    self.logger.error(f"[send_message] Ошибка при отправке файла: {e2}")
                    self.logger.debug(traceback.format_exc())

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
    def send_attache(self, chat_id, file, id_topic=None):
        if not file:
            return
        with open(file, "rb") as fileraw:
            if file.split(".")[-1] in ("png", "jpg", "jpeg"):
                self.bot.send_photo(chat_id, fileraw)
            else:
                self.bot.send_document(
                    chat_id=chat_id, document=fileraw, message_thread_id=id_topic
                )
