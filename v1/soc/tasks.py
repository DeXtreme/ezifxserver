from __future__ import absolute_import, unicode_literals
from fxcmpy import fxcmpy
from celery import shared_task,task
from celery.signals import worker_ready
from v1.trades.models import Trade
from .models import SocInfo
from v1.account.models import Account
from django.db.models import Sum
from django.conf import settings
from time import sleep
from datetime import datetime
import math
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from v1.soc.socket import api_token
import json


con=None #fxcm connection

"""
@shared_task
def worker():
    while True:
        trades=Trade.objects.filter(status="O")
        print("In trade")
        for trade in trades:
            time=datetime.utcnow()
            if((time.weekday==6 and time.hour<23) or (time.weekday==5) or (time.weekday==4 and time.hour>21)):
                print("Away for the weekend")
                break
            else:
                tradeTask.delay(trade.trade_id)
        sleep(5)

@shared_task
def tradeTask(trade_id):
    print("working",con.is_connected())
    trade=Trade.objects.get(trade_id=trade_id)
    if(trade is not None):
        print("trade id",trade_id,trade)
        position=None
        try:
            position=con.get_open_position(trade_id)

            quote=position.get_currency().split("/")[1]     
            stoploss=abs(position.get_close()-position.get_stop())
            stoploss_price=position.get_stop()
            current_price=position.get_close()

            if(quote!="USD"):
                exchange=con.get_candles("USD"+"/"+quote,period="H1",number=1)["askclose"].iloc[0]
                risk=(position.get_amount()*1000)*abs(position.get_open()-position.get_stop())/exchange
                if(position.get_isBuy()==True):
                    profit=(position.get_amount()*1000)*(position.get_close()-position.get_open())/exchange
                    stoploss_profit=(position.get_amount()*1000)*(position.get_stop()-position.get_open())/exchange
                else:
                    profit=(position.get_amount()*1000)*(position.get_open()-position.get_close())/exchange
                    stoploss_profit=(position.get_amount()*1000)*(position.get_open()-position.get_stop())/exchange
            else:
                risk=(position.get_amount()*1000)*abs(position.get_open()-position.get_stop())
                if(position.get_isBuy()==True):
                    profit=(position.get_amount()*1000)*(position.get_close()-position.get_open())
                    stoploss_profit=(position.get_amount()*1000)*(position.get_stop()-position.get_open())
                else:
                    profit=(position.get_amount()*1000)*(position.get_open()-position.get_close())
                    stoploss_profit=(position.get_amount()*1000)*(position.get_open()-position.get_stop())
                
            print(round_half_down(profit,decimals=2),round_half_down(stoploss_profit,decimals=2))
            
                        
            trade.risk=round_half_down(risk,decimals=2)
            trade.stoploss=stoploss
            trade.stoploss_price=stoploss_price
            trade.current_price=current_price
            trade.profit=round_half_down(profit,decimals=2)
            trade.stoploss_profit=round_half_down(stoploss_profit,decimals=2)
            trade.save()

        except ValueError:
            try:
                position=con.get_closed_position(trade_id)
                print("trade closed",trade_id)
                

                quote=position.get_currency().split("/")[1]     
                current_price=position.get_close()

                if(quote!="USD"):
                    exchange=con.get_candles("USD"+"/"+quote,period="H1",number=1)["askclose"].iloc[0]
                    if(position.get_isBuy()=="BY"):
                        profit=(position.get_amount()*1000)*(position.get_close()-position.get_open())/exchange
                    else:
                        profit=(position.get_amount()*1000)*(position.get_open()-position.get_close())/exchange
                else:
                    if(position.get_isBuy()=="BY"):
                        profit=(position.get_amount()*1000)*(position.get_close()-position.get_open())
                    else:
                        profit=(position.get_amount()*1000)*(position.get_open()-position.get_close())
                    
                trade.status="C"
                trade.current_price=current_price
                trade.profit=round_half_down(profit,decimals=2),
                trade.save()

            except ValueError:
                print("log this for revision",trade_id)
                trade.status="C"
                trade.save()
                return
            
        channel_layer=get_channel_layer()
        async_to_sync(channel_layer.group_send)("trades",{"type":"update_trades","message":trade.user.username})
        
    else:
        print("Trade not found")

def round_half_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n*multiplier - 0.5) / multiplier
"""

@shared_task(bind=True)
def openTradeWorker(self):
    try:    
        #while True:
        print("Opening trades")
        for pending_trade in Trade.objects.filter(status="PO")|Trade.objects.filter(status="AO"):

            pid=pending_trade.id
            signal=pending_trade.signal              
            user=pending_trade.user

            base=signal.pair[0:3]
            quote=signal.pair[3:]
            
            if(pending_trade.status=="PO"):
                risk=pending_trade.risk  
                atr=settings.ATR_MUL*signal.atr
                risk=(1.0-settings.FEE)*risk #take percent of risk amount as fee

                usable_margin=con.get_accounts().iloc[0]["usableMargin"]
                print("Margin",usable_margin)
                leverage=400 #get leverage
                #leverage2=con.get_model(models=["LeverageProfile"])
                #print("Leverage",leverage2)
                usable_margin-=(Account.objects.all().aggregate(balance__sum=Sum('balance'))["balance__sum"] or 0.0)+(Trade.objects.all().aggregate(risk__sum=Sum('risk'))["risk__sum"] or 0.0)  #subtract sum of balances and trade risks
                usable_margin/=Account.objects.all().count()
                print("Margin",usable_margin)

                if(quote!="USD"):
                    exchange=con.get_candles("USD"+"/"+quote,period=signal.timeframe,number=1).iloc[0]["askclose"]
                    #exchange=get_candles("USD"+"/"+quote,"H1")["ask"]

                    #candle=get_candles(base+"/"+quote,"H1") #extra work for non_majors
                    candle=con.get_candles(base+"/"+quote,period=signal.timeframe,number=1).iloc[0]
                    ask=candle["askclose"]
                    bid=candle["bidclose"]
                    if(quote=="JPY"):
                        spread=abs(ask-bid)*100
                    else:
                        spread=abs(ask-bid)*10000
                    print("spread",spread)

                    print("exchange",exchange)
                    lot=risk/((10/exchange) * atr)
                    lot= round_half_down(round_half_down(lot/signal.min_lot,decimals=5)*signal.min_lot,decimals=2)
                    print("lot",lot)

                    atr=risk/((10/exchange)*lot)-spread

                    if((lot*100000*ask/(leverage*exchange))>usable_margin):
                        raise Exception("Not enough free margin")
                    
                    if(lot<signal.min_lot):
                        raise Exception("Risk too small")
                
                else:
                    candle=con.get_candles(base+"/"+quote,period=signal.timeframe,number=1).iloc[0]
                    ask=candle["askclose"]
                    bid=candle["bidclose"]
                    spread=abs(ask-bid)*10000
                    print("spread",spread)

                    lot=risk/(10 * atr)
                    lot= round_half_up(round_half_up(lot/signal.min_lot,decimals=5)*signal.min_lot,decimals=2)
                    print("lot",lot)
                    
                    atr=risk/((10*lot))-spread

                    if((lot*100000*ask/leverage)>usable_margin):
                        raise Exception("Not enough free margin")

                    if(lot<signal.min_lot):
                        raise Exception("Risk too small")

                        
                #trade=open_trade(base+"/"+quote,(signal.action=="BY"),lot,atr)
                trade=con.open_trade(base+"/"+quote,(signal.action=="BY"),lot*100,"GTC","AtMarket",is_in_pips=True,stop=(-1*atr if signal.action=="BY" else atr),trailing_step=1)
                print(trade)


                pending_trade.status="AO"
                pending_trade.trade_id=trade.get_tradeId()
                pending_trade.save()

            else:
                if(quote!="USD"):
                    exchange=con.get_candles("USD"+"/"+quote,period=signal.timeframe,number=1).iloc[0]["askclose"]
                trade=con.open_pos[pending_trade.trade_id]
            if(trade is not None):
                trade_id=trade.get_tradeId()
                trade=con.open_pos[trade_id]
                lot_size=trade.get_amount()/100
                stoploss=abs(trade.get_open()-trade.get_stop())
                stoploss_price=trade.get_stop()
                current_price=trade.get_close()

                if(quote!="USD"):
                    risk=(trade.get_amount()*1000)*abs(trade.get_open()-trade.get_stop())/exchange
                    if(signal.action=="BY"):
                        profit=(trade.get_amount()*1000)*(trade.get_close()-trade.get_open())/exchange
                        stoploss_profit=(trade.get_amount()*1000)*(trade.get_stop()-trade.get_open())/exchange
                    else:
                        profit=(trade.get_amount()*1000)*(trade.get_open()-trade.get_close())/exchange
                        stoploss_profit=(trade.get_amount()*1000)*(trade.get_open()-trade.get_stop())/exchange
                else:
                    risk=(trade.get_amount()*1000)*abs(trade.get_open()-trade.get_stop())
                    if(signal.action=="BY"):
                        profit=(trade.get_amount()*1000)*(trade.get_close()-trade.get_open())
                        stoploss_profit=(trade.get_amount()*1000)*(trade.get_stop()-trade.get_open())
                    else:
                        profit=(trade.get_amount()*1000)*(trade.get_open()-trade.get_close())
                        stoploss_profit=(trade.get_amount()*1000)*(trade.get_open()-trade.get_stop())


                pending_trade.risk=round_half_down(risk,decimals=2)
                pending_trade.trade_id=trade_id
                pending_trade.stoploss=stoploss
                pending_trade.stoploss_price=stoploss_price
                pending_trade.current_price=current_price
                pending_trade.previous_price=current_price
                pending_trade.profit=round_half_down(profit,decimals=2)
                pending_trade.lot_size=lot_size
                pending_trade.stoploss_profit=round_half_down(stoploss_profit,decimals=2)
                pending_trade.status="O"
                pending_trade.save()

                account=Account.objects.get(user=user)
                account.balance=account.balance-max(round_half_down(risk*1.01,decimals=2),0.01)
                account.save()

                

                """return {
                    "risk":round_half_down(risk,decimals=2),
                    "trade_id":trade_id,
                    "stoploss":stoploss,
                    "stoploss_price":stoploss_price,
                    "current_price":current_price,
                    "previous_price":current_price,
                    "profit":round_half_down(profit,decimals=2),
                    "lot_size":lot_size,
                    "stoploss_profit":round_half_down(stoploss_profit,decimals=2)} """

            else:
                raise Exception("Could not place trade")
        openTradeWorker.delay()
    except Exception as exc:
        print(exc)
        raise self.retry(countdown=5, exc=exc)

def round_half_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n*multiplier + 0.5) / multiplier

def round_half_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n*multiplier - 0.5) / multiplier


@shared_task
def updateTasker():
    global con
    offset=0
    limit=10
    while True:
        print("in updater",con.socket.sid)
        if(offset<Trade.objects.filter(status="O").count()):
            updateTask.delay(offset,offset+limit)
            offset+=limit
            sleep(0.001)
        else:
            offset=0
            break
    updateTasker.delay()
        

@shared_task
def updateTask(start,stop):
    try:
        print("updating",start,stop)
        for trade in Trade.objects.filter(status="O")[start:stop]:
            if(trade.trade_id in con.open_pos):
                position=con.open_pos[trade.trade_id]
                signal=trade.signal
                quote=position.get_currency().split("/")[1]     
                stoploss=abs(position.get_close()-position.get_stop())
                stoploss_price=position.get_stop()
                current_price=position.get_close()

                if(quote!="USD"):
                    exchange=con.get_candles("USD"+"/"+quote,period=signal.timeframe,number=1)["askclose"].iloc[0]
                    if(position.get_isBuy()==True):
                        profit=(position.get_amount()*1000)*(position.get_close()-position.get_open())/exchange
                        stoploss_profit=(position.get_amount()*1000)*(position.get_stop()-position.get_open())/exchange
                    else:
                        profit=(position.get_amount()*1000)*(position.get_open()-position.get_close())/exchange
                        stoploss_profit=(position.get_amount()*1000)*(position.get_open()-position.get_stop())/exchange
                else:
                    if(position.get_isBuy()==True):
                        profit=(position.get_amount()*1000)*(position.get_close()-position.get_open())
                        stoploss_profit=(position.get_amount()*1000)*(position.get_stop()-position.get_open())
                    else:
                        profit=(position.get_amount()*1000)*(position.get_open()-position.get_close())
                        stoploss_profit=(position.get_amount()*1000)*(position.get_open()-position.get_stop())
                        
                                
                trade.stoploss=stoploss
                trade.stoploss_price=stoploss_price
                trade.current_price=current_price
                trade.profit=round_half_down(profit,decimals=2)
                trade.stoploss_profit=round_half_down(stoploss_profit,decimals=2)
                trade.save()

                print("updated",trade.trade_id)

            elif(trade.trade_id in con.closed_pos):
                position=con.closed_pos[trade.trade_id]
                 
                quote=position.get_currency().split("/")[1]     
                current_price=position.get_close()

                if(quote!="USD"):
                    exchange=con.get_candles("USD"+"/"+quote,period=signal.timeframe,number=1)["askclose"].iloc[0]
                    if(position.get_isBuy()==True):
                        profit=(position.get_amount()*1000)*(position.get_close()-position.get_open())/exchange
                    else:
                        profit=(position.get_amount()*1000)*(position.get_open()-position.get_close())/exchange
                else:
                    if(position.get_isBuy()==True):
                        profit=(position.get_amount()*1000)*(position.get_close()-position.get_open())
                    else:
                        profit=(position.get_amount()*1000)*(position.get_open()-position.get_close())
                                 

                trade.profit=round_half_down(profit,decimals=2)
                trade.status="C"
                trade.save()

                account=Account.objects.get(user=trade.user)
                account.balance=round_half_down(account.balance+profit+trade.risk,decimals=2)
                account.save()

                print("closed",trade.trade_id)
            else:
                trade.status="E"
                trade.save()


        channel_layer=get_channel_layer()
        async_to_sync(channel_layer.group_send)("trades",{"type":"update_trades","message":trade.user.username})
    except Exception as e:
        print(e)

@shared_task(bind=True)
def closeTradeWorker(self):
    try:    
        #while True:
        print("Closing trades")
        for pending_trade in Trade.objects.filter(status="PC")|Trade.objects.filter(status="AC"):

            pid=pending_trade.id
            signal=pending_trade.signal              
            user=pending_trade.user

            base=signal.pair[0:3]
            quote=signal.pair[3:]
            
            if(pending_trade.status=="PC"):      
                con.close_trade(pending_trade.trade_id,int(pending_trade.lot_size*100),time_in_force="GTC")
                pending_trade.status="AC"
                pending_trade.save()

            
            if(pending_trade.trade_id in con.closed_pos):
                trade=con.closed_pos[pending_trade.trade_id]
                trade_id=trade.get_tradeId()
                current_price=trade.get_close()

                if(quote!="USD"):
                    exchange=con.get_candles("USD"+"/"+quote,period=signal.timeframe,number=1).iloc[0]["askclose"]
                    if(trade.get_isBuy()):
                        profit=(trade.get_amount()*1000)*(trade.get_close()-trade.get_open())/exchange
                    else:
                        profit=(trade.get_amount()*1000)*(trade.get_open()-trade.get_close())/exchange
                else:
                    if(trade.get_isBuy()):
                        profit=(trade.get_amount()*1000)*(trade.get_close()-trade.get_open())
                    else:
                        profit=(trade.get_amount()*1000)*(trade.get_open()-trade.get_close())


                
                pending_trade.current_price=current_price
                pending_trade.previous_price=current_price
                pending_trade.profit=round_half_down(profit,decimals=2)
                pending_trade.status="C"
                pending_trade.save()

                account=Account.objects.get(user=pending_trade.user)
                account.balance=round_half_down(account.balance+profit+pending_trade.risk,decimals=2)
                account.save()

        closeTradeWorker.delay()
    except Exception as exc:
        print(exc)
        raise self.retry(countdown=5, exc=exc)
        


@worker_ready.connect
def start(sender=None, headers=None, body=None, **kwargs):
    global con
    con=efxfxcmpy(access_token=api_token,log_level='error')
    print("FXCM connected")
    SocInfo.objects.update_or_create(pk=1,defaults={"offers":json.dumps(con.offers),"account_id":str(con.default_account)})

    openTradeWorker.delay()
    closeTradeWorker.delay()
    updateTasker.delay()


class efxfxcmpy(fxcmpy):
    def __on_connect__(self, msg=''):
        super().__on_connect__()
        SocInfo.objects.update_or_create(pk=1,defaults={"socket_id":self.socket.sid})


