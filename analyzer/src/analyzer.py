import pandas as pd
import re
import unicodedata
from datetime import datetime
from typing import Dict, List, Any, Tuple, Union
from pathlib import Path
import logging
import os


class Analyzer:
    """
    A class to apply patterns to data dictionaries organized by language.
    Processes patterns efficiently and handles errors gracefully.
    """
    
    def __init__(self, log_dir: str = "data/log"):
        """
        Initialize the Analyzer.
        
        Args:
            log_dir (str): Directory for log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        # Store processed patterns for efficiency
        self.processed_patterns: Dict[str, Dict[str, Any]] = {}
        
        # Store results by pattern name
        self.results: Dict[str, Dict[str, pd.DataFrame]] = {}
        
        # Track which data goes in each column for saving later
        self.column_mapping: Dict[str, List[str]] = {}
    
    def _setup_logging(self):
        """Setup logging configuration."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"analyzer_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Analyzer initialized. Log file: {log_file}")
    
    def _normalize_text_for_comparison(self, text: str) -> str:
        """
        Normalize text for accent and case-insensitive comparison.
        Handles Greco-Roman languages (Spanish, English, French, German, etc.) by:
        - Removing accents and diacritics
        - Converting to lowercase
        - Normalizing unicode characters
        - Removing common symbols like periods, commas, etc.
        
        Args:
            text (str): Text to normalize
            
        Returns:
            str: Normalized text ready for comparison
        """
        if not text:
            return ""
        
        # Convert to string if not already
        text_str = str(text)
        
        # Strip leading and trailing whitespace
        text_str = text_str.strip()
        
        # Normalize unicode characters (NFD decomposes characters with diacritics)
        normalized = unicodedata.normalize('NFD', text_str)
        
        # Remove combining characters (accents, diacritics, etc.)
        # This removes characters like combining acute accent (U+0301)
        cleaned = ''.join(char for char in normalized if not unicodedata.combining(char))
        
        # Remove common symbols and punctuation
        # This removes periods, commas, exclamation marks, question marks, etc.
        cleaned = re.sub(r'[.,!?;:()\[\]{}"\'-]', '', cleaned)
        
        # Convert to lowercase for case-insensitive comparison
        result = cleaned.lower()
        
        return result
    
    def _clean_pattern_text(self, text: str) -> str:
        """
        Clean pattern text by stripping spaces and removing symbols.
        This is used specifically for cleaning pattern values before comparison.
        
        Args:
            text (str): Pattern text to clean
            
        Returns:
            str: Cleaned pattern text
        """
        if not text:
            return ""
        
        # Convert to string if not already
        text_str = str(text)
        
        # Strip leading and trailing whitespace
        text_str = text_str.strip()
        
        # Remove common symbols and punctuation
        # This removes periods, commas, exclamation marks, question marks, etc.
        cleaned = re.sub(r'[.,!?;:()\[\]{}"\'-]', '', text_str)
        
        return cleaned
    
    def _normalize_column_name(self, column_name: str) -> str:
        """
        Normalize column names for consistent matching.
        Converts to lowercase, removes extra spaces, and standardizes common variations.
        
        Args:
            column_name (str): Original column name
            
        Returns:
            str: Normalized column name
        """
        if not column_name:
            return ""
        
        # Convert to string and normalize
        col_str = str(column_name)
        
        # Convert to lowercase
        normalized = col_str.lower()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        # Standardize common variations
        column_mappings = {
            'tweet id': 'tweet_id',
            'tweet_id': 'tweet_id',
            'usuario nombre': 'usuario_nombre',
            'usuario genero': 'usuario_genero',
            'tipo de verificacion': 'tipo_de_verificacion',
            'public metrics dump': 'public_metrics_dump',
            'user dump': 'user_dump',
            'tweet dump': 'tweet_dump',
            'source file': '_source_file',
            'source path': '_source_path',
            'sheet name': '_sheet_name',
            'language': '_language'
        }
        
        # Apply standardizations
        for original, standard in column_mappings.items():
            if normalized == original:
                normalized = standard
                break
        
        return normalized
    
    def _process_patterns(self, patterns: Dict[str, Dict[str, List]]) -> None:
        """
        Pre-process patterns to make pattern application more efficient.
        Separates numeric and string patterns, pre-compiles regex for numbers.
        
        Args:
            patterns (Dict[str, Dict[str, List]]): Raw patterns from pattern reader
        """
        self.logger.info("Processing patterns for efficient matching...")
        
        for pattern_name, pattern_data in patterns.items():
            processed_pattern = {
                'string_fields': {},
                'numeric_fields': {},
                'date_fields': {},
                'boolean_fields': {},
                'original_pattern': pattern_data
            }
            
            for column_name, values in pattern_data.items():
                if not values:
                    continue
                    
                # Normalize column name for consistent matching
                normalized_column_name = self._normalize_column_name(column_name)
                
                # Check if this is a numeric field based on first value
                first_value = str(values[0])
                
                if self._is_date_field(first_value):
                    processed_pattern['date_fields'][normalized_column_name] = self._process_date_values(values)
                elif self._is_numeric_field(first_value):
                    processed_pattern['numeric_fields'][normalized_column_name] = self._process_numeric_values(values)
                elif self._is_boolean_field(values):
                    processed_pattern['boolean_fields'][normalized_column_name] = values
                else:
                    # Clean string pattern values by stripping spaces and removing symbols
                    cleaned_values = [self._clean_pattern_text(value) for value in values]
                    processed_pattern['string_fields'][normalized_column_name] = cleaned_values
            
            self.processed_patterns[pattern_name] = processed_pattern
            self.logger.info(f"Processed pattern '{pattern_name}': {len(processed_pattern['string_fields'])} string, "
                           f"{len(processed_pattern['numeric_fields'])} numeric, "
                           f"{len(processed_pattern['date_fields'])} date fields")
    
    def _is_numeric_field(self, value: str) -> bool:
        """Check if a field value indicates numeric comparison."""
        return bool(re.match(r'^[<>=]\d+', value))
    
    def _is_date_field(self, value: str) -> bool:
        """Check if a field value indicates date comparison."""
        return bool(re.match(r'^[<>=]\d{4}-\d{2}-\d{2}', value))
    
    def _is_boolean_field(self, values: List) -> bool:
        """Check if a field contains boolean values."""
        if not values:  # Empty list is not a boolean field
            return False
        return all(isinstance(v, bool) for v in values)
    
    def _process_numeric_values(self, values: List[str]) -> List[Dict[str, Union[str, float]]]:
        """
        Process numeric values to extract operator and value.
        
        Args:
            values (List[str]): List of numeric comparison strings like [">1000", "<10000"]
            
        Returns:
            List[Dict[str, Union[str, float]]]: List of processed numeric conditions
        """
        processed = []
        
        for value in values:
            try:
                # Extract operator and numeric value
                match = re.match(r'^([<>=])(.+)$', str(value))
                if match:
                    operator, num_str = match.groups()
                    num_value = float(num_str)
                    processed.append({
                        'operator': operator,
                        'value': num_value,
                        'original': value
                    })
                else:
                    # If no operator, treat as equality
                    num_value = float(value)
                    processed.append({
                        'operator': '=',
                        'value': num_value,
                        'original': value
                    })
            except (ValueError, TypeError) as e:
                self.logger.warning(f"Could not process numeric value '{value}': {e}")
                continue
        
        return processed
    
    def _process_date_values(self, values: List[str]) -> List[Dict[str, Union[str, datetime]]]:
        """
        Process date values to extract operator and date value.
        
        Args:
            values (List[str]): List of date comparison strings like [">2024-01-01"]
            
        Returns:
            List[Dict[str, Union[str, datetime]]]: List of processed date conditions
        """
        processed = []
        
        for value in values:
            try:
                # Extract operator and date value
                match = re.match(r'^([<>=])(.+)$', str(value))
                if match:
                    operator, date_str = match.groups()
                    date_value = datetime.strptime(date_str, '%Y-%m-%d')
                    processed.append({
                        'operator': operator,
                        'value': date_value,
                        'original': value
                    })
                else:
                    # If no operator, treat as equality
                    date_value = datetime.strptime(value, '%Y-%m-%d')
                    processed.append({
                        'operator': '=',
                        'value': date_value,
                        'original': value
                    })
            except (ValueError, TypeError) as e:
                self.logger.warning(f"Could not process date value '{value}': {e}")
                continue
        
        return processed
    
    def _check_string_condition(self, row_value: Any, pattern_values: List[str]) -> bool:
        """
        Check if a string field matches the pattern condition.
        Uses accent and case-insensitive comparison for Greco-Roman languages.
        Pattern values are already cleaned (stripped spaces and symbols removed).
        
        Args:
            row_value (Any): Value from the data row
            pattern_values (List[str]): List of already cleaned acceptable values
            
        Returns:
            bool: True if condition is met
        """
        if pd.isna(row_value):
            return False
            
        # Normalize row value for accent and case-insensitive comparison
        # This also strips spaces and removes symbols for consistency
        row_str = self._normalize_text_for_comparison(row_value)
        
        # Check if any pattern value matches the row value
        for pattern_value in pattern_values:
            # Pattern values are already cleaned, just normalize for comparison
            normalized_pattern = self._normalize_text_for_comparison(pattern_value)
            
            # More flexible matching: check if pattern is in row OR row is in pattern
            # This handles cases where the pattern might be a partial match
            if (normalized_pattern in row_str or 
                row_str in normalized_pattern or
                self._calculate_similarity(normalized_pattern, row_str) > 0.7):
                return True
        
        return False
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate a simple similarity score between two texts.
        Returns a value between 0 and 1, where 1 means identical.
        
        Args:
            text1 (str): First text
            text2 (str): Second text
            
        Returns:
            float: Similarity score (0-1)
        """
        if not text1 or not text2:
            return 0.0
        
        # Convert to sets of words for comparison
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        if union == 0:
            return 0.0
        
        return intersection / union
    
    def _check_numeric_condition(self, row_value: Any, pattern_conditions: List[Dict]) -> bool:
        """
        Check if a numeric field matches the pattern conditions.
        
        Args:
            row_value (Any): Value from the data row
            pattern_conditions (List[Dict]): List of processed numeric conditions
            
        Returns:
            bool: True if at least one condition is met
        """
        if pd.isna(row_value):
            return False
            
        try:
            row_num = float(row_value)
        except (ValueError, TypeError):
            return False
        
        # Check if at least one condition is met
        for condition in pattern_conditions:
            operator = condition['operator']
            pattern_value = condition['value']
            
            if operator == '=' and row_num == pattern_value:
                return True
            elif operator == '>' and row_num > pattern_value:
                return True
            elif operator == '<' and row_num < pattern_value:
                return True
        
        return False
    
    def _check_date_condition(self, row_value: Any, pattern_conditions: List[Dict]) -> bool:
        """
        Check if a date field matches the pattern conditions.
        
        Args:
            row_value (Any): Value from the data row
            pattern_conditions (List[Dict]): List of processed date conditions
            
        Returns:
            bool: True if at least one condition is met
        """
        if pd.isna(row_value):
            return False
            
        try:
            # Try to parse the row value as a date
            if isinstance(row_value, str):
                row_date = datetime.strptime(row_value, '%Y-%m-%d')
            elif isinstance(row_value, datetime):
                row_date = row_value
            else:
                return False
        except (ValueError, TypeError):
            return False
        
        # Check if at least one condition is met
        for condition in pattern_conditions:
            operator = condition['operator']
            pattern_value = condition['value']
            
            if operator == '=' and row_date == pattern_value:
                return True
            elif operator == '>' and row_date > pattern_value:
                return True
            elif operator == '<' and row_date < pattern_value:
                return True
        
        return False
    
    def _check_boolean_condition(self, row_value: Any, pattern_values: List[bool]) -> bool:
        """
        Check if a boolean field matches the pattern condition.
        
        Args:
            row_value (Any): Value from the data row
            pattern_values (List[bool]): List of acceptable boolean values
            
        Returns:
            bool: True if condition is met
        """
        if pd.isna(row_value):
            return False
            
        # Convert row value to boolean if possible
        if isinstance(row_value, bool):
            row_bool = row_value
        elif isinstance(row_value, str):
            row_bool = row_value.lower() in ['true', '1', 'yes', 'verdadero']
        elif isinstance(row_value, (int, float)):
            row_bool = bool(row_value)
        else:
            return False
        
        return row_bool in pattern_values
    
    def _check_row_matches_pattern(self, row: pd.Series, pattern_name: str) -> bool:
        """
        Check if a single row matches a specific pattern.
        A row matches a pattern when it matches at least one condition of EACH column described in the pattern.
        
        Args:
            row (pd.Series): Data row to check
            pattern_name (str): Name of the pattern to check against
            
        Returns:
            bool: True if row matches at least one condition of each column in the pattern
        """
        if pattern_name not in self.processed_patterns:
            return False
        
        pattern = self.processed_patterns[pattern_name]
        
        # Helper function to find column with case-insensitive matching
        def find_column_case_insensitive(column_name: str, row_index) -> str:
            """Find column name with case-insensitive matching."""
            normalized_pattern_col = self._normalize_column_name(column_name)
            
            for col in row_index:
                normalized_data_col = self._normalize_column_name(col)
                if normalized_data_col == normalized_pattern_col:
                    return col
            
            return None
        
        # Track which columns have been successfully matched
        matched_columns = set()
        total_columns = 0
        
        # Check string fields
        for column_name, pattern_values in pattern['string_fields'].items():
            total_columns += 1
            actual_column = find_column_case_insensitive(column_name, row.index)
            if actual_column is not None:
                if self._check_string_condition(row[actual_column], pattern_values):
                    matched_columns.add(column_name)
            else:
                self.logger.warning(f"Column '{column_name}' not found in data for pattern '{pattern_name}'. Available columns: {list(row.index)}")
                # If column not found, we can't match it, so return False
                return False
        
        # Check numeric fields
        for column_name, pattern_conditions in pattern['numeric_fields'].items():
            total_columns += 1
            actual_column = find_column_case_insensitive(column_name, row.index)
            if actual_column is not None:
                if self._check_numeric_condition(row[actual_column], pattern_conditions):
                    matched_columns.add(column_name)
            else:
                self.logger.warning(f"Column '{column_name}' not found in data for pattern '{pattern_name}'. Available columns: {list(row.index)}")
                # If column not found, we can't match it, so return False
                return False
        
        # Check date fields
        for column_name, pattern_conditions in pattern['date_fields'].items():
            total_columns += 1
            actual_column = find_column_case_insensitive(column_name, row.index)
            if actual_column is not None:
                if self._check_date_condition(row[actual_column], pattern_conditions):
                    matched_columns.add(column_name)
            else:
                self.logger.warning(f"Column '{column_name}' not found in data for pattern '{pattern_name}'. Available columns: {list(row.index)}")
                # If column not found, we can't match it, so return False
                return False
        
        # Check boolean fields
        for column_name, pattern_values in pattern['boolean_fields'].items():
            total_columns += 1
            actual_column = find_column_case_insensitive(column_name, row.index)
            if actual_column is not None:
                if self._check_boolean_condition(row[actual_column], pattern_values):
                    matched_columns.add(column_name)
            else:
                self.logger.warning(f"Column '{column_name}' not found in data for pattern '{pattern_name}'. Available columns: {list(row.index)}")
                # If column not found, we can't match it, so return False
                return False
        
        # Return True only if ALL columns have at least one condition matched
        return len(matched_columns) == total_columns
    
    def apply_patterns(self, data: Dict[str, pd.DataFrame], patterns: Dict[str, Dict[str, List]]) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Apply patterns to data organized by language.
        
        Args:
            data (Dict[str, pd.DataFrame]): Data organized by language
            patterns (Dict[str, Dict[str, List]]): Patterns to apply
            
        Returns:
            Dict[str, Dict[str, pd.DataFrame]]: Results organized by pattern name and language
        """
        self.logger.info("Starting pattern application...")
        
        # Process patterns for efficiency
        self._process_patterns(patterns)
        
        # Initialize results structure
        self.results = {pattern_name: {} for pattern_name in patterns.keys()}
        
        # Track column mapping for each pattern
        for pattern_name in patterns.keys():
            # Store normalized column names for consistent matching
            normalized_columns = []
            for col in patterns[pattern_name].keys():
                normalized_col = self._normalize_column_name(col)
                normalized_columns.append(normalized_col)
            self.column_mapping[pattern_name] = normalized_columns
        
        # Apply patterns to each language's data
        for language, df in data.items():
            self.logger.info(f"Processing language: {language} ({len(df)} rows)")
            
            for pattern_name in patterns.keys():
                self.logger.info(f"  Applying pattern: {pattern_name}")
                
                # Find matching rows
                matching_rows = []
                
                for idx, row in df.iterrows():
                    try:
                        if self._check_row_matches_pattern(row, pattern_name):
                            matching_rows.append(row)
                    except Exception as e:
                        self.logger.error(f"Error checking row {idx} against pattern '{pattern_name}': {e}")
                        continue
                
                # Store results
                if matching_rows:
                    result_df = pd.DataFrame(matching_rows)
                    self.results[pattern_name][language] = result_df
                    self.logger.info(f"    Found {len(matching_rows)} matching rows")
                else:
                    self.logger.info(f"    No matching rows found")
        
        self.logger.info("Pattern application completed")
        return self.results
    
    def get_results(self, pattern_name: str = None) -> Union[Dict[str, pd.DataFrame], Dict[str, Dict[str, pd.DataFrame]]]:
        """
        Get results for a specific pattern or all patterns.
        
        Args:
            pattern_name (str, optional): Specific pattern name. If None, returns all results.
            
        Returns:
            Union[Dict[str, pd.DataFrame], Dict[str, Dict[str, pd.DataFrame]]]: Results
        """
        if pattern_name:
            return self.results.get(pattern_name, {})
        return self.results
    
    def get_column_mapping(self, pattern_name: str = None) -> Union[List[str], Dict[str, List[str]]]:
        """
        Get column mapping for a specific pattern or all patterns.
        
        Args:
            pattern_name (str, optional): Specific pattern name. If None, returns all mappings.
            
        Returns:
            Union[List[str], Dict[str, List[str]]]: Column mapping
        """
        if pattern_name:
            return self.column_mapping.get(pattern_name, [])
        return self.column_mapping
    
    def save_results(self, output_dir: str = "data/output") -> None:
        """
        Save results to files organized by pattern and language.
        
        Args:
            output_dir (str): Directory to save results
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for pattern_name, language_results in self.results.items():
            if not language_results:
                continue
                
            # Create pattern directory
            pattern_dir = output_path / f"{pattern_name}_{timestamp}"
            pattern_dir.mkdir(exist_ok=True)
            
            # Save each language's results
            for language, df in language_results.items():
                if len(df) > 0:
                    filename = f"{language}_results.xlsx"
                    filepath = pattern_dir / filename
                    
                    try:
                        # Reorder columns according to pattern column mapping
                        if pattern_name in self.column_mapping:
                            pattern_columns = self.column_mapping[pattern_name]
                            # Add any missing columns that exist in the data
                            existing_columns = [col for col in pattern_columns if col in df.columns]
                            other_columns = [col for col in df.columns if col not in pattern_columns]
                            final_columns = existing_columns + other_columns
                            
                            df_reordered = df[final_columns]
                        else:
                            df_reordered = df
                        
                        df_reordered.to_excel(filepath, index=False)
                        self.logger.info(f"Saved {len(df)} rows to {filepath}")
                        
                    except Exception as e:
                        self.logger.error(f"Error saving results for {pattern_name}/{language}: {e}")
        
        self.logger.info(f"Results saved to {output_path}")
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the analysis results.
        Only includes languages that are actually being searched based on the patterns.
        
        Returns:
            Dict[str, Any]: Summary information
        """
        summary = {
            "total_patterns": len(self.results),
            "patterns_processed": list(self.processed_patterns.keys()),
            "results_by_pattern": {},
            "total_matching_rows": 0,
            "languages_searched": set()  # Track unique languages being searched
        }
        
        for pattern_name, language_results in self.results.items():
            pattern_summary = {
                "languages": list(language_results.keys()),
                "total_rows": 0,
                "rows_by_language": {}
            }
            
            for language, df in language_results.items():
                row_count = len(df)
                pattern_summary["rows_by_language"][language] = row_count
                pattern_summary["total_rows"] += row_count
                summary["total_matching_rows"] += row_count
                # Add to set of languages being searched
                summary["languages_searched"].add(language)
            
            summary["results_by_pattern"][pattern_name] = pattern_summary
        
        # Convert set to list for JSON serialization
        summary["languages_searched"] = list(summary["languages_searched"])
        
        return summary
    
    def print_summary(self) -> None:
        """Print a summary of the analysis results to the console."""
        summary = self.get_summary()
        
        print("\n" + "="*60)
        print("PATTERN ANALYSIS SUMMARY")
        print("="*60)
        print(f"Total patterns processed: {summary['total_patterns']}")
        print(f"Languages being searched: {', '.join(summary['languages_searched'])}")
        print(f"Total matching rows found: {summary['total_matching_rows']:,}")
        
        for pattern_name, pattern_summary in summary["results_by_pattern"].items():
            print(f"\n--- {pattern_name.upper()} ---")
            print(f"Total rows: {pattern_summary['total_rows']:,}")
            print("Rows by language:")
            for language, count in pattern_summary["rows_by_language"].items():
                print(f"  {language}: {count:,} rows")
        
        print("="*60)
