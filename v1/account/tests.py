from rest_framework.test import APITestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Account,Deposit,PendingDeposit,PendingWithdrawal
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

class TestLogin(APITestCase):
    def setUp(self):
        self.client=APIClient()
        self.token="testtoken"

        user=User.objects.create_user("TestUser",password="testuser")
        account=Account.objects.create(user=user,name="TestName",phone="0",email="email@gmail.com",account_type="R",balance=0.0)
        PendingDeposit.objects.create(account=account,amount=10,deposit_type="mtn")
        PendingWithdrawal.objects.create(account=account,amount=20,withdrawal_type="mtn")
        token=Token.objects.create(user=user)
        self.user_token=token.key
           
    def testAccessNoToken(self):
        response=self.client.get("/v1/account/user")
        self.assertEquals(status.HTTP_401_UNAUTHORIZED,response.status_code,"Expected 401 received %d" %(response.status_code))

    def testLoginGet(self):
        response=self.client.get("/v1/account/login")
        self.assertEqual(response.status_code,status.HTTP_405_METHOD_NOT_ALLOWED,"Expected 405 received %d" %(response.status_code))

    def testLoginPostNoToken(self):
        response=self.client.post("/v1/account/login",{})
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST,"Expected 400 received %d" %(response.status_code))

    def testLoginPostToken(self):
        response=self.client.post("/v1/account/login",{"token":self.token})
        self.assertContains(response,"token")

    def testAcessWithEmailToken(self):
        response=self.client.post("/v1/account/login",{"token":self.token})
        self.token=response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" %(self.token))
        response=self.client.get("/v1/account/user")
        self.assertEqual(status.HTTP_200_OK,response.status_code,"Expected 200 received %d" %(response.status_code))
    
    def testAcessWithPhoneToken(self):
        response=self.client.post("/v1/account/login",{"token":self.token,"phone":"0272990302","name":"Testuser"})
        self.token=response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" %(self.token))
        response=self.client.get("/v1/account/user")
        self.assertEqual(status.HTTP_200_OK,response.status_code,"Expected 200 received %d" %(response.status_code))

    
    def testGetUserDepositsWithdrawls(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token %s" %(self.user_token))
        response=self.client.get("/v1/account/user")
        print(response.content)
        self.assertContains(response,"deposits")
        self.assertContains(response,"withdrawals")
