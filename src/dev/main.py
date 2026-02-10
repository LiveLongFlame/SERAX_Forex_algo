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
def model(sdor, roc):
    ml_model = ml.load_model(MODEL_PATH)
    return 0

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
    if choice == 1:
        print("Training ML model...")
        #todo: add functionality to either train model with existing data or with new data from the last hour
        print ("+" + "-" * 78 + "+")
        print("| Note: If you want to train ML with your own data.csv, add it to gather_data |")
        print("| and then run the script train.sh                                            |")
        print ("+" + "-" * 78 + "+")

        #todo: add code to train ML model here
    elif choice == 2:
        initial = float(input("Enter initial value $ "))
        
        print(get_live_data(pairs[0]))

        #idea: we get the last 2 hours of market data and calculate the sdor and roc 
        #then feed that to ml and get a prediction 
        # once a prediction is made feed to another functin that executes the trade based on the predicted values 
        # print out the trade and with what currency pair 
        # then when the program stops when the person hits ctrl+c print out a summary of the trading performance for the session

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
