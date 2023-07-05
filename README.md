# AV-Binance-Trading
Idea: Lightweight REST Api for live algorithmic trading on binance.  
API can connect to multiply data connectors: yahoo, binance.   
Can acquire date with different granularity: stream-like, minute, daily.  
There is a poetry package manager. After executing `poetry shell` on host you have access to 
cli with commands for running strategies.  
There is a streamlit dashboard with top trading currencies and several endpoints which 
can run or stop strategies on host for specified currencies.  
There are functional tests which can be run on live services on host or on mocked data acquired from .csv files:
``TEST_ON_LIVE_SERVICES``variable.
FastAPI supports interactive swagger menu.

## Use cases:
* user can view trading currencies
* user can start bot with different strategies
* user can view reports from different strategies
* there can be several users

## Features:
* make up - run the server
* http://localhost:8000/docs - endpoint documentation
* http://localhost:8000/redoc - interactive endpoint documentation


## Disclaimer: Do not use it at home if you don't know how to :)
You will lose money. Created only for educational purposes.


This repository contains several investment strategies based on technical indicators and tweeter post analysis.  

Some of the strategies need to be run in parallel with crypto streams.
## Technologies:
* python
* pandas
* decorators
* streamlit
* websocket
* ta 
* numpy
* fbprohet
* nltk
* spacy
* re
* plotly
* sqlalchemy
* fastapi
* pytest
* docker
* Github Actions
* click
* poetry
* prospector
* Makefile



## Project structure:

* core - main directory of a project
  * streams.py - methods used for starting streaming data to database
  * utils.py - utilities for project management
  * strategies.py - main file containing all investment strategies, they can be run using features scripts
  * models.py - class models
  * converters.py - data converters, adding, naming, converting columns in dataframes
  * constants.py - constants
  * binance.py - integration with binance API, creating orders, get historical data
  * backtesting.py - backtesting performance of strategies on historical data
* features - directory with `python` scripts used to run an investment strategy 
  * streamlit - live dashboard with currency price
* graphics - graphics services used to visualize data and plot currency value, histograms of tweet analysis
* predictions
  * data_extractors.py - different historical data sources for prediction models
  * predict_models.py - fbprophet model for currency forecasting
* twitter
  * tweety - integration with tweety api, get tweets
* top_worst_crypto_view.py - top performing currencies view

## Environment
Create **.env** file:

| **Variable**          | **Description**                      | **Value**  |
|-----------------------|--------------------------------------|------------|
| api_key               | Binance TestNet api key              |            |
| api_secret            | Binance TestNet api secret           |            |
| API_VALID_KEY         | Binance API valid key                |            |
| API_VALID_SECRET      | Binance API secret key               |            |
| consumer_key          | Tweety API consumer key              |            |
| consumer_secret       | Tweety API consumer secret key       |            |
| bearer_token          | Tweety API bearer token              |            |
| access_token          | Tweety API access token              |            |
| access_token_secret   | Tweety API secret access token       |            |
| TEST_ON_LIVE_SERVICES | Should tests run with real services? | True/False |

For testing purposes you can obtain TestNet tokens from: https://testnet.binance.vision/  
Click log in with GitHub and then generate token: https://testnet.binance.vision/key/generate



Poetry:  
``` poetry shell ``` - enter shell  
```exit``` - exit the shell  
``` poetry add pytest --dev ``` - add requirement  
```poetry update```  - update version  
```poetry install```  - install poetry  
```poetry run binance_trading ``` - main command  
```poetry env use /home/user/anaconda3/bin//python```