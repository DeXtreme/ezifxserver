from channels.generic.websocket import JsonWebsocketConsumer
from .models import Trade
from .serializers import TradeSerializer
from asgiref.sync import async_to_sync
from datetime import datetime
import json

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
            if(not self.check_market_close()):
                self.send_json({"status_code":200,"data":serializer.data})
            else:
                self.send_json({"status_code":451,"data":serializer.data})
            
        else:
            self.send_json({"status_code":401,"data":[]})
            self.close()

    def disconnect(self, close_code):
         async_to_sync(self.channel_layer.group_discard)(
           "trades",
            self.channel_name
        )

    def check_market_close(self):
        time=datetime.utcnow()
        return ((time.weekday==4 and time.hour>21) or (time.weekday==5) or (time.weekday==6 and time.hour<23)
        or (time.month==12 and time.date==24 and time.hour>21) or (time.month==12 and time.date==25) or (time.month==12 and time.date==25 and time.hour<23)
        or (time.month==12 and time.date==31 and time.hour>21) or (time.month==1 and time.date==1) or (time.month==1 and time.date==1 and time.hour<23))

    def update_trades(self,event):
        if(event["message"]==self.scope["user"].username):
            open_trades=Trade.objects.filter(user__username=self.scope["user"].username,status="O")
            serializer=TradeSerializer(open_trades,many=True)
            if(not self.check_market_close()):
                self.send_json({"status_code":200,"data":serializer.data})
            else:
                self.send_json({"status_code":451,"data":serializer.data})

