.PHONY: setup install run clean help venv

# Detect OS
ifeq ($(OS),Windows_NT)
    PYTHON := python
    VENV_ACTIVATE := venv\Scripts\activate
    RM := rmdir /s /q
    FIND := powershell -Command "Get-ChildItem -Recurse -Include"
    MKDIR := mkdir
else
    PYTHON := python3
    VENV_ACTIVATE := source venv/bin/activate
    RM := rm -rf
    FIND := find . -name
    MKDIR := mkdir -p
endif

# Default target
help:
	@echo "Available commands:"
	@echo "  make venv    - Create Python virtual environment"
	@echo "  make setup   - Create .env file from template"
	@echo "  make install - Install Python dependencies and package"
	@echo "  make run     - Run Womter with pattern matching"
	@echo "  make run-all - Run Womter without pattern matching"
	@echo "  make clean   - Remove Python cache files and venv"
	@echo "  make all     - Setup venv, install, and run"

# Create Python virtual environment
venv:
	@echo "Creating Python virtual environment..."
ifeq ($(OS),Windows_NT)
	@if not exist "venv" ( \
		$(PYTHON) -m venv venv && \
		echo Virtual environment created \
	) else ( \
		echo Virtual environment already exists \
	)
else
	@if [ ! -d "venv" ]; then \
		$(PYTHON) -m venv venv; \
		echo "Virtual environment created"; \
	else \
		echo "Virtual environment already exists"; \
	fi
endif

# Create .env file from template
setup:
	@echo "Setting up environment..."
ifeq ($(OS),Windows_NT)
	@if not exist ".env" ( \
		copy env.example .env && \
		echo Created .env file from template && \
		echo Please edit .env and set your EXCEL_FILE_PATH \
	) else ( \
		echo .env file already exists \
	)
else
	@if [ ! -f .env ]; then \
		cp env.example .env; \
		echo "Created .env file from template"; \
		echo "Please edit .env and set your EXCEL_FILE_PATH"; \
	else \
		echo ".env file already exists"; \
	fi
endif

# Install Python dependencies
install: venv
	@echo "Installing dependencies..."
ifeq ($(OS),Windows_NT)
	@$(VENV_ACTIVATE) && pip install -r requirements.txt
	@echo "Installing package in development mode..."
	@$(VENV_ACTIVATE) && pip install -e .
else
	@$(VENV_ACTIVATE) && pip install -r requirements.txt
	@echo "Installing package in development mode..."
	@$(VENV_ACTIVATE) && pip install -e .
endif

# Run the Womter program
run: install
	@echo "Running Womter with pattern matching..."
ifeq ($(OS),Windows_NT)
	@$(VENV_ACTIVATE) && python main.py
else
	@$(VENV_ACTIVATE) && python main.py
endif

# Run the Womter program without patterns
run-all: install
	@echo "Running Womter without pattern matching..."
ifeq ($(OS),Windows_NT)
	@$(VENV_ACTIVATE) && python main.py --no-patterns
else
	@$(VENV_ACTIVATE) && python main.py --no-patterns
endif



# Clean Python cache files and virtual environment
clean:
	@echo "Cleaning cache files and virtual environment..."
ifeq ($(OS),Windows_NT)
	@powershell -Command "Get-ChildItem -Recurse -Include '__pycache__' -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
	@powershell -Command "Get-ChildItem -Recurse -Include '*.pyc' | Remove-Item -Force -ErrorAction SilentlyContinue"
	@powershell -Command "Get-ChildItem -Recurse -Include '*.pyo' | Remove-Item -Force -ErrorAction SilentlyContinue"
	@powershell -Command "Get-ChildItem -Recurse -Include '*.egg-info' -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
	@if exist "venv" ( \
		$(RM) venv && \
		echo Virtual environment removed \
	)
else
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name "*.pyo" -delete 2>/dev/null || true
	@find . -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@if [ -d "venv" ]; then \
		rm -rf venv; \
		echo "Virtual environment removed"; \
	fi
endif

# Setup, install, and run
all: setup install run 