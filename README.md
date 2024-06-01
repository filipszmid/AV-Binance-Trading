### Disclaimer: Do not use it at home if you don't know how to :)
You will lose money. Created only for educational purposes.

# AV-Binance-Trading
Trading service for different investment strategies based on technical indicators and tweeter post analysis 
executed with binance API. Historic data is acquired from yahoo and binance streams.   
There are different type of granularity: stream, minute, daily.  
Some of the strategies need to be run in parallel with crypto streams to database.

Prerequisites: 
 * Python 3.9 
 * Poetry 1.7.1
 * Docker 20.10.22
 * Make 4.2.1

## Quickstart

* ```make install``` **Virtual environment**  is managed with poetry package manager.
After executing `poetry shell` on host machine you have access to 
cli with commands to run different strategies.


* ```make up-frontend``` **Frontend**  of this app is a streamlit dashboard with top trading currencies and other functionalities.
    * http://localhost:8501/home - dashboard

* ``` make up``` **Backend**  is FastAPI with endpoints for managing strategies on host for specified currencies. 
It supports interactive swagger menu.

    * http://localhost:8000/docs - endpoint documentation
    * http://localhost:8000/redoc - interactive endpoint documentation
  

* ```make test``` **Tests** can be run on live services on host or on mocked data acquired from .csv files depending on 
``TEST_ON_LIVE_SERVICES``variable to choice.

## Use cases:
* multiple users can use this app and log in/ sign in into dashboard
* user can enter dashboard and view top trading currencies
* user can start trading with different strategies
* user can view profit reports from different strategies

``make help:``
```
Please use make target where target is one of:
clean               clean up temp and trash files
format              format code
help                display help message
install             install dependencies
lint                run static code checkers
test                run pytest
up-front            run dashboard
up                  run API
```

Example scripts need to be run with **python** starting in **examples/** directory!

If `make test` won't run try to `make clean`, there are problems with cache.

Main bot is trading currencies defined in **position_checks** table, it can be reloaded 
within **reloads_position_checks()**
from file defined **tests/test_data_position_checks_basic.csv**.

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

## Poetry
Top used commands for poetry package manager:  
``` poetry shell ``` - enter shell  
```exit``` - exit the shell  
``` poetry add pytest --dev ``` - add requirement  
```poetry update```  - update version  
```poetry install```  - install poetry  
```poetry run binance_trading ``` - main command  
```poetry env use /home/lorbi/.cache/pypoetry/virtualenvs/av-crypto-trading-84RDaCA4-py3.9/bin/python```  - use new python  
``` poetry lock --no-update``` - update lock file after chaning pyproject.toml
```poetry self update``` - update the version of poetry  
my interpreter:
```/home/lorbi/.cache/pypoetry/virtualenvs/av-crypto-trading-q9kMY0JF-py3.9/bin/python```
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

## Common issues:

* error: command '/usr/bin/x86_64-linux-gnu-gcc' failed with exit code 1

```sudo apt-get install python3.9-dev build-essential```

Git large files:
```
sudo apt-get install git-lfs
git lfs install
git lfs track "*.csv"
git lfs pull
```