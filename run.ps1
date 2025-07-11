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
        $pythonCommands = @("python", "python3", "py")
        $venvCreated = $false
        
        foreach ($cmd in $pythonCommands) {
            try {
                & $cmd -m venv venv 2>$null
                if (Test-Path "venv") {
                    Write-Host "Virtual environment created using $cmd"
                    $venvCreated = $true
                    break
                }
            } catch {
                continue
            }
        }
        
        if (-not $venvCreated) {
            Write-Host "ERROR: Could not create virtual environment. Please ensure Python is installed and in PATH." -ForegroundColor Red
            Write-Host "Try running: python --version or python3 --version" -ForegroundColor Yellow
            exit 1
        }
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
    try {
        & venv\Scripts\activate.ps1
        & venv\Scripts\pip.exe install -r requirements.txt
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERROR: Could not install requirements" -ForegroundColor Red
            exit 1
        }
        Write-Host "Installing package in development mode..."
        & venv\Scripts\pip.exe install -e .
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERROR: Could not install package in development mode" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "ERROR: Could not activate virtual environment" -ForegroundColor Red
        Write-Host "Trying alternative activation method..." -ForegroundColor Yellow
        try {
            & venv\Scripts\pip.exe install -r requirements.txt
            if ($LASTEXITCODE -ne 0) {
                Write-Host "ERROR: Could not install requirements" -ForegroundColor Red
                exit 1
            }
            Write-Host "Installing package in development mode..."
            & venv\Scripts\pip.exe install -e .
            if ($LASTEXITCODE -ne 0) {
                Write-Host "ERROR: Could not install package in development mode" -ForegroundColor Red
                exit 1
            }
        } catch {
            Write-Host "ERROR: Could not install packages" -ForegroundColor Red
            exit 1
        }
    }
}

function Run-Womter {
    Install-Dependencies
    Write-Host "Running Womter with pattern matching..."
    try {
        & venv\Scripts\activate.ps1
        & venv\Scripts\python.exe main.py
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERROR: Could not run Womter" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "ERROR: Could not run Womter" -ForegroundColor Red
        Write-Host "Trying alternative method..." -ForegroundColor Yellow
        try {
            & venv\Scripts\python.exe main.py
            if ($LASTEXITCODE -ne 0) {
                Write-Host "ERROR: Could not run Womter" -ForegroundColor Red
                exit 1
            }
        } catch {
            Write-Host "ERROR: Could not run Womter" -ForegroundColor Red
            exit 1
        }
    }
}

function Run-WomterAll {
    Install-Dependencies
    Write-Host "Running Womter without pattern matching..."
    try {
        & venv\Scripts\activate.ps1
        & venv\Scripts\python.exe main.py --no-patterns
        if ($LASTEXITCODE -ne 0) {
            Write-Host "ERROR: Could not run Womter" -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "ERROR: Could not run Womter" -ForegroundColor Red
        Write-Host "Trying alternative method..." -ForegroundColor Yellow
        try {
            & venv\Scripts\python.exe main.py --no-patterns
            if ($LASTEXITCODE -ne 0) {
                Write-Host "ERROR: Could not run Womter" -ForegroundColor Red
                exit 1
            }
        } catch {
            Write-Host "ERROR: Could not run Womter" -ForegroundColor Red
            exit 1
        }
    }
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