from datetime import datetime,time,timedelta
import time as sleep_time
import sys

def round_open_index(get_index, dynamic_index):
    if dynamic_index == "NIFTY 50":
        rounded_open_index = round(get_index // 50) * 50
        if get_index % 50 >= 25:
            rounded_open_index += 50
    elif dynamic_index == 'BANKNIFTY':
        rounded_open_index = round(get_index // 100) * 100
        if get_index % 100 >= 50:
            rounded_open_index += 100
    return rounded_open_index

# Test cases
get_index = 21951.4
dynamic_index = "NIFTY 50"
rounded_open_index = round_open_index(get_index, dynamic_index)
print(rounded_open_index)  # Output: 21200

get_index = 21951.4
dynamic_index = "NIFTY 50"
rounded_open_index = round_open_index(get_index, dynamic_index)
print(rounded_open_index)  # Output: 21250

sys.exit()

list1 = [1,None]
for i in list1:
    print(i)
 
order = 1

other_order_id = next(id for id in list1 if id != order)
print(other_order_id)
               
sys.exit()






data = [[1, 2], [3, 4]]
for i in data:
    value1 = i[0]
    value2 = i[1]
    if value1 == 1:
        for j in data:
            inner_value1 = j[0]
            inner_value2 = j[1]
            if inner_value1 != value1:
                print(inner_value1)
sys.exit()
lot_size = 3
desired_quantity = 50

# Adjust the quantity to be a multiple of the lot size
adjusted_quantity = (lot_size * desired_quantity )
print(adjusted_quantity)

sys.exit()

list1 = [
     1,[
          [
               "akhil",
               "python programing"
          ]
     ]
]


ce_strike_lp = [
    195,
    [
        ["44804", "NIFTY08FEB2421850CE"]
    ],
    
]

# Values to add
dynamic_xforbuy = 100
dynamic_xfortriggerprice_buy = 1
dynamic_lots_quantity = 1

# Create a new list with the additional values
additional_values = [dynamic_xforbuy, dynamic_xfortriggerprice_buy, dynamic_lots_quantity]
print(additional_values)

# Concatenate the original list with the additional values
ce_strike_lp =  ce_strike_lp[1] + additional_values

# Display the modified list
print(ce_strike_lp)
sys.exit()

my_list = [117, [["20080", "NIFTY5021700CE"]]]

buyplus = 100
triggerprice = 1
quantity = 1

# Add the new values to the list
my_list.extend([buyplus, triggerprice, quantity])

# Display the modified list
print(my_list)
sys.exit()

lot_size = 3
desired_quantity = 50

# Adjust the quantity to be a multiple of the lot size
adjusted_quantity = lot_size * desired_quantity 
print(adjusted_quantity)

# Use t
sys.exit()
data = [
    ["2024-01-31T10:00:00+05:30", 197.55, 199.85, 181.5, 182.2, 8453],
    ["2024-01-31T10:01:00+05:30", 184.55, 186.1, 177.1, 180.4, 8023],
    ["2024-01-31T10:02:00+05:30", 180.9, 187.3, 178.75, 181.15, 4808],
    ["2024-01-31T10:03:00+05:30", 180.45, 196.0, 180.45, 194.0, 7748],
    ["2024-01-31T10:04:00+05:30", 191.95, 200.55, 188.3, 200.45, 5246]
]

# Extract the low prices from each list
low_prices = [item[3] for item in data]
print(low_prices)
# Find the minimum low price
min_low_price = min(low_prices)

# Print or return the result
print(min_low_price)

sys.exit()
def get_today_date_tdngsymbl():
        today_date = datetime.now().date()
        formatted_expiry = today_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
        return formatted_expiry


indexname = "NIFTY 50"
today_expiry_date_str = get_today_date_tdngsymbl()
today_expiry_date = datetime.strptime(today_expiry_date_str, "%a, %d %b %Y %H:%M:%S GMT")
weekday = today_expiry_date.weekday()
        
if indexname == "NIFTY 50":
    days_to_add = (3 - weekday) % 7
elif indexname == "BANKNIFTY":
    days_to_add = (2 - weekday) % 7

nearest_weekday = today_expiry_date + timedelta(days=days_to_add)
        # Format the nearest weekday date as a string
#nearest_weekday_str = nearest_weekday.strftime("%a, %d %b %Y %H:%M:%S")
nearest_weekday_str = nearest_weekday.strftime("%Y-%m-%d")


expiry_date = datetime(2024, 2, 1)

formatted_date = expiry_date.strftime("%d%b%Y").upper()

print(nearest_weekday_str)
sys.exit()
get_index = 21741.55
dynamic_index = 'BANKNIFTY'
roundfig_openindex = round(get_index)
if dynamic_index == "NIFTY 50":
    rounded_openindex = round(roundfig_openindex / 50 + 0.5) * 50
elif dynamic_index == 'BANKNIFTY':
    rounded_openindex = round(roundfig_openindex / 100 + 0.5) * 100

print(rounded_openindex)
sys.exit()

def get_today_date():
        today_date = datetime.now().date()
        formatted_today_year = today_date.strftime("%Y,%#m,%#d")
        return formatted_today_year

today = get_today_date()
print(today)
print(type(today))
year, month, day = today.split(",")
# Create a datetime object representing the time at which you want to get the NIFTY 50 or BANKNIFTY index open price
from_date_time = datetime(int(year),int(month),int(day),14,30,0)
to_date_time = datetime(int(year),int(month),int(day),14,31,0)
onetime = from_date_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z',
print(onetime)
print(type(onetime))
from_date_time_str = "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(
    from_date_time.year, from_date_time.month, from_date_time.day,
    from_date_time.hour, from_date_time.minute, from_date_time.second
)
print(from_date_time_str)
print(type(from_date_time_str))

print(from_date_time)
print(type(from_date_time))
print(to_date_time)
       