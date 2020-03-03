from django.apps import AppConfig
import sys

class SocConfig(AppConfig):
    name = 'v1.soc'

    def ready(self):
        from .socket import initialize
        if "worker" not in sys.argv:
            pass
            initialize()
