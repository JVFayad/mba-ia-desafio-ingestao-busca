SHELL := /bin/bash
VENV_DIR := venv
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip

.PHONY: help init create-venv activate-venv install db-up ingest chat

help:
	@echo "Targets disponiveis:"
	@echo "  make create-venv    - cria uma virtualenv chamada venv"
	@echo "  make activate-venv  - abre um shell com a venv ativada"
	@echo "  make install        - instala as dependencias do projeto"
	@echo "  make db-up          - sobe os servicos do docker em background"
	@echo "  make ingest         - executa a ingestao do PDF"
	@echo "  make chat           - inicia o chat da aplicacao"
	@echo "  make init            - executa install, db-up e ingest"

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