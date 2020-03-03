from django.contrib import admin
from .models import SignalGenerator,Signal

admin.site.register(Signal)
admin.site.register(SignalGenerator)
