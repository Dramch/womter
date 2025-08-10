.PHONY: all develop start clean

# Default
all: develop

# -------------------------
# OS detection & variables
# -------------------------
ifeq ($(OS),Windows_NT)
  # Windows
  PY_BOOT := py
  PY := venv\Scripts\python.exe
  PIP := venv\Scripts\pip.exe

  develop:
	@if not exist venv ( $(PY_BOOT) -m venv venv )
	@$(PY) -m pip install --upgrade pip
	@$(PIP) install -r requirements.txt

  start: develop
	@$(PY) src\main.py

  clean:
	@if exist venv rmdir /s /q venv
	@if exist __pycache__ rmdir /s /q __pycache__
	@for /d %%d in (*\__pycache__) do rmdir /s /q "%%d"

else
  # Linux / macOS
  PY_BOOT ?= python3
  PY := venv/bin/python
  PIP := venv/bin/pip

  develop:
	@test -d venv || $(PY_BOOT) -m venv venv
	@$(PY) -m pip install --upgrade pip
	@$(PIP) install -r requirements.txt

  start: develop
	@$(PY) src/main.py

  clean:
	@rm -rf venv __pycache__ */__pycache__
endif
