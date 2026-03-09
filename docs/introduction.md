# Welcome
This is the documentation for the SEARX Project and everthing you need to know. 
# What is SEARX?
SEARX is a free and open-source machine learning algorithm that is designed to be fast and efficient when trading FX. The main concept behind SEARX is to use a combination of technical indicators and machine learning techniques to predict the future price movements of currency pairs. The algorithm is designed to be flexible and can be customized to suit the needs of different traders.
# Implementation
SEARX is implemented in Python and C++. The ML is created in C++ in order to allow fast execution and low latency, while Python is used for connecting to IBKR (Interactive Brokers) and for data processing. 

The program takes in input of the current currency pair, you want to trade, and the amount you want to invest. The algorithm then uses a combination of technical indicators and machine learning techniques to predict the future price movements of the currency pair. Based on the predictions, the algorithm will make a decision on whether to buy,sell or hold the currency pair. Then the algorithm will be re-trained with new informaiton and the process will repeat itself. Once you stop the program you will see your current open positions and your profit/loss as well as your current balance.
## Algorithm 
For more understanding about the algorith, please check the [Maths](maths.md) page.

## Future Plans
Right now the program is desinged only for 1 currency pair, at a time and the ml is very much in (v1) however in the future I plan to add multiple currency pairs and also to improve the machine learning algorithm by adding more features and using more advanced techniques. 
