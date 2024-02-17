from flask import Flask,request,jsonify,json
from SmartApi import SmartConnect
import pyotp
from logzero import logger
import requests
import time as sleep_time
import sys
from datetime import datetime,time,timedelta
import time as sleep_time


# Create a Flask web application
app = Flask(__name__)

app.secret_key = '9601574b-c305-4824-b2ef-016e138e6aef'
# Your AngleOne SmartAPI credentials
api_key = 'IiO0DeTk'
username = 'REUG1397'
pwd = '2209'
# Initialize the SmartApi object
#smartApi = SmartConnect(api_key)
smartApi = SmartConnect(api_key=api_key)
# Your TOTP token (you need to replace this with your actual TOTP token)
token = "3ENHXY6BSSGFFWGFOEY2GPGQPM"
# Your correlation ID (you can generate this dynamically if needed)
#correlation_id = "abcde"
# Generate TOTP
try:
    totp = pyotp.TOTP(token).now()
except Exception as e:
    logger.error("Invalid Token: The provided token is not valid.")
    raise e
# Generate session
data = smartApi.generateSession(username, pwd, totp)
if data['status'] == False:
    logger.error(data)
else:
    # Successful session generation
    authToken = data['data']['jwtToken']
    refreshToken = data['data']['refreshToken']
    # Fetch the feed token
    feedToken = smartApi.getfeedToken()

@app.route('/sell_check')
def sell_order():
    ready_for_sell = [
  {
    "data": {
      "averageprice": 16.45,
      "cancelsize": "0",
      "disclosedquantity": "0",
      "duration": "DAY",
      "exchange": "NSE",
      "exchorderupdatetime": "16-Feb-2024 11:28:49",
      "exchtime": "16-Feb-2024 11:28:49",
      "expirydate": "",
      "filledshares": "2",
      "fillid": "",
      "filltime": "",
      "instrumenttype": "",
      "lotsize": "1",
      "optiontype": "",
      "orderid": "240216000318017",
      "orderstatus": "complete",
      "ordertag": "",
      "ordertype": "LIMIT",
      "parentorderid": "",
      "price": 16.45,
      "producttype": "INTRADAY",
      "quantity": "2",
      "squareoff": 0.0,
      "status": "complete",
      "stoploss": 0.0,
      "strikeprice": -1.0,
      "symboltoken": "14366",
      "text": "",
      "tradingsymbol": "IDEA-EQ",
      "trailingstoploss": 0.0,
      "transactiontype": "BUY",
      "triggerprice": 0.0,
      "unfilledshares": "0",
      "uniqueorderid": "4cb05962-1303-4f6d-b4f5-8a8b66f89876",
      "updatetime": "16-Feb-2024 11:28:49",
      "variety": "NORMAL"
    },
    "errorcode": "",
    "message": "SUCCESS",
    "status": True
  }
]

    def get_live_stock_price(tradingsymbol,symboltoken):
        #return [tradingsymbol,symboltoken]
        try:
            exchange = "NSE"
            quote = smartApi.ltpData(exchange,tradingsymbol,symboltoken)
            #return quote
            ltp = quote['data']['ltp']
            return ltp
            #return str(ltp)
        except Exception as e:
            return json.dumps({"Error in get_live_stock_price":str(e)}),500
    
    def place_sell_order(tradingsymbol,symboltoken,live_price,quantity,smartApi):
        #return [tradingsymbol,live_price,symboltoken,quantity ]
        #live_price = str(live_price)
        #return live_price
        data_sell = []  
        try:
            params_sell =  { "variety": "NORMAL",
                            "tradingsymbol":tradingsymbol ,
                            "symboltoken": symboltoken,
                            "transactiontype": "SELL",
                            "exchange": "NSE",
                            "ordertype": "LIMIT",
                            "producttype": "INTRADAY",
                            "duration": "DAY",
                            "price": str(live_price),
                            "quantity": quantity
                            }
            #return params_sell
            response = smartApi.placeOrderFullResponse(orderparams=params_sell)
            return response
            order_id = response['data']['orderid']
            unique_order_id = response['data']['uniqueorderid']
            data_sell.append(order_id)
            data_sell.append(unique_order_id)
            return data_sell
            # return data_sell
        except Exception as e:
            return json.dumps({"Error in place_sell_order":str(e)}),500


    def orderlist_check_placesell(average_price,tradingsymbol,symboltoken,quantity,dynamic_xfor_add_up_sell,dynamic_xfor_sub_down_sell,smartApi):
        #return [average_price,tradingsymbol,symboltoken,quantity,dynamic_xfor_add_up_sell,dynamic_xfor_sub_down_sell]
        try:
            sell_for_up = average_price + float(dynamic_xfor_add_up_sell)
            #return str(sell_for_up)
            sell_for_down = average_price - float(dynamic_xfor_sub_down_sell)
            sell_time_str = "15:15"
            sell_time = time(*map(int, sell_time_str.split(':')))
            sell_triggered = False
            # sell_decreased_to = 0.1
            # sell_decreased_value = sell_for_up - sell_decreased_to
            while True:
                live_price = get_live_stock_price(tradingsymbol,symboltoken)
                return live_price
                #sell_for_up is 130 if live price is 122 then sell_for_down should changes to 0.0
                # if live_price_int >= sell_decreased_value:
                #     dynamic_xfor_sub_down_sell = 0.0
                #     sell_for_down = average_price - float(dynamic_xfor_sub_down_sell)
                    #print("sell for down is 0.0")
                # Check if the graph goes up or goes down and trigger sell
                if live_price >= sell_for_up or live_price <= sell_for_down:
                    sell_order_id = place_sell_order(tradingsymbol,symboltoken,live_price,quantity,smartApi)
                    break
                current_time = datetime.now().time()
                # Check if it's time to sell
                if current_time >= sell_time and not sell_triggered:
                    sell_order_id = place_sell_order(tradingsymbol,symboltoken,live_price,quantity)
                    sell_triggered = True
                    break
                sleep_time.sleep(3)
                print("hello")
            return sell_order_id
        except Exception as e:
            return json.dumps({"Error in orderlist_check_placesell":str(e)}),500 

    dynamic_xfor_add_up_sell = 0.05
    dynamic_xfor_sub_down_sell = 0.05

    result = orderlist_check_placesell(ready_for_sell[0]['data']['averageprice'],ready_for_sell[0]['data']['tradingsymbol'],ready_for_sell[0]['data']['symboltoken'],ready_for_sell[0]['data']['quantity'],dynamic_xfor_add_up_sell,dynamic_xfor_sub_down_sell,smartApi)
    return result

if __name__ == '__main__':
    # Run the app on http://127.0.0.1:5000/
    app.run(debug=True)