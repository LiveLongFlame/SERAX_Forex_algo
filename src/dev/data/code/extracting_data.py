# Program will go throuhg each currency pair and request a chunk of the data each time and store it as a csv file in a specified folder.
# The reason we do this is because IBKR does not allow big certain amount of request data. Therefore, we will break the data into different chuncks then run another program which will allow us to combine the chunk data.
from datetime import *
from ib_insync import *
import pandas as pd
import os
import time

# Connects to ib gateway software and information
ib = IB()
ib.connect('127.0.0.1', 4002, clientId=1)

# create base directory 
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#Differnt currency pairs
pairs = [
        ('EUR','USD'),
        ('USD','JPY'),
        ('GBP','USD'),
        ('USD','CHF'),
        ('USD','CAD'),
        ('AUD','USD'),
        ('NZD','USD'),
        ]

# Set parameters that we want to extract information
end_date = datetime.now()
start_date = end_date - timedelta(days=5*365)
delta = timedelta(days=2)
bar_size = '1 min'

# Save the data into the data folder
save_folder = os.path.join(BASE_DIR, 'data')
os.makedirs(save_folder, exist_ok=True)

#Function goes ahead and itrates through the different data and retrives information from api. From here it will go ahead and save the information into a csv file and then move on the next time chunk. 
# The time starts getting informaiton from 5 years ago and each chunk contains two days worth of information 
def fetch_and_save(contract_name, contract):
    current_start = start_date
    chunk_count = 0
    while current_start < end_date:
        current_end = min(current_start + delta, end_date)
        durtaion_days = (current_end - current_start).days
        try:
            # Getting historical data from api
            data = ib.reqHistoricalData(contract, endDateTime=current_end, durationStr=f'{durtaion_days} D', barSizeSetting=bar_size, whatToShow='MIDPOINT', useRTH=False, formatDate=1)

            # Check if the data returned correctly 
            if data: 
                df = util.df(data)
                # Save the chunk into the folder set 
                chunk_file = os.path.join(save_folder, f"{contract_name}_chunk{chunk_count}.csv")
                df.to_csv(chunk_file, index=False)
                print(f"Saved {chunk_file} {len(df)} rows")
                chunk_count +=1
            else:
                print(f"No data found for {contract_name} chunk {chunk_count}")
        except Exception as e: 
            print(f"Error fetching {contract_name}: {e}")
            # Wating before returning
            time.sleep(1)
        # Change the current start time till the end and go again in while loop to get next set of information 
        current_start = current_end
        time.sleep(0.5)
    return 0;

# Defining test pair
# todo: gain 1 year worth of information and verify this is correct 
# loop through the different pairs and contain the information and added them
base = pairs[0][0]
quote = pairs[0][1]
contract_name = f"{base}_{quote}"
contract = Forex(f"{base}{quote}")
print("Fetching data for " + contract_name + " ...")
fetch_and_save(contract_name, contract)

