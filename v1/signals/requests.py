from v1.trades.models import Trade
from v1.account.models import Account
from django.db.models import Sum
import requests
import math
from v1.soc.socket import get_candles,get_usableMargin
from efxapi.common import round_half_up,round_half_down,get_market_times
from django.conf import settings

#get pair info as part of retrieve
def getMarketInfo(signal):
    try:
        base=signal.pair[0:3]
        quote=signal.pair[3:]
        atr=settings.ATR_MUL*signal.atr
        
        usable_margin=get_usableMargin()
        print("Usable margin",usable_margin)
        leverage=400 #get leverage
        #leverage2=con.get_model(models=["LeverageProfile"])
        #print("Leverage",leverage2)
        usable_margin-=(Account.objects.all().aggregate(balance__sum=Sum('balance'))["balance__sum"] or 0.0)+(Trade.objects.filter(status="O").aggregate(risk__sum=Sum('risk'))["risk__sum"] or 0.0)  #subtract sum of balances and trade risks
        usable_margin/=Account.objects.all().count()
        print("Margin per user",usable_margin)

        #if(quote!="USD"):
        exchange=get_candles("USD"+"/"+quote,signal.timeframe)["ask"] if quote!="USD" else 1
        rate=get_candles(base+"/"+quote,signal.timeframe)
        per_pip=10 if quote!="JPY" else 1000 #pip value is 1000 for yen 10 for USD
        
        rate=rate["ask"] if signal.action=="BY" else rate["bid"]
        
        """if(signal=="BY"):
            rate=rate["ask"] #extra work for non_majors
        else:
            rate=rate["bid"]
        """
            
        print("exchange",exchange)
        min_risk=signal.min_lot*((per_pip/exchange) * atr)
        print("min_risk",min_risk)

        if((signal.min_lot*100000*rate/(leverage*exchange))>usable_margin):
            raise Exception() #no free margin

        max_lot=(usable_margin*leverage)/(100000*rate/exchange)
        print("max_lot",max_lot)
        max_risk=max_lot*((per_pip/exchange) * atr)
        print("max_risk",max_risk)

        if(max_lot<signal.min_lot):
            raise Exception() #no free margin
        
        """
        else:
            rate=get_candles(base+"/"+quote,signal.timeframe)
            if(signal=="BY"):
                rate=rate["ask"] #extra work for non_majors
            else:
                rate=rate["bid"]

            min_risk=signal.min_lot*(10 * atr)
            print("min_risk",min_risk)

            if((signal.min_lot*100000*rate/leverage)>usable_margin):
                raise Exception() #no free margin

            max_lot=(usable_margin*leverage)/(100000*rate)
            print("max_lot",max_lot)
            max_risk=max_lot*(10 * atr)
            print("max_risk",max_risk)

            if(max_lot<signal.min_lot):
                raise Exception() #no free margin
        """
        close_time,open_time=get_market_times()

        return {"id":signal.id,
                "min_risk":round_half_up(min_risk,2),
                "max_risk":round_half_down(max_risk,2),
                "close_time":close_time.strftime("%a %H:%M UTC"),
                "open_time":open_time.strftime("%a %H:%M UTC")}
    except Exception as e:
        print(e)
        raise Exception()




