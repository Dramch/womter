import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Union
import logging


class Writter:
    """
    A class to write analysis results to Excel files.
    Creates one tab per pattern with all matching rows across languages.
    """
    
    def __init__(self, log_dir: str = "data/log"):
        """
        Initialize the Writter.
        
        Args:
            log_dir (str): Directory for log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Setup logging configuration."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"writter_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Writter initialized. Log file: {log_file}")
    
    def write_analysis_results(self, 
                             analyzer_results: Dict[str, Dict[str, pd.DataFrame]], 
                             original_patterns: Dict[str, Dict[str, List]], 
                             output_dir: str = "data/output") -> str:
        """
        Write analysis results to an Excel file with one tab per pattern.
        
        Args:
            analyzer_results (Dict[str, Dict[str, pd.DataFrame]]): Results from analyzer organized by pattern and language
            original_patterns (Dict[str, Dict[str, List]]): Original patterns with column names
            output_dir (str): Directory to save the Excel file
            
        Returns:
            str: Path to the created Excel file
        """
        self.logger.info("Starting to write analysis results to Excel...")
        
        # Create output directory only if it doesn't exist
        output_path = Path(output_dir)
        if not output_path.exists():
            output_path.mkdir(parents=True, exist_ok=True)
        
        # Generate timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"analysis_{timestamp}.xlsx"
        filepath = output_path / filename
        
        try:
            # Create Excel writer
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                self.logger.info(f"Creating Excel file: {filepath}")
                
                # Create and write summary sheet first
                self._create_summary_sheet(writer, analyzer_results)
                
                # Process each pattern
                for pattern_name, language_results in analyzer_results.items():
                    if not language_results:
                        self.logger.warning(f"No results found for pattern '{pattern_name}', skipping...")
                        continue
                    
                    self.logger.info(f"Processing pattern: {pattern_name}")
                    
                    # Get original column names for this pattern (not normalized)
                    if pattern_name in original_patterns:
                        original_columns = list(original_patterns[pattern_name].keys())
                    else:
                        self.logger.warning(f"Original pattern not found for '{pattern_name}', using data columns")
                        # Fallback: use columns from first language's data
                        first_language = next(iter(language_results))
                        original_columns = list(language_results[first_language].columns)
                    
                    # Combine all matching rows from all languages for this pattern
                    all_matching_rows = []
                    
                    for language, df in language_results.items():
                        if len(df) > 0:
                            self.logger.info(f"  Adding {len(df)} rows from language: {language}")
                            
                            # Add language identifier column if not present
                            if '_language' not in df.columns:
                                df_with_lang = df.copy()
                                df_with_lang['_language'] = language
                            else:
                                df_with_lang = df.copy()
                            
                            all_matching_rows.append(df_with_lang)
                    
                    if all_matching_rows:
                        # Combine all dataframes
                        combined_df = pd.concat(all_matching_rows, ignore_index=True)
                        
                        # Reorder columns to prioritize pattern columns, then add others
                        final_columns = []
                        
                        # Add pattern columns first (in original order)
                        for col in original_columns:
                            if col in combined_df.columns:
                                final_columns.append(col)
                        
                        # Add remaining columns that weren't in the pattern
                        for col in combined_df.columns:
                            if col not in final_columns:
                                final_columns.append(col)
                        
                        # Reorder the dataframe
                        final_df = combined_df[final_columns]
                        
                        # Write to Excel tab
                        sheet_name = self._sanitize_sheet_name(pattern_name)
                        final_df.to_excel(writer, sheet_name=sheet_name, index=False)
                        
                        # Auto-adjust column widths
                        self._adjust_column_widths(writer, sheet_name, final_df)
                    else:
                        pass
            
            return str(filepath)
            
        except Exception as e:
            raise
    
    def _create_summary_sheet(self, writer: pd.ExcelWriter, analyzer_results: Dict[str, Dict[str, pd.DataFrame]]) -> None:
        """
        Create and write the summary sheet as the first tab.
        
        Args:
            writer (pd.ExcelWriter): Excel writer object
            analyzer_results (Dict[str, Dict[str, pd.DataFrame]]): Results from analyzer
        """
        try:
    
            
            # Create summary data
            summary_data = []
            
            for pattern_name, language_results in analyzer_results.items():
                total_rows = 0
                language_counts = {}
                
                for language, df in language_results.items():
                    row_count = len(df)
                    total_rows += row_count
                    language_counts[language] = row_count
                
                summary_data.append({
                    'Pattern Name': pattern_name,
                    'Total Matches': total_rows,
                    'Languages': ', '.join(language_counts.keys()) if language_counts else 'None',
                    'Rows by Language': str(language_counts) if language_counts else 'No matches'
                })
            
            # Create summary dataframe
            summary_df = pd.DataFrame(summary_data)
            
            # Write summary sheet first (this will be the first tab)
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            
            # Auto-adjust column widths for summary
            self._adjust_column_widths(writer, 'Summary', summary_df)
            
            
        except Exception as e:
            pass
    
    def _sanitize_sheet_name(self, name: str) -> str:
        """
        Sanitize sheet name to comply with Excel naming restrictions.
        Excel sheet names cannot exceed 31 characters and cannot contain certain characters.
        
        Args:
            name (str): Original sheet name
            
        Returns:
            str: Sanitized sheet name
        """
        # Remove or replace invalid characters
        invalid_chars = ['\\', '/', '*', '?', ':', '[', ']']
        sanitized = name
        
        for char in invalid_chars:
            sanitized = sanitized.replace(char, '_')
        
        # Truncate if too long (Excel limit is 31 characters)
        if len(sanitized) > 31:
            sanitized = sanitized[:28] + "..."
        
        return sanitized
    
    def _adjust_column_widths(self, writer: pd.ExcelWriter, sheet_name: str, df: pd.DataFrame) -> None:
        """
        Auto-adjust column widths for better readability.
        
        Args:
            writer (pd.ExcelWriter): Excel writer object
            sheet_name (str): Name of the sheet
            df (pd.DataFrame): Dataframe to adjust columns for
        """
        try:
            # Get the worksheet
            worksheet = writer.sheets[sheet_name]
            
            # Calculate optimal width for each column
            for idx, col in enumerate(df.columns):
                # Get maximum length of column header and data
                max_length = len(str(col))
                
                # Check data lengths (sample first 100 rows to avoid performance issues)
                sample_data = df[col].head(100).astype(str)
                if len(sample_data) > 0:
                    max_data_length = sample_data.str.len().max()
                    max_length = max(max_length, max_data_length)
                
                # Add some padding and set reasonable limits
                optimal_width = min(max(max_length + 2, 10), 50)
                
                # Set column width (Excel column width is approximately 0.7 * character width)
                worksheet.column_dimensions[chr(65 + idx)].width = optimal_width
                
        except Exception as e:
            pass
