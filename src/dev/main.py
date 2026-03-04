# This file is the main entry point for the application. It initializes the application and starts the main loop.
import sys
import os
import pybind11
from ib_insync import *
import pandas as pd 
import numpy as np
import ml
from datetime import datetime
from zoneinfo import ZoneInfo
from colorama import init, Fore, Style
# Initialize colorama
init(autoreset=True)

MODEL_PATH= "model/trading_model.xml"
CSV_DATA = "data/ohlc.csv"
# Loads the trained model
ml.load_model(MODEL_PATH)

pairs = ['EURUSD', 'USDJPY' , 'GBPUSD', 'USDCHF', 'USDCAD', 'AUDUSD', 'NZDUSD', 'AUDNZD', 'EURGBP', 'EURJPY']
ib = IB()

# --------------------------------- Live Market data ----------------------------------
# determines for the ccy pair if the market is open or closed
# todo: need to fix this function as it says market is closed however it is open... need to look into this
def is_market_open(pair):
    contract = Forex(pair, exchange='IDEALPRO')
    ib.qualifyContracts(contract)

    details = ib.reqContractDetails(contract)
    if not details:
        return False

    liquid_hours = details[0].liquidHours
    now = datetime.now(ZoneInfo("US/Eastern"))

    sessions = liquid_hours.split(';')

    for session in sessions:
        if not session or "CLOSED" in session:
            continue

        try:
            start_str, end_str = session.split('-')

            start_dt = datetime.strptime(
                start_str, "%Y%m%d:%H%M"
            ).replace(tzinfo=ZoneInfo("US/Eastern"))

            end_dt = datetime.strptime(
                end_str, "%Y%m%d:%H%M"
            ).replace(tzinfo=ZoneInfo("US/Eastern"))

            if start_dt <= now <= end_dt:
                return True

        except ValueError:
            # In case IBKR changes formatting slightly
            continue

    return False


# For each ccy pair will gather live data of the close prices within a give window
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
    
    print(df['close'])
    return df['close'].values

# gets live market data per tick
def get_live_data(pair):
    contract = Forex(pair, exchange='IDEALPRO')
    ib.qualifyContracts(contract)
    ticker = ib.reqMktData(contract)
    ib.sleep(2)
    return ticker
# -------------------------------------------------------------------------------------



# -----------------------------------  SDOR and ROC ---------------------------------------------
def sdor(returns: np.ndarray):
    downside = returns[returns < 0]
    if len(downside) == 0:
        return 0.0
    return np.sqrt(np.mean(downside ** 2))

def roc(close_prices: np.ndarray):
    return np.diff(close_prices) / close_prices[:-1]

# calcualtes the stadarad deviation and the rate of change
def calcuate_sdor_and_roc(close_prices):
    returns = np.diff(close_prices) / close_prices[:-1]
    sdor_value = np.sqrt(np.mean(returns[returns < 0]**2)) if len(returns[returns < 0]) > 0 else 0.0
    roc_value = returns[-1] if len(returns) > 0 else 0.0
    return sdor_value, roc_value
# ----------------------------------------------------------------------------------------------


# Based on model predictions this function will handle if a trade happens or not
def trade(pair, trade_units=10000):
    """
    Execute trade based on ML prediction
    pair: str, currency pair e.g. 'AUDUSD'
    trade_units: int, number of base currency units to trade
    """
    # Ensure market is open
    if not is_market_open(pair):
        print(f"{pair} market is closed. Skipping trade.")
        return

    # Fetch live data for features (last 2 hours) 
    close_prices = fetch_live_window(pair, duration='7200 S')
    if len(close_prices) < 2:
        print(f"Not enough data for {pair}. Skipping trade.")
        return

    # Calculate SDOR and ROC
    sdor_val, roc_val = calcuate_sdor_and_roc(close_prices)

    # Get ML prediction
    prob_matrix = ml.predict_prob_loaded(roc_val, sdor_val)
    action_index = int(np.argmax(prob_matrix))  # 0=SELL, 1=HOLD, 2=BUY
    action_str = {0: "Sell", 1: "Hold", 2: "Buy"}[action_index]

    print(f"Predicted action for {pair}: {action_str}")
    print(f"Probabilities: {prob_matrix}")

    if action_str == "Hold":
        print(f"Holding position for {pair}. No trade executed.")
        return

    # Create IBKR contract
    contract = Forex(pair, exchange='IDEALPRO')
    ib.qualifyContracts(contract)

    # Determine order type
    if action_str == "Buy":
        order = MarketOrder("BUY", trade_units)
    else:
        order = MarketOrder("SELL", trade_units)

    # Place the order
    trade = ib.placeOrder(contract, order)
    ib.sleep(1)  # Give IB a moment to process

    print(f"Order executed: {action_str} {trade_units} units of {pair}")

# --------------- Testing trade to see what will happen (force to execute a trade [igonres ml prediction]) ----------------
def trade_test(pair, trade_units=10000):
    if not is_market_open(pair):
        print(f"{pair} market is closed. Skipping trade.")
        return

    contract = Forex(pair, exchange='IDEALPRO')
    ib.qualifyContracts(contract)
    order = MarketOrder("BUY", trade_units)
    trade = ib.placeOrder(contract, order)

    ib.sleep(2)

    status = trade.orderStatus.status
    if status == "Filled":
        print(Fore.GREEN + f"Order executed: BUY {trade_units} units of {pair}")
    else:
        print(Fore.RED + f"Order NOT executed. Status: {status}")
        # Print IBKR messages from log
        for entry in trade.log:
            if entry.message:
                print(Fore.RED + f"Reason: {entry.message}")

    # Show positions
    print("\nOpen Positions:")
    for pos in ib.positions():
        color = Fore.GREEN if pos.position >= 0 else Fore.RED
        print(f"{pos.contract.symbol}: {color}{pos.position} units at avg price {pos.avgCost}{Style.RESET_ALL}")
    # Fetch account summary after trade account_summary = ib.accountSummary()
    #todo: need to printing the current position in the market and need to show the profit and easy to read data for understanding
    summary = ib.accountSummary()
    for s in summary:
        if s.tag == "NetLiquidation":
            print("Account Value:", s.value, s.currency)



# -----------------------------------------------------------------------------


# checks the prediction of what a person should do manually 
# note: this function is for testing only and is useless otherwise for the moment
#todo: re-look at this function to see if it is nesscarry
def ml_prediction(close_prices, roc_weight=0.5, sdor_weight=0.5, bias=0.0):
    sdor_val, roc_val = calcuate_sdor_and_roc(close_prices)
    action_str = ml.predict_action(roc_val, sdor_val, roc_weight, sdor_weight, bias)
    return {0: "Sell", 1: "Hold", 2: "Buy"}[action_str]

def menu():
    print("Menu:")
    print("1. Trade with Model")
    print("2. Exit")
    choice = int(input("\n> "))
    print("\n")
    if choice == 1:
        # print(get_live_data(pairs[0]))
        print("Welcome to trading with SEARX! (Saurman's Eye Risk Analysis FX) \n\n")
        print("Your current cash in account is: ")
        summary = ib.accountSummary()
        for s in summary:
            if s.tag == "NetLiquidation":
                print("Account Value:", s.value, s.currency)

        pair = input("Input currency pair: ").upper()
        if len(pair) != 6:
            raise ValueError("\nMust enter a vaild curreny pair")
        bid = input("Input intial bid amount: ")
        trade_test(pair, bid)


        
        '''
        todo: 
        3. pass new data to c++ functuion that updates model in memory 
        4. make prediction and execute trade based on prediction and current market conditions
        5. need to restart cash account with --restart flag when starting program in order to make sure that everything works for trading

        Idea: 
        - So the user enters a bid in which gets spilt up evenly across the diffferent defined currancy pairs
        - from here there will be a model for each currecny pair 
        - the models will update with the current live data and store all in memory 
        - from here you will see the different currecny pairs and see how it is going 
        - Example: (if - color is red, else green)
            PAIR (Initnal bid): + 100
            AUDUSD (100): -34
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
