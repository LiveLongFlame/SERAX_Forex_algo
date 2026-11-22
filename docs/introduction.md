# SERAX introduction

SERAX is an educational project for exploring machine-learning forecasts on
foreign-exchange price data. Its current development version connects to
Interactive Brokers (IBKR) and monitors EUR/USD and AUD/USD.

## Current program

[`../src/dev/main.py`](../src/dev/main.py) subscribes to one-minute IBKR midpoint
bars. When a bar is complete, the program computes features from prior bars and
displays the model's estimated probabilities for a decrease, neutral move, or
increase over the next 15 one-minute bars.

The program is a probability monitor: it does not submit orders, manage
positions, or calculate account profit and loss. A displayed probability is a
model estimate, not a guarantee or investment recommendation. The current
classifier's probability calibration and trading usefulness have not been
established.

The model lifecycle is:

1. Train and compare models using [`../src/dev/model_testing.ipynb`](../src/dev/model_testing.ipynb).
2. Load the selected per-currency model artifact in
   [`../src/dev/live_model.py`](../src/dev/live_model.py).
3. Generate a new prediction after each completed one-minute bar.
4. Retrain at startup and then daily, using historical data and saved live bars
   only when their 15-minute forward labels have matured.

For installation and run instructions, see the
[repository README](../README.md). For target and feature definitions, see
[Maths](maths.md).

## Earlier design ideas

Some project history refers to a C++ classifier, buy/sell/hold actions, order
execution, or account-level profit and loss. Those describe earlier or planned
ideas, not the current Python probability-monitor implementation.
