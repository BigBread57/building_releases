import json
import sys
import time
from typing import Optional

import requests

from building_releases import settings
from building_releases.analysis_porject import ProjectInfo


class AnalysisPipeline(object):
    """Класс для анализа pipelines в Gitlab."""

    def __init__(self, project: ProjectInfo, new_name_tag: str, *args, **kwargs):  # noqa: E501
        """Инициализируем переменные для работы."""
        self.project = project
        self.name_tag = new_name_tag

        self.url = '{gitlab}/api/v4/projects/{id}/pipelines'.format(
            gitlab=settings.GITLAB_URL,
            id=self.project.info.id,
        )
        self.response = requests.get(
            url=self.url,
            headers=settings.HEADERS,
            timeout=10,
        )

        self.pipeline_id: Optional[int] = None
        self.url_pipeline = '{gitlab}/api/v4/projects/{project_id}/pipelines{pipeline_id}'  # noqa: E501

    def check_pipelines(self):

        if self.response.status_code == 200:
            # Преобразуем text ответа в json и анализируем.
            for pipeline in json.loads(self.response.text):
                if pipeline.get('ref') == self.name_tag:
                    self.pipeline_id = pipeline.get('id')

            if self.pipeline_id:
                self.check_status()
            else:
                print(
                    f'Нет pipeline c именем {self.name_tag} для проекта: +'
                    f'{self.project.info.name}.',
                )
                sys.exit()

        print(
            f'Проблема с pipelines в проекте: {self.project.info.name}.' +
            f'Код: {self.response.status_code}. Текст {self.response.text}.'
        )
        sys.exit()

    def check_status(self):
        """Проверяем статус pipeline каждую минуту."""
        status = None
        count = 0

        # Пока не будет получен результат, анализируем pipelines.
        # Максимум анализируем 10 минут.
        while status not in {'success', 'failed'}:

            if count < 10:
                count += 1

            else:
                print(
                    f'В проекте {self.project.info.name} долго крутятся ' +
                    f'pipeline. Необходимо проверить.'
                )
                sys.exit()

            time.sleep(60)
            response = requests.get(
                url=self.url_pipeline.format(
                    gitlab=settings.GITLAB_URL,
                    project_id=self.project.info.id,
                    pipeline_id=self.pipeline_id,
                ),
                headers=settings.HEADERS,
                timeout=10,
            )

            if response.status_code == 200:
                json_text = json.loads(response.text)
                status = json_text.get('status')
            else:
                print(
                    f'Получение pipeline в проекте {self.project.info.name} ' +
                    f'с id {self.pipeline_id} невозможно.' +
                    f'Код: {response.status_code}. Текст: {response.text}',
                )
                sys.exit()
