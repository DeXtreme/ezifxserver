from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from rest_framework.authtoken.models import Token
from django.db import close_old_connections
from django.core.exceptions import PermissionDenied
from v1.trades import routing

class TokenAuthMiddleware:
    """
    Token authorization middleware for Django Channels 2
    """

    def __init__(self, inner):
        self.inner = inner

    def __call__(self, scope):
        headers = dict(scope['headers'])
        if b'authorization' in headers:
            token_name, token_key = headers[b'authorization'].decode().split()
            if token_name == 'Token':
                token = Token.objects.get(key=token_key)
                scope['user'] = token.user
                close_old_connections()
        return self.inner(scope)

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': TokenAuthMiddleware(
            URLRouter(
                routing.websocket_urlpatterns
            )
        )
})