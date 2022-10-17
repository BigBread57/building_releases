import os

from dotenv import load_dotenv

env_path = os.path.expanduser(os.path.join(os.getcwd(), 'config'))
load_dotenv(os.path.join(env_path, '.env'))

# Стандартная ветка для релизов.
DEFAULT_REF = os.environ.get('DEFAULT_REF', 'develop')

# Порядок создания тегов в проектах.
ORDER_OF_CREATING_TAGS = os.environ.get('ORDER_OF_CREATING_TAGS')

# Токен доступа в Gitlab. Процесс создания описан:
# https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html
GITLAB_TOKEN = os.environ.get('GITLAB_TOKEN')

# Url-адрес до Gitlab.
GITLAB_URL = os.environ.get('GITLAB_URL')

# Указываем для чего создаем теги (релиз, пре-релиз). Необходимо передать начало
# тега для того, чтобы новые теги имели корректное название.
PATTERN_TAG = os.environ.get('PATTERN_TAG')

# Заголовок с авторизацией для Gitlab.
HEADERS = {'PRIVATE-TOKEN': GITLAB_TOKEN}

