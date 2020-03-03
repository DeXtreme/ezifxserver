from rest_framework.test import APITestCase,APIClient
from .models import SignalGenerator,Signal
from django.contrib.auth.models import User
from v1.account.models import Account
from rest_framework.authtoken.models import Token
from rest_framework import status

class TestSignals(APITestCase):


    def setUp(self):
        self.client=APIClient()
        
        generator=SignalGenerator.objects.create(name="TestGen",generator_type="RG")
        self.generator_token=generator.token

        Signal.objects.create(pair="EURUSD",action="BY",timeframe="D",bars=[1.0,2.0],generator=generator)
        Signal.objects.create(pair="EURUSD",action="BY",timeframe="D",bars=[1.0,2.0],generator=generator)
        Signal.objects.create(pair="EURUSD",action="BY",timeframe="D",bars=[1.0,2.0],generator=generator)

        user=User.objects.create_user("TestUser",password="testuser")
        Account.objects.create(user=user,name="TestName",phone="0",email="email@gmail.com",account_type="RG",balance=0.0)
        token=Token.objects.create(user=user)
        self.user_token=token.key
        
    def testAddSignalNoToken(self):
        response=self.client.post("/v1/signals/",{"pair":"eurusd","action":"BY","timeframe":"D",
        "atr":10,"min_lot":0.1},format="json")
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED,"Expected 401 received %d" %(response.status_code))


    def testAddSignalsNoBars(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" %(self.generator_token))
        response=self.client.post("/v1/signals/",{"pair":"eurusd","action":"BY","timeframe":"D",
        "atr":10,"min_lot":0.1},format="json")
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST,"Expected 400 received %d" %(response.status_code))

    def testAddSignalsInvalidBars(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" %(self.generator_token))
        response=self.client.post("/v1/signals/",{"pair":"eurusd","action":"BY","timeframe":"D",
        "atr":10,"min_lot":0.1,"bars":[[1,2,3],[3,4,5]]},format="json")
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST,"Expected 400 received %d" %(response.status_code))

    def testAddSignals(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" %(self.generator_token))
        response=self.client.post("/v1/signals/",{"pair":"eurusd","action":"BY","timeframe":"D",
        "atr":10,"min_lot":0.1,"bars":[1.0,2.0,3.0,4.0]},format="json")
        self.assertEqual(response.status_code,status.HTTP_200_OK,"Expected 200 received %d" %(response.status_code))

    def testGetSignalsNoToken(self):
        response=self.client.get("/v1/signals/")
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED,"Expected 401 received %d" %(response.status_code))

    def testGetSignals(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" %(self.user_token))
        response=self.client.get("/v1/signals/")
        self.assertContains(response,"pair")
        #self.assertEqual(response.status_code,status.HTTP_200_OK,"Expected 200 received %d" %(response.status_code))

    def testGetSignalsNext(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" %(self.user_token))
        response=self.client.get("/v1/signals/?next=0")
        print(response.data)
        signal_id=response.data["results"][1]["id"]
        next_signal_id=response.data["results"][0]["id"]
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" %(self.user_token))
        response=self.client.get("/v1/signals/?next=%d" %(signal_id))
        self.assertEqual(response.data["results"][0]["id"],next_signal_id)

    def testGetSignalsPrev(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" %(self.user_token))
        response=self.client.get("/v1/signals/")
        print(response.data)
        signal_id=response.data["results"][0]["id"]
        prev_signal_id=response.data["results"][1]["id"]
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" %(self.user_token))
        response=self.client.get("/v1/signals/?prev=%d" %(signal_id))
        self.assertEqual(response.data["results"][0]["id"],prev_signal_id)

    def testGetSignalInfo(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" %(self.generator_token))
        response=self.client.post("/v1/signals/",{"pair":"eurusd","action":"BY","timeframe":"D",
        "atr":10,"min_lot":0.1,"bars":[[1.0,2.0],[2.0,3.0]]},format="json")
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" %(self.user_token))
        response=self.client.get("/v1/signals/")
        signal_id=response.data["results"][0]["id"]
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" %(self.user_token))
        response=self.client.get("/v1/signals/%d/" %(signal_id))
        self.assertContains(response,"max")
