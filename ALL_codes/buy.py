from flask import Flask,request,jsonify,json
from SmartApi import SmartConnect
import pyotp
from logzero import logger
import requests
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

@app.route('/buy_order')
def buy_order():
    #place order
    try:
        # orderparams = {
        #     "variety": "NORMAL",
        #     "tradingsymbol": "SBIN-EQ",
        #     "symboltoken": "3045",
        #     "transactiontype": "BUY",
        #     "exchange": "NSE",
        #     "ordertype": "LIMIT",
        #     "producttype": "INTRADAY",
        #     "duration": "DAY",
        #     "price": "19500",
        #     "squareoff": "0",
        #     "stoploss": "0",
        #     "quantity": "1"
        #     }
        orderparams = {
            #"ordertype": "LIMIT",
            #"variety": "STOPLOSS",
            "variety":"NORMAL",
            "tradingsymbol": "IDEA-EQ",
            "symboltoken": "14366",
            "transactiontype": "BUY",
            "exchange": "NSE",
            #"ordertype": "STOPLOSS_LIMIT",
            "ordertype": "LIMIT",
            "producttype": "INTRADAY",
            "price": '16.45', #
            #"triggerprice": '272.5', #
            "duration": "DAY",
            "squareoff": "0",
            "stoploss": "0",
            "quantity": "2"
            }

        # orderid = smartApi.placeOrder(orderparams)
        # return str(orderid)
        response = SmartConnect.placeOrderFullResponse(smartApi,orderparams=orderparams)
        return response
    
    except Exception as e:
        return json.dumps({"Error in buy_order":str(e)}),500
    

# Run the application if this script is executed
if __name__ == '__main__':
    # Run the app on http://127.0.0.1:5000/
    app.run(debug=True)