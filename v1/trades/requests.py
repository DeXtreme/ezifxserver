from .models import Trade
import math
from v1.soc.tasks import openTradeWorker,closeTradeWorker
from time import sleep
from v1.account.models import Account


def closeTrade(trade):
    try:
        trade.status="PC"
        trade.save()
        count=0
        while count<10:
            pending=Trade.objects.get(id=trade.id)
            closeTradeWorker.apply_async(args=[trade.id],kwargs={"priority":0})
            if(pending.status=="C"):
                return pending
            count+=1
            sleep(1)
        raise Exception()
    except:
        raise Exception()


def round_half_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n*multiplier + 0.5) / multiplier

def round_half_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n*multiplier - 0.5) / multiplier


def openTrade(user,signal,risk):
    try:
        account=Account.objects.get(user=user)
        if(account.balance<risk):
            raise Exception("Trade could not be opened.Insufficient balance")

        pending=Trade.objects.create(user=user,signal=signal,risk=risk,status="PO")
        count=0
        while count<10:
            pending=Trade.objects.get(id=pending.id)
            openTradeWorker.apply_async(args=[pending.id],kwargs={"priority":0})
            if(pending.status=="O"):
                return pending
            count+=1
            sleep(1)
        raise Exception()
    except Exception as e:
        print(e)
        raise Exception()
