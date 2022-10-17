import json
import re
import sys


def get_new_name_tag(project_id: str, status_code: int, text: str) -> str:
    """Анализ GET projects/<id>/repository/tags."""
    if status_code == 200:
        # Преобразуем text ответа в json
        json_text = json.loads(text)
        # Отправляем название тега для первого элемента списка. Первый элемент
        # - это последний тег (https://docs.gitlab.com/ee/api/tags.html).
        last_name_tag = json_text[0].get('name')

        # Проверяем, корректность имени последнего тега.
        correct_name_last_tag(last_name_tag)

        # Формируем имя для следующего тега.
        return get_new_name(last_name_tag)

    print(f'Поломалось, на доступе к тегу проекта: {project_id}')
    sys.exit()


def correct_name_last_tag(last_name_tag: str):
    """Проверяем корректность имени последнего тега."""
    if not re.search(r'v(([0-9])+\.?)+[0-9]+$', last_name_tag):
        print('Странное версионирование, я не понимаю что вы хотите')
        sys.exit()


def get_new_name(last_name_tag: str):
    """Формируем новое имя для тега."""
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
            return f'{get_new_name(last_name_tag[:-1])}0'

    # Если это точка, то пропускаем символ и увеличиваем число перед точкой.
    elif char_tag == '.':
        return f'{get_new_name(last_name_tag[:-1])}.'

    # Если это символ v, то после символа ставим 1.
    elif char_tag == 'v':
        return f'{last_name_tag}1'


def check_create_tag(project_id: str, status_code: int, text: str) -> None:
    """Проверяем, что тег создался успешно."""
    if status_code != 201:
        print(
            f'В проекте {project_id} при создании тега возникал ошибка. ' +
            f'Код: {status_code}. Текст: {text}',
        )
        sys.exit()
