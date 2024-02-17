from flask import Flask, render_template, request, jsonify, session 
from SmartApi import SmartConnect  # Import the SmartApi library
import pyotp
from logzero import logger
from datetime import datetime,time,timedelta
import time as sleep_time
import requests
import pandas as pd
import credentials

app = Flask(__name__)
app.secret_key = '9601574b-c305-4824-b2ef-016e138e6aef '

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
#print(data)

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
        indexname = 'NIFTY' # "BANKNIFTY"
        if indexname == "NIFTY":
            index = "NIFTY"
        elif indexname == "BANKNIFTY":
            index = "BANKNIFTY"
        else:
            raise ValueError("We don't support other than BANKNIFTY & NIFTY 50")
    
        intializeSymbolTokenMap()
        index_instrument_token = getTokenInfo('NSE','',index,'','','').iloc[0]['token']
        #return str(index_instrument_token)
        today = get_today_date()
        year, month, day = today.split(",")
        # Create a datetime object representing the time at which you want to get the NIFTY 50 or BANKNIFTY index open price
        from_date_time = datetime(int(year),int(month),int(day),10,0,0)
        #return str(from_date_time)
        to_date_time = datetime(int(year),int(month),int(day),10,0,0)
        from_date_time_str = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}".format(
            from_date_time.year, from_date_time.month, from_date_time.day,
            from_date_time.hour, from_date_time.minute)
        to_date_time_str = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}".format(
            to_date_time.year, to_date_time.month, to_date_time.day,
            to_date_time.hour, to_date_time.minute)
        
        params = {
                "exchange": "NSE",
                "symboltoken": index_instrument_token,
                "interval": "ONE_MINUTE",
                "fromdate": from_date_time_str,
                "todate": to_date_time_str
            }

        # Example: Get historical data for a particular instrument
        index_historical_data = smartApi.getCandleData(params)
        return index_historical_data
        index_open = index_historical_data['data'][0][1]
        return str(index_open)
    
    
    except Exception as e:
        logger.exception(f"Error fetching historical data: {e}")
        return jsonify({"status": "error", "message": str(e)})


if __name__ == '__main__':
    app.run(debug=True)