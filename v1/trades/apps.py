from django.apps import AppConfig
from efxapi.socket import con
import multiprocessing as mp
import time

class TradesConfig(AppConfig):
    name = 'v1.trades'



