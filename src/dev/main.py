# This file is the main entry point for the application. It initializes the application and starts the main loop.
import sys
import os
import pybind11
from ib_insync import *
import pandas as pd 
import numpy as np
import ml

MODEL_PATH= "model/trading_model.xml"
CSV_DATA = "data/ohlc.csv"

pairs = ['EURUSD', 'USDJPY' , 'GDPUSD', 'USDCHF', 'USDCAD', 'AUDUSD', 'NZDUSD']

ib = IB()

#todo: this function should take the sdor and roc values and feed them to the ML model to get a prediction for the next price movement
def model(sdor, roc, roc_weight, sdor_weight, bias):
    prob = ml.predict_action(roc, sdor, roc_weight, sdor_weight, bias)
    action_str = {0: "Sell", 1: "Hold", 2: "Buy"}[prob]
    return action_str

def calcuate_sdor_and_roc(pair):
    contract = Forex(pair, exchange='IDEALPRO')
    ib.qualifyContracts(contract)
    bars = ib.reqHistoricalData(
        contract,
        endDateTime='',
        durationStr='2 H',
        barSizeSetting='1 min',
        whatToShow='MIDPOINT',
        useRTH=True,
        formatDate=1
    )
    df = util.df(bars)
    close_prices = df['close'].values
    returns = roc(close_prices)
    sdor_value = sdor(returns)
    roc_value = roc(close_prices)[-1]  # Get the most recent ROC value
    return sdor_value, roc_value

def get_live_data(pair):
    contract = Forex(pair, exchange='IDEALPRO')
    ib.qualifyContracts(contract)
    ticker = ib.reqMktData(contract)
    ib.sleep(2)
    return ticker

#todo: this function should execute a trade based on the predicted values from the ML model and the current market conditions
def trade():
    return 0

def sdor(returns: np.ndarray):
    downside = returns[returns < 0]
    if len(downside) == 0:
        return 0.0
    return np.sqrt(np.mean(downside ** 2))

def roc(close_prices: np.ndarray):
    return np.diff(close_prices) / close_prices[:-1]

def menu():
    print("Menu:")
    print("1. Train ML model")
    print("2. Use ML model to make predictions")
    print("3. Exit")
    choice = int(input("\n> "))
    print("\n")
    #todo: get rid of this since it is out of scope of project
    if choice == 1:
        print("Training ML model...")
        #todo: add functionality to either train model with existing data or with new data from the last hour
        print ("+" + "-" * 78 + "+")
        print("| Note: If you want to train ML with your own data.csv, add it to gather_data |")
        print("| and then run the script train.sh                                            |")
        print ("+" + "-" * 78 + "+")

        #todo: add code to train ML model here
    elif choice == 2:
        initial = float(input("Enter initial bid:  "))
        
        # prints out live data
        # print(get_live_data(pairs[0]))
        
        # fake but reasonable values
        roc_val = 0.0002
        sdor_val = 0.0008
        roc_weight = 0.5
        sdor_weight = 0.5
        bias = 0.1
        # todo: need to add trained model
        print(model(sdor_val, roc_val, roc_weight, sdor_weight, bias))
        

        '''
        todo: 
        1. Load pretrained ml model 
        2. feed live data into train_model to calulate roc and sdor then feed those values into the model
        3. pass new data to c++ functuion that updates model in memory 
        4. make prediction and execute trade based on prediction and current market conditions

        '''

        
    elif choice == 3:
        print("Exiting application...")
        sys.exit()
    else:
        print("Invalid input. Please try again.")
        menu()

def main():
    print("Starting application...")
    print("Initializing IB connection...")
    #change port denpending on your IB Gateway or TWS settings
    ib.connect('127.0.0', 4002, clientId=1)
    print("IB connection established...")

    #todo: get live paper trail data 
    #todo: add ml model 
    print("\n\n Hello and welcome to SEARX (Saurman's Eye Risk Analysis FX) \n\n")
    menu()


if __name__ == "__main__":
    main()
