.PHONY: setup install run clean help venv

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
	@if [ ! -d "venv" ]; then \
		python3 -m venv venv; \
		echo "Virtual environment created"; \
	else \
		echo "Virtual environment already exists"; \
	fi

# Create .env file from template
setup:
	@echo "Setting up environment..."
	@if [ ! -f .env ]; then \
		cp env.example .env; \
		echo "Created .env file from template"; \
		echo "Please edit .env and set your EXCEL_FILE_PATH"; \
	else \
		echo ".env file already exists"; \
	fi

# Install Python dependencies
install: venv
	@echo "Installing dependencies..."
	@source venv/bin/activate && pip install -r requirements.txt
	@echo "Installing package in development mode..."
	@source venv/bin/activate && pip install -e .

# Run the Womter program
run: install
	@echo "Running Womter with pattern matching..."
	@source venv/bin/activate && python main.py

# Run the Womter program without patterns
run-all: install
	@echo "Running Womter without pattern matching..."
	@source venv/bin/activate && python main.py --no-patterns



# Clean Python cache files and virtual environment
clean:
	@echo "Cleaning cache files and virtual environment..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "*.pyo" -delete 2>/dev/null || true
	find . -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@if [ -d "venv" ]; then \
		rm -rf venv; \
		echo "Virtual environment removed"; \
	fi

# Setup, install, and run
all: setup install run 