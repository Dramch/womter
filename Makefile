.PHONY: all develop start start-api start-analyzer start-merger clean install-deps \
         analyzer-setup analyzer-install analyzer-run analyzer-run-all analyzer-copy-latest analyzer-clean analyzer-all analyzer-start \
         api-develop api-start api-clean \
         merger-develop merger-start merger-clean merger-data-copy

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
	@$(PIP) install -r analyzer/requirements.txt
	@$(PIP) install -r api/requirements.txt
	@$(PIP) install -r merger/requirements.txt

  start: develop
	@echo "Use 'make start-api', 'make start-analyzer', or 'make start-merger' to run specific projects"

  start-api: develop
	@make -C api start

  start-analyzer: develop
	@make -C analyzer start

  start-merger: develop
	@make -C merger start

  # Analyzer commands
  analyzer-start: develop
	@make -C analyzer start

  analyzer-setup: develop
	@make -C analyzer setup

  analyzer-install: develop
	@make -C analyzer install

  analyzer-run: develop
	@make -C analyzer run

  analyzer-run-all: develop
	@make -C analyzer run-all

  analyzer-clean: develop
	@make -C analyzer clean


  analyzer-copy-latest: develop
	@make -C analyzer copy-latest

  analyzer-all: develop
	@make -C analyzer all

  # API commands
  api-develop: develop
	@make -C api develop

  api-start: develop
	@make -C api start

  api-clean: develop
	@make -C api clean

  # Merger commands
  merger-develop: develop
	@make -C merger develop

  merger-start: develop
	@make -C merger start

  merger-clean: develop
	@make -C merger clean

  merger-data-copy: develop
	@make -C merger data-copy

  clean:
	@if exist venv rmdir /s /q venv
	@if exist __pycache__ rmdir /s /q __pycache__
	@for /d %%d in (*\__pycache__) do rmdir /s /q "%%d"
	@make -C api clean
	@make -C merger clean

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
	@$(PIP) install -r analyzer/requirements.txt
	@$(PIP) install -r api/requirements.txt
	@$(PIP) install -r merger/requirements.txt

  start: develop
	@echo "Use 'make start-api', 'make start-analyzer', or 'make start-merger' to run specific projects"

  start-api: develop
	@make -C api start

  start-analyzer: develop
	@make -C analyzer start

  start-merger: develop
	@make -C merger start

  # Analyzer commands
  analyzer-start: develop
	@make -C analyzer start

  analyzer-setup: develop
	@make -C analyzer setup

  analyzer-install: develop
	@make -C analyzer install

  analyzer-run: develop
	@make -C analyzer run

  analyzer-run-all: develop
	@make -C analyzer run-all

  analyzer-copy-latest: develop
	@make -C analyzer copy-latest

  analyzer-clean: develop
	@make -C analyzer clean

  analyzer-all: develop
	@make -C analyzer all

  # API commands
  api-develop: develop
	@make -C api develop

  api-start: develop
	@make -C api start

  api-clean: develop
	@make -C api clean

  # Merger commands
  merger-develop: develop
	@make -C merger develop

  merger-start: develop
	@make -C merger start

  merger-clean: develop
	@make -C merger clean

  merger-data-copy: develop
	@make -C merger data-copy

  clean:
	@rm -rf venv __pycache__ */__pycache__
	@make -C api clean
	@make -C merger clean
endif