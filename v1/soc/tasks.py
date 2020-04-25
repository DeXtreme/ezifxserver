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
import pytz
import math
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from v1.soc.socket import api_token
from efxapi.common import round_half_up,round_half_down,is_market_open
import json


con=None #fxcm connection
channel_layer=None

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
def updateTasker():
    global con
    offset=0
    limit=10
    while True:
        print("in updater",con.socket.sid)
        if(offset<Trade.objects.filter(status="O").count()):
            updateTask.apply_async((offset,offset+limit),priority=5)
            offset+=limit
            #sleep(0.001)
        else:
            offset=0
            break
    updateTasker.apply_async(priority=9)


"""

@shared_task(bind=True)
def openTradeWorker(self,pk):
    try:    
        #while True:
        print("Opening trades")
        for pending_trade in Trade.objects.filter(status="PO",id=pk)|Trade.objects.filter(status="AO",id=pk):

            pid=pending_trade.id
            signal=pending_trade.signal   
            timeframe="%s%s" %("m" if signal.timeframe[0].lower()=="m" else "H",signal.timeframe[1:])           
            user=pending_trade.user

            base=signal.pair[0:3]
            quote=signal.pair[3:]
            
            if(pending_trade.status=="PO"):
                risk=pending_trade.risk  
                atr=settings.ATR_MUL*signal.atr
                risk=(1.0-settings.FEE)*risk #take percent of risk amount as fee and use rest !!!!!

                usable_margin=con.get_accounts().iloc[0]["usableMargin"]
                print("Usable margin",usable_margin)
                leverage=400 #get leverage
                #leverage2=con.get_model(models=["LeverageProfile"])
                #print("Leverage",leverage2)
                usable_margin-=(Account.objects.all().aggregate(balance__sum=Sum('balance'))["balance__sum"] or 0.0)+(Trade.objects.all().aggregate(risk__sum=Sum('risk'))["risk__sum"] or 0.0)  #subtract sum of balances and trade risks
                usable_margin/=Account.objects.all().count()
                print("Margin per user",usable_margin)

                #if(quote!="USD"):
                per_pip=10 if quote!="JPY" else 1000

                exchange=con.get_candles("USD"+"/"+quote,period=timeframe,number=1).iloc[0]["askclose"] if quote!="USD" else 1

                candle=con.get_candles(base+"/"+quote,period=timeframe,number=1).iloc[0]
                ask=candle["askclose"]
                bid=candle["bidclose"]

                spread=abs(ask-bid)*10000 if quote!="JPY" else abs(ask-bid)*100
                print("spread",spread)

                """if(quote=="JPY"):
                    spread=abs(ask-bid)*100 #
                else:
                    spread=abs(ask-bid)*10000
                """

                print("exchange",exchange)
                lot=risk/((per_pip/exchange) * atr)
                lot= round_half_down(round_half_down(lot/signal.min_lot,decimals=5)*signal.min_lot,decimals=2)
                print("lot",lot)

                atr=risk/((per_pip/exchange)*lot)-spread

                if(lot<signal.min_lot):
                    raise Exception("Risk too small")

                if((lot*100000*ask/(leverage*exchange))>usable_margin):
                    raise Exception("Free margin insufficient")

                """
                else:
                    candle=con.get_candles(base+"/"+quote,period=timeframe,number=1).iloc[0]
                    ask=candle["askclose"]
                    bid=candle["bidclose"]

                    spread=abs(ask-bid)*10000
                    print("spread",spread)

                    lot=risk/(10 * atr)
                    lot= round_half_down(round_half_down(lot/signal.min_lot,decimals=5)*signal.min_lot,decimals=2)
                    print("lot",lot)
                    
                    atr=risk/((10*lot))-spread #

                    if((lot*100000*ask/leverage)>usable_margin):
                        raise Exception("Not enough free margin")

                    if(lot<signal.min_lot):
                        raise Exception("Risk too small")
                """
                        
                trade=con.open_trade(base+"/"+quote,(signal.action=="BY"),lot*100,"GTC","AtMarket",is_in_pips=True,stop=(-1*int(atr)),trailing_step=1)
                print(trade)

                pending_trade.status="AO"
                pending_trade.trade_id=trade.get_tradeId()
                pending_trade.save()

            else:
                #if(quote!="USD"):
                    #exchange=con.get_candles("USD"+"/"+quote,period=timeframe,number=1).iloc[0]["askclose"]
                exchange=con.get_candles("USD"+"/"+quote,period=timeframe,number=1).iloc[0]["askclose"] if quote!="USD" else 1
                trade=con.open_pos[pending_trade.trade_id]

            if(trade is not None):
                trade_id=trade.get_tradeId()
                trade=con.open_pos[trade_id]
                lot_size=trade.get_amount()/100
                stoploss=abs(trade.get_open()-trade.get_stop())
                stoploss_price=trade.get_stop()
                current_price=trade.get_close()

                """
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
                """

                risk=(trade.get_amount()*1000)*abs(trade.get_open()-trade.get_stop())/exchange #trade amount is in Ks of units not lots
                if(signal.action=="BY"):
                    profit=(trade.get_amount()*1000)*(trade.get_close()-trade.get_open())/exchange
                    stoploss_profit=(trade.get_amount()*1000)*(trade.get_stop()-trade.get_open())/exchange
                else:
                    profit=(trade.get_amount()*1000)*(trade.get_open()-trade.get_close())/exchange
                    stoploss_profit=(trade.get_amount()*1000)*(trade.get_open()-trade.get_stop())/exchange

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
                account.balance-=(risk+max(round_half_down(risk*settings.FEE,decimals=2),0.01))
                account.save()

                return True

            else:
                raise Exception("Could not place trade")
    except Exception as exc:
        print(exc)
        raise self.retry(max_retries=5, exc=exc,countdown=1)


@shared_task
def uptimeTask():
    global con
    print("Started Uptime...",con.is_connected())
    while True:
        try:

            if(not con.is_connected()):
                print("Reconnecting...")
                #con.socket.disconnect()
                #con.__init__(access_token=api_token,log_level='error')
                #sleep(10)
            else:
                if(not is_market_open()):
                    trade_count=Trade.objects.filter(status="O").count()
                    if (trade_count>0):
                        con.close_all()

                    sleep(60) #make it an hour
        except Exception as e:
            print(e)
        sleep(10)


"""    

 @shared_task
def updateTasker():
    global con
    offset=0
    limit=10
    while True:
        try:
            print("In Updater",con.is_connected())

            if(not con.is_connected()):
                print("Reconnecting...")
                con.__init__(access_token=api_token,log_level='error')
            else:
                trade_count=Trade.objects.filter(status="O").count()
                if(trade_count>0 and not is_market_open()):
                    con.close_all()
                    
                if(trade_count>0 and offset<trade_count):
                    updateTask.apply_async([offset,offset+limit],priority=5)
                    offset+=limit
                    sleep(0.01)
                else:
                    offset=0

        except Exception as e:
            print(e)
        sleep(1)

@shared_task
def updateTask(start,stop):
    try:
        print("updating",start,stop)
        for trade in Trade.objects.filter(status="O")[start:stop]:
            trade=Trade.objects.get(id=trade.id) #get current state
            if(trade.trade_id in con.open_pos):
                position=con.open_pos[trade.trade_id]
                signal=trade.signal
                timeframe="%s%s" %("m" if signal.timeframe[0].lower()=="m" else "H",signal.timeframe[1:])
                quote=position.get_currency().split("/")[1]     
                stoploss=abs(position.get_close()-position.get_stop())
                stoploss_price=position.get_stop()
                current_price=position.get_close()

                #if(quote!="USD"):
                exchange=con.get_candles("USD"+"/"+quote,period=timeframe,number=1)["askclose"].iloc[0] if quote!="USD" else 1
                if(position.get_isBuy()==True):
                    profit=(position.get_amount()*1000)*(position.get_close()-position.get_open())/exchange
                    stoploss_profit=(position.get_amount()*1000)*(position.get_stop()-position.get_open())/exchange
                else:
                    profit=(position.get_amount()*1000)*(position.get_open()-position.get_close())/exchange
                    stoploss_profit=(position.get_amount()*1000)*(position.get_open()-position.get_stop())/exchange
       
                                
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

                #if(quote!="USD"):
                exchange=con.get_candles("USD"+"/"+quote,period=timeframe,number=1)["askclose"].iloc[0] if (quote!="USD") else 1
                if(position.get_isBuy()==True):
                    profit=(position.get_amount()*1000)*(position.get_close()-position.get_open())/exchange
                else:
                    profit=(position.get_amount()*1000)*(position.get_open()-position.get_close())/exchange              

                trade.profit=round_half_down(profit,decimals=2)
                trade.status="C"
                trade.save()

                account=Account.objects.get(user=trade.user)
                account.balance=round_half_down(account.balance+profit+trade.risk,decimals=2)
                account.save()

                print("closed",trade.trade_id)
            else:
                #check closed from api
                #trade.status="E"
                #trade.save()
                pass

        channel_layer=get_channel_layer()
        async_to_sync(channel_layer.group_send)("trades",{"type":"update_trades","message":trade.user.username})
    except Exception as e:
        print(e)
"""

@shared_task
def updateOpenTask(trade_id):
    try:
        print("updating open",trade_id)
        #for trade in Trade.objects.filter(status="O",trade_id=tradeid):
        trade=Trade.objects.get(trade_id=trade_id,status="O") #get current state
        if(trade.trade_id in con.open_pos):
            position=con.open_pos[trade.trade_id]
            signal=trade.signal
            timeframe="%s%s" %("m" if signal.timeframe[0].lower()=="m" else "H",signal.timeframe[1:])
            quote=position.get_currency().split("/")[1]     
            stoploss=abs(position.get_close()-position.get_stop())
            stoploss_price=position.get_stop()
            current_price=position.get_close()

            #if(quote!="USD"):
            exchange=con.get_candles("USD"+"/"+quote,period=timeframe,number=1)["askclose"].iloc[0] if quote!="USD" else 1
            if(position.get_isBuy()==True):
                profit=(position.get_amount()*1000)*(position.get_close()-position.get_open())/exchange
                stoploss_profit=(position.get_amount()*1000)*(position.get_stop()-position.get_open())/exchange
            else:
                profit=(position.get_amount()*1000)*(position.get_open()-position.get_close())/exchange
                stoploss_profit=(position.get_amount()*1000)*(position.get_open()-position.get_stop())/exchange
    
                            
            trade.stoploss=stoploss
            trade.stoploss_price=stoploss_price
            trade.current_price=current_price
            trade.profit=round_half_down(profit,decimals=2)
            trade.stoploss_profit=round_half_down(stoploss_profit,decimals=2)
            trade.save()

            print("updated",trade.trade_id)

        else:
            #check closed from api
            #trade.status="E"
            #trade.save()
            pass

        
        async_to_sync(channel_layer.group_send,True)("trades",{"type":"update_trades","message":trade.user.username})

    except Exception as e:
        print(e)


@shared_task
def updateCloseTask(trade_id):
    try:
        print("updating close",trade_id)
        #for trade in Trade.objects.filter(status="O",trade_id=tradeid):
        trade=Trade.objects.get(trade_id=trade_id,status="O") #get current state
        if (trade and trade.trade_id in con.closed_pos):
            position=con.closed_pos[trade.trade_id]
                
            quote=position.get_currency().split("/")[1]     
            current_price=position.get_close()

            #if(quote!="USD"):
            exchange=con.get_candles("USD"+"/"+quote,period=timeframe,number=1)["askclose"].iloc[0] if (quote!="USD") else 1
            if(position.get_isBuy()==True):
                profit=(position.get_amount()*1000)*(position.get_close()-position.get_open())/exchange
            else:
                profit=(position.get_amount()*1000)*(position.get_open()-position.get_close())/exchange              

            trade.profit=round_half_down(profit,decimals=2)
            trade.status="C"
            trade.save()

            account=Account.objects.get(user=trade.user)
            account.balance=round_half_down(account.balance+profit+trade.risk,decimals=2)
            account.save()

            print("closed",trade.trade_id)
        else:
            #check closed from api
            #trade.status="E"
            #trade.save()
            pass

        async_to_sync(channel_layer.group_send,True)("trades",{"type":"update_trades","message":trade.user.username})
    except Exception as e:
        print(e)

@shared_task(bind=True)
def closeTradeWorker(self,pk):
    try:    
        #while True:
        print("Closing trades")
        for pending_trade in Trade.objects.filter(status="PC",id=pk)|Trade.objects.filter(status="AC",id=pk):

            pid=pending_trade.id
            signal=pending_trade.signal              
            user=pending_trade.user

            base=signal.pair[0:3]
            quote=signal.pair[3:]
            
            if(pending_trade.status=="PC"):      
                con.close_trade(pending_trade.trade_id,int(pending_trade.lot_size*100),time_in_force="GTC")
                pending_trade.status="AC"
                pending_trade.save()

            
            #if(pending_trade.trade_id in con.closed_pos):
            trade=con.closed_pos[pending_trade.trade_id]
            trade_id=trade.get_tradeId()
            current_price=trade.get_close()

            #if(quote!="USD"):
            exchange=con.get_candles("USD"+"/"+quote,period=signal.timeframe.lower(),number=1).iloc[0]["askclose"] if quote!="USD" else 1
            if(trade.get_isBuy()):
                profit=(trade.get_amount()*1000)*(trade.get_close()-trade.get_open())/exchange
            else:
                profit=(trade.get_amount()*1000)*(trade.get_open()-trade.get_close())/exchange
            
            """
            else:
                if(trade.get_isBuy()):
                    profit=(trade.get_amount()*1000)*(trade.get_close()-trade.get_open())
                else:
                    profit=(trade.get_amount()*1000)*(trade.get_open()-trade.get_close())
            """
    
            pending_trade.current_price=current_price
            pending_trade.previous_price=current_price
            pending_trade.profit=round_half_down(profit,decimals=2)
            pending_trade.status="C"
            pending_trade.save()

            account=Account.objects.get(user=pending_trade.user)
            account.balance=round_half_down(account.balance+profit+pending_trade.risk,decimals=2)
            account.save()

            return True
    except Exception as exc:
        print(exc)
        raise self.retry(max_retries=5, exc=exc,countdown=1)
    
        


@worker_ready.connect
def start(sender=None, headers=None, body=None, **kwargs):
    global con
    global channel_layer
    con=efxfxcmpy(access_token=api_token,log_level='error')
    if(con.is_connected()):
        print("FXCM connected")
        channel_layer=get_channel_layer()
        SocInfo.objects.update_or_create(pk=1,defaults={"offers":json.dumps(con.offers),"account_id":str(con.default_account)})
        uptimeTask.apply_async(priority=0)
    else:
        print("FXCM disconnected")


class efxfxcmpy(fxcmpy):
    def __on_connect__(self, msg=''):
        super().__on_connect__()
        SocInfo.objects.update_or_create(pk=1,defaults={"socket_id":self.socket.sid})


    def __collect_positions__(self):
        super().__collect_positions__()
        for trade_id in self.open_pos.keys():
            updateOpenTask.apply_async([trade_id],priority=5)
        for trade_id in self.closed_pos.keys():
            updateCloseTask.apply_async([trade_id],priority=5)

    def __on_open_pos_update__(self,msg):
        super().__on_open_pos_update__(msg)
        try:
            data = json.loads(msg)

            print(data)
            if 'tradeId' in data and data['tradeId'] != '' and "action" not in data:
                trade_id = int(data['tradeId'])
                updateOpenTask.apply_async([trade_id],priority=5)
        except Exception as e:
            print('Error in __on_open_pos_update',e)


    def __on_closed_pos_update__(self,msg):
        super().__on_closed_pos_update__(msg)
        try:
            data = json.loads(msg)

            if 'tradeId' in data and data['tradeId'] != '' and "action" in data and data["action"] == 'I':
                trade_id = int(data['tradeId'])
                #check if O or PC
                updateCloseTask.apply_async([trade_id],priority=5)
        except Exception as e:
            print('Error in __on_closed_pos_update',e)

        




