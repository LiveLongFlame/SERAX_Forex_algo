/* End goal: test program over paper trailing in which you can test the performance over 2 years worth of data modelling
 * testing: testing will be done over span of a few weeks in order to dial in the ML training to its absolute best*/
// todo; need to fix program since now looking at new ohlc.csv file.....
#include <armadillo>
#include <mlpack.hpp>
#include <mlpack/core/util/version.hpp>
#include <armadillo>
#include <cmath> 
#include <vector>
#include "objects/PRICE.h"

// function calulates the Rate-of-change(ROC) and returns its value
arma::vec roc(const arma::vec& cPrice){
	// amra better implementaiton 
	return arma::diff(cPrice) / cPrice.head(cPrice.n_elem - 1 );
}

// function calualtes the Volaitilty (standard devation of returns) 
double sdor(const arma::vec& roc){
	// uses armadillo built in lib for standard devation
	return arma::stddev(roc);
}

// function that finds the probabilty allowing the ML to decide a function
double actionProbabilty(double roc, double sdor, double roc_weight, double sdor_weight, double bias = 0.0){
	// logistic regression with 2 features 
	double z = roc_weight * roc - sdor_weight * sdor + bias;
	return 1.0 / (1.0+ std::exp(-z));
}
// enum in order to do three classification
enum Action{
	SELL = 0,
	HOLD = 1,
	BUY = 2
};

// decides the different thersholds where the ML whill decide 
// NOTE: There values are subject to chagne over time 
Action decideAction(double prob, double buyThreshold = 0.6, double sellThreshold = 0.4){
	if(prob >= buyThreshold) return BUY;
	if(prob <= sellThreshold) return SELL;
	return HOLD;

}
int main(){
	//CSV Structure: date, open, high,low,close,volume,average, barCount

	arma::mat raw;
	mlpack::data::Load("data/code/ohlc.csv",raw, true);

	std::cout.precision(15);
	

	std::cout << raw.n_rows << " rows and " << raw.n_cols << " columns loaded.\n";

	size_t window = 30; // 30-minute window
	// swap rows and columns to make processing easier
	raw = raw.t();
	arma::vec closePrices = raw.col(3);

	std::vector<double> featuresROC;
	std::vector<double> featureVOL;
	std::vector<size_t> labels;

	for (size_t i = window; i+1 < closePrices.n_elem; i++) {
		arma::vec windowPrices = closePrices.subvec(i - window, i);

		arma::vec r = roc(windowPrices);
		double vol = sdor(r);
		double lastRoc = r.tail(1)(0);

		featuresROC.push_back(lastRoc);
		featureVOL.push_back(vol);

		// we label 1 if the price has gone up next tick else 0
		double futureReturn = (closePrices(i+1) - closePrices(i)) / closePrices(i);
		labels.push_back(futureReturn > 0 ? 1 : 0);
	}

	
	size_t N = labels.size();
	arma::mat X(2, N);
	arma::Row<size_t> y(N);

	for (size_t i = 0; i < N; ++i) {
		X(0, i) = featuresROC[i];
		X(1, i) = featureVOL[i];
		y(i) = labels[i];
	}

	std::cout << "Training Model...\n";
	// using mlpack logistic regression to train the model
	mlpack::regression::LogisticRegression<> model(X, y);

	std::cout << "Model trained.\n";
	model.Parameters().print();

	//todo: Save model to file for later use
	//todo: remove date from raw data 






	return 0;

}

