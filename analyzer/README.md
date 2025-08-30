# Pattern Analyzer

A Python-based pattern matching system that applies predefined patterns to data organized by language. The system efficiently processes patterns and matches them against data rows, supporting various data types including strings, numbers, dates, and booleans.

## Features

- **Multi-language Support**: Processes data organized by language tabs
- **Flexible Pattern Matching**: Supports string containment, numeric comparisons (>, <, =), date comparisons, and boolean matching
- **Efficient Processing**: Pre-processes patterns for optimal performance
- **Error Handling**: Graceful error handling with comprehensive logging
- **Column Tracking**: Maintains column mapping for organized output
- **Excel Output**: Saves results in organized Excel files by pattern and language

## Installation

1. Ensure you have Python 3.8+ installed
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Basic Usage

```python
from analyzer import Analyzer
from data_reader import DataReader
from pattern_reader import PatternReader

# Initialize components
data_reader = DataReader("data/input")
pattern_reader = PatternReader("data/patterns")
analyzer = Analyzer("data/log")

# Load data and patterns
data = data_reader.read_all_files()
patterns = pattern_reader.read_patterns()

# Apply patterns
results = analyzer.apply_patterns(data, patterns)

# Save results
analyzer.save_results("data/output")

# Get summary
analyzer.print_summary()
```

### Running the Application

```bash
# Run the main application
python src/main.py

# Run tests
python test_analyzer.py
```

## Pattern Format

Patterns are defined in JSON files with the following structure:

```json
{
    "name": "Pattern Name",
    "pattern": {
        "Column Name": ["value1", "value2"],
        "Numeric Column": [">1000", "<10000"],
        "Date Column": [">2024-01-01", "<2024-12-31"],
        "Boolean Column": [true, false]
    }
}
```

### Pattern Types

#### String Fields
- **Matching**: Uses substring containment (case-insensitive)
- **Example**: `"texto": ["vamos alonso", "hello world"]`
- **Behavior**: Matches if any pattern value is contained in the data

#### Numeric Fields
- **Operators**: `>`, `<`, `=`
- **Example**: `"seguidores": [">1000", "<10000"]`
- **Behavior**: Matches if at least one condition is satisfied

#### Date Fields
- **Format**: `YYYY-MM-DD`
- **Operators**: `>`, `<`, `=`
- **Example**: `"fecha": [">2024-01-01", "<2024-12-31"]`
- **Behavior**: Matches if at least one condition is satisfied

#### Boolean Fields
- **Values**: `true`, `false`
- **Example**: `"verificado": [true, false]`
- **Behavior**: Exact match with boolean conversion

## Data Structure

The system expects data organized by language in Excel files:

```
data/input/
├── file1.xlsx
│   ├── es (Spanish tab)
│   ├── en (English tab)
│   └── fr (French tab)
└── file2.xlsx
    ├── es
    ├── en
    └── fr
```

## Output Structure

Results are saved in organized directories:

```
data/output/
├── Pattern1_20241201_143022/
│   ├── es_results.xlsx
│   ├── en_results.xlsx
│   └── fr_results.xlsx
└── Pattern2_20241201_143022/
    ├── es_results.xlsx
    └── en_results.xlsx
```

## Logging

The system provides comprehensive logging:

- **Location**: `data/log/`
- **Format**: `analyzer_YYYYMMDD_HHMMSS.log`
- **Level**: INFO and above
- **Content**: Pattern processing, matching results, errors, and warnings

## Error Handling

The system handles errors gracefully:

- **Data Type Errors**: Logs warnings and continues processing
- **Missing Columns**: Logs warnings and skips pattern
- **File I/O Errors**: Logs errors and continues with available data
- **Pattern Validation**: Logs validation failures

## Performance Features

- **Pattern Pre-processing**: Separates and optimizes different field types
- **Efficient Matching**: Uses optimized comparison methods
- **Memory Management**: Processes data in chunks when possible
- **Column Indexing**: Leverages pandas indexing for fast lookups

## API Reference

### Analyzer Class

#### Methods

- `apply_patterns(data, patterns)`: Apply patterns to data
- `get_results(pattern_name=None)`: Retrieve results
- `get_column_mapping(pattern_name=None)`: Get column organization
- `save_results(output_dir)`: Save results to files
- `get_summary()`: Get analysis summary
- `print_summary()`: Print summary to console

#### Properties

- `processed_patterns`: Pre-processed patterns for efficiency
- `results`: Pattern matching results
- `column_mapping`: Column organization tracking

### DataReader Class

- `read_all_files()`: Read all Excel files from input directory
- `get_language_data(language)`: Get data for specific language
- `get_all_data()`: Get all data organized by language
- `get_columns()`: Get column names
- `get_languages()`: Get available languages

### PatternReader Class

- `read_patterns()`: Load and validate all pattern files
- `get_pattern(pattern_name)`: Get specific pattern
- `get_all_pattern_names()`: Get list of pattern names
- `get_pattern_columns(pattern_name)`: Get columns for pattern

## Examples

### Custom Pattern Application

```python
# Create custom analyzer
analyzer = Analyzer()

# Apply specific patterns
custom_patterns = {
    "My Pattern": {
        "texto": ["keyword1", "keyword2"],
        "seguidores": [">5000"]
    }
}

# Apply to specific data
results = analyzer.apply_patterns(my_data, custom_patterns)

# Get results for specific pattern
pattern_results = analyzer.get_results("My Pattern")
```

### Batch Processing

```python
# Process multiple data sources
for data_source in data_sources:
    data = data_reader.read_from_source(data_source)
    results = analyzer.apply_patterns(data, patterns)
    analyzer.save_results(f"output/{data_source}")
```

## Troubleshooting

### Common Issues

1. **Column Mismatch**: Ensure data columns match pattern columns after normalization
2. **Date Format**: Use YYYY-MM-DD format for date comparisons
3. **Numeric Values**: Ensure numeric fields contain valid numbers or comparison operators
4. **File Permissions**: Check write permissions for log and output directories

### Debug Mode

Enable detailed logging by modifying the logging level in the Analyzer class:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Follow the existing code style
2. Add tests for new functionality
3. Update documentation for API changes
4. Ensure error handling is comprehensive

## License

This project is part of the Womter analysis system.
