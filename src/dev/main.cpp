/* End goal: test program over paper trailing in which you can test the performance over 2 years worth of data modelling
 * testing: testing will be done over span of a few weeks in order to dial in the ML training to its absolute best*/
#include <armadillo>
#include <mlpack.hpp>
#include <mlpack/core/util/version.hpp>
#include <armadillo>
#include <cmath> 
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
	// csv information that gets broken up into are seperated with 
	// date, open, high,low,close,volume,average, barCount
	// exmaple: 2024-12-19 17:15:00-5:00, 1.036425, 1.036445, 1.0364, 1.036405, -1.0, -1.0, -1

	// loading data into amradillo
	arma::mat raw;

	// load csv file  
	mlpack::data::Load("data/code/combined.csv",raw, true);

	std::cout.precision(17);
	
	// for printing out more pericse values from the first row 
	// i must be 1 else the ML will take in the date as input
	// note: the date could be useful later as more a historic data training however for now it is not important
	
	//todo: extracting the closing prices
	
	// Creating new pricing object
	PRICE P(raw.col(0)[0], raw.col(0)[1], raw.col(0)[2], raw.col(0)[3], raw.col(0)[4], raw.col(0)[5], raw.col(0)[6], raw.col(0)[7]);
	P.printPrice();

	// idea of what ML evalutation could be 
	/* size_t window = 30; // 30-minute window
	double roc_w = 1.2;
	double sdor_w = 0.8;
	double bias = 0.0;

	for (size_t i = window; i < closePrices.n_elem; ++i) {
		arma::vec windowPrices = closePrices.subvec(i - window, i);

		arma::vec r = roc(windowPrices);
		double vol = sdor(r);
		double lastRoc = r.tail(1)(0);

		double prob = actionProbability(lastRoc, vol, roc_w, sdor_w, bias);
		Action action = decideAction(prob);

		if (action == BUY)
			std::cout << "BUY @ index " << i << " prob=" << prob << "\n";
		else if (action == SELL)
			std::cout << "SELL @ index " << i << " prob=" << prob << "\n";
	} */


	


	return 0;

}

