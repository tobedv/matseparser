SHELL := $(shell which bash)
ENV = /usr/bin/env

.SHELLFLAGS = -c
.SILENT: ;
.ONESHELL: ;
.NOTPARALLEL: ;
.EXPORT_ALL_VARIABLES: ;

.PHONY: install run coverage test

install:
	export PIPENV_VENV_IN_PROJECT=true
	pipenv install --dev --skip-lock

run: install
	pipenv run python src/main.py

coverage: install
	pipenv run pytest --cov src test

test: install
	pipenv run pytest .