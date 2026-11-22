# Forecast and feature definitions

This page describes the three-class, 15-minute-ahead model currently used by the
development runner. One bar is one minute, so a 15-bar horizon is approximately
15 minutes when the feed has no missing bars.

## Forecast target

For the close price at bar \(t\), the forward return is:

\[
R_{t,15} = \frac{C_{t+15} - C_t}{C_t}
\]

The notebook uses a neutral threshold of one basis point:

\[
\epsilon = \frac{1}{10{,}000} = 0.0001 = 0.01\%
\]

The target class is:

\[
y_t =
\begin{cases}
-1 & R_{t,15} < -\epsilon \quad \text{(decrease)}\\
0 & -\epsilon \le R_{t,15} \le \epsilon \quad \text{(neutral)}\\
1 & R_{t,15} > \epsilon \quad \text{(increase)}
\end{cases}
\]

The model returns one estimated probability per class. These probabilities are
not guaranteed to be calibrated and should not be interpreted as certainty.

## Input features

Features use observed OHLC prices and returns:

- **Returns:** close-to-close percentage returns over 1, 5, 15, and 30 bars.
- **Log returns:** logarithmic close-to-close return.
- **Candle shape:** candle body, full high-low range, and upper/lower wick sizes.
- **Rolling volatility:** standard deviation of log returns over 15 and 60 bars.
- **Moving-average ratios:** current close relative to its 20-bar simple and
  50-bar exponential moving averages.
- **Lagged returns:** additional 5- and 15-bar log-return history.

Before fitting, the notebook shifts model input features by one bar within each
currency pair. The live inference path uses the same convention. This ensures
the feature vector for a prediction only contains information from prior bars;
the target remains the subsequent 15-bar return.

The rolling statistics and percentage changes are row-based. They represent
minutes only when the input data contains consecutive one-minute bars.

## Training and evaluation

The notebook splits each pair chronologically: the first 80% of usable
observations are used for training and the last 20% for the holdout evaluation.
It compares:

1. **Logistic regression**, with median imputation, standardization, and
   class-balanced fitting.
2. **Histogram gradient boosting**, with median imputation and
   class-balanced fitting.

The saved model is the candidate with the lower holdout log loss. The live
retraining task fits the selected model type on rows with known 15-bar outcomes;
it does not retrain on an unfinished future label.

These metrics measure performance on the available historical sample only.
They do not establish profitability, account for transaction costs or slippage,
or guarantee future performance.

## Earlier concepts

The repository previously explored a one-output ROC/volatility probability and
buy/sell/hold actions. Those equations are historical design notes, not the
current three-class model's implementation.
