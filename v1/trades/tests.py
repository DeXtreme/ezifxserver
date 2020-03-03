from rest_framework.test import APITestCase,APIClient
from v1.signals.models import SignalGenerator,Signal
from django.contrib.auth.models import User
from v1.account.models import Account
from .models import Trade
from rest_framework.authtoken.models import Token
from rest_framework import status

class TestSignals(APITestCase):


    def setUp(self):
        self.client=APIClient()        
        generator=SignalGenerator.objects.create(name="TestGen",generator_type="R")
        user=User.objects.create_user("TestUser",password="testuser")
        account=Account.objects.create(user=user,name="TestName",phone="0",email="email@gmail.com",account_type="R",balance=0.0)
        token=Token.objects.create(user=user)
        signal=Signal.objects.create(pair="EURUSD",action="BY",timeframe="D",bars=[[1.0,2.0]],generator=generator)
        self.signal_id=signal.id
        self.user_token=token.key
        
    def testOpenTrade(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" %(self.user_token))
        response=self.client.post("/v1/trades/",{"signal":self.signal_id,"risk":10},format="json")
        self.assertContains(response,"stoploss")
    
    def testCloseTrade(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" %(self.user_token))
        response=self.client.post("/v1/trades/",{"signal":self.signal_id,"risk":10},format="json")
        trade_id=response.data["id"]
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" %(self.user_token))
        response=self.client.get("/v1/trades/%d/close/" %(trade_id))
        print(response)
        self.assertContains(response,"C")

    def testGetTrades(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" %(self.user_token))
        response=self.client.post("/v1/trades/",{"signal":self.signal_id,"risk":10},format="json")
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" %(self.user_token))
        response=self.client.get("/v1/trades/")
        self.assertContains(response,"pair")
        

        
        

        