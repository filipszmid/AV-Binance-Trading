# AV-Binance-Trading
## Disclaimer: Do not use it at home if you don't know how to :)
You will lose money. Created only for educational purposes.


This repository contains several investment strategies based on technical indicators and tweeter post analysis.  

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

| **Variable**             | **Description**                | **Value** |
|--------------------------|--------------------------------|-----------|
| api_key                  | Binance TestNet api key        |           |
| api_secret               | Binance TestNet api secret     |           |
| API_VALID_KEY            | Binance API valid key          |           |
| API_VALID_SECRET         | Binance API secret key         |           |
| consumer_key             | Tweety API consumer key        |           |
| consumer_secret          | Tweety API consumer secret key |           |
| bearer_token             | Tweety API bearer token        |           |
| access_token             | Tweety API access token        |           |
| access_token_secret      | Tweety API secret access token |           |


