

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

#my_trades()

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
    #print(response.json()['result']['wallets'][0])
    for i in range(len(response.json()['result']['wallets'])):
        if float(response.json()['result']['wallets'][i]['balance']) > 0:
            print(f"{response.json()['result']['wallets'][i]['asset']} - {response.json()['result']['wallets'][i]['balance']}")
            

#get_account()

def get_open_order_info():
    string = f"nonce={get_timestamp()}"
    sign = hashing(string)
    url = f"https://stakecube.io/api/v2/exchange/spot/myOpenOrder?nonce={get_timestamp()}&signature={sign}"
    response = requests.get(url, headers = headers)
    #print(response.json()['result'])
    return response.json()['result']


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
orders = get_open_order_info()     # ['id'] - open
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
        	
    closed_ids = []

    for closed_trade in closed_trades['result']:
        closed_ids.append(closed_trade['orderId'])

    



    for sell_order in sell_orders:
        for i in range(len(closed_trades['result'])):
            try:                                                       # testing try
                if sell_order['orderId'] == closed_trades['result'][i]['orderId']:                # testing more - looks like an error happens when a buy gets 'invalid signature parameter'
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
                    buy_orders.append(new_buy_order['result'])
                    print(f"buy_orders - {buy_orders}")


                    print(i)
                    print("new sell_orders array")
                    print(sell_orders)
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
                sell_orders.append(new_sell_order['result'])
                print(f"sell_orders - {sell_orders}")
                print(i)
                #del buy_orders[i]
                print("new buy_orders array")
                print(buy_orders)
                break


    for order_id in closed_ids:
        buy_orders = [buy_order for buy_order in buy_orders if buy_order['orderId'] != order_id]

        sell_orders = [sell_order for sell_order in sell_orders if sell_order['orderId'] != order_id]

    print("pausing")
    time.sleep(5)



# a quick CLI menu so user does not have to constantly change out traded pairs
# eventually will add grid_size, amount, etc
# funtional but useless for now



# def main():
#     loop_dict = {'A': get_account, 'B': get_open_order_info, 'C': }
#     while True:
#         print()
#         print("Welcome to the test menu")
#         print('''What would you like to do:
# A - Check available account balances 
# B - Check open positions ''')
#         print()
#         answer = input("Enter 'A', 'B' or 'Q' to quit: ").upper()
#         if answer == 'Q':
#             break
#         for x in loop_dict:
#             if x == answer:
#                 loop_dict[x]()
#                 #test = loop_dict[x]()      # - printing info from function or creating an object that has value? - figure out as loop gets bigger
#                 #print(test)



# if __name__ == '__main__':
#     main()