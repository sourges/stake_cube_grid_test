import hmac
import time
import hashlib
import requests
from urllib.parse import urlencode
import json


### works for public / private api calls. interacting with "POST" exchange commands as of now does not work as intended 


KEY = ''
SECRET = ''
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



response = send_signed_request("GET", "/user/account")
print(response['result']['wallets'])

#filename = 'sctest.json'

#with open(filename, 'w') as f:
#    json.dump(response, f, indent = 4)
