from flask import Flask, render_template, request, jsonify, session
from SmartApi import SmartConnect 
import pyotp,json,os
from logzero import logger
import credentials
import time
from pytz import timezone
from operations import get_index_info,get_strike_lowprice,buy_stock,check_and_cancel_order,orderlist_check_placesell
# Create a Flask web application
app = Flask(__name__,template_folder='templates',static_folder='static')
#app.config['SERVER_TIMEOUT'] = 12000
#os.environ['TZ'] = 'Asia/Kolkata'
# Angleone Client Credentials
app.secret_key =credentials.secret_key
api_key = credentials.api_key
username = credentials.username
pwd = credentials.pwd
# Initialize the SmartApi object
smartapi = SmartConnect(api_key=credentials.api_key)
# Your TOTP token (you need to replace this with your actual TOTP token)
token = credentials.token
# Your correlation ID (you can generate this dynamically if needed)
#correlation_id = "abcde"
# Generate TOTP
try:
    totp = pyotp.TOTP(token).now()
except Exception as e:
    logger.error("Invalid Token: The provided token is not valid.")
    raise e
# Generate session
data = smartapi.generateSession(username, pwd, totp)
if data['status'] == False:
    logger.error(data)
else:
    # Successful session generation
    authToken = data['data']['jwtToken']
    refreshToken = data['data']['refreshToken']
    # Fetch the feed token getfeedToken
    feedToken = smartapi.getfeedToken()
# HTML 
@app.route('/')
def index():
    return render_template('index.html')
# Main Function
@app.route('/trading',methods=['GET', 'POST'])
def main():
    try:
        try :
            if request.method == 'POST':
                dynamic_time = request.form.get('xfortime')
                dynamic_index = request.form.get('index')
                dynamic_xforindex = request.form.get('xforindex')
                dynamic_xforbuy = request.form.get('xforbuyprice')
                dynamic_xfortriggerprice_buy = request.form.get('xfortriggerprice_buy')
                dynamic_quantity = request.form.get('lots_quantity')
                dynamic_xfor_add_up_sell = request.form.get('xfor_add_up_sell')
                dynamic_xfor_sub_down_sell = request.form.get('xfor_sub_down_sell')
        except Exception as e:
            return json.dumps({"Error in post values :":str(e)}),500
        dynamic_time_int = int(dynamic_time)
        try :
            get_index = get_index_info(dynamic_time_int,dynamic_index,smartapi)
            #return str(get_index)
        except Exception as e:
            return json.dumps({"Error in app.py get_index :":str(e)}),500
        if not isinstance(get_index, (int, float)):
        # If it's not a float or int, raise a ValueError
            raise ValueError("Invalid index value: {}".format(get_index))
        roundfig_openindex = round(get_index)
        #return str(roundfig_openindex)
        if dynamic_index == "NIFTY":
            rounded_openindex = round(roundfig_openindex / 50) * 50
        elif dynamic_index == 'BANKNIFTY':
            rounded_openindex = round(roundfig_openindex / 100) * 100
        #return str(rounded_openindex)
        ce_strike = int(rounded_openindex) - int(dynamic_xforindex)
        pe_strike = int(rounded_openindex) + int(dynamic_xforindex)
        #return [ce_strike,pe_strike]
        try :
            ce_strike_lp = get_strike_lowprice(dynamic_time_int,dynamic_index,ce_strike,"CE",smartapi)
        except Exception as e:
            return json.dumps({"Error in app.py ce_strike_lp :":str(e)}),500
        try:
            pe_strike_lp = get_strike_lowprice(dynamic_time_int,dynamic_index,pe_strike,"PE",smartapi)
        except Exception as e:
            return json.dumps({"Error in app.py pe_strike_lp :":str(e)}),500
        #return [ce_strike_lp,pe_strike_lp]
        ce_strike_lp.extend([dynamic_xforbuy,dynamic_xfortriggerprice_buy,dynamic_quantity])
        pe_strike_lp.extend([dynamic_xforbuy,dynamic_xfortriggerprice_buy,dynamic_quantity])
        #return [ce_strike_lp,pe_strike_lp]
        items_to_buy = [ce_strike_lp,pe_strike_lp]
        #return items_to_buy
        try:
            triggered_buy_data_ids = buy_stock(dynamic_time_int,dynamic_index,items_to_buy,smartapi)
            #return triggered_buy_data_ids
        except Exception as e:
            return json.dumps({"Error in app.py triggered_buy_data_ids :":str(e)}),500
        unique_order_ids_result = [triggered_buy_data_ids[i:i+2] for i in range(0, len(triggered_buy_data_ids), 2)]
        #return unique_order_ids_result
        try:
            complete_order_dict = check_and_cancel_order(unique_order_ids_result,smartapi)
            #return complete_order_dict
        except Exception as e:
            return json.dumps({"Error in app.py complete_order_dict :":str(e)}),500
        try:
            sell_order_id = orderlist_check_placesell(complete_order_dict[0]['data']['averageprice'],complete_order_dict[0]['data']['tradingsymbol'],complete_order_dict[0]['data']['symboltoken'],complete_order_dict[0]['data']['quantity'],dynamic_xfor_add_up_sell,dynamic_xfor_sub_down_sell,smartapi)
            return sell_order_id
        except Exception as e:
            return json.dumps({"Error in app.py complete_order_dict :":str(e)}),500
    except Exception as e:
        return json.dumps({"Error in app.py tradestock :":str(e)}),500
if __name__ == '__main__':
     app.run(host='0.0.0.0',port=5001,debug=True)