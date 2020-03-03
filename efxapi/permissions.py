from rest_framework.exceptions import APIException
from rest_framework import status
from rest_framework.permissions import BasePermission
from datetime import datetime

class MarketClosedException(APIException):
    default_detail="Markets are currently closed"
    status_code=status.HTTP_451_UNAVAILABLE_FOR_LEGAL_REASONS


class MarketPermission(BasePermission):
    def has_permission(self,request,view):
        time=datetime.utcnow()
        if((time.weekday==4 and time.hour>21) or (time.weekday==5) or (time.weekday==6 and time.hour<23) #friday 9pm to sunday 11pm
        or (time.month==12 and time.date==24 and time.hour>21) or (time.month==12 and time.date==25) or (time.month==12 and time.date==25 and time.hour<23) #24/12 9pm to 25/12 11pm
        or (time.month==12 and time.date==31 and time.hour>21) or (time.month==1 and time.date==1) or (time.month==1 and time.date==1 and time.hour<23)): #31/12 9pm to 01/01 11pm
            raise MarketClosedException()
        return True