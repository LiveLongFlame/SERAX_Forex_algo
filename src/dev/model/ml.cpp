/* End goal: test program over paper trailing in which you can test the performance over 2 years worth of data modelling
 * testing: testing will be done over span of a few weeks in order to dial in the ML training to its absolute best*/
//todo: would be nice to have if i could go head and create a flag such as -train or something to tell the progrma to use pybind or just train the model
#include <armadillo>
#include <mlpack.hpp>
#include <mlpack/core/util/version.hpp>
#include <armadillo>
#include <cmath> 
#include <mlpack/methods/logistic_regression/logistic_regression.hpp>
#include <mlpack/methods/softmax_regression/softmax_regression.hpp>
#include <vector>
#include "objects/PRICE.h"

// Global variable to store model in memory
mlpack::regression::SoftmaxRegression model;


// function calulates the Rate-of-change(ROC) and returns its value
arma::vec roc(const arma::vec& cPrice){
	// amra better implementaiton 
	return arma::diff(cPrice) / cPrice.head(cPrice.n_elem - 1 );
}

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
Action decideAction(double roc, double sdor)
{
    // Prepare input column (features)
    arma::mat input(2, 1);
    input(0, 0) = roc;
    input(1, 0) = sdor;

    // Predicted class index (0 = SELL, 1 = HOLD, 2 = BUY)
    arma::Row<size_t> predicted;
    model.Classify(input, predicted);

    // Return corresponding Action
    return static_cast<Action>(predicted(0));
}



//------------------ comment out when running Makefile in order to test model
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
namespace py = pybind11;
bool initialized = false;
arma::mat X_train;        // features
arma::Row<size_t> y_train; // labels


// Function that loads the model 
void load_model(const std::string& path) {
    mlpack::data::Load(path, "model", model, true); // true = fatal if fail
}

// Gets models features and makes prediction
// Function to predict action using the loaded model
std::vector<double> predict_prob_loaded(double roc, double sdor)
{
    arma::mat input(2, 1);
    input(0, 0) = roc;
    input(1, 0) = sdor;

    arma::mat probabilities;
    model.Classify(input, probabilities);  // fills probabilities for each class

    // Convert arma::mat to std::vector
    std::vector<double> prob(probabilities.n_elem);
    for (size_t i = 0; i < probabilities.n_elem; ++i)
        prob[i] = probabilities(i);

    return prob;
}
// Predict function based on action the ml takes 
// todo: need to add saved ml and add its weight for final outcome
int predict_action(double roc, double sdor, double roc_weight = 1.0, double sdor_weight = 1.0, double bias = 0.0){
    Action act = decideAction(roc,sdor);
    return static_cast<int>(act);
}


// Function that updates and re-train th ml model with new data 
void update_model(double roc, double sdor, int label){
	arma::vec new_point(2);
	new_point(0) = roc;
	new_point(1) = sdor;

	if (!initialized)
	{
		X_train = new_point;
		y_train = arma::Row<size_t>(1);
		y_train(0) = label;
		initialized = true;
	}
	else
	{
		X_train.insert_cols(X_train.n_cols, new_point);
		y_train.insert_cols(y_train.n_cols, arma::Row<size_t>({(size_t)label}));
	}

	model = mlpack::regression::SoftmaxRegression(X_train, y_train, 3);
}
// function that saves the model
void save_model(const std::string& path)
{
    mlpack::data::Save(path, "model", model, true);
}

// Comment out when running Makefile in order to test model
PYBIND11_MODULE(ml, m) {
    m.doc() = "SERAX ML training module";
	m.def("predict_action",&predict_action,
			py::arg("roc"), py::arg("sdor"), py::arg("roc_weight") = 1.0, py::arg("sdor_weight") = 1.0, py::arg("bias") = 0.0);

	m.def("load_model", &load_model, py::arg("path"));
	m.def("predict_prob_loaded", &predict_prob_loaded, py::arg("roc"), py::arg("sdor"));

	m.def("predict_action",&predict_action);
	m.def("predict_prob_loaded",&predict_prob_loaded);

	m.def("load_model",&load_model);
	m.def("update_model",&update_model);
	m.def("save_model",&save_model);
}

//---------------------------------------------------------------------------

// Uncomment main when testing the model
/* int main(){
	//CSV Structure: date, open, high,low,close,volume,average, barCount

	arma::mat raw;
	mlpack::data::Load("../data/ohlc.csv", raw, true);
	std::cout.precision(15);

	// printing out rows and cols in the data set
	std::cout << raw.n_rows << " rows and " << raw.n_cols << " columns loaded.\n";

	// the time in which how much data should we look at to calcuatlte the sdor and roc.. in this case it is 30min 
	// Note: since csv data is in 1 minture intervals it calcuatels every 30 entries.... 
	// This value can be changed and inputed for more a fine tune answer
	std::cout << "Enter window (how many entries of data to calcualte sdor and roc): ";
	size_t window; std::cin >> window; 

	// swap rows and columns in order for arma to read the data 
	raw = raw.t();
	
	//extracting only the close prices 
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

		// we calculate the futurereutrn and use multi-class to predict these values
		double futureReturn = (closePrices(i+1) - closePrices(i)) / closePrices(i);
		if (futureReturn > 0.001) labels.push_back(BUY);
		else if (futureReturn < -0.001) labels.push_back(SELL);
		else labels.push_back(HOLD);
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
	mlpack::regression::SoftmaxRegression model(X,y,3);

	std::cout << "Model trained.\n";
	model.Parameters().print();

	mlpack::data::Save("trading_model.xml", "model", model, true);
	std::cout << "Model saved to trading_model.xml\n";
	

	return 0;

} */
