# this whole thing needs cleaning up lmao



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
	#print(response.json()[])
	return response.json()['result']

# orders = get_order_info()  # - active with id
# active_orders = []
# sell_orders = [12345, 3454566, 4087354]

# for count in range(len(orders['result'])):
# 	active_orders.append(orders['result'][count]['id'])
# print(active_orders)
# for i in sell_orders:
# 	if i not in active_orders:
# 		new_buy_price = float(order_info['price']) - grid_size

		




def close_single_order(orderId):
	string = f"orderId={orderId}&nonce={get_timestamp()}"    # nonce has to come after
	sign = hashing(string)
	params = f"orderId={orderId}&nonce={get_timestamp()}&signature={sign}"
	url =  "https://stakecube.io/api/v2/exchange/spot/cancel"
	response = requests.post(url, headers = headers, data = params)
	print(response)
	print(response.json())


#orderId = ''
#close_single_order(orderId)






# places single order 
# will need to exchange alot of info for variables to be passed through
def place_order(price, position_size, side):
	string = f"market=BITB_DOGE&side={side}&price={price}&amount={position_size}&nonce={get_timestamp()}"
	sign = hashing(string)
	params = f"market=BITB_DOGE&side={side}&price={price}&amount={position_size}&nonce={get_timestamp()}&signature={sign}"
	url = "https://stakecube.io/api/v2/exchange/spot/order"
	response = requests.post(url, headers = headers, data = params)
	return response.json()


# price = 0.003
# order = place_order(price, config.position_size, side = "SELL")
# print("printing outside")
# print(order)
# sell_orders = []
# sell_orders.append(order['result']['orderId'])
# print(f"inside sell_orders - {sell_orders}")


#get_order_info()

# sell_order = get_order_info(sell_orders['orderId'])
# print(sell_order)


# doesnt have orderId
def order_history():
	string = f"market=BITB_DOGE&nonce={get_timestamp()}"
	sign = hashing(string)
	url = f"https://stakecube.io/api/v2/exchange/spot/myOrderHistory?market=BITB_DOGE&nonce={get_timestamp()}&signature={sign}"
	response = requests.get(url, headers = headers)
	print(response)
	print(response.json())
	return response.json()

#order_history()


# past trades - has orderID but not if order was filled 
def my_trades():
	string = f"market=BITB_DOGE&nonce={get_timestamp()}"
	sign = hashing(string)
	url = f"https://stakecube.io/api/v2/exchange/spot/myTrades?market=BITB_DOGE&nonce={get_timestamp()}&signature={sign}"
	response = requests.get(url, headers = headers)
	
	#print(response.json()['result'])
	return response.json()


#my_trades()
#get_order_info()


# closed_trades = my_trades()
# orders = get_order_info()

# for order in orders['result']:
# 	for count in range(len(closed_trades['result'])):
# 		if order['id'] == closed_trades['result'][count]['id']:
# 			print("trade is closed")
# 			print(order['price'])


	




def get_single_ticker():
	url = "https://stakecube.io/api/v2/exchange/spot/orderbook?market=BITB_DOGE"
	orderbook = requests.get(url, headers = headers)
	#print(orderbook.json()['result']['asks'])   # sells = ask
	sell_count = len(orderbook.json()['result']['asks'])
	#print(orderbook.json()['result']['asks'][sell_count-1]) # best sell order
	#print(orderbook.json()['result']['bids'][0])

	best_ask = orderbook.json()['result']['asks'][sell_count-1]['price']
	best_bid = orderbook.json()['result']['bids'][0]['price']
	#print(best_ask, best_bid)

	average = (float(best_ask) + float(best_bid)) / 2
	print(f"average - {average}")

	return average

# get_single_ticker()

# # will take out prints later - using them for testing right now
def test_grid():
	current_price = get_single_ticker()
# 	current_price = float(current_price)
# 	curren_price = round(current_price, 3)
	buy_orders = []
	sell_orders = []


	# 	# sell grid
	for i in range(config.number_sell_gridlines):
		price = current_price + (config.grid_size * (i+1))
		price = round(price, 8)
		#print(price)
		time.sleep(1)
		order = place_order(price, config.position_size, side = "SELL")

		
		

		sell_orders.append(order['result'])

	# # for testing
	# order = place_order(0.002785, 2, "SELL")   # for testing 
	# sell_orders.append(order['result'])

	# order = place_order(0.00289, 2, "SELL")
	# sell_orders.append(order['result'])

	
	# 	print(f"Sell orders - {sell_orders}")

	# print("final sell array")	
	# print(sell_orders)



# # 	# buy grid
	for i in range(config.number_buy_gridlines):
		price = current_price - (config.grid_size * (i+1))
		price = round(price, 8)

		print(price)  

		time.sleep(1)
		order = place_order(price, config.position_size, side = "BUY")
		buy_orders.append(order['result'])
		print(f"Buy orders - {buy_orders}")

	return sell_orders, buy_orders


sell_orders, buy_orders = test_grid()   # - upon restart take this out and test what it does before the loop starts - ***********************
closed_orders = []
# active_orders = []
# orders = get_order_info()
# for count in range(len(orders['result'])):
# 	active_orders.append(orders['result'][count])








#closed_trades = my_trades()                     #  ['orderId'] - closed
orders = get_order_info()                       # ['id'] - open
#print(orders)									# ['orderId'] - sell_orders

#print(closed_trades['result'])

# closed orderId

while True:
	
	closed_trades = my_trades()
	print("*****************************************")
	#print(closed_trades['result'])
	#for order in orders:
	count = 0
	for sell_order in sell_orders:
		for i in range(len(closed_trades['result'])):
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


				print(count)
				del sell_orders[count]
				print("new sell_orders array")
				print(sell_orders)
				break
		count +=1		




	count = 0
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


				print(count)
				del buy_orders[count]
				print("new buy_orders array")
				print(buy_orders)
				break
		count +=1	



	print("pausing")
	time.sleep(5)

# if order_info['isActive'] == closed_order_status:
# 			closed_order_ids.append(order_info['id'])
			
# 			print(f"Closed Orders - {closed_order_ids}")

# 			new_buy_price = float(order_info['price']) - grid_size
# 			new_buy_order = place_order(new_buy_price, position_size, "BUY")
# 			buy_orders.append(new_buy_order['data'])










	# for sell_order in sell_orders:
	# 	for active_order in active_orders:
	# 		if sell_order['orderId'] == active_order['id']:
	# 			print("in active order")
	# print("pausing")
	# time.sleep(5)

# while True:
# 	closed_order_ids = []
# 	active_orders = []
	
# 	orders = get_order_info()
# 	for i in range (len(orders['result']))
# 	active_orders.append(orders['result'][i]['id'])

# 	for sell_order in sell_orders:
# 		if sell_order in active_orders['result']

# 		print("checking sells")
# 		count = 0
# 		for count in range(len(active_orders['result'])):
# 			if orders['result'][count]['id'] == sell_order:
# 				print("good")
# 			count += 1

# 		if order_info['isActive'] == closed_order_status:
# 			closed_order_ids.append(order_info['id'])
			
# 			print(f"Closed Orders - {closed_order_ids}")

# 			new_buy_price = float(order_info['price']) - grid_size
# 			new_buy_order = place_order(new_buy_price, position_size, "BUY")
# 			buy_orders.append(new_buy_order['data'])

			

# # need to make sure this append works - print out buy_ourders again with new append


# 		time.sleep(check_orders_frequency)

# 	for buy_order in buy_orders:
# 		try:
# 			order = get_order_info(buy_order['orderId'])
# 		 	# print(order)

# 			order_info = order['data']
# 		except Exception as e:
# 			print("error in #2")
# 			continue

# 		if order_info['isActive'] == closed_order_status:
# 			closed_order_ids.append(order_info['id'])

# 			print(f"Closed Orders - {closed_order_ids}")

# 			new_sell_price = float(order_info['price']) + grid_size
# 			new_sell_order = place_order(new_sell_price, position_size, "SELL")
# 			sell_orders.append(new_sell_order['data'])

# 		time.sleep(check_orders_frequency)

	
# 	for order_id in closed_order_ids:
# 		buy_orders = [buy_order for buy_order in buy_orders if buy_order['orderId'] != order_id]
# 		print(f" Buy list - {buy_orders}")
		
# 		sell_orders = [sell_order for sell_order in sell_orders if sell_order['orderId'] != order_id]
# 		print(f" Sell list - {sell_orders}")

