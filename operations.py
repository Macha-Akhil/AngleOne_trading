from flask import render_template, request, jsonify, session   
import json
from logzero import logger
from datetime import datetime,time,timedelta
import time as sleep_time
import requests
import pandas as pd
import credentials
from retrying import retry
import asyncio
#smartApi = SmartConnect(api_key=credentials.api_key)#
def get_today_date_tdngsymbl():
        today_date = datetime.now().date()
        formatted_expiry = today_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
        return formatted_expiry
def get_today_date():
        today_date = datetime.now().date()
        formatted_today_year = today_date.strftime("%Y,%#m,%#d")
        return formatted_today_year
#function -- before 10am or 1pm(13pm) submitting the request with required data
async def wait_until_market_open(target_time):
    current_time = datetime.now().time()
    while True:
        if current_time >= target_time:
            break
        print("waiting for correct time .....")  
        current_time = datetime.now().time()
        await asyncio.sleep(60)
#
def intializeSymbolTokenMap():
    url = 'https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json'
    d = requests.get(url).json()
    global token_df
    token_df = pd.DataFrame.from_dict(d)
    #token_df['expiry'] = pd.to_datetime(token_df['expiry'])
    token_df['expiry'] = pd.to_datetime(token_df['expiry'], format='%d%b%Y')
    token_df = token_df.astype({'strike':float})
    credentials.token_map = token_df
#
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
# STEP - 1
# Morning 10Am or 1pm  NIFTY 50 or BANKNIFTY Index value
def get_index_info(indextime,indexname,smartApi):
    try:
        if indextime == 10:
            indextime = 10
        elif indextime == 13:
            indextime = 13
        else:
            raise ValueError("We don't support other than 10AM & 1PM (13) time")
        #calling the function before the time to submit
        # target_time = time(indextime,1)
        # print("wait for 10:01 (or) 13:01 .....")
        # wait_until_market_open(target_time)
        if indexname == "NIFTY":
            index = "NIFTY"
        elif indexname == "BANKNIFTY":
            index = "BANKNIFTY"
        else:
            raise ValueError("We don't support other than BANKNIFTY & NIFTY(50)")
        intializeSymbolTokenMap()
        index_instrument_token = getTokenInfo('NSE','',index,'','','').iloc[0]['token']
        #return str(index_instrument_token)
        today = get_today_date()
        year, month, day = today.split(",")
        # Create a datetime object representing the time at which you want to get the NIFTY 50 or BANKNIFTY index open price
        from_date_time = datetime(int(year),int(month),int(6),indextime,0,0)
        #return str(from_date_time)
        to_date_time = datetime(int(year),int(month),int(6),indextime,0,0)
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
        #return params
        # Example: Get historical data for a particular instrument
        index_historical_data = smartApi.getCandleData(params)
        #return index_historical_data
        index_open = index_historical_data['data'][0][1]
        return index_open
    except Exception as e:
        logger.exception(f"Error fetching historical data: {e}")
        return jsonify({"status": "error", "message": str(e)})
# STEP - 2
# Morning 10:01 - 10:04 min of low value of ( NIFTY 50 or BANKNIFTY ) CE AND PE values
def get_strike_lowprice(indextime,indexname,strike_price,option,smartApi):
    #return strike_price
    try:
        if indextime == 10:
            indextime = 10
        elif indextime == 13:
            indextime = 13
        else:
            raise ValueError("We don't support other than 10AM & 1PM (13) time")
        #calling the function before the time to submit
        target_time = time(indextime,4)
        print("wait for 10:04 (or) 13:04 .....")
        wait_until_market_open(target_time)
        today_expiry_date_str = get_today_date_tdngsymbl()
        today_expiry_date = datetime.strptime(today_expiry_date_str, "%a, %d %b %Y %H:%M:%S GMT")
        weekday = today_expiry_date.weekday()
        if indexname == "NIFTY":
            nifty_weekday_add = 3 # thursday
            days_to_add = (nifty_weekday_add - weekday) % 7
        elif indexname == "BANKNIFTY":
            banknifty_weekday_add = 2 # wednesday
            days_to_add = (banknifty_weekday_add - weekday) % 7
        # Calculate the nearest weekday date ### "22FEB2024"
        nearest_weekday = today_expiry_date + timedelta(days=days_to_add)
        # Format the nearest weekday date as a string
        #nearest_weekday_str = nearest_weekday.strftime("%a, %d %b %Y %H:%M:%S")
        nearest_weekday_str = nearest_weekday.strftime("%Y-%m-%d")
        #return(nearest_weekday_str)
        intializeSymbolTokenMap()
        token_info = getTokenInfo('NFO','OPTIDX',indexname,strike_price,option,nearest_weekday_str)
        #return str(token_info)
        # If it is empty , check one day from present date
        # below if condition checks tuesday , wednesday , thursday and friday
        if token_info.empty:
            days_to_add_num = 3 if indexname == "BANKNIFTY" else 4  # 3 thursday (banknifty) -- # 4 friday (nifty)
            days_to_add = (days_to_add_num - weekday) % 7
            nearest_weekday = today_expiry_date + timedelta(days=days_to_add)
            nearest_weekday_str = nearest_weekday.strftime("%Y-%m-%d")
            token_info = getTokenInfo('NFO', 'OPTIDX', indexname, strike_price, option, nearest_weekday_str)
            # If still empty, check  before date later from present date
            if token_info.empty: 
                days_to_add_num = 1 if indexname == "BANKNIFTY" else 2 # 1 Tuesday (Banknifty) -- # 2 wednesday (nifty)
                days_to_add = (days_to_add_num - weekday) % 7
                nearest_weekday = today_expiry_date - timedelta(days=days_to_add)
                nearest_weekday_str = nearest_weekday.strftime("%Y-%m-%d")
                token_info = getTokenInfo('NFO', 'OPTIDX', indexname, strike_price, option, nearest_weekday_str)   
                # if still empty , banknifty is wednesday and it check on friday         
                if indexname == "BANKNIFTY" and token_info.empty:
                    days_to_add_num = 4 # 4 Friday (banknifty)
                    days_to_add = (days_to_add_num - weekday) % 7
                    nearest_weekday = today_expiry_date + timedelta(days=days_to_add)
                    nearest_weekday_str = nearest_weekday.strftime("%Y-%m-%d")
                    token_info = getTokenInfo('NFO', 'OPTIDX', indexname, strike_price, option, nearest_weekday_str)
                # if still empty , nifty is thursday and it check on wednesday befor days 
                if indexname == "NIFTY" and token_info.empty:
                    days_to_add_num = 1 # 1 tuesday (nifty)
                    days_to_add = (days_to_add_num - weekday) % 7
                    nearest_weekday = today_expiry_date + timedelta(days=days_to_add)
                    nearest_weekday_str = nearest_weekday.strftime("%Y-%m-%d")
                    token_info = getTokenInfo('NFO', 'OPTIDX', indexname, strike_price, option, nearest_weekday_str)
        #return str(token_info)
        token_info_ = token_info['token'].tolist()
        symbol_info_ = token_info['symbol'].tolist()
        result_list = list(zip(token_info_, symbol_info_))
        #return result_list
        today = get_today_date()
        year, month, day = today.split(",")
        # Create a datetime object representing the time at which you want to get the NIFTY 50 or BANKNIFTY index open price
        from_date_time_ce = datetime(int(year),int(month),int(day),indextime,0,0)
        to_date_time_ce = datetime(int(year),int(month),int(day),indextime,4,0)
        from_date_time_str_ = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}".format(
            from_date_time_ce.year, from_date_time_ce.month, from_date_time_ce.day,
            from_date_time_ce.hour, from_date_time_ce.minute)
        to_date_time_str_ = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}".format(
            to_date_time_ce.year, to_date_time_ce.month, to_date_time_ce.day,
            to_date_time_ce.hour, to_date_time_ce.minute)
        params_ce_pe = {
                "exchange": "NFO",
                "symboltoken": result_list[0][0],
                "interval": "ONE_MINUTE",
                "fromdate": from_date_time_str_,
                "todate": to_date_time_str_
            }
        # Example: Get historical data for a particular instrument
        index_historical_data = smartApi.getCandleData(params_ce_pe)
        #return index_historical_data
        low_prices = [item[3] for item in index_historical_data['data']]
        min_low_price = min(low_prices)
        roundfig_low_value_option = round(min_low_price)
        return [min_low_price,result_list]
        return [roundfig_low_value_option,result_list]    
    except Exception as e:
        logger.exception(f"Error fetching historical data: {e}")
        return jsonify({"status": "error", "message": str(e)})    
# STEP - 3
# Trigger the CE AND PE values for buy 
def buy_stock(indextime,indexname,items_to_buy,smartApi):
    try:
        if indextime == 10:
            indextime = 10
        elif indextime == 13:
            indextime = 13
        else:
            raise ValueError("We don't support other than 10AM & 1PM (13) time")
        #calling the function before the time to submit
        target_time = time(indextime,5)
        print("wait for 10:05 (or) 13:05 .....")
        wait_until_market_open(target_time)
        triggered_data=[]   
        for item in items_to_buy:
            buy_price = int(item[0]) + float(item[2])
            trigger_price = buy_price - float(item[3])
            if indexname ==  'NIFTY':
                lot_size = item[4]
                desired_quantity = 50
                #adjusted_quantity = int(lot_size) * desired_quantity
            elif indexname ==  'BANKNIFTY':
                lot_size = item[4]
                desired_quantity = 15
                #adjusted_quantity = int(lot_size) * desired_quantity
            else:
                raise ValueError("Buy_Stock : Invalid indexname")
            adjusted_quantity = int(lot_size) * desired_quantity
            params_buy ={
                    "variety": "STOPLOSS",
                    "symboltoken": item[1][0][0], 
                    "tradingsymbol": item[1][0][1],
                    "transactiontype": "BUY",  
                    "exchange": "NFO",
                    "ordertype": "STOPLOSS_LIMIT", 
                    "producttype": "INTRADAY", 
                    "duration": "DAY", 
                    "price": buy_price, 
                    "triggerprice": trigger_price, 
                    "quantity": adjusted_quantity 
                } 
            #return params_buy
            order_data = smartApi.placeOrderFullResponse(orderparams=params_buy)
            order_id = order_data['data']['orderid']
            unique_order_id = order_data['data']['uniqueorderid']
            triggered_data.append(order_id)
            triggered_data.append(unique_order_id)
        return triggered_data        
    except Exception as e:
        logger.exception(f"Error fetching historical data: {e}")
        return jsonify({"status": "error", "message": str(e)})   
# STEP - 4 (SUB)
# If one stock ce or pe buy than other ce or pe get cancelled ( Below 4 functions for that:) 
# Function to check order status 
@retry(wait_fixed=2000,stop_max_attempt_number=None) 
def check_order_status(unique_order_id,smartApi):
    #statuss = None
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
        print(f"Error in check_order_status : {e}")
        raise  # Re-raise the exception to trigger retry
        #return json.dumps({"Error in check_order_status":str(e)}),500 
# STEP - 4 (SUB)
# Function to cancel another order (SELL) for a specific order ID
#@retry(wait_fixed=2000) 
def cancel_other_order(unique_order_ids,smartApi):
    try:
        order_variety = "NORMAL"
        existing_order_status = check_order_status(unique_order_ids[1],smartApi)
        #return existing_order_status
        if existing_order_status[0]['data']['status'] == "trigger pending" or existing_order_status[0]['data']['status'] == "open":
            smartApi.cancelOrder(order_id=unique_order_ids[0],variety=order_variety) 
        else:
            smartApi.cancelOrder(order_id=unique_order_ids[0],variety=order_variety)
    except (IndexError, KeyError):
        print("Order is already cancelled or rejected....")
    except Exception as e:
        print(f"Error in cancel_other_order: {e}")
        #return json.dumps({"Error in cancel_other_order":str(e)}),500
# STEP - 4 (SUB)  
#List to store order statuses
def check_status(unique_order_ids,smartApi):
    #return unique_order_ids
    try:
        for order_info in unique_order_ids:
            order_status_details = check_order_status(order_info[1],smartApi)
            #return order_status_details
            order_status_completed_or_not = order_status_details[0]["data"]["status"]
            if order_status_completed_or_not == "complete":
                order_status_complete = order_status_details
                other_order_id = next(order_id for order_id in unique_order_ids if order_id[0] != order_status_details[0]['data']['orderid'])
                cancel_other_order(other_order_id,smartApi)
                return order_status_complete
    except Exception as e:
        return json.dumps({"Error in check_status":str(e)}),500
# STEP - 4  
#@retry(wait_fixed=2000)             
def check_and_cancel_order(unique_order_ids,smartApi):
    #return unique_order_ids
    try:
        trigger_orders_cancel_time_str = "15:15"
        trigger_orders_cancel_time = time(*map(int, trigger_orders_cancel_time_str.split(':')))
        while True:
            order_status = check_status(unique_order_ids,smartApi)
            #return order_status
            if order_status is not None:
                order_status_complete_data = order_status
                break
            current_time = datetime.now().time()
            if current_time >= trigger_orders_cancel_time:
                for order_info in unique_order_ids:
                    cancel_other_order(order_info,smartApi)
                return("Triggered orders are not buyed so At 3:15pm orders are cancelled.")
            sleep_time.sleep(2)
            print("checking orders....")
        return order_status_complete_data
    except Exception as e:
        print(f"Error occurred: {e}")
        time.sleep(5)  # Wait for a few seconds before retrying
        check_and_cancel_order(unique_order_ids,smartApi)  # Retry the main function
    # except Exception as e:
    #         return json.dumps({"Error in check_and_cancel_order":str(e)}),500
# STEP - 5 (SUB)    
# Sell the stock using details fetch live data (LTPDATA) and sell for up if graph goes up or sell for down if graph goes down  ( 3 functions used )
@retry(wait_fixed=1000,stop_max_attempt_number=None)
def get_live_stock_price(tradingsymbol,symboltoken,smartApi):
    #return [tradingsymbol,symboltoken]
    try:
        exchange = "NFO"
        quote = smartApi.ltpData(exchange,tradingsymbol,symboltoken)
        ltp = quote['data']['ltp']
        ltp = float(ltp)
        return ltp
    except Exception as e:
        print(f"Error in get_live_stock_price : {e}")
        #return json.dumps({"Error in get_live_stock_price":str(e)}),500
# STEP - 5 (SUB)
# Sell the order    
def place_sell_order(tradingsymbol,symboltoken,quantity,smartApi):
    #data_sell = []  
    try:
        params_sell =  { "variety": "NORMAL",
                        "tradingsymbol":tradingsymbol ,
                        "symboltoken": symboltoken,
                        "transactiontype": "SELL",
                        "exchange": "NFO",
                        "ordertype": "MARKET",
                        "producttype": "INTRADAY",
                        "duration": "DAY",
                        "quantity": quantity
                        }
        #return params_sell
        response = smartApi.placeOrderFullResponse(orderparams=params_sell)
        return response
    except Exception as e:
        return json.dumps({"Error in place_sell_order":str(e)}),500
# STEP - 5 
# Check sell the order graph is up or down 
def orderlist_check_placesell(average_price,tradingsymbol,symboltoken,quantity,dynamic_xfor_add_up_sell,dynamic_xfor_sub_down_sell,smartApi):
    #return [average_price,tradingsymbol,symboltoken,quantity,dynamic_xfor_add_up_sell,dynamic_xfor_sub_down_sell]
    try:
        sell_for_up = float(average_price + float(dynamic_xfor_add_up_sell))
        sell_for_down = float(average_price - float(dynamic_xfor_sub_down_sell))
        sell_time_str = "15:15"
        sell_time = time(*map(int, sell_time_str.split(':')))
        sell_triggered = False
        sell_decreased_to = 10
        sell_decreased_value = sell_for_up - sell_decreased_to
        sell_decreased_value_boolean = False
        while True:
            live_price = get_live_stock_price(tradingsymbol,symboltoken,smartApi)
            if live_price is not None:
                if isinstance(live_price, tuple):
                    live_price = float(live_price[0])
                else:
                    live_price = float(live_price)
                #return live_price
                #sell_for_up is 130 if live price is 122 then sell_for_down should changes to 0.0
                if live_price >= sell_decreased_value and not sell_decreased_value_boolean:
                    dynamic_xfor_sub_down_sell = 0.0
                    sell_for_down = average_price - float(dynamic_xfor_sub_down_sell)
                    sell_decreased_value_boolean = True
                    print("sell for down is 0.0")
                # Check if the graph goes up ( or ) goes down and trigger sell
                if live_price >= sell_for_up or live_price <= sell_for_down:
                    sell_order_id = place_sell_order(tradingsymbol,symboltoken,quantity,smartApi)
                    break
            current_time = datetime.now().time()
            # Check if it's time to sell
            if current_time >= sell_time and not sell_triggered:
                sell_order_id = place_sell_order(tradingsymbol,symboltoken,quantity,smartApi)
                sell_triggered = True
                return("buy orders are not sell so At 3:15pm orders are cancelled,due to market timing")
            sleep_time.sleep(1)
            print(f"checking for sell......")
        return sell_order_id
    except Exception as e:
        return json.dumps({"Error in orderlist_check_placesell":str(e)}),500 
