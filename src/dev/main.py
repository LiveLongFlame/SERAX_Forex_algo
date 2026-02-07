# This file is the main entry point for the application. It initializes the application and starts the main loop.
import sys
import os
import pybind11
from ib_insync import *
import pandas as pd 
import numpy as np
#todo: import ML model here

#todo: create function that gets live data from the last hour and feeds it into sdor and roc 
#todo: after calcualting sdor and roc, feed those values into the ML model to make predictions
#todo: each trade should be based on the predicted values from the ML model and the current market conditions 
#todo: print out users current balance, open positions, and any other relevant information to the console for each live trade
#todo: users should be alowwed to hit ctrl+c to exit the application at any time and the program should print out a summary of the users trading performance for the session before exiting
def sdor(roc_vals: np.ndarray):
    return np.std(roc_vals, ddof=0) 

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
        print("Initial value: $", initial)
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
    # ib = IB()
    #change port denpending on your IB Gateway or TWS settings
    # ib.connect('127.0.0', 4002, clientId=1)
    print("IB connection established...")

    #todo: get live paper trail data 
    #todo: add ml model 
    print("\n\n Hello and welcome to SEARX (Saurman's Eye Risk Analysis FX) \n\n")
    menu()


if __name__ == "__main__":
    main()
