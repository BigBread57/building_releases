from building_releases import settings


def get_info_for_create_tags(project_info: str) -> dict:
    """Получаем название ветки, из которой будет делаться тег.
    
    Проверяем в каком формате были переданы данные в переменной
    ORDER_OF_CREATING_TAGS. Если в формате 200-master, то в ref возвращаем
    master, иначе ref - берется из настроек. Стандартно - develop.
    """
    # Проверяем, обязательно ли создавать тег, перед созданием второго тега.
    if project_info.find('*') == -1:
        check_pipeline = False
    else:
        # Удаляем символ '*', указывающий на обязательное создание тега.
        project_info = project_info[:-1]
        check_pipeline = True

    # Проверяем, была ли передана ветка из которой необходимо создать тег.
    if len(project_info.split('-')) == 2:
        ref = project_info[1]
    else:
        ref = settings.DEFAULT_REF

    return {
        'id': project_info[0],
        'ref': ref,
        'check_pipeline': check_pipeline,
    }
