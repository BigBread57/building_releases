from building_releases import settings
from building_releases.analysis_pipelines import AnalysisPipeline
from building_releases.analysis_porject import ProjectInfo
from building_releases.analysis_tags import AnalysisTag, CreateTag
from building_releases.helpers import get_info_for_create_tags


def get_tags_order():
    """Получить порядок создания тегов в проектах."""
    # Анализируем порядок создания тегов в проектах.
    # Бывает два типа тегов. Обычный - проверяется факт того, что он создался
    # и обязательный (помечается *) - проверяется еще pipelines по тегу.
    for project_info in settings.ORDER_OF_CREATING_TAGS.split(','):
        info_for_create_tags = get_info_for_create_tags(project_info)

        # Получаем основную информацию о проекте (его имя, ссылку и другое).
        project = ProjectInfo(info_for_create_tags)

        # Если нужно проверять успешное создание тега, перед созданием тега
        # в следующем проекте, то после создания анализируем pipeline.
        # Иначе просто создаем тег в следующем по порядке проекте.
        if info_for_create_tags.get('check_pipeline'):
            # Получаем новое имя для тега.
            analysis_tag = AnalysisTag(project)
            new_name_tag = analysis_tag.get_new_name_tag()
            # Создаем новый тег.
            CreateTag(project, new_name_tag)
            # Проверяем pipeline. Проверка осуществляется до тех пор, пока не
            # будет получен результат (успех или ошибка).
            AnalysisPipeline(project, new_name_tag)

        else:
            # Получаем новое имя для тега.
            analysis_tag = AnalysisTag(project)
            new_name_tag = analysis_tag.get_new_name_tag()
            # Создаем новый тег.
            CreateTag(project, new_name_tag)
