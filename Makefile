.PHONY: develop install start

# Default target
all: develop

develop:
	@test -d venv || python3 -m venv venv
	@venv/bin/pip install -r requirements.txt

start: develop
	@venv/bin/python src/main.py
