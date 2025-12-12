# Implementation
## V.1 
For version 1 we want to create a simple Algorithm where we get the Rate of Change (ROC) and the Volatility using Standard Deviation and create probability to see when the machine should Sell, Buy or Hold
### Price Momentum: ROC (Rate of Change)
We will calculate the change of which the currencies fluxurates over a period of time. Given $n$ is time, $$\text{|ROC|} = \frac{Price_t - Price_{t-n}}{Price_{t-n}} \times 100,\text{where } n \text{ is time.}$$
#### Example
***
If the AUD/USD = 0.60/1.00, and yesterday was 1/1, then in $n = 1$ day $$\begin{aligned}\text{|ROC|} = \frac{0.60 - 1}{1} \times 100 = 40\end{aligned}$$ meaning there was a 40% price change
***

### Volatility (Standard Deviation of returns) [Risk]
Throughout forex prices fluxuatie constanly. One way we can help predict the overall trend of the current currency pair. We first look at the $r_t =$ Price/time, which we can use $$r_t = \frac{P_t - P_{t-1}}{P_{t-1}}$$
From here we can compute the mean such that, $$\bar{r} = \frac{1}{N}\sum^N_{t=1}r_t$$where $N = time$
Once he mean is calculated we can use the standard deviation formula $$\sigma = \sqrt{\frac{1}{N-1}\sum^N_{i=1}(r_t - \bar{r})^2}$$ where higher $\sigma \to$ Prices Flucurate More $\to$ Higher risk and lower $\sigma \to$ Price are stable $\to$ lower risk. 

### Probability
Now that have the risk and ROC we can go ahead ande the margin with $$p(up) = \frac{1}{1+e^{-(\alpha \cdot ROC-\beta \cdot \sigma)}}$$where $\alpha =$ weight of ROC, $\beta =$ weight of risk. 

Since we have calculated the probability of risk we can finalise our choices by $$Choice = $$ 
## V2
In version1 although we have calculated the ROC and risk, we can better calculated better risk with more common methods such as GRACH (Generalised Autoregressive Conditional Heteroskedasticity).Further, adding a logistic regression and plat scaling for improved probability calculations. 
### GRACH Model
GRACH increases accuracy as instead of assuming constant variance, GRACH assumes that periods of high volatility tend to follow high volatility, and calm periods follow calm periods. 
We write a basic return model shown as,  $$r_t = \mu + \sigma_t \cdot z_t$$ where $\mu$ is the mean return, $\sigma_i$ is time-varying volatility, and $z_t$ is a standardised shock (often assumed to be normal). 
The main part of GRACH model is written as, $$\sigma^2_t = \omega + \alpha \cdot e^2_{t-1}+ \beta \cdot \sigma^2_{t-1}$$ where $e_{t-1} = r_{t-1} - \mu$. $\alpha$, makes the volatility respond to large market moves while $\beta$ controls how persistent volatility is over time and $\omega$, is constant, as the volatility floor.  
Further we can gather a Long-run mean allowing us estimate the "natural" volatility level of the assess when the markets are calm. This is defined as,  $$\sigma^2 = \frac{\omega}{1-\alpha - \beta}$$
### Logistic Regression 
Logistic regression is a statistical model used to predict between 0 and 1 based on input features. This can be defined as, 
$$p = \frac{1}{1+ e^{-(\beta_0 + \beta_1 x_1 + \ldots)}}$$
### Plat Scaling 
Now Play Scaling is a calibration method in which takes in the models raw score and converts it into a more accurate, better calibrated probability. This can be written as $$P(y=1 |f) = \frac{1}{1 + exp(Af + B)}$$ where $f$ = model's raw Score. A,B are learned on a validation set. 