import requests

from building_releases.analysis_pipelines import check_pipelines
from building_releases.analysis_tags import get_new_name_tag, check_create_tag
from building_releases.helpers import get_project_ref
from building_releases.settings import ORDER_OF_TGS_IN_PROJECT


def get_tags_order():
    """Получить порядок создания тегов в проектах."""
    # Анализируем порядок создания тегов в проектах.
    # Бывает два типа тегов. Обычный - проверяется факт того, что он создался
    # и обязательный (помечается *) - проверяется еще pipelines по тегу.
    for project_info in ORDER_OF_TGS_IN_PROJECT.split(','):
        # Получаем id и название ветки.
        project_id = project_info[0]
        project_ref = get_project_ref(project_info)
        # Получаем основную информацию о проекте (его имя, ссылку и другое).
        # FIXME: написать логику.

        # Если нет *, которая указывает на обязательное успешное создание тега,
        # перед созданием тега в следующем проекте, то просто создаем тег и
        # анализируем информацию о следующем проекте.
        if project_info.find('*') == -1:

            if len(project_info.split('-')) == 2:
                project_ref = project_info[1]
            else:
                project_ref = DEFAULT_REF
            project_id = project_info[0]

            # Получаем все созданные теги по проекту. Отправляем результат
            # запроса на анализ.
            response_get_tags = requests.get(
                url=f'{GITLAB_URL}api/v4/projects/{project_id}/repository/tags',
                headers=HEADERS,
                timeout=10,
            )
            # Получаем новое имя для тега.
            new_name_tag = get_new_name_tag(
                project_id,
                response_get_tags.status_code,
                response_get_tags.text,
            )

            # Создаем новый тег
            response_post_tags = requests.post(
                url=f'{GITLAB_URL}api/v4/projects/{project_id}/repository/tags',
                headers=HEADERS,
                data={
                    'tag_name': new_name_tag,
                    'ref': project_ref,
                },
                timeout=10,
            )
            # Проверяем успех создания тега.
            check_create_tag(
                project_id,
                response_post_tags.status_code,
                response_post_tags.text,
            )

        else:
            # FIXME: Убрать дубликат кода:
            # Получаем все созданные теги по проекту. Отправляем результат
            # запроса на анализ.
            response_get_tags = requests.get(
                url=f'{GITLAB_URL}api/v4/projects/{project_id}/repository/tags',
                headers=HEADERS,
                timeout=10,
            )
            # Получаем новое имя для тега.
            new_name_tag = get_new_name_tag(
                project_id,
                response_get_tags.status_code,
                response_get_tags.text,
            )

            # Создаем новый тег
            response_post_tags = requests.post(
                url=f'{GITLAB_URL}api/v4/projects/{project_id}/repository/tags',
                headers=HEADERS,
                data={
                    'tag_name': new_name_tag,
                    'ref': project_ref,
                },
                timeout=10,
            )
            # Проверяем успех создания тега.
            check_create_tag(
                project_id,
                response_post_tags.status_code,
                response_post_tags.text,
            )



            # Получаем последние 20 pipelines.
            response_get_pipelines = requests.get(
                url=f'{GITLAB_URL}api/v4/projects/{project_id}/pipelines/',
                headers=HEADERS,
                timeout=10,
            )
            # Проверяем результат pipelines.
            check_pipelines(
                project_id,
                response_get_pipelines.status_code,
                response_get_pipelines.text,
                new_name_tag,
            )


