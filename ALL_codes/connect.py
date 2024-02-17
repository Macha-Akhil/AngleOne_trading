from flask import Flask, render_template, request, jsonify, session
from SmartApi import SmartConnect  # Import the SmartApi library
import pyotp
from logzero import logger

app = Flask(__name__)
app.secret_key = '9601574b-c305-4824-b2ef-016e138e6aef '

# Your AngleOne SmartAPI credentials
api_key = 'IiO0DeTk'
username = 'REUG1397'
pwd = '2209'

# Initialize the SmartApi object
smartApi = SmartConnect(api_key)

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

@app.route('/')
def buy_stock():
    #place order
    try:
        orderparams = {
            "variety": "NORMAL",
            "tradingsymbol": "SBIN-EQ",
            "symboltoken": "3045",
            "transactiontype": "BUY",
            "exchange": "NSE",
            "ordertype": "LIMIT",
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price": "19500",
            "squareoff": "0",
            "stoploss": "0",
            "quantity": "1"
            }
        # Method 1: Place an order and return the order ID
        orderid = smartApi.placeOrder(orderparams)
        logger.info(f"PlaceOrder : {orderid}")
        return jsonify({"status": "success", "orderid": orderid})  # Add a return statement here
        # Method 2: Place an order and return the full response
        # response = smartApi.placeOrderFullResponse(orderparams)
        # logger.info(f"PlaceOrder : {response}")
    except Exception as e:
        logger.exception(f"Order placement failed: {e}")
        return jsonify({"status": "error", "message": str(e)})  # Add a return statement for error cases

if __name__ == '__main__':
    app.run(debug=True)