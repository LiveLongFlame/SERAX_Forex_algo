# SERAX Forex Algorithm

SERAX is an educational forex time-series modeling project. The current development
program connects to Interactive Brokers (IBKR), monitors EUR/USD and AUD/USD
one-minute midpoint bars, and displays model-estimated probabilities that the
price will increase, decrease, or remain neutral over the following 15 bars.
It also prints rolling candlestick charts of the latest 15 completed one-minute
bars for EUR/USD and AUD/USD.

> **Caution:** This project is for learning and experimentation, not live trading.
> Its predictions are not trading advice, are not guaranteed to be calibrated, and
> the program does not place orders.

## Current implementation

- Python live runner: [`src/dev/main.py`](src/dev/main.py)
- Feature generation, inference, and daily model refresh:
  [`src/dev/live_model.py`](src/dev/live_model.py)
- Training and evaluation notebook: [`src/dev/model_testing.ipynb`](src/dev/model_testing.ipynb)
- Saved model artifacts: [`src/dev/model_output/`](src/dev/model_output/)
- Historical training data: [`src/dev/data/`](src/dev/data/)

The notebook compares logistic regression and histogram gradient boosting using a
chronological holdout set. The saved model artifact is selected by test log loss.
The live runner uses the saved artifact to make a new prediction when a completed
one-minute bar arrives. The terminal colors increase green, decrease red, and
neutral yellow.

## Requirements

- Python 3.10 or newer
- TWS or IB Gateway with API access enabled
- IBKR forex market-data permissions for EUR/USD and AUD/USD
- The historical CSV files and model artifacts listed above

Create and activate a virtual environment from the repository root, then install
the Python dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install ib-insync pandas numpy scikit-learn joblib matplotlib seaborn jupyter
```

## IBKR configuration

Start TWS or IB Gateway and enable socket/API clients in its API settings. The
runner defaults to `127.0.0.1:4002`, the common IB Gateway paper-trading port.
Common default ports are:

| Application | Paper | Live |
|---|---:|---:|
| IB Gateway | 4002 | 4001 |
| TWS | 7497 | 7496 |

Set environment variables if your host, port, or client ID differs:

```bash
export IB_HOST=127.0.0.1
export IB_PORT=4002
export IB_CLIENT_ID=17
```

Use the port configured in your own TWS/Gateway settings. A connection-refused
message usually means the application is not running, API access is disabled, or
the host/port does not match.

## Run the live probability monitor

From the repository root:

```bash
source .venv/bin/activate
python src/dev/main.py
```

The runner requests recent one-minute midpoint history, then subscribes to
continuously updated bars. It displays probabilities and refreshes the terminal
candlestick charts after a bar completes. Press `Ctrl+C` to stop. If stdout is not
an interactive terminal, color output is disabled.

The program saves incoming completed bars under `src/dev/data/live/`. It attempts
to retrain both pair models at startup and then every 24 hours, using historical
CSV data plus saved live bars. Training labels are only used when the full
15-minute future outcome is available.

## Train models in the notebook

Open `src/dev/model_testing.ipynb` in Jupyter with the environment above. Its CSV
paths are relative to `src/dev`, so set the notebook working directory to that
folder before running the cells. It reads `data/ohlc_eur_usd.csv` and
`data/ohlc_aud_usd.csv`. The final training cells create or replace the artifacts
in `src/dev/model_output/`.

The live daily retrainer instead reads `combined_eur_usd.csv` and
`combined_aud_usd.csv` in `src/dev/data/`, merging in saved live bars. Re-run
notebook training after changing model features or labels, then restart the live
runner so the new artifacts are loaded.

## Forecast interpretation

The three displayed values are probabilities for:

- **Decrease:** the 15-bar forward close return is below -1 basis point.
- **Neutral:** the return is between -1 and +1 basis point, inclusive.
- **Increase:** the return is above +1 basis point.

One basis point is 0.01% of the current price. The model uses past price-derived
features, shifted so a prediction only uses information available before its
forecast bar. See [`docs/maths.md`](docs/maths.md) for definitions and caveats.
