from channels.generic.websocket import JsonWebsocketConsumer
from .models import Trade
from .serializers import TradeSerializer
from asgiref.sync import async_to_sync
from datetime import datetime
import pytz
import json
from efxapi.common import is_market_open,get_market_times

class TradesConsumer(JsonWebsocketConsumer): #try jsonwebsocket
    def connect(self):
        if("user" in self.scope):
            async_to_sync(self.channel_layer.group_add)(
                "trades",
                self.channel_name
            )
            
            self.accept()
            open_trades=Trade.objects.filter(user__username=self.scope["user"].username,status="O")
            serializer=TradeSerializer(open_trades,many=True)
            if(is_market_open()):
                self.send_json({"status_code":200,"data":serializer.data})
            else:
                self.send_json({"status_code":451,"data":serializer.data,"detail":"%s" %(get_market_times()[1].strftime("%a %H:%M"))})
            
        else:
            self.send_json({"status_code":401,"data":[]})
            self.close()

    def disconnect(self, close_code):
         async_to_sync(self.channel_layer.group_discard)(
           "trades",
            self.channel_name
        )



    def update_trades(self,event):
        #if(event["message"]==self.scope["user"].username):
        open_trades=Trade.objects.filter(user__username=self.scope["user"].username,status="O")
        serializer=TradeSerializer(open_trades,many=True)
        if(is_market_open()):
            self.send_json({"status_code":200,"data":serializer.data})
        else:
            self.send_json({"status_code":451,"data":serializer.data,"detail":"%s" %(get_market_times()[1].strftime("%a %H:%M"))})

