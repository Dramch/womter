param(
    [string]$Command = ""
)

# Default target
if ($Command -eq "") {
    Write-Host "Available commands:"
    Write-Host "  .\run.ps1 venv    - Create Python virtual environment"
    Write-Host "  .\run.ps1 setup   - Create .env file from template"
    Write-Host "  .\run.ps1 install - Install Python dependencies and package"
    Write-Host "  .\run.ps1 run     - Run Womter with pattern matching"
    Write-Host "  .\run.ps1 run-all - Run Womter without pattern matching"
    Write-Host "  .\run.ps1 clean   - Remove Python cache files and venv"
    Write-Host "  .\run.ps1 all     - Setup venv, install, and run"
    exit
}

function Create-Venv {
    Write-Host "Creating Python virtual environment..."
    if (-not (Test-Path "venv")) {
        python -m venv venv
        Write-Host "Virtual environment created"
    } else {
        Write-Host "Virtual environment already exists"
    }
}

function Setup-Environment {
    Write-Host "Setting up environment..."
    if (-not (Test-Path ".env")) {
        Copy-Item env.example .env
        Write-Host "Created .env file from template"
        Write-Host "Please edit .env and set your EXCEL_FILE_PATH"
    } else {
        Write-Host ".env file already exists"
    }
}

function Install-Dependencies {
    Create-Venv
    Write-Host "Installing dependencies..."
    & venv\Scripts\activate.ps1
    pip install -r requirements.txt
    Write-Host "Installing package in development mode..."
    pip install -e .
}

function Run-Womter {
    Install-Dependencies
    Write-Host "Running Womter with pattern matching..."
    & venv\Scripts\activate.ps1
    python main.py
}

function Run-WomterAll {
    Install-Dependencies
    Write-Host "Running Womter without pattern matching..."
    & venv\Scripts\activate.ps1
    python main.py --no-patterns
}

function Clean-Project {
    Write-Host "Cleaning cache files and virtual environment..."
    Get-ChildItem -Recurse -Include "__pycache__" -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Recurse -Include "*.pyc" | Remove-Item -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Recurse -Include "*.pyo" | Remove-Item -Force -ErrorAction SilentlyContinue
    Get-ChildItem -Recurse -Include "*.egg-info" -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    if (Test-Path "venv") {
        Remove-Item -Recurse -Force venv
        Write-Host "Virtual environment removed"
    }
}

function Run-All {
    Setup-Environment
    Run-Womter
}

# Execute the requested command
switch ($Command) {
    "venv" { Create-Venv }
    "setup" { Setup-Environment }
    "install" { Install-Dependencies }
    "run" { Run-Womter }
    "run-all" { Run-WomterAll }
    "clean" { Clean-Project }
    "all" { Run-All }
    default {
        Write-Host "Unknown command: $Command"
        exit 1
    }
} 