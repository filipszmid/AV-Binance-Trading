SHELL := /bin/bash
POETRY := $(shell command -v poetry 2> /dev/null)

-include .env

_BOLD := $(shell tput -T ansi bold)
_COLS := $(shell tput -T ansi cols)
_DEFAULT := $(shell tput -T ansi sgr0)
_ITALICS := $(shell tput -T ansi sitm)
_BLUE := $(shell tput -T ansi setaf 4)
_CYAN := $(shell tput -T ansi setaf 6)
_GREEN := $(shell tput -T ansi setaf 2)
_MAGENTA := $(shell tput -T ansi setaf 5)
_RED := $(shell tput -T ansi setaf 1)
_YELLOW := $(shell tput -T ansi setaf 3)


.PHONY: test-vars
test-vars::
	@echo "Repository:" git@github.com:$(_USER)/$(_PROJECT).git
	@echo "Current working dir: "$(_CURRENT_DIR_NAME)
	@echo "Language:" $(LANGUAGE)
	@echo "Service name:" $(SERVICE_NAME)
	@echo "GH package:" $(GH_PACKAGE)


.PHONY: install
install::  ## install dependencies
	poetry install


.PHONY: up
up:: ## run API
	uvicorn av_crypto_trading.main:app --reload


.PHONY: up-front
up-front:: ## run dashboard
	poetry run streamlit run frontend/main_app.py


.PHONY: help
help:: ## display this help message
	$(info Please use $(_BOLD)make $(_DEFAULT)$(_ITALICS)$(_CYAN)target$(_DEFAULT) where \
	$(_ITALICS)$(_CYAN)target$(_DEFAULT) is one of:)
	@grep --no-filename "^[a-zA-Z]" $(MAKEFILE_LIST) | \
		sort | \
		awk -F ":.*?## " 'NF==2 {printf "$(_CYAN)%-20s$(_DEFAULT)%s\n", $$1, $$2}'


.PHONY: test
test:: ## run pytest
	poetry run pytest -rP --disable-warnings # -n 10
	#$(POETRY) run pytest


.PHONY: format
format::  ## format code
	poetry run isort . && poetry run black .


.PHONY: lint
lint::  ## run static code checkers
	poetry run prospector


.PHONY: clean
clean:: ## clean up temp and trash files
	find . -type f -name "*.py[cdo]" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	rm -rf .coverage .mypy_cache .pytest_cache *.egg-info build dist public

.PHONY: cl
cl:: ## clean RL outputs
	rm -rf `find . -type d -name "stocks_dqn_seed*"`
	rm -rf `find . -type d -name "stocks_dqn_deploy*"`
	rm -rf examples/RL/fig_random/* examples/RL/fig/* examples/RL/stocks_dqn_deploy
