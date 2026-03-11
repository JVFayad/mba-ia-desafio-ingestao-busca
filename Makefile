SHELL := /bin/bash
VENV_DIR := venv
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip

.PHONY: help init create-venv activate-venv install db-up ingest chat format lint test coverage

help:
	@echo "Targets disponiveis:"
	@echo "  make create-venv    - cria uma virtualenv chamada venv"
	@echo "  make activate-venv  - abre um shell com a venv ativada"
	@echo "  make install        - instala as dependencias do projeto"
	@echo "  make db-up          - sobe os servicos do docker em background"
	@echo "  make ingest         - executa a ingestao do PDF"
	@echo "  make chat           - inicia o chat da aplicacao"
	@echo "  make init           - executa install, db-up e ingest"
	@echo "  make format         - formata o codigo com black"
	@echo "  make lint           - valida o codigo com flake8"
	@echo "  make test           - roda os testes unitarios com pytest"
	@echo "  make coverage       - roda testes com cobertura minima de 100%"

init: install db-up ingest

create-venv:
	python -m venv venv

activate-venv:
	@source venv/bin/activate && exec bash

install:
	$(PIP) install -r requirements.txt

db-up:
	docker compose up -d

ingest:
	$(PYTHON) src/ingest.py

chat:
	$(PYTHON) src/chat.py

format:
	$(PYTHON) -m black src/ tests/

lint:
	$(PYTHON) -m flake8 src/ tests/

test:
	$(PYTHON) -m pytest tests/ -v

coverage:
	$(PYTHON) -m pytest tests/ -v --cov=src --cov-report=term-missing --cov-fail-under=100