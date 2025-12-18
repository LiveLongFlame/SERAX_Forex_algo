# This file is for connecting to the ibkr api and extracting historical data in order to train ML aglo
from ib_insync import *
# util.startLoop()  # uncomment this line when in a notebook

ib = IB()
ib.connect('127.0.0.1', 4002, clientId=1)

contract = Forex('EURAUD')
bars = ib.reqHistoricalData(
    contract, endDateTime='', durationStr='6 M',
    barSizeSetting='1 hour', whatToShow='MIDPOINT', useRTH=True)

# convert to pandas dataframe (pandas needs to be installed):
df = util.df(bars)
print(df)
