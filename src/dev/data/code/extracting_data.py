# Program will go throuhg each currency pair and request a chunk of the data each time and store it as a csv file in a specified folder.
# The reason we do this is because IBKR does not allow big certain amount of request data. Therefore, we will break the data into different chuncks then run another program which will allow us to combine the chunk data.
from datetime import datetime
from ib_insync import *
import pandas as pd
import datatime
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
end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=5*365)
delta = datetime.timedelta(days=2)
bar_size = '1min'

# Save the data into the data folder
save_folder = os.path.join(BASE_DIR, 'data')
os.makedirs(save_folder, exist_ok=True)

#Function to fetch historical data in chunks
def fetch_and_save(contract_name, contract):
    #todo: connect to gateway with parameters 
    #todo: create loop the itrates through the data and information allowing extract information
    #todo: move informationa and save things into a csv file 
    return 0;
