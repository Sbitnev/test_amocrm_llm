import os

import dotenv
from amocrm_api import AmoOAuthClient


dotenv.load_dotenv()

# Инициализация переменных для пагинации
LIMIT = 250


client = AmoOAuthClient(
    access_token=os.environ.get("access_token"),
    refresh_token=os.environ.get("refresh_token"),
    crm_url=os.environ.get("crm_url"),
    client_id=os.environ.get("client_id"),
    client_secret=os.environ.get("client_secret"),
    redirect_uri=os.environ.get("redirect_uri")
)


def get_objects(LABEL, last_run_timestamp: int = 0, limit: int = 250, page: int = 1, params = None):
    # Проверка валидности сущности
    # valid_entities = ['leads', 'contacts', 'companies']
    # if entity not in valid_entities:
    #     raise ValueError(f"Неверный идентификатор сущности: {entity}. Доступные сущности: {valid_entities}")
    filters = {'updated_at__from': last_run_timestamp}
    result = []
    while True:
        if LABEL == 'pipelines':
            method_name = 'get_pipelines'
            method = getattr(client, method_name)
            data = method()
        elif LABEL == 'statuses':
            method_name = 'get_pipeline_statuses'
            method = getattr(client, method_name)
            data = method(**params)
        elif LABEL == 'unsorted':
            method_name = 'get_unsorted_leads'
            method = getattr(client, method_name)
            data = method(limit=limit, page=page)
        else:
            method_name = 'get_' + LABEL
            method = getattr(client, method_name)
            data = method(limit=limit, page=page, filters=filters)
        if data:
            entries = data['_embedded'][LABEL]
        else:
            break
        result.extend(entries)
        # Если на текущей странице меньше лидов, чем limit, значит это последняя страница
        if len(entries) < limit:
            break
        # Переход к следующей странице
        page += 1
    return result