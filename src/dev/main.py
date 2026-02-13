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

def ml_prediction(close_prices, roc_weight=0.5, sdor_weight=0.5, bias=0.0):
    sdor_val, roc_val = calcuate_sdor_and_roc(close_prices)
    action_str = ml.predict_action(roc_val, sdor_val, roc_weight, sdor_weight, bias)
    return {0: "Sell", 1: "Hold", 2: "Buy"}[action_str]


def fetch_live_window(pair, duration='120 S'):
    contract = Forex(pair, exchange='IDEALPRO')
    ib.qualifyContracts(contract)
    bars = ib.reqHistoricalData(
        contract,
        endDateTime='',
        durationStr=duration,   
        barSizeSetting='1 min',
        whatToShow='MIDPOINT',
        useRTH=True,
        formatDate=1
    )
    if not bars:
        print(f"No historical data returned for {pair} with duration {duration}")
        return np.array([])
    
    df = util.df(bars)
    if 'close' not in df:
        print(f"'close' column not found in data for {pair}")
        return np.array([])
    
    return df['close'].values


def calcuate_sdor_and_roc(close_prices):
    returns = np.diff(close_prices) / close_prices[:-1]
    sdor_value = np.sqrt(np.mean(returns[returns < 0]**2)) if len(returns[returns < 0]) > 0 else 0.0
    roc_value = returns[-1] if len(returns) > 0 else 0.0
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
    print("1. Trade with Model")
    print("2. Exit")
    choice = int(input("\n> "))
    print("\n")
    if choice == 1:
        # print(get_live_data(pairs[0]))
        # pair = input("Input currency pair: ")
        close_prices = fetch_live_window(pairs[0], duration= '120 S')  
        if len(close_prices) == 0:
            print("No data, skipping prediction")
        else:
            prediction = ml_prediction(close_prices)

        print(f"Predicted action: {prediction}")
        prediction = ml_prediction(close_prices)
        # initial = float(input("Enter initial bid:  "))
        
        # prints out live data
        # print(get_live_data(pairs[0]))
        
        

        '''
        todo: 
        1. Load pretrained ml model 
        3. pass new data to c++ functuion that updates model in memory 
        4. make prediction and execute trade based on prediction and current market conditions

        '''

    elif choice == 2:
        print("Exiting application...")
        sys.exit()
    else:
        print("Invalid input. Please try again.")
        menu()

def main():
    print("Starting application...")
    print("Initializing IB connection...")
    #change port depending on your IB Gateway or TWS (check settings to let you know what port you are pointing to)
    ib.connect('127.0.0', 4002, clientId=1)
    print("IB connection established...")

    print("\n\n Hello and welcome to SEARX (Saurman's Eye Risk Analysis FX) \n\n")
    menu()

if __name__ == "__main__":
    main()
