from flask import Flask,request,jsonify,json
from SmartApi import SmartConnect
import pyotp
from logzero import logger
import requests
import time as sleep_time
import sys


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

@app.route('/cancel_order')
def buy_order():
    #unique_order_ids = ["240208000489967","383921ad-5575-48ac-ba43-f6409731f463"]
#     [
#     "240215000682830",
#     "27c70bb5-b750-4767-93f0-c212b667ff8f"
#   ],
    order_variety = "NORMAL"
    id = smartApi.cancelOrder(order_id="240215000682830",variety=order_variety,) 
    return id

@app.route('/sell_live_check')
def sell_check_live():
    tradingsymbol = "IDEA-EQ"
    symboltoken = "14366"

    quote = smartApi.ltpData('NSE',tradingsymbol,symboltoken)
    return quote


if __name__ == '__main__':
    # Run the app on http://127.0.0.1:5000/
    app.run(debug=True)