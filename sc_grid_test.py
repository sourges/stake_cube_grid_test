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
    query_string = urlencode(payload, True)
    if query_string:
        query_string = "{}&nonce={}".format(query_string, get_timestamp())
        #query_string = "{}".format(query_string)
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

check_open_orders()

def close_order():
    params = {
        "orderId": "4013114"
        # id: 3908643
    }
    response = send_signed_request("POST", "/exchange/spot/cancel", params)
    print(response)
    

#close_order()

def send_order():
    params = {
        "market": "SCC_BTC",
        "side": "BUY",
        "price": .000009,
        "amount": 10

    }

    response = send_signed_request("POST", "/exchange/spot/order", params)
    print(response)


# nonce = get_timestamp()

# string = f"nonce={nonce}"
# #string = f"orderId=3911505&nonce={nonce}"

# sign = hashing(string)
# url = f"https://stakecube.io/api/v2/exchange/spot/myOpenOrder?nonce={nonce}&signature={sign}"
# #url = f"https://stakecube.io/api/v2/exchange/spot/cancel" #?orderId=3911505&nonce={nonce}&signature={sign}"
# #params = f"orderId=3911505&nonce={nonce}&signature={sign}"
# #response = requests.post(url, headers = headers, data = params)
# response = requests.get(url, headers = headers)
# print(response)
# print(response.json())