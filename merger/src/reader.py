#!/usr/bin/env python3
"""
Data reader for the merger application.

This module efficiently reads all data files from the input directory,
loads them into memory, and removes duplicate rows while preserving
the first occurrence of each unique row. It also handles Excel files
with multiple language tabs and organizes data by language.
"""

import os
import pandas as pd
import glob
from typing import Dict, List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataReader:
    """Efficiently reads and processes data files from input directory."""
    
    def __init__(self, input_dir: str = "data/input"):
        """
        Initialize the DataReader.
        
        Args:
            input_dir (str): Path to the input directory containing data files
        """
        self.input_dir = input_dir
        self.data_frames: Dict[str, pd.DataFrame] = {}
        self.language_data: Dict[str, pd.DataFrame] = {}  # Data organized by language
        self.combined_data: Optional[pd.DataFrame] = None
        self.duplicate_stats: Dict[str, int] = {}
        self.file_columns: Dict[str, List[str]] = {}  # Store columns for each file
        self.language_columns: Dict[str, List[str]] = {}  # Store columns for each language
        
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions."""
        return ['.csv', '.xlsx', '.xls']
    
    def find_data_files(self) -> List[str]:
        """
        Find all data files in the input directory.
        
        Returns:
            List[str]: List of file paths
        """
        if not os.path.exists(self.input_dir):
            logger.warning(f"Input directory '{self.input_dir}' does not exist")
            return []
        
        files = []
        for ext in self.get_supported_extensions():
            pattern = os.path.join(self.input_dir, f"*{ext}")
            files.extend(glob.glob(pattern))
        
        logger.info(f"Found {len(files)} data files in {self.input_dir}")
        return sorted(files)
    
    def read_excel_with_languages(self, file_path: str) -> Dict[str, pd.DataFrame]:
        """
        Read Excel file with multiple language tabs.
        
        Args:
            file_path (str): Path to the Excel file
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary with language names as keys and DataFrames as values
        """
        try:
            # Read all sheets from Excel file
            excel_file = pd.ExcelFile(file_path)
            sheet_names = excel_file.sheet_names
            
            logger.info(f"Reading Excel file with {len(sheet_names)} language tabs: {sheet_names}")
            
            language_dfs = {}
            for sheet_name in sheet_names:
                try:
                    # Read each sheet (language)
                    df = pd.read_excel(file_path, sheet_name=sheet_name)
                    
                    if not df.empty:
                        # Add metadata columns
                        df['_source_file'] = os.path.basename(file_path)
                        df['_source_path'] = file_path
                        df['_language'] = sheet_name
                        df['_sheet_name'] = sheet_name
                        
                        # Store by language name
                        language_dfs[sheet_name] = df
                        
                        # Store column information for this language
                        self.language_columns[sheet_name] = list(df.columns)
                        
                        logger.info(f"  Language '{sheet_name}': {len(df)} rows, {len(df.columns)} columns")
                    else:
                        logger.warning(f"  Language '{sheet_name}' is empty, skipping")
                        
                except Exception as e:
                    logger.error(f"  Error reading language '{sheet_name}': {str(e)}")
                    continue
            
            return language_dfs
            
        except Exception as e:
            logger.error(f"Error reading Excel file {file_path}: {str(e)}")
            return {}
    
    def read_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        Read a single data file based on its extension.
        
        Args:
            file_path (str): Path to the file to read
            
        Returns:
            Optional[pd.DataFrame]: DataFrame if successful, None if failed
        """
        try:
            file_ext = os.path.splitext(file_path)[1].lower()
            file_name = os.path.basename(file_path)
            
            logger.info(f"Reading file: {file_name}")
            
            if file_ext in ['.xlsx', '.xls']:
                # Handle Excel files with language tabs
                language_dfs = self.read_excel_with_languages(file_path)
                
                if language_dfs:
                    # Store each language DataFrame separately
                    for language, df in language_dfs.items():
                        language_key = f"{file_name}_{language}"
                        self.data_frames[language_key] = df
                        
                        # Also store in language_data dictionary
                        if language not in self.language_data:
                            self.language_data[language] = df
                        else:
                            # Append to existing language data
                            self.language_data[language] = pd.concat(
                                [self.language_data[language], df], 
                                ignore_index=True, 
                                sort=False
                            )
                    
                    # Return the first language DataFrame for backward compatibility
                    first_language = list(language_dfs.keys())[0]
                    return language_dfs[first_language]
                else:
                    return None
                    
            elif file_ext == '.csv':
                # Try different encodings for CSV files
                for encoding in ['utf-8', 'latin-1', 'cp1252']:
                    try:
                        df = pd.read_csv(file_path, encoding=encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    logger.error(f"Could not read {file_name} with any encoding")
                    return None
                
                # Add source file information
                df['_source_file'] = file_name
                df['_source_path'] = file_path
                df['_language'] = 'unknown'  # CSV files don't have language tabs
                df['_sheet_name'] = 'N/A'
                
                # Store column information for this file
                self.file_columns[file_name] = list(df.columns)
                
                return df
                

                
            else:
                logger.warning(f"Unsupported file type: {file_ext}")
                return None
            
        except Exception as e:
            logger.error(f"Error reading {file_path}: {str(e)}")
            return None
    
    def load_all_data(self) -> bool:
        """
        Load all data files from the input directory.
        
        Returns:
            bool: True if successful, False otherwise
        """
        files = self.find_data_files()
        if not files:
            logger.error("No data files found to process")
            return False
        
        # Read all files
        for file_path in files:
            df = self.read_file(file_path)
            # Note: Excel files are handled specially in read_file method
        
        if not self.data_frames:
            logger.error("No valid data could be loaded")
            return False
        
        logger.info(f"Successfully loaded {len(self.data_frames)} data frames")
        logger.info(f"Data organized by {len(self.language_data)} languages: {list(self.language_data.keys())}")
        return True
    
    def combine_data(self) -> bool:
        """
        Combine all loaded data frames into a single DataFrame.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.data_frames:
            logger.error("No data frames to combine")
            return False
        
        try:
            # Combine all data frames
            dfs = list(self.data_frames.values())
            self.combined_data = pd.concat(dfs, ignore_index=True, sort=False)
            
            logger.info(f"Combined data: {len(self.combined_data)} total rows, {len(self.combined_data.columns)} columns")
            return True
            
        except Exception as e:
            logger.error(f"Error combining data: {str(e)}")
            return False
    
    def remove_duplicates(self, subset: Optional[List[str]] = None) -> bool:
        """
        Remove duplicate rows from combined data.
        
        Args:
            subset (Optional[List[str]]): Columns to consider for duplicate detection.
                                        If None, considers all columns except metadata columns.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if self.combined_data is None:
            logger.error("No combined data to process")
            return False
        
        try:
            initial_rows = len(self.combined_data)
            
            # Define metadata columns to exclude from duplicate detection
            metadata_cols = ['_source_file', '_source_path', '_language', '_sheet_name']
            
            # Determine which columns to use for duplicate detection
            if subset is None:
                # Use all columns except metadata columns
                subset = [col for col in self.combined_data.columns if col not in metadata_cols]
            
            # Remove duplicates, keeping first occurrence
            self.combined_data = self.combined_data.drop_duplicates(
                subset=subset,
                keep='first'
            )
            
            final_rows = len(self.combined_data)
            duplicates_removed = initial_rows - final_rows
            
            self.duplicate_stats = {
                'initial_rows': initial_rows,
                'final_rows': final_rows,
                'duplicates_removed': duplicates_removed
            }
            
            logger.info(f"Duplicate removal complete:")
            logger.info(f"  Initial rows: {initial_rows}")
            logger.info(f"  Final rows: {final_rows}")
            logger.info(f"  Duplicates removed: {duplicates_removed}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error removing duplicates: {str(e)}")
            return False
    
    def get_language_data(self, language: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Get data organized by language.
        
        Args:
            language (Optional[str]): Specific language to return. If None, returns all languages.
        
        Returns:
            Dict[str, pd.DataFrame]: Language data dictionary
        """
        if language:
            return {language: self.language_data.get(language, pd.DataFrame())}
        return self.language_data.copy()
    
    def get_data_summary(self) -> Dict:
        """
        Get a summary of the loaded and processed data.
        
        Returns:
            Dict: Summary information
        """
        summary = {
            'files_loaded': len(self.data_frames),
            'file_names': list(self.data_frames.keys()),
            'languages_found': list(self.language_data.keys()),
            'language_data_counts': {lang: len(df) for lang, df in self.language_data.items()},
            'duplicate_stats': self.duplicate_stats.copy() if self.duplicate_stats else {},
            'file_columns': self.file_columns.copy(),
            'language_columns': self.language_columns.copy(),
        }
        
        if self.combined_data is not None:
            summary.update({
                'total_rows': len(self.combined_data),
                'total_columns': len(self.combined_data.columns),
                'column_names': list(self.combined_data.columns),
                'memory_usage_mb': self.combined_data.memory_usage(deep=True).sum() / 1024 / 1024
            })
        
        return summary
    
    def get_combined_data(self) -> Optional[pd.DataFrame]:
        """
        Get the combined and deduplicated data.
        
        Returns:
            Optional[pd.DataFrame]: Combined data if available, None otherwise
        """
        return self.combined_data.copy() if self.combined_data is not None else None
    
    def get_column_structure(self) -> Dict[str, List[str]]:
        """
        Get the column structure for all files and languages.
        This information can be used by the writer to format new Excel files.
        
        Returns:
            Dict[str, List[str]]: Dictionary with file/language names as keys and column lists as values
        """
        column_structure = {}
        
        # Add file-level columns
        column_structure.update(self.file_columns)
        
        # Add language-level columns
        column_structure.update(self.language_columns)
        
        return column_structure
    
    def get_original_columns(self, exclude_metadata: bool = True) -> List[str]:
        """
        Get the original columns from the source files, excluding metadata columns.
        
        Args:
            exclude_metadata (bool): Whether to exclude metadata columns
            
        Returns:
            List[str]: List of original column names
        """
        if self.combined_data is None:
            return []
        
        metadata_cols = ['_source_file', '_source_path', '_language', '_sheet_name']
        
        if exclude_metadata:
            return [col for col in self.combined_data.columns if col not in metadata_cols]
        else:
            return list(self.combined_data.columns)
    
    def process_all_data(self, subset: Optional[List[str]] = None) -> bool:
        """
        Complete data processing pipeline: load, combine, and deduplicate.
        
        Args:
            subset (Optional[List[str]]): Columns to consider for duplicate detection.
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Starting data processing pipeline...")
        
        # Step 1: Load all data files
        if not self.load_all_data():
            return False
        
        # Step 2: Combine all data
        if not self.combine_data():
            return False
        
        # Step 3: Remove duplicates
        if not self.remove_duplicates(subset):
            return False
        
        logger.info("Data processing pipeline completed successfully")
        return True