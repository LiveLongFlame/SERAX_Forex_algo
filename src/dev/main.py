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

ml.train_model(CSV_DATA, MODEL_PATH)
#todo: print out users current balance, open positions, and any other relevant information to the console for each live trade
#todo: users should be alowwed to hit ctrl+c to exit the application at any time and the program should print out a summary of the users trading performance for the session before exiting

pairs = ['EURUSD', 'USDJPY' , 'GDPUSD', 'USDCHF', 'USDCAD', 'AUDUSD', 'NZDUSD']

def ml_model(ccy_pair, ib, model):
    contract = Forex(ccy_pair)
    ib.qualifyContracts(contract)
    bars = ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr='2 H',
            barSizeSetting='1 min',
            whatToShow='MIDPOINT',
            useRTH=False,
            formatDate=1
            )
    df = util.df(bars)
    df.set_index('date', inplace=True)

    if not bars:
        print("No data received for the specified currency pair.")
        return 1 
    
    #todo: implement model with pybind 11
    return 0

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
        #FOR TESTING PURPOSES ONLY
        print("Initial value: ", initial)
        print(ml.__doc__)
        #------------------------------------
        #todo: add code to use ML model to make predictions here
    elif choice == 3:
        print("Exiting application...")
        sys.exit()
    else:
        print("Invalid input. Please try again.")
        menu()

def main():
    print("Starting application...")
    print("Initializing IB connection...")
    ib = IB()
    #change port denpending on your IB Gateway or TWS settings
    ib.connect('127.0.0', 4002, clientId=1)
    print("IB connection established...")

    #todo: get live paper trail data 
    #todo: add ml model 
    print("\n\n Hello and welcome to SEARX (Saurman's Eye Risk Analysis FX) \n\n")
    menu()


if __name__ == "__main__":
    main()
