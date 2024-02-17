from flask import Flask, render_template, request, jsonify, session 
from SmartApi import SmartConnect  # Import the SmartApi library
import pyotp
from logzero import logger
from datetime import datetime,time,timedelta
import time as sleep_time
import requests
import pandas as pd
import credentials
import sys

app = Flask(__name__)

app.secret_key = '9601574b-c305-4824-b2ef-016e138e6aef'
# Your AngleOne SmartAPI credentials
api_key = 'IiO0DeTk'
username = 'REUG1397'
pwd = '2209'
# Initialize the SmartApi object
#smartApi = SmartConnect(api_key)
smartApi = SmartConnect(api_key=credentials.api_key)
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
    
def get_today_date_tdngsymbl():
        today_date = datetime.now().date()
        formatted_expiry = today_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
        return formatted_expiry

def get_today_date():
        today_date = datetime.now().date()
        formatted_today_year = today_date.strftime("%Y,%#m,%#d")
        return formatted_today_year

def intializeSymbolTokenMap():
    url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
    d = requests.get(url).json()
    global token_df
    token_df = pd.DataFrame.from_dict(d)
    token_df['expiry'] = pd.to_datetime(token_df['expiry'])
    token_df = token_df.astype({'strike':float})
    credentials.token_map = token_df

def getTokenInfo(exch_seg,instrumenttype,symbol,strike_price,ce_pe,expiry_date):
    df = credentials.token_map
    strike_price = strike_price*100
    if exch_seg == 'NSE':
        eq_df = df[(df['exch_seg'] == 'NSE')]
        return eq_df[(eq_df['name'] == symbol)]
    elif exch_seg == 'NFO':
        ce_pe_filter = df['symbol'].apply(lambda x: x.endswith(ce_pe))
        expiry_filter = df['expiry'] == expiry_date
        return df[(df['exch_seg'] == 'NFO') & (df['instrumenttype'] == instrumenttype) & (df['name'] == symbol) & (df['strike'] == strike_price) & ce_pe_filter & expiry_filter].sort_values(by=['expiry'])

@app.route('/')
def get_historical_data():
    try:
        
        #get_index = 21741.55
        index_open = 21555.85
        indexname = 'NIFTY'
        dynamic_index = 'NIFTY'
        roundfig_openindex = round(index_open)
        if dynamic_index == "NIFTY":
            rounded_openindex = round(roundfig_openindex / 50 + 0.5) * 50
        elif dynamic_index == 'BANKNIFTY':
            rounded_openindex = round(roundfig_openindex / 100 + 0.5) * 100
            
        dynamic_xforindex = 100

        ce_strike = int(rounded_openindex) - int(dynamic_xforindex)
        pe_strike = int(rounded_openindex) + int(dynamic_xforindex)
        #return str(ce_strike)

        today_expiry_date_str = get_today_date_tdngsymbl()
        today_expiry_date = datetime.strptime(today_expiry_date_str, "%a, %d %b %Y %H:%M:%S GMT")
        weekday = today_expiry_date.weekday()
        
        if indexname == "NIFTY":
            days_to_add = (3 - weekday) % 7
        elif indexname == "BANKNIFTY":
            days_to_add = (2 - weekday) % 7
        # Calculate the nearest weekday date ### "22FEB2024"
        nearest_weekday = today_expiry_date + timedelta(days=days_to_add)
        # Format the nearest weekday date as a string
        #nearest_weekday_str = nearest_weekday.strftime("%a, %d %b %Y %H:%M:%S")
        nearest_weekday_str = nearest_weekday.strftime("%Y-%m-%d")
        indexname = 'NIFTY'
        intializeSymbolTokenMap()
        token_info_CE = getTokenInfo('NFO','OPTIDX',indexname,ce_strike,'CE',nearest_weekday_str)
        token_info_PE = getTokenInfo('NFO','OPTIDX',indexname,pe_strike,'PE',nearest_weekday_str)
        tokens_CE = token_info_CE['token'].tolist()
        symbols_CE = token_info_CE['symbol'].tolist()
        result_list = list(zip(tokens_CE, symbols_CE))
        #return result_list

        # tokens_PE = token_info_PE['token'].tolist()
        # symbols_PE = token_info_PE['symbol'].tolist()

        # # Combine the lists into a list of lists
        # result_list = [list(item) for item in zip(tokens_CE, symbols_CE, tokens_PE, symbols_PE)]
        # return result_list

        #print(token_info_CE,token_info_PE)
        #return str(token_info_CE)
        today = get_today_date()
        year, month, day = today.split(",")
        # Create a datetime object representing the time at which you want to get the NIFTY 50 or BANKNIFTY index open price
        from_date_time_ce = datetime(int(year),int(month),int(day),10,0,0)
        #return str(from_date_time)
        to_date_time_ce = datetime(int(year),int(month),int(day),10,4,0)
        from_date_time_str_cepe = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}".format(
            from_date_time_ce.year, from_date_time_ce.month, from_date_time_ce.day,
            from_date_time_ce.hour, from_date_time_ce.minute)
        to_date_time_str_cepe = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}".format(
            to_date_time_ce.year, to_date_time_ce.month, to_date_time_ce.day,
            to_date_time_ce.hour, to_date_time_ce.minute)
        
        params_ce_pe = {
                "exchange": "NFO",
                "symboltoken": result_list[0][0],
                "interval": "ONE_MINUTE",
                "fromdate": from_date_time_str_cepe,
                "todate": to_date_time_str_cepe
            }
        #return params_ce_pe

        # Example: Get historical data for a particular instrument
        index_historical_data = smartApi.getCandleData(params_ce_pe)
        #return index_historical_data
        low_prices = [item[3] for item in index_historical_data['data']]
        #print(low_prices)
        # Find the minimum low price
        min_low_price = min(low_prices)
        # Print or return the result
        #print(min_low_price)

        roundfig_low_value_option = round(min_low_price)
        #return [roundfig_low_value_option,result_list]
        # [
        #     177,
        #     [
        #         [
        #         "38023",
        #         "NIFTY01FEB2421500CE"
        #         ]
        #     ]
        #     ]
        buy_at_value = 20
        trigger_at_value = 1
        quantity = '15'
        buy_price = int(roundfig_low_value_option) + float(buy_at_value)
        #return str(roundfig_low_value_option)
        trigger_price = buy_price - float(trigger_at_value)
        #return result_list
        params_buy ={
                "variety": "STOPLOSS",
                "symboltoken": result_list[0][0], #
                "tradingsymbol": result_list[0][1],#
                "transactiontype": "BUY",  # "BUY" or "SELL"  #
                "exchange": "NFO",#
                "ordertype": "STOPLOSS_LIMIT", #
                "producttype": "INTRADAY", #
                "duration": "DAY", #
                "price": buy_price, #
                "triggerprice": trigger_price, #
                "quantity": '1' #
            }
        #return str(params_buy)
        orderid = smartApi.placeOrder(params_buy)
        return str(orderid)

    
    except Exception as e:
        logger.exception(f"Error fetching historical data: {e}")
        return jsonify({"status": "error", "message": str(e)})

     





if __name__ == '__main__':
    app.run(debug=True)