.PHONY: all develop start clean data-copy

PROGRAM_NAME="merger"

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

  # Copy data from API output to merger input
  data-copy:
	@echo "Checking for API output data..."
	@if exist "..\api\data\output" ( \
		echo Creating merger/data/input directory if it doesn't exist... && \
		if not exist "data\input" mkdir "data\input" && \
		echo Copying files from api/data/output to merger/data/input... && \
		echo (Overwriting existing files with latest versions) && \
		xcopy "..\api\data\output\*" "data\input\" /E /Y /Q && \
		echo Data copy completed successfully - latest versions copied \
	) else ( \
		echo WARNING: api/data/output directory does not exist && \
		echo Please ensure the API has generated output data first && \
		echo You can run 'make start-api' to generate data \
	)

  start: develop data-copy
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

  # Copy data from API output to merger input
  data-copy:
	@echo "Checking for API output data..."
	@if [ -d "../api/data/output" ]; then \
		echo "Creating merger/data/input directory if it doesn't exist..."; \
		mkdir -p data/input; \
		echo "Copying files from api/data/output to merger/data/input..."; \
		echo "(Overwriting existing files with latest versions)"; \
		if [ -n "$$(ls -A ../api/data/output 2>/dev/null)" ]; then \
			cp -r ../api/data/output/* data/input/ 2>/dev/null || true; \
			echo "Data copy completed successfully - latest versions copied"; \
		else \
			echo "API output directory is empty - no files to copy"; \
		fi; \
	else \
		echo "WARNING: api/data/output directory does not exist"; \
		echo "Please ensure the API has generated output data first"; \
		echo "You can run 'make start-api' to generate data"; \
	fi

  start: develop data-copy
	@$(PY) src/main.py

  clean:
	@rm -rf __pycache__ */__pycache__
endif
