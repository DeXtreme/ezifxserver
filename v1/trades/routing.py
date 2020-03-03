from django.urls import re_path
from .consumers import TradesConsumer

from . import consumers

websocket_urlpatterns = [
    re_path(r'v1/ws/trades', TradesConsumer),
]