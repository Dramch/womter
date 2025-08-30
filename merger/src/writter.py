#!/usr/bin/env python3
"""
Data writer for the merger application.

This module writes data from a dictionary to an XLSX file with language-specific tabs
and an "all" tab containing all the data. It preserves the original column order
and handles Excel file creation efficiently.
"""

import os
import pandas as pd
from typing import Dict, List, Optional
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DataWriter:
    """Writes data to Excel files with language-specific tabs."""
    
    def __init__(self, output_dir: str = "data/output"):
        """
        Initialize the DataWriter.
        
        Args:
            output_dir (str): Path to the output directory for generated files
        """
        self.output_dir = output_dir
        self.ensure_output_dir()
        
    def ensure_output_dir(self):
        """Create output directory if it doesn't exist."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            logger.info(f"Created output directory: {self.output_dir}")
    
    def get_column_order(self, language_data: Dict[str, pd.DataFrame]) -> List[str]:
        """
        Determine the column order based on the first language DataFrame.
        This ensures consistent column ordering across all tabs.
        
        Args:
            language_data (Dict[str, pd.DataFrame]): Dictionary with language DataFrames
            
        Returns:
            List[str]: Ordered list of column names
        """
        if not language_data:
            return []
        
        # Get the first language DataFrame to determine column order
        first_language = list(language_data.keys())[0]
        first_df = language_data[first_language]
        
        # Filter out metadata columns and get original columns
        metadata_cols = ['_source_file', '_source_path', '_language', '_sheet_name']
        original_cols = [col for col in first_df.columns if col not in metadata_cols]
        
        # Add metadata columns at the end
        ordered_cols = original_cols + metadata_cols
        
        logger.info(f"Column order determined: {len(ordered_cols)} columns")
        return ordered_cols
    
    def prepare_dataframe_for_writing(self, df: pd.DataFrame, column_order: List[str]) -> pd.DataFrame:
        """
        Prepare a DataFrame for writing by reordering columns and handling missing columns.
        
        Args:
            df (pd.DataFrame): Input DataFrame
            column_order (List[str]): Desired column order
            
        Returns:
            pd.DataFrame: Prepared DataFrame with correct column order
        """
        # Create a copy to avoid modifying the original
        prepared_df = df.copy()
        
        # Add missing columns with empty values if they don't exist
        for col in column_order:
            if col not in prepared_df.columns:
                prepared_df[col] = ''
                logger.debug(f"Added missing column '{col}' with empty values")
        
        # Reorder columns according to the specified order
        # Only include columns that exist in the DataFrame
        existing_cols = [col for col in column_order if col in prepared_df.columns]
        prepared_df = prepared_df[existing_cols]
        
        return prepared_df
    
    def write_to_excel(self, 
                      language_data: Dict[str, pd.DataFrame], 
                      filename: Optional[str] = None,
                      include_all_tab: bool = True) -> str:
        """
        Write data to an XLSX file with language-specific tabs and optional "all" tab.
        
        Args:
            language_data (Dict[str, pd.DataFrame]): Dictionary with language names as keys and DataFrames as values
            filename (Optional[str]): Output filename. If None, generates a timestamped name
            include_all_tab (bool): Whether to include an "all" tab with all data
            
        Returns:
            str: Path to the created file
        """
        if not language_data:
            logger.error("No language data provided for writing")
            return ""
        
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"merged_data_{timestamp}.xlsx"
        
        # Ensure .xlsx extension
        if not filename.endswith('.xlsx'):
            filename = filename.replace('.xlsm', '.xlsx').replace('.xls', '.xlsx')
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
        
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            # Determine column order
            column_order = self.get_column_order(language_data)
            if not column_order:
                logger.error("Could not determine column order")
                return ""
            
            # Create ExcelWriter with XLSX format
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                
                # Write each language to its own tab
                for language, df in language_data.items():
                    if df.empty:
                        logger.warning(f"Language '{language}' has no data, skipping tab")
                        continue
                    
                    # Prepare DataFrame for writing
                    prepared_df = self.prepare_dataframe_for_writing(df, column_order)
                    
                    # Write to Excel tab
                    sheet_name = self._sanitize_sheet_name(language)
                    prepared_df.to_excel(writer, sheet_name=sheet_name, index=False)
                    
                    logger.info(f"Written language '{language}' to tab '{sheet_name}': {len(prepared_df)} rows")
                
                # Write "all" tab if requested
                if include_all_tab:
                    self._write_all_tab(writer, language_data, column_order)
                
            logger.info(f"Successfully created XLSX file: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error writing to Excel file: {str(e)}")
            return ""
    
    def _write_all_tab(self, writer: pd.ExcelWriter, 
                       language_data: Dict[str, pd.DataFrame], 
                       column_order: List[str]):
        """
        Write the "all" tab containing all data combined.
        
        Args:
            writer (pd.ExcelWriter): Excel writer object
            language_data (Dict[str, pd.DataFrame]): Dictionary with language DataFrames
            column_order (List[str]): Desired column order
        """
        try:
            # Combine all language DataFrames
            all_dfs = []
            for language, df in language_data.items():
                if not df.empty:
                    # Add language column if not present
                    if '_language' not in df.columns:
                        df = df.copy()
                        df['_language'] = language
                    all_dfs.append(df)
            
            if all_dfs:
                # Concatenate all DataFrames
                combined_df = pd.concat(all_dfs, ignore_index=True, sort=False)
                
                # Prepare combined DataFrame for writing
                prepared_combined_df = self.prepare_dataframe_for_writing(combined_df, column_order)
                
                # Write to "all" tab
                prepared_combined_df.to_excel(writer, sheet_name='all', index=False)
                
                logger.info(f"Written 'all' tab: {len(prepared_combined_df)} total rows")
            else:
                logger.warning("No data available for 'all' tab")
                
        except Exception as e:
            logger.error(f"Error writing 'all' tab: {str(e)}")
    
    def _sanitize_sheet_name(self, sheet_name: str) -> str:
        """
        Sanitize sheet name to comply with Excel naming restrictions.
        
        Args:
            sheet_name (str): Original sheet name
            
        Returns:
            str: Sanitized sheet name
        """
        # Excel sheet names cannot exceed 31 characters
        if len(sheet_name) > 31:
            sheet_name = sheet_name[:31]
        
        # Remove invalid characters
        invalid_chars = ['\\', '/', '*', '?', ':', '[', ']']
        for char in invalid_chars:
            sheet_name = sheet_name.replace(char, '_')
        
        return sheet_name
    
    def write_from_reader_data(self, reader_data: Dict, filename: Optional[str] = None) -> str:
        """
        Convenience method to write data directly from reader output.
        
        Args:
            reader_data (Dict): Dictionary containing language_data and combined_data
            filename (Optional[str]): Output filename
            
        Returns:
            str: Path to the created file
        """
        if 'language_data' not in reader_data:
            logger.error("Reader data must contain 'language_data' key")
            return ""
        
        language_data = reader_data['language_data']
        
        # Check if we should include combined data in the "all" tab
        include_all_tab = 'combined_data' in reader_data and reader_data['combined_data'] is not None
        
        return self.write_to_excel(language_data, filename, include_all_tab)
    
    def get_output_info(self) -> Dict:
        """
        Get information about the output directory and writer configuration.
        
        Returns:
            Dict: Output information
        """
        return {
            'output_directory': self.output_dir,
            'output_directory_exists': os.path.exists(self.output_dir),
            'output_directory_writable': os.access(self.output_dir, os.W_OK) if os.path.exists(self.output_dir) else False
        }


def write_data_to_excel(language_data: Dict[str, pd.DataFrame], 
                       output_path: str,
                       include_all_tab: bool = True) -> bool:
    """
    Convenience function to quickly write data to Excel.
    
    Args:
        language_data (Dict[str, pd.DataFrame]): Dictionary with language DataFrames
        output_path (str): Full path for the output file
        include_all_tab (bool): Whether to include an "all" tab
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Extract directory and filename from output_path
        output_dir = os.path.dirname(output_path)
        filename = os.path.basename(output_path)
        
        # Create writer with specified output directory
        writer = DataWriter(output_dir if output_dir else ".")
        
        # Write the file
        result_path = writer.write_to_excel(language_data, filename, include_all_tab)
        
        return bool(result_path)
        
    except Exception as e:
        logger.error(f"Error in write_data_to_excel: {str(e)}")
        return False
