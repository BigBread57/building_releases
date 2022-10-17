import json
import re
import sys
from typing import Optional

import requests

from building_releases import settings
from building_releases.analysis_porject import ProjectInfo


class AnalysisTag(object):
    """Осуществляем анализ тегов."""

    def __init__(self, project: ProjectInfo, *args,  **kwargs):
        """Инициализируем переменные для работы."""
        self.project = project

        self.url = '{gitlab}/api/v4/projects/{id}/repository/tags'.format(
            gitlab=settings.GITLAB_URL,
            id=self.project.info.id,
        )
        self.response = requests.get(
            url=self.url,
            headers=settings.HEADERS,
            timeout=10,
        )

    def get_new_name_tag(self) -> str:
        """Анализ GET projects/<id>/repository/tags."""
        if self.response.status_code == 200:
            # Преобразуем text ответа в json и анализируем.
            for tag in json.loads(self.response.text):
                if last_name_tag := self.correct_name_last_tag(tag):
                    # Если успешно получили имя последнего тега, то формируем
                    # название для нового тега.
                    return self.get_new_name(last_name_tag)

        print(
            'Не удалось получить доступ к тегам в ' +
            f'проекте: {self.project.info.name}. ' +
            f'Код: {self.response.status_code}. Текст {self.response.text}.'
        )
        sys.exit()

    def correct_name_last_tag(self, tag: dict) -> Optional[str]:
        """Проверяем корректность имени тега."""
        # Если название тега имеет нужный шаблон (релиз, пре-релиз
        # и др.), то далее работаем с ним, иначе ищем дальше.
        if tag.get('name').find(settings.PATTERN_TAG) != -1:
            last_name_tag = tag.get('name')

            # Сразу проверяем корректность версионирования.
            if not re.search(r'v(([0-9])+\.?)+[0-9]+$', last_name_tag):
                print(
                    f'Странное версионирование в '
                    f'проекте: {self.project.info.name}. ' +
                    f'Было получено: {last_name_tag}. Если так и должно ' +
                    'быть, то пишите разработчику.'
                )
                sys.exit()

            return last_name_tag

        return None

    def get_new_name(self, last_name_tag: str):
        """Формируем новое имя для тега.

        Формирование тега происходит за счет рекурсии.
        """
        # Получаем последний символ в названии последнего тега.
        char_tag = last_name_tag[-1]

        # Если это число, то просто его увеличиваем на 1.
        if char_tag.isdigit():
            char_tag = int(char_tag)
            # Если последнее число не 9, то увеличиваем на 1, то есть было v0.1,
            # станет v0.2
            if char_tag != 9:
                return f'{last_name_tag[:-1]}{char_tag+1}'

            # Если последнее число 9, то увеличиваем следующее число на 1, то
            # есть было v0.9, станет v1.0 или было v0.09, станет v0.10.
            # Достигается то путем рекурсии.
            elif char_tag == 9:
                return f'{self.get_new_name(last_name_tag[:-1])}0'

        # Если это точка, то пропускаем символ и увеличиваем число перед точкой.
        elif char_tag == '.':
            return f'{self.get_new_name(last_name_tag[:-1])}.'

        # Если это символ v, то после символа ставим 1.
        elif char_tag == 'v':
            return f'{last_name_tag}1'


class CreateTag(object):
    """Создаем новый тег."""

    def __init__(self, project: ProjectInfo, new_name_tag: str, *args, **kwargs):  # noqa: E501
        """Инициализируем переменные для работы."""
        self.project = project
        self.name_tag = new_name_tag

        self.url = '{gitlab}/api/v4/projects/{id}/repository/tags'.format(
            gitlab=settings.GITLAB_URL,
            id=self.project.info.id,
        )
        self.response = requests.post(
            url=self.url,
            headers=settings.HEADERS,
            data={
                'tag_name': self.name_tag,
                'ref': self.project.info.ref,
            },
            timeout=10,
        )

        self.check_create_tag()

    def check_create_tag(self) -> None:
        """Проверяем, что тег создался успешно."""
        if self.response.status_code != 201:
            print(
                f'В проекте {self.project.info.name} при создании тега ' +
                f'возникла ошибка. Код: {self.response.status_code}. Текст: ' +
                f'{self.response.text}.',
            )
            sys.exit()
