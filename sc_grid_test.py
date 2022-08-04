# clean this whole mess up


import hmac
import time
import hashlib
import requests
from urllib.parse import urlencode
import json
import config


headers = {"Content-Type": "application/x-www-form-urlencoded;charset=utf-8", "X-API-KEY": config.KEY}

def hashing(query_string):
    return hmac.new(
        config.SECRET.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256
    ).hexdigest()

def get_timestamp():
    return int(time.time() * 1000)



def get_order_info():
	string = f"nonce={get_timestamp()}"
	sign = hashing(string)
	url = f"https://stakecube.io/api/v2/exchange/spot/myOpenOrder?nonce={get_timestamp()}&signature={sign}"
	response = requests.get(url, headers = headers)
	return response.json()['result']



def close_single_order(orderId):
	string = f"orderId={orderId}&nonce={get_timestamp()}"    # nonce has to come after
	sign = hashing(string)
	params = f"orderId={orderId}&nonce={get_timestamp()}&signature={sign}"
	url =  "https://stakecube.io/api/v2/exchange/spot/cancel"
	response = requests.post(url, headers = headers, data = params)
	print(response)
	print(response.json())



# places single order 

def place_order(price, position_size, side):
    string = f"market=SCC_BTC&side={side}&price={price}&amount={position_size}&nonce={get_timestamp()}"
    sign = hashing(string)
    params = f"market=SCC_BTC&side={side}&price={price}&amount={position_size}&nonce={get_timestamp()}&signature={sign}"
    url = "https://stakecube.io/api/v2/exchange/spot/order"
    response = requests.post(url, headers = headers, data = params)
    print(response.json())
    return response.json()



# doesnt have orderId

def order_history():
	string = f"market=SCC_BTC&nonce={get_timestamp()}"
	sign = hashing(string)
	url = f"https://stakecube.io/api/v2/exchange/spot/myOrderHistory?market=SCC_BTC&nonce={get_timestamp()}&signature={sign}"
	response = requests.get(url, headers = headers)
	print(response)
	print(response.json())
	return response.json()


# past trades - has orderID but not if order was filled 

def my_trades():
	string = f"market=SCC_BTC&nonce={get_timestamp()}"
	sign = hashing(string)
	url = f"https://stakecube.io/api/v2/exchange/spot/myTrades?market=SCC_BTC&nonce={get_timestamp()}&signature={sign}"
	response = requests.get(url, headers = headers)
	return response.json()



def get_single_ticker():
	url = "https://stakecube.io/api/v2/exchange/spot/orderbook?market=SCC_BTC"
	orderbook = requests.get(url, headers = headers)
	sell_count = len(orderbook.json()['result']['asks'])

	best_ask = orderbook.json()['result']['asks'][sell_count-1]['price']
	best_bid = orderbook.json()['result']['bids'][0]['price']

	average = (float(best_ask) + float(best_bid)) / 2
	print(f"average - {average}")

	return average


# will take out prints later - using them for testing right now

def test_grid():

	current_price = get_single_ticker()  # to get the median price
	buy_orders = []
	sell_orders = []

	# sell grid

	for i in range(config.number_sell_gridlines):
		price = current_price + (config.grid_size * (i+1))
		price = round(price, 8)
		time.sleep(1)
		order = place_order(price, config.position_size, side = "SELL")
		sell_orders.append(order['result'])


 	# buy grid

	for i in range(config.number_buy_gridlines):
		price = current_price - (config.grid_size * (i+1))
		price = round(price, 8)

		time.sleep(1)
		order = place_order(price, config.position_size, side = "BUY")
		buy_orders.append(order['result'])

	return sell_orders, buy_orders


sell_orders, buy_orders = test_grid()  
closed_orders = []


# closed_trades = my_trades() # ['orderId'] 
orders = get_order_info()     # ['id'] - open
# sell_orders, buy_orders     # ['orderId'] 



# all prints in this loop for testing, will give more meaningful info later / take out random prints

while True:

    time.sleep(1)
    try:
        closed_trades = my_trades()
    except Exception as e:
        print("check closed trades failed")
    else:
        print("*****************************************")
        	

        for sell_order in sell_orders:
            for i in range(len(closed_trades['result'])):
               # try:                                                       # testing try off and on while figuring out random error
                    if sell_order['orderId'] == closed_trades['result'][i]['orderId']:    
                        print("****************************** sell_order loop ***************************")
                        print("trade is closed")
                        print("old sell_orders")
                        print(sell_orders)
                        print(sell_order['price'])
                        print(f"sell_order orderId = {sell_order['orderId']}")
                        new_buy_price = float(sell_order['price']) - config.grid_size
                        new_buy_order = place_order(new_buy_price, config.position_size, "BUY")
                        buy_orders.append(new_buy_order['result'])
                        print(f"buy_orders - {buy_orders}")


                        print(i)
                        del sell_orders[i]
                        print("new sell_orders array")
                        print(sell_orders)
                        break
                #except Exception as e:
                 #   print("/////////////////////// if error //////////////")
                  #  continue	



        for buy_order in buy_orders:
        	for i in range(len(closed_trades['result'])):
        		if buy_order['orderId'] == closed_trades['result'][i]['orderId']:
        			print("**********************************************  buy_order loop ****************************")
        			print("trade is closed")
        			print("old buy_orders")
        			print(buy_orders)
        			print(buy_order['price'])
        			print(f"buy_order orderId = {buy_order['orderId']}")
        			new_buy_price = float(buy_order['price']) + config.grid_size
        			new_buy_order = place_order(new_buy_price, config.position_size, "SELL")
        			sell_orders.append(new_buy_order['result'])
        			print(f"sell_orders - {sell_orders}")


        			print(i)
        			del buy_orders[i]
        			print("new buy_orders array")
        			print(buy_orders)
        			break

        print("pausing")
        time.sleep(5)

