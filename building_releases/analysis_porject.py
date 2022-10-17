import json
from dataclasses import dataclass
from typing import Optional

import requests

from building_releases import settings


@dataclass
class Project:
    """Минимальная информация о проекте."""
    id: int
    name: str
    web_url: str
    check_pipeline: bool
    ref: str


class ProjectInfo(object):
    """Класс для анализа основной информации о проекте в Gitlab."""

    def __init__(self, info_for_create_tags: dict, *args, **kwargs):
        """Инициализируем переменные для работы."""
        self.info_for_create_tags = info_for_create_tags
        self.url = '{gitlab}/api/v4/projects/{id}'.format(
            gitlab=settings.GITLAB_URL,
            id=self.info_for_create_tags.get('id'),
        )
        self.info: Optional[Project] = None
        self.get_info()

    def get_info(self):
        """Получаем информацию о проекте."""
        response = requests.get(
            url=self.url,
            headers=settings.HEADERS,
            timeout=10,
        )

        if response.status_code == 200:
            json_text = json.loads(response.text)
            self.info = Project(
                id=int(self.info_for_create_tags.get('check_pipeline')),
                name=json_text.get('name'),
                web_url=json_text.get('web_url'),
                check_pipeline=self.info_for_create_tags.get('check_pipeline'),
                ref=self.info_for_create_tags.get('ref'),
            )
