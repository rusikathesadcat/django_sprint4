"""
ASGI конфигурация для проекта blogicum.

Предоставляет ASGI вызываемый объект как переменную уровня модуля с именем ``application``.

Для получения дополнительной информации об этом файле см.
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogicum.settings')

application = get_asgi_application()
