from rest_framework.exceptions import APIException
from rest_framework import status
from rest_framework.permissions import BasePermission
from datetime import datetime
import pytz
from efxapi.common import is_market_open,get_market_times

class MarketClosedException(APIException):
    default_detail="%s" %(get_market_times()[1].strftime("%a %H:%M UTC"))
    status_code=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS


class MarketPermission(BasePermission):
    def has_permission(self,request,view):
        if(not is_market_open()):
            print("closed")
            raise MarketClosedException()
        print("Open")
        return True