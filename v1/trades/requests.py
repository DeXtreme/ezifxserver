from .models import Trade
import math
from v1.soc.tasks import openTradeWorker,closeTradeWorker
from v1.signals.requests import getMarketInfo
from time import sleep
from efxapi.common import round_half_up,round_half_down
from v1.account.models import Account


def closeTrade(trade):
    try:
        trade.status="PC"
        trade.save()

        pending=None
        pending=Trade.objects.get(id=trade.id)
        task=closeTradeWorker.apply_async([trade.id],priority=0,expires=15)
        result=task.get()
        if(result==True):
            return Trade.objects.get(id=pending.id)
        else:
            raise Exception()
        
    except:
        if(pending):
            pending.status="O"
            pending.save()
        raise Exception()



def openTrade(user,signal,risk):
    try:
        account=Account.objects.get(user=user)
        if(account.balance<risk):
            raise Exception("Trade could not be opened.Insufficient balance")

        info=getMarketInfo(signal)

        if(risk<info["min_risk"]):
            raise Exception("Trade could not be opened.Risk amount below minimum")
        elif(risk>info["max_risk"]):
            raise Exception("Trade could not be opened.Risk amount above maximum")
        else:
            pass
        
        pending=None
        pending=Trade.objects.create(user=user,signal=signal,risk=risk,status="PO")
        task=openTradeWorker.apply_async([pending.id],priority=0,expires=15)   
        result=task.get()
        if(result!=True):
            raise Exception()

        return Trade.objects.get(id=pending.id)

    except Exception as e:
        print(e)
        if(pending):
            pending.delete()
        raise Exception()
