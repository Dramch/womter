import json
import os
import glob
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Tuple


class PatternReader:
    def __init__(self, patterns_dir: str = "data/patterns", examples_dir: str = "data/patterns/examples"):
        self.patterns_dir = Path(patterns_dir)
        self.examples_dir = Path(examples_dir)
        self.log_dir = Path("data/log")
        
        # Create directories if they don't exist
        if not self.patterns_dir.exists():
            self.patterns_dir.mkdir(parents=True, exist_ok=True)
        if not self.examples_dir.exists():
            self.examples_dir.mkdir(parents=True, exist_ok=True)
        if not self.log_dir.exists():
            self.log_dir.mkdir(parents=True, exist_ok=True)
            
        self.template_path = self.examples_dir / "template.json"
        
        # Store all patterns in an easy-to-use format
        self.patterns: Dict[str, Dict[str, List]] = {}
        
        # Load template for validation
        self.template = self._load_template()
    
    def _normalize_column_name(self, column_name: str) -> str:
        """
        Normalize column name by removing accents and converting to lowercase.
        Same approach as in data_reader.py
        
        Args:
            column_name (str): Original column name
            
        Returns:
            str: Normalized column name (tideless and lowercase)
        """
        # Remove accents and convert to lowercase
        normalized = unicodedata.normalize('NFD', str(column_name))
        normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
        return normalized.lower()
    
    def _load_template(self) -> Dict[str, Any]:
        """Load the template JSON for validation."""
        try:
            with open(self.template_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load template from {self.template_path}: {e}")
            return {}
    
    def _validate_pattern(self, pattern_data: Dict[str, Any], filename: str) -> Tuple[bool, List[str]]:
        """Validate a pattern JSON against basic structure requirements."""
        errors = []
        
        # Check if required top-level keys exist
        if "name" not in pattern_data:
            errors.append("Missing 'name' field")
        
        if "pattern" not in pattern_data:
            errors.append("Missing 'pattern' field")
            return False, errors
        
        # Check if pattern is a dictionary
        if not isinstance(pattern_data["pattern"], dict):
            errors.append("'pattern' field must be a dictionary")
            return False, errors
        
        # Check if all pattern values are lists
        for field, value in pattern_data["pattern"].items():
            if not isinstance(value, list):
                errors.append(f"Field '{field}' must be a list, got {type(value).__name__}")
        
        return len(errors) == 0, errors
    
    def _get_pattern_files(self) -> List[str]:
        """Get all JSON files from patterns directory, excluding examples."""
        pattern_files = []
        
        # Get all .json files in patterns directory
        json_files = list(self.patterns_dir.glob("*.json"))
        
        for file_path in json_files:
            # Skip files in examples directory
            if self.examples_dir not in file_path.parents:
                pattern_files.append(str(file_path))
        
        return pattern_files
    
    def _normalize_pattern_columns(self, pattern_data: Dict[str, Any]) -> Dict[str, List]:
        """
        Normalize pattern columns by converting keys to lowercase and removing accents.
        Returns a dictionary with normalized column names as keys.
        
        Args:
            pattern_data (Dict[str, Any]): Original pattern data
            
        Returns:
            Dict[str, List]: Pattern with normalized column names
        """
        normalized_pattern = {}
        
        if "pattern" in pattern_data:
            for column_name, values in pattern_data["pattern"].items():
                normalized_column = self._normalize_column_name(column_name)
                normalized_pattern[normalized_column] = values
        
        return normalized_pattern
    
    def read_patterns(self) -> Dict[str, Dict[str, List]]:
        """
        Read all valid pattern JSONs and return a dictionary with pattern names as keys.
        Each pattern value contains normalized column names (lowercase, no accents).
        
        Returns:
            Dict[str, Dict[str, List]]: Dictionary with pattern names as keys and 
                                       normalized column patterns as values
        """
        self.patterns = {}
        validation_results = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        pattern_files = self._get_pattern_files()
        
        for file_path in pattern_files:
            filename = os.path.basename(file_path)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    pattern_data = json.load(f)
                
                # Validate the pattern
                is_valid, errors = self._validate_pattern(pattern_data, filename)
                
                if is_valid:
                    # Extract pattern name (use filename without extension as fallback)
                    pattern_name = pattern_data.get("name", filename.replace(".json", ""))
                    
                    # Normalize the pattern columns and store
                    normalized_pattern = self._normalize_pattern_columns(pattern_data)
                    self.patterns[pattern_name] = normalized_pattern
                    
                    validation_results.append(f"✓ {filename}: Valid pattern '{pattern_name}' with {len(normalized_pattern)} columns")
                else:
                    validation_results.append(f"✗ {filename}: Invalid - {', '.join(errors)}")
                    
            except json.JSONDecodeError as e:
                validation_results.append(f"✗ {filename}: Invalid JSON format - {str(e)}")
            except Exception as e:
                validation_results.append(f"✗ {filename}: Error reading file - {str(e)}")
        
        # Log validation results
        self._log_validation_results(validation_results, timestamp, len(self.patterns), len(pattern_files))
        
        return self.patterns
    
    def get_pattern(self, pattern_name: str) -> Dict[str, List]:
        """
        Get a specific pattern by name.
        
        Args:
            pattern_name (str): Name of the pattern to retrieve
            
        Returns:
            Dict[str, List]: Pattern with normalized column names, or empty dict if not found
        """
        return self.patterns.get(pattern_name, {})
    
    def get_all_pattern_names(self) -> List[str]:
        """
        Get list of all available pattern names.
        
        Returns:
            List[str]: List of pattern names
        """
        return list(self.patterns.keys())
    
    def get_pattern_columns(self, pattern_name: str) -> List[str]:
        """
        Get the normalized column names for a specific pattern.
        
        Args:
            pattern_name (str): Name of the pattern
            
        Returns:
            List[str]: List of normalized column names
        """
        pattern = self.get_pattern(pattern_name)
        return list(pattern.keys()) if pattern else []
    
    def _log_validation_results(self, results: List[str], timestamp: str, valid_count: int, total_count: int):
        """Log validation results to file."""
        log_filename = f"analysis_{timestamp}.log"
        log_path = self.log_dir / log_filename
        
        try:
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(f"Pattern Analysis Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 60 + "\n\n")
                f.write(f"Total files processed: {total_count}\n")
                f.write(f"Valid patterns: {valid_count}\n")
                f.write(f"Invalid patterns: {total_count - valid_count}\n\n")
                f.write("Detailed Results:\n")
                f.write("-" * 30 + "\n")
                
                for result in results:
                    f.write(f"{result}\n")
                
                f.write(f"\nLog written to: {log_path}\n")
            
            print(f"Validation results logged to: {log_path}")
            
        except Exception as e:
            print(f"Warning: Could not write to log file {log_path}: {e}")


def main():
    """Example usage of PatternReader."""
    reader = PatternReader()
    patterns = reader.read_patterns()
    
    print(f"\nSuccessfully loaded {len(patterns)} valid patterns:")
    for name, pattern_data in patterns.items():
        print(f"  - {name}: {len(pattern_data)} columns")
        # Show first few columns as example
        columns = list(pattern_data.keys())[:5]
        print(f"    Columns: {', '.join(columns)}...")
    
    # Demonstrate easy access to patterns
    if patterns:
        first_pattern_name = list(patterns.keys())[0]
        print(f"\nExample - accessing pattern '{first_pattern_name}':")
        pattern = reader.get_pattern(first_pattern_name)
        print(f"Columns: {list(pattern.keys())}")
    
    return patterns


if __name__ == "__main__":
    main()
