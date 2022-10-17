import json
import sys
import time

import requests

from building_releases.main import GITLAB_URL, HEADERS


def check_pipelines(
        project_id: str,
        status_code: int,
        text: str,
        new_name_tag: str,
) -> str:
    # Переменная для запоминая id нужного pipeline.
    pipeline_id = None

    if status_code == 200:
        # Преобразуем text ответа в json.
        json_text = json.loads(text)

        # Ищем в pipelines нужный pipeline по имени тега и запоминаем его id.
        for pipeline in json_text:
            if pipeline.get('ref') == new_name_tag:
                pipeline_id = pipeline.get('id')

        if pipeline_id:
            check_status(project_id, pipeline_id)
        else:
            print(f'Нет pipeline для проекта: {project_id}')
            sys.exit()

    print(f'Проблема с pipelines  в проекте: {project_id}')
    sys.exit()


def check_status(project_id: str, pipeline_id: int):
    """Проверяем статус pipeline каждую минуту."""
    status = None
    count = 0

    while status in {'success', 'failed'}:
        if count < 10:
            count += 1
        else:
            print('Долго ждем получение статуса, проверить надо.')
            sys.exit()

        time.sleep(60)
        response_get_pipeline = requests.get(
            url=f'{GITLAB_URL}api/v4/projects/{project_id}/pipelines/{pipeline_id}',  # noqa: E501
            headers=HEADERS,
            timeout=10,
        )
        if response_get_pipeline.status_code == 200:
            json_text = json.loads(response_get_pipeline.text)
            status = json_text.get('status')
        else:
            print(
                f'Получение pipeline с id {pipeline_id} невозможно' +
                f'Код: {response_get_pipeline.status_code}. ' +
                f'Текст: {response_get_pipeline.text}',
            )
            sys.exit()
