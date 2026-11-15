# AV-Binance-Trading
A comprehensive algorithmic trading system for crypto assets using Reinforcement Learning, XGBoost, and Time Series Forecasting (Prophet). Supports live trading on Binance/Bybit via WebSockets, and backtesting with historical data. Includes a FastAPI control plane, Streamlit dashboard, and Slack bot integrations.

<div align="center">

  <img src="data/docs/images/vid.gif" alt="Demo Video" />
  <p><em>Fig. 1 - Demo walkthrough of the dashboard and trading workflows.</em></p>

</div>

## Table of Contents

- [UI Views](#ui-views)
- [Quickstart](#quickstart)
  - [Development (Local Stack)](#development-local-stack)
  - [Production (Docker Compose)](#production-docker-compose)
- [Prerequisites:](#prerequisites)
- [User Management And Dashboard Auth](#user-management-and-dashboard-auth)
- [FastAPI endpoints](#fastapi-endpoints)
- [Streamlit UI image](#streamlit-ui-image)
- [Use cases](#use-cases)
- [Slack Bot Commands](#slack-bot-commands)
  - [Starting Bots (`trade`)](#starting-bots-`trade`)
  - [Managing Bots](#managing-bots)
- [Project Structure](#project-structure)
- [Environment](#environment)
  - [Tweet Novelty Live X Access](#tweet-novelty-live-x-access)
- [Key Technologies Used](#key-technologies-used)
- [Poetry](#poetry)
- [Local MLflow Experiment Tracking](#local-mlflow-experiment-tracking)
- [Make Commands](#make-commands)
- [CI/CD Pipeline And Tests](#cicd-pipeline-and-tests)
- [Ad-Hoc Operations](#ad-hoc-operations)
  - [Publishing Docker Images (GitHub Container Registry)](#publishing-docker-images-github-container-registry)
  - [1. Authenticate with GitHub](#1-authenticate-with-github)
  - [2. Build and Push (Local Machine)](#2-build-and-push-local-machine)
  - [3. Pull and Run (Remote Instance)](#3-pull-and-run-remote-instance)
  - [Deployment to NAS:](#deployment-to-nas)
  - [Deployment to GCP:](#deployment-to-gcp)
  - [RAM profiling](#ram-profiling)
  - [Run tensorboard on NAS:](#run-tensorboard-on-nas)
  - [Github release:](#github-release)
- [Clean Architecture View](#clean-architecture-view)
- [Module Contracts](#module-contracts)
- [Environment and Algorithm Contract](#environment-and-algorithm-contract)
- [Model and Data Flow](#model-and-data-flow)
- [Usage Sequence](#usage-sequence)
- [Cloud Services View](#cloud-services-view)
- [Why PostgreSQL?](#why-postgresql?)
- [Schema Design](#schema-design)
- [Table Definitions](#table-definitions)
- [Known issues:](#known-issues)
  - [OOM during training](#oom-during-training)
- [Disclaimer](#disclaimer)

## UI Views

Screenshots are ordered by the dashboard navigation flow. Each entry uses a
`*-page` indicator so the README matches the Streamlit page structure.

### login-page: Authentication

Secure dashboard login backed by FastAPI and PostgreSQL. In production the user
must authenticate before the trading pages are visible.

![login-page](data/docs/images/login.png)
<p align="center"><em>Fig. 2 - Login page for protected dashboard access.</em></p>

### 01-page: Summary

Top-level trading overview with live portfolio status, active agents, profit
summary, and the best performing strategy groups.

![summary-page](data/docs/images/trophy-page.png)
<p align="center"><em>Fig. 3 - Summary page with trading overview and best agents.</em></p>

### 02-page: Bot Control

Operational control surface for starting, stopping, and monitoring strategies
across supported algorithms and symbols.

![bot-control-page](data/docs/images/bot-control-page.png)
<p align="center"><em>Fig. 4 - Bot Control page for starting and stopping strategies.</em></p>

### 03-page: Performance

Detailed backtest and live-trading analysis with trade markers, PnL inspection,
and strategy comparison over selected periods.

![performance-page](data/docs/images/performance-page.png)
<p align="center"><em>Fig. 5 - Performance page for PnL and trade analysis.</em></p>

### 04-page: Calendar View

Calendar-style PnL view for checking how trading performance is distributed
across days and months.

![calendar-page](data/docs/images/calendar-page.png)
<p align="center"><em>Fig. 6 - Calendar View page for daily and monthly PnL.</em></p>

### 05-page: Trending Coins

Market-scanning page for tracking trending crypto assets and quickly selecting
symbols for deeper analysis or trading.

![trending-coins-page](data/docs/images/trending-coins-page.png)
<p align="center"><em>Fig. 7 - Trending Coins page for market scanning.</em></p>

### 06-page: Live Crypto

Live market view for monitoring current crypto prices, recent movement, and
market context while bots are running.

![live-view-page](data/docs/images/live-view-page.png)
<p align="center"><em>Fig. 8 - Live Crypto page for real-time market monitoring.</em></p>

### 07-page: Forecasting

Forecasting workspace for loading model runs and comparing predicted price paths
against recent market candles.

![forecasting-page](data/docs/images/forecasting-page.png)
<p align="center"><em>Fig. 9 - Forecasting page for model run forecasts.</em></p>

### 08-page: Tweet Manual Signal

Manual tweet novelty interface for scoring market-moving tweets, saving
predictions, checking outcomes, and invoking fast manual trade decisions.

![tweet-novelty-page](data/docs/images/tweet-novelty-page.png)
<p align="center"><em>Fig. 10 - Tweet Manual Signal page for fast tweet-driven decisions.</em></p>

### slack-interface: Fast Market Decisions

Slack is the lightweight decision interface for urgent market actions. It lets
the operator start bots, inspect positions, request charts, and close exposure
without opening the full dashboard.

![slack-interface](data/docs/images/slack-interface.png)
<p align="center"><em>Fig. 11 - Slack interface for fast market operations.</em></p>

### slack-training: Training And Run Feedback

Slack training messages keep experiment and live-run feedback close to the
operator, so model progress and trading status can be checked while decisions
are being made.

![slack-training](data/docs/images/slack-training.png)
<p align="center"><em>Fig. 12 - Slack training feedback for model and run updates.</em></p>

## Quickstart

### Development (Local Stack)
The easiest way to start developing is to spin up the local development stack:
```bash
make up-dev
```
This runs the Postgres DB, FastAPI backend, Streamlit dashboard, and Slack bot locally in one go. It automatically applies Alembic migrations if models change!

### Production (Docker Compose)
Build and start the full local stack using Docker Compose:
```bash
docker compose up --build -d
```
The compose stack starts FastAPI, Streamlit, Postgres, nginx, and the Slack Socket Mode bot. The Slack service reuses the backend image and calls FastAPI through `API_URL=http://api:8000`, so dashboard-started jobs can still be managed from Slack.

Reset containers and volumes before a clean rebuild (removes Postgres data volume):
```bash
docker compose down -v
docker compose up --build -d
```


### Environment Variables Configuration

Before starting the stack, you need to configure your API keys. Copy the provided `dev.env` (or create a `.env` file) and fill in the required values.

| Variable Group | Variables | Where to get it | Example Dummy Value |
| --- | --- | --- | --- |
| **Binance (TestNet)** | `api_key`, `api_secret` | [Binance Vision](https://testnet.binance.vision/) | `testnet_key_123` |
| **Binance (Prod)** | `API_VALID_KEY`, `API_VALID_SECRET` | [Binance API Management](https://www.binance.com/en/my/settings/api-management) | `prod_key_456` |
| **Bybit (TestNet)** | `BYBIT_TEST_API_KEY`, `BYBIT_TEST_API_SECRET` | [Bybit TestNet API](https://testnet.bybit.com/app/user/api-management) | `bybit_test_789` |
| **Bybit (Prod)** | `BYBIT_VALID_API_KEY`, `BYBIT_VALID_API_SECRET` | [Bybit API Management](https://www.bybit.com/app/user/api-management) | `bybit_prod_012` |
| **X / Twitter** | `consumer_key`, `bearer_token`, `X_BEARER_TOKEN`, etc. | [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard) | `xoxb-dummy-token` |
| **Slack Bot** | `SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN`, `SLACK_USER_ID` | [Slack API Apps](https://api.slack.com/apps) (Enable Socket Mode) | `xapp-dummy-token` |
| **System** | `ENV`, `TEST_ON_LIVE_SERVICES` | Local configuration preference | `dev`, `False` |

*Note: For a fully commented reference, check the `dev.env` file in the root of the project.*

## Prerequisites: 
 * Python 3.9.20
 * Poetry 2.2.1
 * Docker 20.10.22
 * Make 4.2.1

## User Management And Dashboard Auth

In `ENV=prod`, the Streamlit dashboard shows the login screen first. Login is handled by FastAPI with a bearer token, and dashboard pages stay hidden until the token is valid.

Add these values to `.env` before starting the Docker Compose stack:

```bash
ENV=prod
DASHBOARD_ADMIN_EMAIL=your@email.com
DASHBOARD_ADMIN_PASSWORD=change-this-password
DASHBOARD_AUTH_SECRET=change-this-long-random-secret
```

On API startup, `DASHBOARD_ADMIN_EMAIL` and `DASHBOARD_ADMIN_PASSWORD` create the first dashboard admin user if that email does not already exist. Do not commit real credentials.

Optional service token for non-browser clients such as Slack:

```bash
API_SERVICE_TOKEN=change-this-service-token
```

Clients can then call protected API endpoints with:

```bash
Authorization: Bearer $API_SERVICE_TOKEN
```

Registration via the UI is disabled for security. To add a new user through the FastAPI service in production, start the API first and call the protected endpoint with the configured service token:

```bash
# Replace 'Your Name', 'your@email.com', and 'your_password' with actual values
API_SERVICE_TOKEN=change-this-service-token poetry run python -c "from interface.ui.database import add_userdata, make_hashes; add_userdata('Your Name', 'your@email.com', make_hashes('your_password'))"
```

## FastAPI endpoints

Authentication uses bearer tokens. In `ENV=prod`, every protected endpoint requires either a dashboard token from `POST /auth/login` or the configured `API_SERVICE_TOKEN`. In non-prod environments, the API allows protected routes for local development.

| Method | Path | Auth | Definition |
| --- | --- | --- | --- |
| `GET` | `/` | Public | Health/welcome response. |
| `POST` | `/auth/login` | Public | Body `{email, password}`. Returns `{access_token, token_type}` for dashboard sessions. |
| `GET` | `/auth/me` | Bearer | Returns the authenticated dashboard user. |
| `POST` | `/ui/users/table` | Bearer | Ensures database tables exist. Kept for the legacy UI helper. |
| `POST` | `/ui/users/` | Bearer | Body `{username, email, hashed_password}`. Creates a dashboard user from an already-hashed password. |
| `POST` | `/ui/users/login` | Bearer | Body `{email, hashed_password}`. Protected legacy credential check; prefer `/auth/login`. |
| `GET` | `/ui/users/` | Bearer | Query `skip`, `limit`. Lists dashboard users. |
| `POST` | `/users/` | Bearer | Body `{email, password}`. Creates a user and hashes the password server-side. |
| `GET` | `/users/` | Bearer | Query `skip`, `limit`. Lists users. |
| `GET` | `/users/{user_id}` | Bearer | Returns one user by numeric id. |
| `GET` | `/dashboard/checkpoints/{algo}` | Bearer | Lists available checkpoints or strategy names for an algorithm. |
| `GET` | `/dashboard/summary/metrics` | Bearer | Returns total profit, trade count, win rate, and active-agent count. |
| `GET` | `/dashboard/summary/top-agents` | Bearer | Query `limit`. Returns top profitable agent groups. |
| `GET` | `/dashboard/calendar/earnings` | Bearer | Query `year`, `month`. Returns daily earnings for the calendar view. |
| `GET` | `/dashboard/performance/jobs` | Bearer | Query `start_date`, `end_date`, `coin`. Returns jobs with trades in that period. |
| `GET` | `/dashboard/performance/bets` | Bearer | Query `start_date`, `end_date`, `coin`, optional `job_id`. Returns trade markers. |
| `GET` | `/dashboard/performance/prices` | Bearer | Query `start_date`, `end_date`, `coin`. Returns stored price data for charting. |
| `GET` | `/dashboard/forecasting/runs` | Bearer | Lists available Prophet forecast model runs and metadata. |
| `GET` | `/dashboard/forecasting/forecast` | Bearer | Query `symbol`, `horizon`, `run_id`. Returns recent candles and forecast rows for the chart. |
| `GET` | `/dashboard/tweets/analysis` | Bearer | Query `about`, `number`, `lookback`. Returns top words, tags/mentions, and top liked tweets. |
| `POST` | `/bots/run` | Bearer | Query `algo`, `checkpoint`, `coin`, `params`. Starts a bot process and stores a bot job. |
| `POST` | `/bots/stop/{job_id}` | Bearer | Stops one running bot job or marks it stopped if only the DB record remains. |
| `POST` | `/bots/stop-all` | Bearer | Stops every tracked running bot job and marks active DB jobs stopped. |
| `POST` | `/bots/chart/{job_id}` | Bearer | Query optional `episode`. Renders or returns the chart path for a bot. |
| `GET` | `/bots/active` | Bearer | Lists running bot jobs. |
| `POST` | `/shutdown` | Bearer | Requests FastAPI shutdown in a background task. |
| `GET` | `/bots/positions` | Bearer | Returns the live trading positions for all active bots. |
| `GET` | `/dashboard/tweets/manual/runs` | Bearer | Lists available manual tweet novelty run names. |
| `POST` | `/dashboard/tweets/manual/predict` | Bearer | Predicts novelty for a text based on a specific model run. |
| `POST` | `/dashboard/tweets/manual/save` | Bearer | Saves a manual tweet along with its novelty score. |
| `GET` | `/dashboard/tweets/manual/predictions` | Bearer | Gets the history of manual predictions. |
| `POST` | `/dashboard/tweets/manual/mark` | Bearer | Marks a manual prediction as True/False (correctness check). |
| `POST` | `/dashboard/tweets/manual/trade` | Bearer | Signals the system to trade based on a manual tweet prediction. |
| `GET` | `/dashboard/tweets/manual/source-stats` | Bearer | Gets stats for manual vs automated tweets over time. |

## Streamlit UI image

`Dockerfile.ui` is intentionally UI-only. It copies only `interface/ui`, `interface/__init__.py`, `master_config.py`, `README.md`, and documentation images; it does not copy `av_crypto_trading`, model artifacts, or database code. The image installs the slim Poetry `ui` dependency group, so dashboard pages must call FastAPI for backend work such as database reads, bot management, forecasting, and tweet analysis.

## Use cases:
* Authorized users can log in to the dashboard (Self-registration is disabled).
* user can enter dashboard and view top trading currencies
* user can start trading with different strategies
* user can view profit reports from different strategies

Example scripts need to be run with **python** starting in **examples/** directory!

If `make test` won't run try to `make clean`, there are problems with cache.

Main bot is trading currencies defined in the **position_checks** table.

## Slack Bot Commands

The Slack bot allows you to manage trading bots and view their status directly from Slack. The `trade` command supports different algorithms (e.g., `rl`, `stat`, `xg`). When you start a bot, it will return a unique `job_id` which you can use for further commands.

### Starting Bots (`trade`)

**Usage:** `trade <algo> <run_name> [ckpt_name] <episodes> <currency> <bet_size>`

*   **Reinforcement Learning (RL):**
    You only need to specify the run folder name and the checkpoint filename.
    ```
    trade rl {run_name} {checkpoint_filename} 10 BTCUSDT 500
    ```
*   **Statistical Strategy:**
    ```
    trade stat AlgoChopMA600VolumeStrategyV6 10 BTCUSDT 500
    ```
*   **XGBoost:**
    The `xgboost_classifier.pkl` suffix is automatically appended.
    ```
    trade xg hyperopt_run_20250417-153202_lod 10 BTCUSDT 500
    ```

### Managing Bots

Use the `job_id` returned by the `trade` command (or the dashboard) to manage specific bots.

*   **View Positions:** View the current market positions of all active bots, or filter by a specific job ID.
    ```
    positions
    positions e4a1b2c3
    ```
*   **Generate Chart:** Render and upload the latest evaluation chart for a specific bot.
    ```
    chart e4a1b2c3
    ```
*   **Stop a Bot:** Close open positions and stop the bot's execution process.
    ```
    close e4a1b2c3
    ```

## Project Structure

This project is a modular crypto trading system combining streaming, trading strategies, ML models, backtesting, and interactive interfaces.

```text
av_crypto_trading/                         # Domain package: trading logic, data, models
├── connectors/                            # External systems and persistence adapters
│   ├── binance/                           # Binance historical/live data and execution helpers
│   ├── bybit/                             # Bybit data/executor used by live/manual trading
│   ├── postgres_db/                       # Current SQLAlchemy models, queries, Alembic migrations
│   │   ├── models.py                      # Authoritative PostgreSQL schema definition
│   │   ├── queries.py                     # DB write/read helpers used by API and environments
│   │   ├── migrator.py                    # Runs Alembic migrations on API startup
│   │   └── migrations/                    # Versioned DB schema migrations
│   ├── sentiment/                         # Fear/greed, LunarCrush, Nansen-style data adapters
│   ├── twitter/                           # Legacy tweet collection and tweet text utilities
│   └── x/                                 # X recent-search connector for live tweet novelty
├── core/                                  # Shared constants, model identity, stream orchestration
├── environments/                          # Trading environments for training, backtest, live run
│   ├── live/                              # Live exchange environment with order execution
│   ├── statistical/                       # Statistical strategy backtest/live environment
│   ├── memory_mapped/                     # Memory-mapped training environment
│   ├── big_data/, big_data_np/            # Large dataset environment variants
│   └── features.py                        # Common market feature engineering
├── preprocessing/                         # Dataset preparation scripts for large CSV/feature sets
├── strategies/                            # Strategy families and train/evaluation entrypoints
│   ├── reinforcement_learning/            # RL config, policy model wrapper, serial evaluator, train
│   ├── statistical/                       # Rule-based Strategy base and statistical strategies
│   ├── xgboost_classifier/                # Supervised XGBoost features, training, strategy wrapper
│   ├── dqn_classifier/                    # DQN classifier strategy and feature importance tools
│   ├── arima/, fb_prophet/                # Forecasting strategies and training flows
│   ├── tweet_novelty/                     # Tweet novelty NLP model, manual scoring, live strategy
│   └── arbitrage_poly/                    # Polygon arbitrage research, model, inference, backtests
├── graphics/                              # Plotting service for charts and evaluation artifacts
├── pandas_ta/                             # Local technical indicator implementations
└── schemas.py                             # Pydantic schemas shared by API/UI/integrations

interface/                                # Human and service-facing interfaces
├── api/                                   # FastAPI control plane split into app, routers, dependencies, services
├── ui/                                    # Streamlit dashboard and pages
│   ├── app.py                             # Dashboard entrypoint
│   └── pages/                             # Summary, bot control, performance, calendar, tweets, etc.
├── slack/                                 # Slack Socket Mode bot for fast market operations
└── cli/                                   # Click CLIs: prod bot control, train/tune, evaluation

evaluation/                               # Backtest/live evaluation jobs and tracking helpers
├── constants.py                           # Shared evaluation defaults
├── model_registry.py                      # Model artifact path resolution and strategy discovery
├── backtesting/                           # Backtest evaluators and job scripts
├── live_testing/                          # Live/simulated-live evaluators and job scripts
└── tracking/                              # MLflow tracking and MLflow config fingerprints

data/                                     # Local datasets, runs, docs images, eval outputs
├── docs/images/                           # README/About page screenshots and demo media
├── runs/                                  # Model artifacts mounted into prod API/Slack containers
└── evals/                                 # Backtest/live charts and reports

Dockerfile                                # Backend/API/Slack image
Dockerfile.ui                             # Slim Streamlit UI image
docker-compose.yml                        # Local/dev compose stack
docker-compose.prod.yml                   # GHCR image-based production stack
Makefile                                  # Common dev, training, Docker, deployment commands
master_config.py                          # Global paths/env mode/run naming
pyproject.toml                            # Poetry dependencies and groups
```

## Environment
See Quickstart for environment variables setup.

### Tweet Novelty Live X Access

Backtesting the tweet novelty strategy does not need any X API access. It reads
the trained run artifact `tweet_novelty_signals.csv`, aligns the latest signal
to each historical market timestamp, and trades from that saved timeline.
For tweet novelty runs, the backtest also reads the run metadata and uses the
same market file/test range that was used when the model was trained. To
backtest another symbol, train the run with that symbol's market CSV first.

Live testing uses the Agent Control Panel `Coin / Pair` value as the exchange
pair for the Binance stream and Bybit executor. Prefer explicit pairs such as
`BTCUSDT` or `ETHUSDT`; aliases like `BTC`, `Bitcoin`, and `ETH` are normalized
to their `USDT` pair.

Live tweet novelty testing can also fetch fresh posts from X. Add only this
value to `.env`:

```bash
X_BEARER_TOKEN=your-x-api-bearer-token
```

Everything else for X live fetching is defined as constants in
`av_crypto_trading/connectors/x/data.py`: search URL, per-symbol search terms,
lookback window, request timeout, page count, and page size. The X API path is
implemented but has not been tested yet in this repo environment because no new
X API access is available here.

## Key Technologies Used

This project brings together modern ML tooling, trading infrastructure, and deployment frameworks:

*   **🧠 Machine Learning:** Stable-Baselines3 (PPO, A2C, DQN), DI-engine, Tianshou, XGBoost, Transformers, Prophet, SHAP.
*   **📊 Data Handling & Streaming:** pandas, NumPy, Vaex, Finta, pandas-ta, SmartMoneyConcepts, Unicorn Binance WebSocket API.
*   **📈 Visualization & Dashboards:** Streamlit, Plotly, Pyecharts, TensorBoard.
*   **🧰 Project Infrastructure:** FastAPI, Slack Bolt / SDK, SQLAlchemy, **Alembic** (migrations), PostgreSQL, Click, MLflow, Hydra.
*   **🧪 DevOps & Testing:** Poetry, Docker, GitHub Actions (CI/CD), Pytest, Prospector, Black, isort.

![TB](data/docs/images/tensorboard-example.png)
<p align="center"><em>Fig. 13 - TensorBoard view for training diagnostics.</em></p>

## Poetry
Top used commands for poetry package manager:  
``` poetry shell ``` - enter shell  
```exit``` - exit the shell  
``` poetry add pytest --dev ``` - add requirement  
```poetry update```  - update version  
```poetry install```  - install poetry  
```poetry run binance_trading ``` - main command  
```poetry env use /path/to/your/virtualenv/bin/python```  - use new python  
``` poetry lock --no-update``` - update lock file after chaning pyproject.toml
```poetry self update``` - update the version of poetry  
my interpreter:
```/path/to/your/virtualenv/bin/python```

## Local MLflow Experiment Tracking

RL training still writes TensorBoard logs exactly as before. MLflow is an additional local index for answering experiment questions across runs and checkpoints.

Start the local MLflow UI:

```bash
make mlflow_ui
```

`make mlflow_ui` uses the same local tracking directory as training: `Config.TRAIN_LOG_DIR/mlflow`. In dev this is `data/runs/mlflow`. If you want to run it directly in dev:

```bash
poetry run mlflow ui --backend-store-uri "file://$(pwd)/data/runs/mlflow" --host 127.0.0.1 --port 5000
```

Open:

```text
http://127.0.0.1:5000
```

![mlflow-ui](data/docs/images/mlflow-ui.png)
<p align="center"><em>Fig. 14 - MLflow UI for comparing training runs and checkpoints.</em></p>

What you should see:

* Experiment: `reinforcement_learning`
* One MLflow run for each RL training run.
* Params: important values from `config.py` and env config, for example learning rate, batch size, replay buffer size, epsilon decay, train/test range, dataset file, features version, TP/SL.
* Metrics: `serial_eval.*`, `checkpoint_eval.*`, and numeric best checkpoint metrics like `best.avg_profit`.
* Tags: dataset aggregation, train/test ranges, comparable signatures, review status, and best checkpoint path.
* Artifacts: `config/tracked_params.json`, `config/comparable_signature.json`, `evaluation/checkpoint_evaluations.jsonl`, and `evaluation/best_checkpoint.json`.

How to answer the common questions:

* Which checkpoint was best for this run? Open the run and check tags `best.checkpoint_iter`, `best.checkpoint_path`, and metric `best.avg_profit`. The same information is also saved in `data/runs/reinforcement_learning/<run_name>/evaluation/best_checkpoint.json`.
* Can two runs be compared? Filter/group by the same `tags.compare.comparable_signature`. Also check `tags.data.aggregation_minutes`, `tags.data.train_range`, and `tags.data.test_range`. A `1` minute run should not be compared against a `60` minute run.
* Which hyperparameter probably helped? First filter to one `tags.compare.comparable_signature`, then compare columns such as `params.policy.learn.learning_rate`, `params.policy.learn.batch_size`, `params.policy.collect.n_sample`, `params.policy.other.eps.decay`, and sort by `metrics.best.avg_profit`.
* What changed between two runs? Select both runs in MLflow and use Compare. The params table will show changed values from both config files.
* Mark a run as good for later:

```bash
poetry run evaluation mlflow mark-run --run-name "<run_name>" --label good --note "short reason"
```

Then filter in the MLflow UI by:

```text
tags.review.status = "good"
```

Quick terminal lookback for one run:

```bash
poetry run evaluation mlflow show-run --run-name "<run_name>"
```

## Make Commands

```text
Please use make target where target is one of:
board_nas           SUBDIR=r/ro/xg/sl Run tensorboard pointing to a specific subdirectory
board               run training board monitoring
build               Build the AI Trader app docker image
build-ghcr          Build and tag the main app image for GHCR
build-ghcr-ui       Build and tag the slim UI image for GHCR
cl                  clean RL outputs
clean               clean up temp and trash files
copy_gcp_evals      Copy eval dirs from GCP to local filesystem
deploy_model        Copy model to the remote instance
down-dev            stop dev scripts and dev db
eval_backtest       run evaluation job
eval_livetest       run live evaluation
format              format code
get_log             Download ai_trader.log from GCP instance
help                display this help message
install             install all dependencies
lint                run static code checkers
logs                Show container logs
mlflow_ui           run local MLflow UI for training experiments
prod-clean-docker   Remove unused Docker containers/images/cache without deleting volumes
prod-down           Stop prod stack
prod-logs           Follow prod logs
prod-ps             Show prod containers
prod-pull           Pull prod images from GHCR
prod-restart        Pull latest image and restart prod stack
prod-up             Start prod stack
publish             ⭐ Build BOTH images and push them to GHCR in one shot
pull-all            ⭐ Pull BOTH images from GHCR in one shot
pull-ghcr           Pull the main app image from GHCR
pull-ghcr-ui        Pull the slim UI image from GHCR
push-ghcr           Push the main app image to GHCR
push-ghcr-ui        Push the slim UI image to GHCR
run                 Run the AI Trader container (detached, with .env)
save                Save Docker image to NAS path
setup_instance      Prepare GCP instance with pyenv, python, poetry, swap, and ssh key
shell               Start an interactive shell in the running container
simulate            run trading environment simulation
slack               starts slacks ai trader
ssh_gcp_nginx_80    SSH tunnel to expose service
ssh_gcp             Open ssh tunel to NAS
ssh_nas             Open ssh tunel to NAS
stop                Stop the running container
test                run pytest
train_supervised    (TAG= ) runs supervised training
train               (TAG= ) train RL agent
up-api              run API
up-dev              run dev db, API, dashboard, and Slack bot
up-front            run dashboard
```

## CI/CD Pipeline And Tests

The repository keeps CI and deployment in GitHub Actions so the release process
is versioned with the code. Changes to tests, Docker images, deployment steps,
and application code are reviewed together, which makes production updates
repeatable and visible from the PR.

```mermaid
flowchart LR
    DraftPR["Draft PR"] --> DraftSkip["CI workflow starts\njobs are skipped"]
    ReadyPR["Ready PR"] --> CI
    PushMaster["Push to master"] --> CI
    ManualRun["Manual workflow"] --> CI

    subgraph CI["CI-Integrate (.github/workflows/CI.yml)"]
        Tests["test\nmake test"]
        Lint["lint\nmake lint"]
        Format["format\nmake format"]
        Docker["docker\nbuild + compose smoke checks"]
        Tests --> Docker
        Lint --> Docker
        Format --> Docker
    end

    CI --> CICD["CI-CD manual workflow"]
    CICD --> Publish["publish\nmake publish to GHCR"]
    Publish --> Deploy["GCP deploy over SSH\npull repo + restart prod compose"]
    Deploy --> Verify["docker compose ps\nruntime verification"]
```

| Job | What it runs | Why it exists |
| --- | --- | --- |
| `test` | `make test` | Runs the pytest suite before any image is trusted. |
| `lint` | `make lint` | Catches static quality issues early in the PR. |
| `format` | `make format` | Keeps formatting consistent with the repository command. |
| `docker` | Docker build, compose startup, API/UI/nginx smoke checks | Verifies the deployed services can build and start together. |
| `CD` | `make publish`, GCP auth, SSH deploy, `prod-down`, `prod-clean-docker`, `prod-pull`, `prod-up` | Publishes immutable GHCR images and restarts the production compose stack in a controlled path. |

Draft PRs do not spend CI minutes on full checks. The same workflow runs once
the PR is marked ready for review, on pushes to `master`, and from manual
dispatch when a release or deployment needs to be forced.

The tests live in `tests/`. Unit and integration tests cover connectors, core
logic, predictions, Slack commands, Twitter/X ingestion, tracking helpers, and
model identity checks. The `tests/e2e/` tests use compact synthetic data to
validate full data contracts across preprocessing, environment setup, hourly
aggregation, live normalization, train/test range splitting, observation
dimensions, and MLflow recap generation. These e2e tests are important because
they catch shape, timestamp, range, and artifact regressions before a model run
or live deployment depends on them.

## Ad-Hoc Operations

### Publishing Docker Images (GitHub Container Registry)

You can build your Docker images locally and push them to your GitHub Container Registry (`ghcr.io`). This allows you to pull the pre-built image directly onto your GCP instance, skipping the heavy build process on the VM.

### 1. Authenticate with GitHub
On both your local machine and your remote instance, you must log in to GHCR using a GitHub Personal Access Token (PAT) with `write:packages` and `read:packages` permissions.

```bash
echo "YOUR_GITHUB_PAT" | docker login ghcr.io -u YOUR_GITHUB_USERNAME --password-stdin
```

### 2. Build and Push (Local Machine)
Build the image and push it to GHCR. Set `GITHUB_USERNAME` to your GitHub username:

```bash
make build-ghcr GITHUB_USERNAME={github_user_name}
make push-ghcr GITHUB_USERNAME={github_user_name}
```

### 3. Pull and Run (Remote Instance)
On your remote instance (e.g., GCP), pull the image:

```bash
make pull-ghcr GITHUB_USERNAME={github_user_name}
```

**Note:** If you want `docker-compose.yml` to use this image, you can tag it to match the compose file:
```bash
docker tag ghcr.io/{github_user_name}/ai-trader:latest av_trader_image:latest
docker compose up -d
```

### Deployment to NAS:
```
ssh {nas_user_name}@{nas_ip_address}
cd {nas_project_directory}
git pull
make stop
make build
make run
```
### Deployment to GCP:
```
sudo apt install google-cloud-sdk
gcloud config set project {gcp_project_id}
gcloud compute instances list
gcloud compute ssh {gcp_user_name}@{gcp_instance_name} --zone={gcp_zone}
# install git, generate ssh key, add to deploy keys
git clone 
sudo apt install build-essential -y
# install docker
make build
# clone the model
make deploy_model CHECKPOINT="reinforcement_learning/{run_name}/ckpt/{checkpoint_filename}"
```

### RAM profiling
```
poetry add filprofiler
poetry run fil-profile run -m av_crypto_trading.reinforcement_learning.train
scp -r {remote_user_name}@{remote_ip_address}:{remote_project_directory}/fil-result ./fil-result-report
```

```
pip install -U scalene
python3 -m pip install memray
```


```
poetry run python -m scalene \
  --memory \
  --memory-leak-detector \
  --profile-all \
  --stacks \
  --html av_crypto_trading/reinforcement_learning/train.py
```
```
http://localhost:11235/
```

```
scp {remote_user_name}@{remote_ip_address}:{remote_project_directory}/memray_report.bin .        
poetry run python3 -m memray run --aggregate -o memray_report.bin av_crypto_trading/reinforcement_learning/train.py       
poetry run python3 -m memray flamegraph memray_report-msi.bin
ssh -X {remote_user_name}@{remote_ip_address}
nautilus .
sshfs {remote_user_name}@{remote_ip_address}:{remote_home_directory} {local_mount_directory} -o allow_other
```


### Run tensorboard on NAS:
```
nohup tensorboard --logdir=/runs/reinforcement_learning --host=0.0.0.0 --port=6006 &
```

### Github release:
```
git tag -a v1.0.3 -m "Fixes in TradingEnvInMemory." 
git push origin v1.0.3
gh release create v1.0.3 \
  --title "AI-Trader-v1.0.3" \       
  --notes "Fixes in TradingEnvInMemory." \
  --latest
```


# Application Architecture

This system is organized around a narrow control plane and a separate trading execution path. The dashboard, Slack bot, and CLI request work; FastAPI validates and starts jobs; evaluators bind a trained algorithm to an environment; environments own market state, streaming, order execution, charts, and persistence.

Live dashboard bots are started as detached OS subprocesses through the existing
`av` CLI (`python -m interface.cli.av agent/statistical ...`) rather than as
`multiprocessing.Process` children of FastAPI. This keeps long-running trading
loops out of uvicorn's process ownership, avoids Python multiprocessing shutdown
joins blocking the API, and still preserves the same dashboard/Slack `job_id`
control interface. FastAPI stores the worker PID/process group in PostgreSQL so
`POST /bots/stop/{job_id}` can terminate the correct live worker later, even
after the in-memory process map is gone.

Package boundaries are intentionally narrow:

- **`interface/api` is HTTP API code only**: app construction, routers,
  dependencies, and API-facing services.
- **`interface/cli` is CLI code only**: `av` is production-safe live bot
  orchestration, `av-train` owns training/tuning commands, and `evaluation`
  owns research evaluation/backtest commands.
- **`evaluation` owns evaluator orchestration**: live/backtest runner setup,
  model artifact resolution, and MLflow tracking boundaries.
- **`av_crypto_trading/strategies` owns strategy/domain logic**: strategy
  contracts, model wrappers, signal logic, and tweet novelty preprocessing/manual
  scoring helpers.

## Clean Architecture View

```mermaid
flowchart TB
    subgraph Interface["Interface Layer"]
        Streamlit["Streamlit dashboard\ninterface/ui"]
        Slack["Slack bot\ninterface/slack"]
        CLI["Click CLI\ninterface/cli"]
    end

    subgraph ApiPkg["FastAPI Package\ninterface/api"]
        APIApp["app.py\ncreate FastAPI app"]
        APIRouters["routers/\nHTTP endpoints only"]
        APIDeps["dependencies.py\nauth, DB sessions, lifespan"]
        APIServices["services/\nAPI orchestration helpers"]
        APIState["state.py\nprocess map"]
    end

    subgraph CliPkg["CLI Package\ninterface/cli"]
        AvCLI["av.py\nprod live bot commands"]
        TrainCLI["train.py\ntraining + tuning commands"]
        EvalCLI["evaluation.py\nresearch eval/backtest commands"]
    end

    subgraph EvalPkg["Evaluation Package\nevaluation"]
        ModelRegistry["model_registry.py\nartifact + strategy discovery"]
        LiveOrch["live_testing/orchestration.py\nlive runner setup"]
        BacktestOrch["backtesting/orchestration.py\nbacktest runner setup"]
        LiveEval["live_testing/*\nlive evaluators"]
        BacktestEval["backtesting/*\nbacktest evaluators"]
        MLflowTracking["tracking/\nMLflow-only tracking"]
    end

    subgraph WorkerRuntime["Worker Runtime"]
        BotProcess["Detached bot subprocess\nsubprocess.Popen"]
    end

    subgraph EnvDomain["Environment Domain\nav_crypto_trading/environments"]
        EnvLive["TradingEnvLive\nlive market environment"]
        EnvMemory["TradingEnvInMemory / Numpy / BigData\ntraining and backtest environments"]
        Actions["Actions\nBUY / SELL / HOLD"]
    end

    subgraph StrategyDomain["Strategy Domain\nav_crypto_trading/strategies"]
        Strategy["Strategy contract\nforward(df) -> Actions"]
        RLPolicy["RL policy contract\nforward(obs) -> action"]
        TweetNovelty["tweet_novelty/\nNLP model + manual scoring"]
        Statistical["statistical/\nrule-based signals"]
        ModelStrategies["xgboost / arima / fb_prophet / dqn_classifier"]
    end

    subgraph Infra["Infrastructure and Data Layer"]
        Runs["Model artifacts\ndata/runs/<algo>/<run>"]
        MarketData["Market data\nCSV, cached features, live streams"]
        Connectors["Connectors\nBinance, Bybit, X, Twitter, sentiment"]
        Postgres["PostgreSQL\nusers, jobs, bets,\nmanual tweets, live observations"]
        Charts["Evaluation artifacts\ndata/evals"]
    end

    Streamlit -->|"HTTP JSON + bearer token"| APIApp
    Slack -->|"HTTP JSON or command adapter"| APIApp
    CLI --> AvCLI
    CLI --> TrainCLI
    CLI --> EvalCLI
    APIApp --> APIRouters
    APIRouters --> APIDeps
    APIRouters --> APIServices
    APIServices --> APIState
    APIServices -->|"subprocess.Popen + job_id"| BotProcess
    BotProcess -->|"python -m interface.cli.av"| AvCLI
    AvCLI --> ModelRegistry
    AvCLI --> LiveOrch
    EvalCLI --> ModelRegistry
    EvalCLI --> LiveOrch
    EvalCLI --> BacktestOrch
    TrainCLI --> StrategyDomain
    LiveOrch --> LiveEval
    BacktestOrch --> BacktestEval
    LiveEval --> EnvLive
    BacktestEval --> EnvMemory
    Runs -->|"checkpoint/model path"| ModelRegistry
    MarketData --> EnvMemory
    EnvLive -->|"stream/order APIs"| Connectors
    EnvLive -->|"status, bets, chart path"| Postgres
    APIServices -->|"active jobs and dashboard data"| Postgres
    EnvLive --> Charts
    EnvMemory --> Charts
    EnvLive -->|"observation"| Strategy
    EnvLive -->|"observation tensor"| RLPolicy
    StrategyDomain --> Strategy
    StrategyDomain --> RLPolicy
    TweetNovelty --> Strategy
    Statistical --> Strategy
    ModelStrategies --> Strategy
    Strategy --> Actions
    RLPolicy --> Actions
    Actions --> EnvLive
    MLflowTracking --> Runs
```

## Module Contracts

| Boundary | Producer | Consumer | Contract |
| --- | --- | --- | --- |
| Dashboard to API | `interface/ui` | `interface/api/app.py` | HTTP JSON endpoints. The UI does not read model files directly; it asks FastAPI for checkpoints, jobs, charts, and dashboard data. |
| API to bot process | `POST /bots/run` | `subprocess.Popen` running `python -m interface.cli.av` | Creates a `job_id`, resolves the selected checkpoint, stores a `bot_jobs` record, starts a detached OS worker, and persists `bot_pid`, `bot_process_group_id`, and worker log path. |
| Bot process to live evaluator | `av agent --livetest` / `av statistical --livetest` | `evaluation/live_testing/orchestration.py` | Passes `model_type`, `model_path`, `trade_pair`, `bet_size`, `max_episodes`, execution mode, dashboard tag, and `job_id`; updates DB status to `finished` or `error` on exit. |
| CLI to training/tuning | `av-train train-agent`, `av-train train-arima`, `av-train tune-*` | `av_crypto_trading/strategies/*` | Keeps research-only dependencies and commands out of the production bot worker import path. |
| CLI to backtest evaluator | `evaluation agent --backtest` / `evaluation statistical --backtest` | `evaluation/backtesting/orchestration.py` | Resolves the selected model or strategy, builds the matching backtest environment, and calls the existing model/statistical evaluator. |
| Evaluator to environment | `evaluation/live_testing` | `TradingEnvLive` | Calls `reset()`, `start_stream()`, `render()`, and reads `cur_info`, `episode_recap`, `positions_chart_path`, and `job_id`. |
| Environment to algorithm | `TradingEnvLive` | RL policy or `Strategy` | Provides an observation or prepared market dataframe and expects an action compatible with the environment action space. |
| Strategy interface | `Strategy` subclasses | Evaluators and environments | `live_forward(human_df)` prepares input and delegates to `forward(df) -> Actions`. Model strategies may set `FEATURES_FN` or `USE_ENV_OBSERVATION`. |
| Live data connector | Exchange adapters | `TradingEnvLive` | `get_initial_data(lookback_minutes) -> DataFrame` and `process_message(message) -> row dict`. |
| Model artifact contract | `data/runs` | FastAPI and evaluators | Algorithm-specific folders contain loadable checkpoints/models. In Docker prod, these are mounted into the API container at `/app/data/runs`. |
| Persistence contract | Environments, API, and CLI worker | PostgreSQL | Users, bot lifecycle, worker PID/process group, bets, manual tweet predictions, and live observations are stored through SQLAlchemy models and query helpers. |

## API Package Layout

`interface/api/app.py` only creates the FastAPI application and attaches routers.
Route handlers live in `interface/api/routers`, shared request dependencies and
startup logic live in `interface/api/dependencies.py`, and domain-specific API
helpers live in `interface/api/services`. Bot worker process management,
position refreshes, chart signalling, forecasting helpers, checkpoint discovery,
and tweet-novelty/manual-trade helpers are split by responsibility so the API
entrypoint stays small and Docker can still load the app as
`interface.api.app:app`.

## Evaluation Package Layout

`interface/cli/evaluation.py` owns Click options and dispatch only. Live runner
setup, dashboard job status updates, Slack crash reporting, and shutdown signal
handling live in `evaluation/live_testing/orchestration.py`. Backtest runner
setup lives in `evaluation/backtesting/orchestration.py`. Shared model artifact
resolution and statistical strategy discovery live in `evaluation/model_registry.py`.
`evaluation/tracking` is kept for MLflow-only tracking concerns.

## Environment and Algorithm Contract

```mermaid
classDiagram
    class Evaluator {
        +evaluate_model_live(env, max_episodes, tag)
        +evaluate_strategy_live(env, max_episodes, tag)
    }

    class TradingEnvLive {
        +reset()
        +start_stream()
        +render()
        +cur_info
        +episode_recap
        +positions_chart_path
    }

    class TradingEnvInMemory {
        +reset()
        +step(action)
        +render()
    }

    class AbstractLiveDataConnector {
        +get_initial_data(lookback_minutes)
        +process_message(message)
    }

    class Strategy {
        +bind_env(env)
        +prepare_input(human_df, obs_df)
        +live_forward(human_df)
        +forward(df)
    }

    class XGBoostClassifierStrategy
    class ARIMAStrategy
    class FBProphetStrategy
    class TweetNoveltyStrategy
    class StatisticalStrategy

    class RLPolicy {
        +forward(obs)
    }

    class Actions {
        BUY
        SELL
        HOLD
    }

    TradingEnvLive --|> TradingEnvInMemory
    Evaluator --> TradingEnvLive : runs episodes
    TradingEnvLive --> AbstractLiveDataConnector : market stream
    TradingEnvLive --> Strategy : human_df to action
    TradingEnvLive --> RLPolicy : obs to action
    Strategy <|-- XGBoostClassifierStrategy
    Strategy <|-- ARIMAStrategy
    Strategy <|-- FBProphetStrategy
    Strategy <|-- TweetNoveltyStrategy
    Strategy <|-- StatisticalStrategy
    Strategy --> Actions
    RLPolicy --> Actions
    Actions --> TradingEnvLive : env step/order decision
```

The environment is the integration boundary. Algorithms should not manage database writes, Slack uploads, chart file paths, or exchange execution directly. Their job is to convert a prepared observation into an action. The environment and evaluator own runtime effects: streaming, order execution, episode accounting, chart rendering, and persistence.

## Model and Data Flow

```mermaid
flowchart LR
    HostRuns["Host folder\ndata/runs"]
    ApiRuns["API container\n/app/data/runs"]
    Discover["FastAPI\n_discover_checkpoints(algo)"]
    ControlPanel["Bot Control\ncheckpoint selectbox"]
    RunBot["POST /bots/run"]
    Resolve["Resolve checkpoint path"]
    Loader["Evaluator loads model"]
    Env["Trading environment"]

    HostRuns -->|"bind mount in prod\nrepo bind mount in local"| ApiRuns
    ApiRuns --> Discover
    Discover -->|"relative checkpoint list"| ControlPanel
    ControlPanel --> RunBot
    RunBot --> Resolve
    Resolve --> Loader
    Loader --> Env
```

Expected artifact layout:

| Algorithm | Folder | Artifact pattern |
| --- | --- | --- |
| RL | `data/runs/reinforcement_learning/<run>/ckpt/` | `*.pth.tar` |
| XGBoost | `data/runs/xgboost/<run>/` | `xgboost_classifier.pkl` |
| Supervised learning | `data/runs/supervised_learning/<run>/ckpt/` | `*.pth.tar` |
| ARIMA | `data/runs/arima/<run>/` | `arima_model.pkl` |
| Prophet | `data/runs/fb_prophet/<run>/` | `prophet_model.json` |
| Tweet novelty | `data/runs/tweet_novelty/<run>/` | `tweet_novelty_classifier.pkl` |

`Dockerfile.ui` intentionally does not include model artifacts. The Streamlit image calls FastAPI. The API image/container must see `/app/data/runs`, either through the local repo bind mount or the prod `HOST_RUNS_DIR` bind mount.

## Usage Sequence

```mermaid
sequenceDiagram
    actor User
    participant UI as Streamlit UI
    participant API as FastAPI
    participant DB as PostgreSQL
    participant Worker as Detached CLI Subprocess
    participant Eval as Evaluator
    participant Env as TradingEnvLive
    participant Exchange as Exchange APIs
    participant Slack as Slack

    User->>UI: Log in and open Bot Control
    UI->>API: GET /dashboard/checkpoints/{algo}
    API-->>UI: Available model checkpoints
    User->>UI: Select algo, checkpoint, pair, bet size, iterations
    UI->>API: POST /bots/run
    API->>DB: Insert bot_jobs row
    API->>Worker: subprocess.Popen python -m interface.cli.av ... --job-id
    API->>DB: Store bot_pid and process group
    API-->>UI: Return job status
    Worker->>Eval: av agent/statistical calls live runner
    Eval->>Env: Build environment and bind algorithm
    Env->>Exchange: Fetch initial data and open stream
    loop Each episode
        Env->>Env: Build observation
        Env->>Eval: Request action through strategy or RL policy
        Env->>Exchange: Execute order when ENV=prod
        Env->>DB: Update position, bets, profit, progress
        Env-->>Slack: Optional episode message and chart
    end
    UI->>API: GET /bots/active
    API->>DB: Read running jobs
    API-->>UI: Current status and progress
    User->>UI: Stop bot
    UI->>API: POST /bots/stop/{job_id}
    API->>DB: Read bot_pid/process group
    API->>Worker: SIGTERM process group
    Worker->>Env: Close websocket and open positions
    API->>DB: Mark job stopped
```

## Cloud Services View

```mermaid
flowchart TB
    User["Browser user"]
    SlackClient["Slack workspace"]
    GHCR["GitHub Container Registry\nAPI and UI images"]
    Exchanges["Exchange and data APIs\nBinance, Bybit, X"]

    subgraph VM["Cloud VM or NAS host"]
        Nginx["nginx\nport 80"]
        Dashboard["Streamlit container\nai-trader-ui"]
        APIService["FastAPI container\nai-trader"]
        SlackBot["Slack bot container\nai-trader"]
        PostgresSvc["Postgres container\npostgres_data volume"]
        ApiData["api_data volume\nruntime data"]
        RunsMount["host data/runs\nmounted read-only to /app/data/runs"]
    end

    GHCR -->|"docker compose pull"| Dashboard
    GHCR -->|"docker compose pull"| APIService
    GHCR -->|"same backend image"| SlackBot
    User -->|"HTTP"| Nginx
    Nginx --> Dashboard
    Nginx -->|" /api "| APIService
    Dashboard -->|"API_URL=http://api:8000"| APIService
    SlackClient -->|"Socket Mode events"| SlackBot
    SlackBot -->|"API_URL=http://api:8000"| APIService
    APIService --> PostgresSvc
    APIService --> ApiData
    RunsMount --> APIService
    RunsMount --> SlackBot
    APIService --> Exchanges
```

# Database Architecture

## Why PostgreSQL?
The live dashboard and Slack bot need a durable state store while multiple
processes are running. PostgreSQL is used for operational state, not for large
model artifacts or market CSVs. The important reasons are:

- **Concurrency**: FastAPI, live environments, manual tweet scoring, and Slack
  actions can write/read bot state without SQLite-style lock contention.
- **Durability**: Jobs, bets, manual tweet predictions, and live observations
  survive process restarts.
- **Operational queries**: The UI can group active jobs, performance rows,
  manual tweet outcomes, and live observation diagnostics from one relational
  schema.
- **Migration control**: Alembic keeps the local/dev and production schemas
  aligned with `av_crypto_trading/connectors/postgres_db/models.py`.

## Schema Design
The authoritative model definition is
`av_crypto_trading/connectors/postgres_db/models.py`; the initial migration is
`av_crypto_trading/connectors/postgres_db/migrations/versions/0001_initial_postgres_schema.py`.
The current schema tracks dashboard users, bot runs, trade events, manual tweet
signals, and stored live observations.

```mermaid
erDiagram
    BOT_JOBS ||--o{ BOT_BETS : "manages"
    BOT_JOBS ||--o{ TWEET_MANUAL_PREDICTIONS : "scores"
    BOT_JOBS ||--o{ LIVE_OBSERVATIONS : "records"

    USERS {
        int id PK
        string first_name
        string surname
        string email UK
        string hashed_password
        boolean is_active
    }

    BOT_JOBS {
        int id PK
        string job_id UK
        string algo_name
        string checkpoint_path
        string coin
        string params
        string status
        int target_bets
        int completed_bets
        datetime start_time
        datetime end_time
        float total_profit
        float bet_size
        string current_position
    }

    BOT_BETS {
        int id PK
        string job_id FK
        datetime timestamp
        string type
        float price
        float quantity
        float pnl
        string description
    }

    TWEET_MANUAL_PREDICTIONS {
        int id PK
        datetime created_at
        string job_id FK
        string source
        string symbol
        string model_path
        string model_run
        string prediction
        int prediction_label
        string action
        float signal_strength
        float direction_score
        float proba_non_affect
        float proba_novelty_up
        float proba_novelty_down
        string mark_status
        string trade_status
        float pnl
    }

    LIVE_OBSERVATIONS {
        int id PK
        datetime created_at
        datetime timestamp
        string job_id FK
        string algo_name
        string symbol
        string run_name
        string checkpoint_path
        string features_version
        string obs
        string human_obs
        int action
        string position
        boolean is_anomaly
    }
```

The `tweet_manual_predictions` table also stores entry/exit prices,
take-profit/stop-loss settings, Bybit order IDs, open/close bet references, and
the serialized feature snapshot used for scoring. The `live_observations` table
stores raw observation payloads and human-readable equivalents as text so the
dashboard can inspect anomalies without coupling the schema to one feature
version.

## Table Definitions
- **`users`**: Dashboard authentication records. Email is unique and indexed.
- **`bot_jobs`**: One record per dashboard, Slack, or manual-tweet trading job. Tracks algorithm, model/checkpoint path, symbol, params JSON, status, current position, target/completed bet counts, bet size, total PnL, and detached worker process metadata (`bot_pid`, `bot_process_group_id`, `bot_worker_log_path`).
- **`bot_bets`**: Trade event rows linked to `bot_jobs.job_id`. Stores timestamp, trade type, price, quantity, realized/unrealized PnL, and a human-readable description.
- **`tweet_manual_predictions`**: Manual tweet novelty decisions. Stores the scored tweet text, model run, class probabilities, chosen action, mark/outcome fields, optional trade invocation state, Bybit order ID, TP/SL prices, and feature snapshot.
- **`live_observations`**: Debug and monitoring table for live agents. Stores timestamped observations, feature names/equivalents, human OHLCV context, action, position, anomaly flags, and notes.

---

## Known issues:

* GHCR push denied with `permission_denied: write_package`: connect the package to this repository, then in package settings add this repo under **Manage Actions access** with **Write** access.

* error: command '/usr/bin/x86_64-linux-gnu-gcc' failed with exit code 1

```sudo apt-get install python3.9-dev build-essential```

* No module named tkinter:
```
sudo apt-get install python3-tk
```

* Git large files:
```
sudo apt-get install git-lfs
git lfs install
git lfs track "*.csv"
git lfs pull
```

* Error with push, bad object:
```
git push
git fetch --all
git stash push .
git pull 
git push
git stash pop  
```

### OOM during training
Some computers may have OOM process killed during training because of fragmentation issues.
It may help to run with different allocator:
```
sudo apt-get update
sudo apt-get install libgoogle-perftools-dev
LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libtcmalloc.so.4 poetry run python av_crypto_trading/reinforcement_learning/train.py
```

or export the MALLOC variables:
```
export MALLOC_ARENA_MAX=2
```
worth also checking:
```
ldd --version
```

## Disclaimer
Do not use it at home if you don't know how to :) 
You will lose money. Created only for educational purposes.
