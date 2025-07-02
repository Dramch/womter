@echo off

:: Default target
if "%1"=="" (
    echo Available commands:
    echo   run.bat venv    - Create Python virtual environment
    echo   run.bat setup   - Create .env file from template
    echo   run.bat install - Install Python dependencies and package
    echo   run.bat run     - Run Womter with pattern matching
    echo   run.bat run-all - Run Womter without pattern matching
    echo   run.bat clean   - Remove Python cache files and venv
    echo   run.bat all     - Setup venv, install, and run
    exit /b
)

if "%1"=="venv" goto venv
if "%1"=="setup" goto setup
if "%1"=="install" goto install
if "%1"=="run" goto run
if "%1"=="run-all" goto run-all
if "%1"=="clean" goto clean
if "%1"=="all" goto all

echo Unknown command: %1
exit /b 1

:venv
echo Creating Python virtual environment...
if not exist "venv" (
    python -m venv venv 2>nul || python3 -m venv venv 2>nul || py -m venv venv 2>nul
    if exist "venv" (
        echo Virtual environment created
    ) else (
        echo ERROR: Could not create virtual environment. Please ensure Python is installed and in PATH.
        echo Try running: python --version or python3 --version
        exit /b 1
    )
) else (
    echo Virtual environment already exists
)
goto end

:setup
echo Setting up environment...
if not exist ".env" (
    copy env.example .env
    echo Created .env file from template
    echo Please edit .env and set your EXCEL_FILE_PATH
) else (
    echo .env file already exists
)
goto end

:install
call :venv
echo Installing dependencies...
call venv\Scripts\activate
if errorlevel 1 (
    echo ERROR: Could not activate virtual environment
    exit /b 1
)
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Could not install requirements
    exit /b 1
)
echo Installing package in development mode...
pip install -e .
if errorlevel 1 (
    echo ERROR: Could not install package in development mode
    exit /b 1
)
goto end

:run
call :install
echo Running Womter with pattern matching...
call venv\Scripts\activate
python main.py
if errorlevel 1 (
    echo ERROR: Could not run Womter
    exit /b 1
)
goto end

:run-all
call :install
echo Running Womter without pattern matching...
call venv\Scripts\activate
python main.py --no-patterns
if errorlevel 1 (
    echo ERROR: Could not run Womter
    exit /b 1
)
goto end

:clean
echo Cleaning cache files and virtual environment...
powershell -Command "Get-ChildItem -Recurse -Include '__pycache__' -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
powershell -Command "Get-ChildItem -Recurse -Include '*.pyc' | Remove-Item -Force -ErrorAction SilentlyContinue"
powershell -Command "Get-ChildItem -Recurse -Include '*.pyo' | Remove-Item -Force -ErrorAction SilentlyContinue"
powershell -Command "Get-ChildItem -Recurse -Include '*.egg-info' -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
if exist "venv" (
    rmdir /s /q venv
    echo Virtual environment removed
)
goto end

:all
call :setup
call :run
goto end

:end 