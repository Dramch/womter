"""
Excel file reader module.

This module provides functionality to read and display Excel file contents.
"""

import os
import pandas as pd
from dotenv import load_dotenv
from .pattern_matcher import PatternMatcher


class ExcelReader:
    """A class to read and display Excel file contents."""
    
    def __init__(self, file_path: str = None):
        """
        Initialize the Excel reader.
        
        Args:
            file_path: Path to the Excel file. If None, will try to load from .env
        """
        self.file_path = file_path
        if not self.file_path:
            self._load_from_env()
    
    def _load_from_env(self):
        """Load Excel file path from environment variables."""
        load_dotenv()
        self.file_path = os.getenv('EXCEL_FILE_PATH')
        
        if not self.file_path:
            raise ValueError(
                "EXCEL_FILE_PATH not found in environment variables. "
                "Please create a .env file with EXCEL_FILE_PATH=path/to/your/file.xlsx"
            )
    
    def validate_file(self) -> bool:
        """
        Validate that the Excel file exists.
        
        Returns:
            True if file exists, False otherwise
        """
        if not os.path.exists(self.file_path):
            print(f"Error: File not found at {self.file_path}")
            print("Please check the path in your .env file")
            return False
        return True
    
    def read_and_display(self, use_patterns: bool = True):
        """
        Read and display the contents of the Excel file.
        
        Args:
            use_patterns: Whether to apply pattern matching and show only matching rows
        """
        if not self.validate_file():
            return
        
        try:
            print(f"Reading Excel file: {self.file_path}")
            print("-" * 50)
            
            # Read all sheets
            excel_file = pd.ExcelFile(self.file_path)
            
            for sheet_name in excel_file.sheet_names:
                self._display_sheet(sheet_name, use_patterns)
                
        except Exception as e:
            print(f"Error reading Excel file: {e}")
    
    def _display_sheet(self, sheet_name: str, use_patterns: bool = True):
        """
        Display contents of a specific sheet.
        
        Args:
            sheet_name: Name of the sheet to display
            use_patterns: Whether to apply pattern matching
        """
        print(f"\nSheet: {sheet_name}")
        print("=" * 30)
        
        # Read the sheet
        df = pd.read_excel(self.file_path, sheet_name=sheet_name)
        
        # Print basic info
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        if use_patterns:
            # Apply pattern matching
            matcher = PatternMatcher()
            filtered_df, row_matches = matcher.match_patterns(df)
            
            if not filtered_df.empty:
                matcher.display_matches(filtered_df, row_matches, df)
                matcher.save_matches_to_excel(filtered_df, row_matches)
            else:
                print("\nNo rows match the specified patterns.")
                print("Showing all data instead:")
                print("\nAll rows:")
                print(df)
        else:
            # Show all data
            print("\nAll rows:")
            print(df)
        
        # Print data types
        print(f"\nData types:")
        print(df.dtypes)
        
        print("\n" + "-" * 50)


def read_excel_file(file_path: str = None, use_patterns: bool = True):
    """
    Convenience function to read and display Excel file contents.
    
    Args:
        file_path: Path to the Excel file. If None, will try to load from .env
        use_patterns: Whether to apply pattern matching and show only matching rows
    """
    reader = ExcelReader(file_path)
    reader.read_and_display(use_patterns) 