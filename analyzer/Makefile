.PHONY: setup install run clean help start copy-latest

PROGRAM_NAME="analyzer"

# Detect OS and use root venv
ifeq ($(OS),Windows_NT)
    PYTHON := ..\venv\Scripts\python.exe
    PIP := ..\venv\Scripts\pip.exe
    RM := rmdir /s /q
    FIND := powershell -Command "Get-ChildItem -Recurse -Include"
    MKDIR := mkdir
    COPY := copy
else
    PYTHON := ../venv/bin/python
    PIP := ../venv/bin/pip
    RM := rm -rf
    FIND := find . -name
    MKDIR := mkdir -p
    COPY := cp
endif

# Default target - show available commands (like .bat file did)
start:
	@echo "Available commands:"
	@echo "  make start         - Show this help message"
	@echo "  make setup         - Create .env file from template"
	@echo "  make copy-latest   - Copy latest merged file to analyzer input"
	@echo "  make install       - Install Python dependencies and package"
	@echo "  make run           - Run Womter with pattern matching"
	@echo "  make run-all       - Run Womter without pattern matching"
	@echo "  make clean         - Remove Python cache files"
	@echo "  make all           - Setup, copy latest file, install, and run"
	@echo "  make help          - Show detailed help"

# Help target
help:
	@echo "=== $(PROGRAM_NAME) Makefile Help ==="
	@echo ""
	@echo "Available commands:"
	@echo "  make start         - Show available commands"
	@echo "  make setup         - Create .env file from template"
	@echo "  make copy-latest   - Copy latest merged file to analyzer input"
	@echo "  make install       - Install Python dependencies and package"
	@echo "  make run           - Run Womter with pattern matching"
	@echo "  make run-all       - Run Womter without pattern matching"
	@echo "  make clean         - Remove Python cache files"
	@echo "  make all           - Setup, copy latest file, install, and run"
	@echo ""
	@echo "Examples:"
	@echo "  make copy-latest   # Copy latest merged file to analyzer input"
	@echo "  make run           # Run with pattern matching"
	@echo "  make run-all       # Run without pattern matching"
	@echo "  make setup         # Create .env file"
	@echo "  make clean         # Clean cache files"

# Copy latest merged file to analyzer input
copy-latest:
	@echo "Copying latest merged file to analyzer input..."
ifeq ($(OS),Windows_NT)
	@powershell -Command "$$latest = Get-ChildItem '../merger/data/output/merged_data_*.xlsx' | Sort-Object LastWriteTime -Descending | Select-Object -First 1; if ($$latest) { Copy-Item $$latest.FullName './data/input/' -Force; Write-Host 'Copied' $$latest.Name 'to analyzer input'; } else { Write-Host 'No merged data files found'; exit 1; }"
else
	@LATEST_FILE=$$(ls -t ../merger/data/output/merged_data_*.xlsx 2>/dev/null | head -1); \
	if [ -n "$$LATEST_FILE" ]; then \
		$(COPY) "$$LATEST_FILE" ./data/input/; \
		echo "Copied $$(basename $$LATEST_FILE) to analyzer input"; \
	else \
		echo "No merged data files found"; \
		exit 1; \
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
install:
	@echo "Installing dependencies..."
	@$(PIP) install -r requirements.txt
	@echo "Installing package in development mode..."
	@$(PIP) install -e .

# Run the Womter program
run: install
	@echo "Running Womter with pattern matching..."
	@$(PYTHON) src/main.py

# Run the Womter program without patterns
run-all: install
	@echo "Running Womter without pattern matching..."
	@$(PYTHON) src/main.py --no-patterns

# Clean Python cache files
clean:
	@echo "Cleaning cache files..."
ifeq ($(OS),Windows_NT)
	@powershell -Command "Get-ChildItem -Recurse -Include '__pycache__' -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
	@powershell -Command "Get-ChildItem -Recurse -Include '*.pyc' | Remove-Item -Force -ErrorAction SilentlyContinue"
	@powershell -Command "Get-ChildItem -Recurse -Include '*.pyo' | Remove-Item -Force -ErrorAction SilentlyContinue"
	@powershell -Command "Get-ChildItem -Recurse -Include '*.egg-info' -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
else
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name "*.pyo" -delete 2>/dev/null || true
	@find . -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
endif

# Setup, copy latest file, install, and run
all: setup copy-latest install run 