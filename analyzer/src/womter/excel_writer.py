"""
Excel writer module for saving pattern matching results to Excel files.
"""

import os
import json
import pandas as pd
from typing import Dict, List, Optional
from dotenv import load_dotenv


class ExcelWriter:
    """A class to handle writing pattern matching results to Excel files."""
    
    def __init__(self, output_filename: Optional[str] = None):
        """
        Initialize the Excel writer.
        
        Args:
            output_filename: Desired output file name (from .env if not provided)
        """
        self.output_filename = output_filename
        self._load_config()
    
    def _load_config(self):
        """Load configuration from environment variables."""
        load_dotenv()
        if not self.output_filename:
            self.output_filename = os.getenv("OUTPUT_FILENAME", "results.xlsx")
    
    def _get_versioned_filename(self) -> str:
        """
        Get a versioned filename that doesn't exist yet.
        
        Returns:
            Full path to the versioned filename
        """
        # Ensure output directory exists
        output_dir = os.path.join(os.getcwd(), "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Find a new versioned filename
        base, ext = os.path.splitext(self.output_filename)
        version = 1
        while True:
            candidate = os.path.join(output_dir, f"{base}_v{version}{ext}")
            if not os.path.exists(candidate):
                break
            version += 1
        
        return candidate
    
    def save_pattern_results(self, df: pd.DataFrame, row_matches: Dict[int, List[int]], 
                           pattern_groups: List[Dict]) -> str:
        """
        Save pattern matching results to an Excel file.
        
        Args:
            df: Filtered DataFrame with matching rows
            row_matches: Mapping of row indices to matching pattern groups
            pattern_groups: List of pattern group configurations
            
        Returns:
            Path to the saved Excel file
        """
        if df.empty or not row_matches:
            print("No rows to save.")
            return ""
        
        output_path = self._get_versioned_filename()
        
        try:
            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                for i, group in enumerate(pattern_groups):
                    # Find all rows that matched this group
                    matching_indices = [idx for idx, groups in row_matches.items() if i in groups]
                    if not matching_indices:
                        continue
                    
                    # Prepare data for this sheet
                    pattern_str = json.dumps(group, ensure_ascii=False)
                    rows = df.loc[matching_indices, [col for col in ["Cuenta", "Mensaje", "Foro"] if col in df.columns]]
                    # Write header and data starting from row 2
                    rows.to_excel(writer, sheet_name=f"Pattern_{i+1}", startrow=1, index=False)
                # After all sheets are written, write the pattern string in the first row of each sheet
                for i, group in enumerate(pattern_groups):
                    matching_indices = [idx for idx, groups in row_matches.items() if i in groups]
                    if not matching_indices:
                        continue
                    ws = writer.sheets[f"Pattern_{i+1}"]
                    pattern_str = json.dumps(group, ensure_ascii=False)
                    ws.cell(row=1, column=1, value=pattern_str)
            print(f"Results saved to {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error saving Excel file: {e}")
            return ""
    
    def save_simple_results(self, df: pd.DataFrame, sheet_name: str = "Data") -> str:
        """
        Save a simple DataFrame to Excel without pattern grouping.
        
        Args:
            df: DataFrame to save
            sheet_name: Name of the sheet
            
        Returns:
            Path to the saved Excel file
        """
        if df.empty:
            print("No data to save.")
            return ""
        
        output_path = self._get_versioned_filename()
        
        try:
            with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            print(f"Results saved to {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error saving Excel file: {e}")
            return ""


def save_to_excel(df: pd.DataFrame, row_matches: Dict[int, List[int]], 
                 pattern_groups: List[Dict], output_filename: Optional[str] = None) -> str:
    """
    Convenience function to save pattern matching results to Excel.
    
    Args:
        df: Filtered DataFrame with matching rows
        row_matches: Mapping of row indices to matching pattern groups
        pattern_groups: List of pattern group configurations
        output_filename: Optional custom output filename
        
    Returns:
        Path to the saved Excel file
    """
    writer = ExcelWriter(output_filename)
    return writer.save_pattern_results(df, row_matches, pattern_groups) 