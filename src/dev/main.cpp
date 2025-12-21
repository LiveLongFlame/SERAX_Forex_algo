/* End goal: test program over paper trailing in which you can test the performance over 2 years worth of data modelling
 * testing: testing will be done over span of a few weeks in order to dial in the ML training to its absolute best*/
#include <mlpack.hpp>
#include <mlpack/core/util/version.hpp>

using namespace std;
int main(){
	// csv information that gets broken up into are seperated with 
	// date, open, high,low,close,volume,average, barCount
	// exmaple: 2024-12-19 17:15:00-5:00, 1.036425, 1.036445, 1.0364, 1.036405, -1.0, -1.0, -1
	
	/* 	todo: ROC 
	 *	- where, ROC = (Price_initial - (Price_initial - time) / (Price_initial -time)) 
	 *	- Example: 
	 *		ROC = (0.60 -1) \ (1))  = -40
	 *	- Should be function that returns  price change over time 
	 */

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

	/* 	todo: probability  
	 *  - prob = 1 / (1 + e^-(roc_weight * ROC - sdor_weight * sdor))
	 *  - returns thershold where the ML will determine to BUY SELL or HOLD stock
	 *  	*/

	
	// printing version of mlpack and returing it as a string
	cout << "mlpack version: " << mlpack::util::GetVersion() << "\n";

	return 0;

}
	
