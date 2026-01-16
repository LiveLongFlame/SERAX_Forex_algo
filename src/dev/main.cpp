/* End goal: test program over paper trailing in which you can test the performance over 2 years worth of data modelling
 * testing: testing will be done over span of a few weeks in order to dial in the ML training to its absolute best*/
#include <armadillo>
#include <mlpack.hpp>
#include <mlpack/core/util/version.hpp>
#include <armadillo>
#include <cmath> 
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
int main(){
	// csv information that gets broken up into are seperated with 
	// date, open, high,low,close,volume,average, barCount
	// exmaple: 2024-12-19 17:15:00-5:00, 1.036425, 1.036445, 1.0364, 1.036405, -1.0, -1.0, -1

	// loading data into amradillo
	arma::mat raw;

	// load csv file  
	mlpack::data::Load("data/code/combined.csv",raw, true);

	// todo: getting rid of first row of date since it is not needed anymore

	// printing out rows and cols that are present in the current csv table 
	// where the rows are each 1min interval 
	// and each cols is repersented as each different value
	// cout << "Rows: " << raw.n_rows << '\n';
	// cout << "Cols: " << raw.n_cols << '\n';
	
	std::cout.precision(17);
	// printing out row of information
	// std::cout << raw.col(0);
	
	// for printing out more pericse values from the first row 
	for (size_t i =1; i < raw.n_rows; i++){
		std::cout << raw(i,0) << "\n";
	}
	
	//todo: create classfier for ML
	

	/* 	todo: probability  
	 *  - prob = 1 / (1 + e^-(roc_weight * ROC - sdor_weight * sdor))
;	 *  - returns thershold where the ML will determine to BUY SELL or HOLD stock
	 *  	*/


	return 0;

}

