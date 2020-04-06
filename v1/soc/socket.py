from fxcmpy import fxcmpy
import json
import requests
from .models import SocInfo

api_token="f8a14411f06fa9f1f5af75d53ed45a711209c7dc"
offers=[]
account_id=None



#load acc_id,offers and socketid from db
def initialize():
    global api_token
    global offers
    global account_id
    try:

        socinfo=SocInfo.objects.get(pk=1)
        account_id=socinfo.account_id
        socket_id=socinfo.socket_id
        offers=json.loads(socinfo.offers)

    except Exception as e:
        print(e)
        raise Exception("Run Worker First")

def get_credentials():
    socinfo=SocInfo.objects.get(pk=1)
    socket_id=socinfo.socket_id

    bearer_token = 'Bearer '+socket_id+api_token

    request_headers = {
        'User-Agent': 'request',
        'Authorization': bearer_token,
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'}
    
    return request_headers


def get_candles(pair,period):
    global offers
    
    response=requests.get("https://api-demo.fxcm.com:443/candles/"+str(offers[pair])+"/"+period.lower(),params={"num":"1"},headers=get_credentials())

    if(response.status_code==200):
        try:
            response=json.loads(response.text)

            if("error" in response["response"] and response["response"]["error"]):
                raise Exception()

            return {"ask":response["candles"][0][6],"bid":response["candles"][0][2]}
        except:
            print(response.text)
            raise Exception("Server error")
    else:
        raise Exception("Connection error")

def get_usableMargin():
    
    response=requests.get("https://api-demo.fxcm.com:443/trading/get_model",headers=get_credentials(),params={"models":"Account"})
    
    if(response.status_code==200):
        try:
            print(response.text)
            response=json.loads(response.text)

            if("error" in response["response"]):
                raise Exception()

            return response["accounts"][0]["usableMargin"]
        except:
            print(response.text)
            raise Exception("Server error")
    else:
        raise Exception("Connection error")

"""

def initialize():
    global bearer_token
    global api_token
    global offers
    global request_headers
    global account_id
    try:
        with open("account","r") as acc:
            account_id=acc.readline().rstrip()
            offers_json=acc.readline().rstrip()
        
        with open("socketid","r") as soc:
            socket_id=soc.readline().rstrip()

        bearer_token = 'Bearer '+socket_id+api_token
        offers=json.loads(offers_json)

        request_headers = {
            'User-Agent': 'request',
            'Authorization': bearer_token,
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'}
    except Exception as e:
        print(e)
        raise Exception("Run Worker First")

def open_trade(pair,buy,lot,stop):
    global request_headers
    data={
        "account_id":account_id,
        "symbol":pair,
        "is_buy":("true" if buy else "false"),
        "rate":0,
        "amount":int(lot*100),
        "stop":(-1*stop if buy else stop),
        "trailing_step":1,
        "is_in_pips":True,
        "order_type":"AtMarket",
        "time_in_force":"GTC"
    }

    response=requests.post("https://api-demo.fxcm.com:443/trading/open_trade",headers=request_headers,data=data)
    print(response.text)
    if(response.status_code==200):
        try:
            response=json.loads(response.text)
            if("orderId" in response["data"]):
                orderid=response['data']["orderId"]
                for i in range(5):
                    response=requests.get("https://api-demo.fxcm.com:443/trading/get_model",headers=request_headers,params={"models":"Order"})
                    print(response.text)
                    if(response.status_code==200):
                        response=json.loads(response.text)
                        order=(x for x in response["orders"] if x["orderId"]==orderid)
                        if(order and "tradeId" in order):
                            tradeid=order["tradeId"]
                            response=requests.get("https://api-demo.fxcm.com:443/trading/get_model",headers=request_headers,params={"models":"OpenPosition"})
                            print(response.text)
                            if(response.status_code==200):
                                response=json.loads(response.text)
                                return (x for x in response["open_positions"] if x["tradeId"]==tradeid)
                            else:
                                raise Exception("Connection error")
                        
                    else:
                        raise Exception("Connection error")
                raise Exception("Order not placed")
        except Exception as e:
            print(e)
            raise Exception("Server error")
    else:
        raise Exception("Connection error")


def close_trade(tradeid,lot):
    global request_headers
    data={
        "trade_id":tradeid,
        "rate":0,
        "amount": int(lot*100),
        "at_market": 0,
        "order_type": "AtMarket",
        "time_in_force": "GTC"
    }

    response=requests.post("https://api-demo.fxcm.com:443/trading/close_trade",headers=request_headers,data=data)
    if(response.status_code==200):
        response=json.loads(response.text)
        response=requests.get("https://api-demo.fxcm.com:443/trading/get_model",headers=request_headers,params={"models":"ClosedPosition"})
        print(response.text)
        if(response.status_code=="200"):
            response=json.loads(response.text)
            return (x for x in response["closed_positions"] if x["tradeId"]==tradeid)
        else:
            raise Exception("Connection error")
    else:
        raise Exception("Connection error")
                        
"""
    
    
        
        