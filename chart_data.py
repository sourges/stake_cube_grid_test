# for now keeping chart data seperate from grid bot


import hmac
import time
import hashlib
import requests
from urllib.parse import urlencode
import json
import config
import matplotlib.pyplot as plt

headers = {"Content-Type": "application/x-www-form-urlencoded;charset=utf-8", "X-API-KEY": config.KEY}

filename = "chart_data.json"

def hashing(query_string):
    return hmac.new(
        config.SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256
    ).hexdigest()

def get_timestamp():
    return int(time.time() * 1000)


def get_account():
    string = f"nonce={get_timestamp()}"
    sign = hashing(string)
    url = f"https://stakecube.io/api/v2/user/account?nonce={get_timestamp()}&signature={sign}"
    response = requests.get(url, headers = headers)
    print(response)
    print(response.json())


def chart_data():
	string = f"nonce={get_timestamp()}"
	sign = hashing(string)
	url = f"https://stakecube.io/api/v2/exchange/spot/ohlcData?market=BITB_DOGE&interval=1h"
	response = requests.get(url, headers = headers)
	#with open(filename, 'w') as f:
	#	json.dump(response.json(), f)
	print(response)
	# print(len(response.json()['data']['lines']))
	print(len(response.json()['data']['trades']))
	#print(response.json())

chart_data()
