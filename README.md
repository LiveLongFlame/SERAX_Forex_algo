# ⚠️**Caution**
This project is still in development and is not expected to be used in the real market. This is just for learning and better understanding with ML's and forex market. 

# SERAX_Forex_algo
SERAX (Saurman's Eye Risk Analysis FX) is a project to create a Trading Machine learning Algorithm, in order predict when to Sell, But or Hold in the FX market. The model will look at different currency pairs and predict what prices will give the best outcome.  


# 📚 Documentation (Further understanding)
In order to get a better understanding of the maths and idea of the project and the different versions. This will be all under the *"docs"*

# Setup (Linux)
*Note: Commands are using debain. Follow same processes with different distros just replace with ditro installer* 
Here i will go through the basic setup you will need in order to setup the program running. First you will need to install a few important packages in order to run the program. 

## **MLPACK** 
Follow the link to see how to install and setup MLpack: 

`https://www.youtube.com/watch?v=wcEFce7IaS8`

## **IBKR** 
You will need to install and setup your own IBKR trading account and install IBKR Gateway.
*Note: You can also always use TWS as well however you will need to change main.cpp to connect via the port. IBKR provides documentation explaining this*


# Building and Running
## Step 1: Setup Environment
 1. Run `setup_env.sh` to setup the environment variables for the project.
 2. Run `source venv/bin/activate` to activate the virtual environment. 
## Step 2: Build the Project
 1. Run `python3 main.py` to build the project and run the main program. 
## NOTES: 
* Make sure to have your IBKR Gateway running and connected to your account before running the main program.
* The program will start training the model and then will start making predictions based on the trained model
* If build fails, try rebuilding the model by running `rm -rf src/dev/model/build && mkdir src/dev/model/build && cd src/dev/model/build && cmake .. -DPython_EXECUTABLE=../venv/bin/python && cmake --build .` and then try running the main program again.

