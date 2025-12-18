# Program will go throuhg each currency pair and request a chunk of the data each time and store it as a csv file in a specified folder.
# The reason we do this is because IBKR does not allow big certain amount of request data. Therefore, we will break the data into different chuncks then run another program which will allow us to combine the chunk data.
from ib_insync import *
import pandas as pd
import datatime
import os
import time

ib = IB()
ib.connect('127.0.0.1', 4002, clientId=1)

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

# todo: add different parameteres in order to define what data needs to be extracted. Example: 5 Y with bar size of 1min with 2 day chunks....

#todo: save data in csv inside folder 

# call api and extract the information.
