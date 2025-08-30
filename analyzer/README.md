# Womter Project

A professional Python package for reading and displaying contents from Excel files (XLSX format).

## Features

- 📊 Reads all sheets from Excel files
- 🔍 Advanced pattern matching for filtering data
- 📋 Displays comprehensive information (shape, columns, data types)
- 👀 Shows filtered rows based on patterns
- 🛡️ Robust error handling for missing files or invalid paths
- ⚙️ Environment-based configuration
- 📦 Proper Python package structure
- 🎯 Support for multiple patterns in Mensaje column
- 🎯 Optional filtering by Cuenta and Foro columns

## Quick Start

### Using Make (Recommended)

```bash
# Complete setup and run
make all

# Or step by step
make setup    # Create .env file
make install  # Install dependencies and package
make run      # Run with pattern matching
make run-all  # Run without pattern matching
```

### Manual Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

2. **Configure environment:**
   ```bash
   cp env.example .env
   # Edit .env and set EXCEL_FILE_PATH
   ```

3. **Run the program:**
   ```bash
   python main.py              # With pattern matching
   python main.py --no-patterns # Without pattern matching
   ```

## Project Structure

```
womter/
├── src/
│   └── womter/
│       ├── __init__.py      # Package initialization
│       ├── reader.py        # Core Excel reading functionality
│       ├── pattern_matcher.py # Pattern matching functionality
│       └── excel_writer.py  # Excel output functionality
├── main.py                  # Application entry point
├── pyproject.toml           # Modern Python packaging
├── requirements.txt         # Development dependencies
├── patterns.json            # Pattern configuration file
├── env.example             # Environment template
├── .env                    # Environment variables
├── Makefile                # Build automation
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

## Pattern Matching

The application supports filtering Excel data based on complex pattern configurations defined in `patterns.json`:

### Pattern Configuration File

Create a `patterns.json` file in the project root with an array of pattern groups:

```json
[
  {
    "cuenta": "asdsa",
    "foro": "asdas", 
    "mensaje": ["Hola", "Danger"]
  },
  {
    "mensaje": ["ADIOS"],
    "foro": "asdas"
  }
]
```

### Pattern Group Structure

Each pattern group is an object with optional fields:
- `cuenta` - Pattern to match in Cuenta column (optional)
- `foro` - Pattern to match in Foro column (optional)  
- `mensaje` - Array of patterns to search in Mensaje column (optional)

### Pattern Matching Rules

- **Multiple groups**: Uses OR logic between groups (any group can match)
- **Within groups**: Uses AND logic (all specified fields must match)
- **Mensaje patterns**: Uses OR logic within the array (any pattern matches)
- **Missing fields**: If a field is not specified, any value matches
- **Case insensitive**: All pattern matching is case insensitive

## Excel Output

The application automatically saves pattern matching results to Excel files:

### Output Configuration

- **Location**: Results are saved in the `output/` directory
- **Versioning**: Files are never overwritten (e.g., `results_v1.xlsx`, `results_v2.xlsx`)
- **Structure**: Each pattern gets its own sheet with the pattern as the first row
- **Columns**: Cuenta, Mensaje, Foro data for matching rows

### Environment Variables

- `EXCEL_FILE_PATH` - Path to the Excel file to read
- `OUTPUT_FILENAME` - Name for the output Excel file (default: results.xlsx)

### Output Format

Each Excel sheet contains:
1. **Row 1**: JSON string of the pattern configuration
2. **Row 2**: Column headers (Cuenta, Mensaje, Foro)
3. **Row 3+**: Matching data rows

## Development

### Available Make Commands

- `make help` - Show all available commands
- `make venv` - Create Python virtual environment
- `make setup` - Create .env file from template
- `make install` - Install dependencies and package
- `make run` - Run Womter with pattern matching
- `make run-all` - Run Womter without pattern matching
- `make clean` - Remove cache files and virtual environment
- `make all` - Complete setup and run

## Dependencies

- `pandas` - For reading Excel files
- `openpyxl` - Excel file format support
- `python-dotenv` - Environment variable management

## Package Installation

This project can be installed as a Python package:

```bash
pip install -e .
```

After installation, you can use it as a module:

```python
from womter.reader import ExcelReader

reader = ExcelReader("path/to/file.xlsx")
reader.read_and_display()
```
