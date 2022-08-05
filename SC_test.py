import hmac
import time
import hashlib
import requests
from urllib.parse import urlencode
import json
from config import *

BASE_URL = 'https://stakecube.io/api/v2'

def hashing(query_string):
    return hmac.new(
        SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256
    ).hexdigest()


def get_timestamp():
    return int(time.time() * 1000)

def dispatch_request(http_method):
    session = requests.Session()
    session.headers.update(
        {"Content-Type": "application/x-www-form-urlencoded;charset=utf-8", "X-API-KEY": KEY}
    )
    return {
        "GET": session.get,
        "DELETE": session.delete,
        "PUT": session.put,
        "POST": session.post,
    }.get(http_method, "GET")



# used for sending request requires the signature
def send_signed_request(http_method, url_path, payload={}):
    query_string = urlencode(payload)
    if query_string:
        query_string = "{}&nonce={}".format(query_string, get_timestamp())
        #query_string = "nonce={}&{}".format(get_timestamp(), query_string)
    else:
        query_string = "nonce={}".format(get_timestamp())

    url = (
        BASE_URL + url_path + "?" + query_string + "&signature=" + hashing(query_string)

    )
    print("{} {}".format(http_method, url))
    params = {"url": url, "params": {}}
    response = dispatch_request(http_method)(**params)
    return response.json()


def send_public_request(url_path, payload={}):
    query_string = urlencode(payload, True)
    url = BASE_URL + url_path
    if query_string:
        url = url + "?" + query_string
    print("{}".format(url))
    response = dispatch_request("GET")(url=url)
    return response.json()



#response = send_signed_request("GET", "/user/account")


#print(response['result']['wallets'][0])




#response = send_public_request("/exchange/spot/markets")
def order_book(market):
    ### sells and buys orderbook - bids + asks
    orderbook = send_public_request("/exchange/spot/orderbook?market=" + market)
    sells = len(orderbook['result']['asks']) -1
    lowest_sells = orderbook['result']['asks'][sells]['price']
    highest_buys = orderbook['result']['bids'][0]['price']
    middle_price = (float(lowest_sells) + float(highest_buys)) / 2
    print(f"Ask : {lowest_sells}")
    print(f"Bids : {highest_buys}")
    print(f"In between price : {middle_price}")

def check_open_orders():
    response = send_signed_request("GET", "/exchange/spot/myOpenOrder")
    print(response)

#check_open_orders()


def buy_order():
    ### testing buying
    #test = "?market=bitb_doge&side=SELL&price=0.00300000&amount=1"
    params = {
        'market': 'SCC_BTC',
        'side': 'SELL',
        'price': 0.00000940,
        'amount': 5,
        
    }
    
    response = send_signed_request("POST", "/exchange/spot/order", params)
    print(response)

buy_order()

def test_markets():
    params = {
        "category": "ALTS"
    }
    response = send_public_request("/exchange/spot/markets", params)
    print(response['result'].keys())

#test_markets()






def check_my_trades():
    params = {'market': 'SCC_BTC'}
    response = send_signed_request("GET", "/exchange/spot/myTrades", params)
    print(response)


#check_my_trades()


def cancel_order():
    params = {"orderId": 4013114}
    response = send_signed_request("POST", "/exchange/spot/cancel", params)
    print(response)

def cancel_all():
    params = { "market": "MONK_SCC"}
    response = send_signed_request("POST", "/exchange/spot/cancelAll", params)
    print(response)

#cancel_all()
#cancel_order()
#check_open_orders()

#order_book('BITB_DOGE')





#def rate_limit():
#    rate = send_public_request("/system/rateLimits")
     


#filename = 'orderbook.json'

#with open(filename, 'w') as f:
#    json.dump(response, f, indent = 4)


#with open(filename) as f:
#    orderbook = json.load(f)






#print(response['result']['BITB_DOGE'])




#filename = 'sctest2.json'

#with open(filename, 'w') as f:
#    json.dump(response, f, indent = 4)

#for i in response['result']['wallets']:
#    if i['balance'] != "0.00000000":
#        print(i['asset'] +" " + i['balance'])

#print(response['result']['wallets'][0])
#print(len(response['result']['wallets']))



#filename = 'sctest.json'

#with open(filename, 'w') as f:
#    json.dump(response, f, indent = 4)