# This file is the main entry point for the application. It initializes the application and starts the main loop.
import sys
import os
import pybind11
from ib_insync import *
import pandas as pd 
import numpy as np

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
    # ib.connect('127.0.0', 4002, clientId=1)
    print("IB connection established...")

    #todo: get live paper trail data 
    #todo: calcuate roc and sdor
    #todo: add ml model 
    print("\n\n Hello and welcome to SEARX (Saurman's Eye Risk Analysis FX) \n\n")
    menu()


if __name__ == "__main__":
    main()
