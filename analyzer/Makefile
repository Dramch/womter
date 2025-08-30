.PHONY: all develop start start-analyzer clean install-deps \
         analyzer-setup analyzer-install analyzer-run analyzer-copy-latest analyzer-clean analyzer-all \
         setup install run copy-latest clean

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

  develop: install-deps
	@echo "Development environment ready"

  install-deps:
	@if not exist venv ( $(PY_BOOT) -m venv venv )
	@$(PY) -m pip install --upgrade pip
	@$(PIP) install -r requirements.txt
	@$(PIP) install -e .

  start: develop copy-latest
	@echo "Cleaning previous log files..."
	@if exist data\logs rmdir /s /q data\logs
	@mkdir data\logs
	@echo "Running analyzer..."
	@$(PY) src/main.py

  start-analyzer: develop
	@make -C analyzer run

  # Analyzer commands
  analyzer-setup: develop
	@make -C analyzer setup

  analyzer-install: develop
	@make -C analyzer install

  analyzer-run: develop
	@make -C analyzer run

  analyzer-copy-latest: develop
	@make -C analyzer copy-latest

  analyzer-clean: develop
	@make -C analyzer clean

  analyzer-all: develop
	@make -C analyzer all

  # Direct analyzer targets (for when called from root)
  setup: develop
	@echo "Setting up analyzer environment..."
	@if not exist ".env" ( copy env.example .env && echo Created .env file from template ) else ( echo .env file already exists )

  install: develop
	@echo "Installing analyzer dependencies..."
	@$(PIP) install -r requirements.txt
	@$(PIP) install -e .

  run: install
	@echo "Cleaning previous log files..."
	@if exist data\logs rmdir /s /q data\logs
	@mkdir data\logs
	@echo "Running analyzer..."
	@$(PY) src/main.py

  copy-latest: develop
	@echo "Copying latest merged file to analyzer input..."
	@powershell -Command "$$latest = Get-ChildItem '../merger/data/output/merged_data_*.xlsx' | Sort-Object LastWriteTime -Descending | Select-Object -First 1; if ($$latest) { Copy-Item $$latest.FullName './data/input/' -Force; Write-Host 'Copied' $$latest.Name 'to analyzer input'; } else { Write-Host 'No merged data files found'; exit 1; }"

  clean:
	@if exist venv rmdir /s /q venv
	@if exist __pycache__ rmdir /s /q __pycache__
	@for /d %%d in (*\__pycache__) do rmdir /s /q "%%d"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true

else
  # Linux / macOS
  PY_BOOT ?= python3
  PY := venv/bin/python
  PIP := venv/bin/pip

  develop: install-deps
	@echo "Development environment ready"

  install-deps:
	@test -d venv || $(PY_BOOT) -m venv venv
	@$(PY) -m pip install --upgrade pip
	@$(PIP) install -r requirements.txt
	@$(PIP) install -e .

  start: develop copy-latest
	@echo "Cleaning previous log files..."
	@rm -rf data/logs/*
	@mkdir -p data/logs
	@echo "Running analyzer..."
	@$(PY) src/main.py

  start-analyzer: develop
	@make -C analyzer run

  # Analyzer commands
  analyzer-setup: develop
	@make -C analyzer setup

  analyzer-install: develop
	@make -C analyzer install

  analyzer-run: develop
	@make -C analyzer run

  analyzer-copy-latest: develop
	@make -C analyzer copy-latest

  analyzer-clean: develop
	@make -C analyzer clean

  analyzer-all: develop
	@make -C analyzer all

  # Direct analyzer targets (for when called from root)
  setup: develop
	@echo "Setting up analyzer environment..."
	@if [ ! -f .env ]; then cp env.example .env; echo "Created .env file from template"; else echo ".env file already exists"; fi

  install: develop
	@echo "Installing analyzer dependencies..."
	@$(PIP) install -r requirements.txt
	@$(PIP) install -e .

  run: install
	@echo "Cleaning previous log files..."
	@rm -rf data/logs/*
	@mkdir -p data/logs
	@echo "Running analyzer..."
	@$(PY) src/main.py

  copy-latest: develop
	@echo "Copying latest merged file to analyzer input..."
	@LATEST_FILE=$$(ls -t ../merger/data/output/merged_data_*.xlsx 2>/dev/null | head -1); \
	if [ -n "$$LATEST_FILE" ]; then \
		cp "$$LATEST_FILE" ./data/input/; \
		echo "Copied $$(basename $$LATEST_FILE) to analyzer input"; \
	else \
		echo "No merged data files found"; \
		exit 1; \
	fi

  clean:
	@rm -rf venv __pycache__ */__pycache__
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
endif 