.PHONY: all develop start clean

PROGRAM_NAME="api"

# Default
all: develop

# -------------------------
# OS detection & variables
# -------------------------
ifeq ($(OS),Windows_NT)
  # Windows - use root venv
  PY := ..\venv\Scripts\python.exe
  PIP := ..\venv\Scripts\pip.exe

  develop:
	@echo "Using root virtual environment"

  start: develop
	@$(PY) src\main.py

  clean:
	@if exist __pycache__ rmdir /s /q __pycache__
	@for /d %%d in (*\__pycache__) do rmdir /s /q "%%d"

else
  # Linux / macOS - use root venv
  PY := ../venv/bin/python
  PIP := ../venv/bin/pip

  develop:
	@echo "Using root virtual environment"

  start: develop
	@$(PY) src/main.py

  clean:
	@rm -rf __pycache__ */__pycache__
endif
