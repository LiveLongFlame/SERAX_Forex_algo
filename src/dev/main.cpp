/* End goal: test program over paper trailing in which you can test the performance over 2 years worth of data modelling
 * testing: testing will be done over span of a few weeks in order to dial in the ML training to its absolute best*/
#include <armadillo>
#include <mlpack.hpp>
#include <mlpack/core/util/version.hpp>
#include <armadillo>

using namespace std;
// function calulates the Rate-of-change(ROC) and returns its value
float roc(){
	/* 	todo: ROC 
	 *	- where, ROC = (Price_initial - (Price_initial - time) / (Price_initial -time)) 
	 *	- Example: 
	 *		ROC = (0.60 -1) \ (1))  = -40
	 *	- Should be function that returns  price change over time 
	 */
	return 0.0;
}

// function calualtes the Volaitilty (standard devation of returns) 
float sdor(){
	/* 	todo: Voaltility (Standard deviation of returns = sdor ) 
	 *  - Once we have ROC we need to compute for the mean 
	 *  - where the mean = sum_of_all_ROC/number_of_entries 
	 *  - than calcualte the standard devation 
	 *  - where, sdor = root(sum_squared_deviations / number_of_entries -1)
	 *  - where, sum_squared_devations = (every_entry_in_set - mean)^2 
	 *		- Example: 
	 *			- ROC = 0.05, 0.10, 0.07, 0.12, 0.08
	 *			- mean = 0.084
	 *			- (0.05 - 0.084)^2 = val1
	 *			- (0.10 - 0.084)^2 = val2
	 *			- (0.07 - 0.084)^2 = val3
	 *			- (0.12 - 0.084)^2 = val4
	 *			- (0.08 - 0.084)^2 = val5
	 *			- sum_squared_devations = total_of_vals
	 *	- Higher risk = higher sdor
	 *	- lower risk = lower sdor
	 *	- then sdor * 100 in order to get percentage value
	 *  	*/

	return 0.0;
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

	// load csv file and igonre the first col in the csv file 
	// we igonre the first col due to it being date and not int 
	mlpack::data::Load("data/code/combined.csv",raw, true,false, arma::uvec{0});

	// printing out rows and cols that are present in the current csv table 
	// todo: need to get rid of the date col since date is not a int val and mlpack only accpets integers
	// where the rows are each 1min interval 
	// and each cols is repersented as each different value
	cout << "Rows: " << raw.n_rows << '\n';
	cout << "Cols: " << raw.n_cols << '\n';
	
	
	//todo: create classfier for ML
	

	/* 	todo: probability  
	 *  - prob = 1 / (1 + e^-(roc_weight * ROC - sdor_weight * sdor))
	 *  - returns thershold where the ML will determine to BUY SELL or HOLD stock
	 *  	*/


	return 0;

}

