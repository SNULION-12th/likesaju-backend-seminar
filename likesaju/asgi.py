"""
ASGI config for likesaju project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'likesaju.settings')
# application = get_asgi_application()
# 프로토콜에 따라 앱을 분리하기 위해 삭제


# siwon added for websocket protocol routing 0811
# initialize django application object
django_application = get_asgi_application()
# init 이후에 url import  
from  . import urls 
from channels.routing import ProtocolTypeRouter, URLRouter
from webchat.middleware import JWTAuthMiddleWare

application = ProtocolTypeRouter(
    {
        "http" : django_application,
        "websocket": JWTAuthMiddleWare(URLRouter(urls.websocket_urlpatterns)),
    }
)
