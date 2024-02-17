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

@app.route('/order_check')
def order_check():
    
    #order_id = "240205000758445"
    
    def check_order_status(unique_order_id):
        #return unique_order_id
        try:
            statuss = []
            order_details = smartApi.individual_order_details(unique_order_id)
            #return order_details
            status = order_details['data']['orderstatus']
            #return status
            if status in ["complete", "rejected", "cancelled","trigger pending","open"]:
                    statuss.append(order_details) 
            return statuss
        except Exception as e:
            return json.dumps({"Error in check_order_status":str(e)}),500
        
    # Function to cancel another order (SELL) for a specific order ID
    def cancel_other_order(unique_order_ids):
        try:
            order_variety = "NORMAL"
            existing_order_status = check_order_status(unique_order_ids[1])
            #return existing_order_status
            if existing_order_status['data']['status'] == "trigger pending":
                smartApi.cancelOrder(order_id=unique_order_ids[0],variety=order_variety) 
        except Exception as e:
            return json.dumps({"Error in cancel_other_order":str(e)}),500
        
    #List to store order statuses
    def check_status(unique_order_ids):
        #return unique_order_ids
        try:
            #status_details_list = []
            for order_info in unique_order_ids:
                #return order_info[1]
                order_status_details = check_order_status(order_info[1])
                return order_status_details
                order_status_completed_or_not = order_status_details[0]["data"]["orderstatus"]
                #return order_status_completed_or_not
                if order_status_completed_or_not == "complete":
                    order_status_complete = order_status_details
                    #return order_status_complete
                    other_order_id = next(order_id for order_id in unique_order_ids if order_id[0] != order_status_details[0]['data']['orderid'])
                    #return other_order_id  
                    cancel_other_order(other_order_id)   
                    return order_status_complete
        except Exception as e:
            return json.dumps({"Error in check_status":str(e)}),500
                
    def check_and_cancel_order(unique_order_ids):
        #return unique_order_ids
        try:
            while True:
                order_status = check_status(unique_order_ids)
                #return order_status
                if order_status is not None:
                    order_status_complete_data = order_status
                    break
                sleep_time.sleep(2)
                print("checking orders....")
            return order_status_complete_data
        except Exception as e:
            return json.dumps({"Error in check_and_cancel_order":str(e)}),500
        
    unique_order_ids = [
  "240216000318017",
  "4cb05962-1303-4f6d-b4f5-8a8b66f89876",
  "240214000756840",
  "249fc35c-2ded-411b-971a-ca1f97bca7d9"
]
    # one list into inside two lists
    unique_order_ids_result = [unique_order_ids[i:i+2] for i in range(0, len(unique_order_ids), 2)]
    #return unique_order_ids_result
    # one list into inside two lists
    # order_ids = unique_order_ids[::2]
    # unique_ids = unique_order_ids[1::2]
    # # Combine order IDs and unique IDs into pairs
    # pairs = [[order_id, unique_id] for order_id, unique_id in zip(order_ids, unique_ids)]
    # return pairs

    values = check_and_cancel_order(unique_order_ids_result)
    return values


if __name__ == '__main__':
    # Run the app on http://127.0.0.1:5000/
    app.run(debug=True)