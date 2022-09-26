# after testing for a month some errors found.
# current errors - 'invalid signature parameter', 'balance to small', 'pending process need to finish'
#                  'error': 'Order rejected. Error-Code: 99' - have only seen once


# also, sometimes on startup while placing order, invalid signature parameter is sometimes error'd.  will change logic after testing of new errors are completed


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
    string = f"market={config.trading_pair}&side={side}&price={price}&amount={position_size}&nonce={get_timestamp()}"
    sign = hashing(string)
    params = f"market={config.trading_pair}&side={side}&price={price}&amount={position_size}&nonce={get_timestamp()}&signature={sign}"
    url = "https://stakecube.io/api/v2/exchange/spot/order"
    response = requests.post(url, headers = headers, data = params)
    print(response.json())
    return response.json()




# doesnt have orderId

def order_history():
	string = f"market={config.trading_pair}&nonce={get_timestamp()}"
	sign = hashing(string)
	url = f"https://stakecube.io/api/v2/exchange/spot/myOrderHistory?market={config.trading_pair}&nonce={get_timestamp()}&signature={sign}"
	response = requests.get(url, headers = headers)
	print(response)
	print(response.json())
	return response.json()


# past trades - has orderID but not if order was filled 

def my_trades():
    string = f"market={config.trading_pair}&nonce={get_timestamp()}"
    sign = hashing(string)
    url = f"https://stakecube.io/api/v2/exchange/spot/myTrades?market={config.trading_pair}&nonce={get_timestamp()}&signature={sign}"
    response = requests.get(url, headers = headers)
    #print(response.json())
    return response.json()



def get_single_ticker():
	url = f"https://stakecube.io/api/v2/exchange/spot/orderbook?market={config.trading_pair}"
	orderbook = requests.get(url, headers = headers)
	sell_count = len(orderbook.json()['result']['asks'])

	best_ask = orderbook.json()['result']['asks'][sell_count-1]['price']
	best_bid = orderbook.json()['result']['bids'][0]['price']

	average = (float(best_ask) + float(best_bid)) / 2
	print(f"average - {average}")

	return average



# asset / balance / balanceInOrder / balanceInMasternodes / address (wallet address)

def get_account():
    string = f"nonce={get_timestamp()}"
    sign = hashing(string)
    url = f"https://stakecube.io/api/v2/user/account?nonce={get_timestamp()}&signature={sign}"
    response = requests.get(url, headers = headers)
    for i in range(len(response.json()['result']['wallets'])):
        if float(response.json()['result']['wallets'][i]['balance']) > 0:
            print(f"{response.json()['result']['wallets'][i]['asset']} - {response.json()['result']['wallets'][i]['balance']}")



def get_open_order_info():
    string = f"nonce={get_timestamp()}"
    sign = hashing(string)
    url = f"https://stakecube.io/api/v2/exchange/spot/myOpenOrder?nonce={get_timestamp()}&signature={sign}"
    response = requests.get(url, headers = headers)
    return response.json()['result']



# def rate_limit():
#     string = f"nonce={get_timestamp()}"
#     sign = hashing(string)
#     url = f"https://stakecube.io/api/v2/system/rateLimits?nonce={get_timestamp()}&signature={sign}"
#     response = requests.get(url, headers = headers)
#     print(response)
#     print(response.json())

# rate_limit()



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


# all prints in this loop for testing, will give more meaningful info later / take out random prints

while True:

    time.sleep(1)
    try:
        closed_trades = my_trades()
    except Exception as e:
        print("check closed trades failed")
    else:
        print("*****************************************")
        	
    closed_ids = []

    for closed_trade in closed_trades['result']:
        closed_ids.append(closed_trade['orderId'])


    for sell_order in sell_orders:
        for i in range(len(closed_trades['result'])):
            try:                                                                                            # might take out try since the error with the bellow if statement has been corrected
                if sell_order['orderId'] == closed_trades['result'][i]['orderId']:               
                    print("****************************** sell_order loop ***************************")
                    print("trade is closed")
                    print("old sell_orders")
                    print(sell_orders)
                    print(sell_order['price'])
                    print(f"sell_order orderId = {sell_order['orderId']}")
                    new_buy_price = float(sell_order['price']) - config.grid_size
                    print(f"**************test************ {new_buy_price}")
                    time.sleep(1)
                    new_buy_order = place_order(new_buy_price, config.position_size, side = "BUY")



                    while new_buy_order['success'] == False:                     # 2 errors fixed here ( currently testing ) - invalid signature parameter, pending process need to finish
                        print("************** BUY ERROR*************")           # this will give an infiniate loop if not enough balance, will add if statement 
                        time.sleep(1)                        
                        new_buy_order = place_order(new_buy_price, config.position_size, side = "BUY")




                    buy_orders.append(new_buy_order['result'])
                    print(f"buy_orders - {buy_orders}")
                    
                    break
            except Exception as e:
                print("/////////////////////// if error //////////////")
                continue	




    for buy_order in buy_orders:
        for i in range(len(closed_trades['result'])):
            if buy_order['orderId'] == closed_trades['result'][i]['orderId']:
                print("**********************************************  buy_order loop ****************************")
                print("trade is closed")
                print("old buy_orders")
                print(buy_orders)
                print(buy_order['price'])
                print(f"buy_order orderId = {buy_order['orderId']}")
                new_sell_price = float(buy_order['price']) + config.grid_size
                print(f"********test********** {new_sell_price}")
                time.sleep(1)
                new_sell_order = place_order(new_sell_price, config.position_size, side = "SELL")





                while new_sell_order['success'] == False:
                    print("**************pending process need to finish ERROR*************")     # 2 errors fixed here ( currently testing ) - invalid signature parameter, pending process need to finish
                    time.sleep(1)                                                                # this will give an infiniate loop if not enough balance, will add if statement
                    new_sell_order = place_order(new_sell_price, config.position_size, side = "SELL")



                sell_orders.append(new_sell_order['result'])
                print(f"sell_orders - {sell_orders}")
                
                break


    for order_id in closed_ids:  # need try here?
        buy_orders = [buy_order for buy_order in buy_orders if buy_order['orderId'] != order_id]

        sell_orders = [sell_order for sell_order in sell_orders if sell_order['orderId'] != order_id]

    print(f"pausing {config.trading_pair}")
    time.sleep(5)
