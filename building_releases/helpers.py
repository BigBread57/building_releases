from building_releases.settings import DEFAULT_REF


def get_project_ref(project_info: str) -> str:
    """Получаем название ветки, из которой будет делаться тег."""
    # Проверяем в каком формате были переданы данные в переменной
    # ORDER_OF_TGS_IN_PROJECT. Если в формате 200-master, то в ref возвращаем
    # master, иначе ref - берется из настроек.
    if len(project_info.split('-')) == 2:
        return project_info[1]

    return DEFAULT_REF
