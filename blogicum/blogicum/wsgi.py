"""
WSGI конфигурация для проекта blogicum.

Предоставляет WSGI вызываемый объект как переменную уровня модуля с именем ``application``.

Для получения дополнительной информации об этом файле см.
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'blogicum.settings')

application = get_wsgi_application()
