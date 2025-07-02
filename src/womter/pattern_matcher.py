"""
Pattern matcher module for filtering Excel data based on string patterns.
"""

import os
import json
import pandas as pd
from typing import List, Optional, Dict, Any, Union
from dotenv import load_dotenv
from datetime import datetime
from .excel_writer import ExcelWriter


class PatternMatcher:
    """A class to match patterns in Excel data and filter rows."""
    
    def __init__(self, patterns_file: str = "patterns.json"):
        """
        Initialize the pattern matcher.
        
        Args:
            patterns_file: Path to JSON file containing pattern configurations
        """
        self.patterns_file = patterns_file
        self.pattern_groups = []
        self._load_patterns()
    
    def _load_patterns(self):
        """Load patterns from JSON file."""
        try:
            if os.path.exists(self.patterns_file):
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    self.pattern_groups = json.load(f)
                print(f"Loaded {len(self.pattern_groups)} pattern group(s) from {self.patterns_file}")
            else:
                print(f"Pattern file {self.patterns_file} not found. No filtering will be applied.")
                self.pattern_groups = []
        except json.JSONDecodeError as e:
            print(f"Error parsing patterns file: {e}")
            self.pattern_groups = []
        except Exception as e:
            print(f"Error loading patterns: {e}")
            self.pattern_groups = []
    
    def match_patterns(self, df: pd.DataFrame) -> tuple[pd.DataFrame, Dict[int, List[int]]]:
        """
        Filter DataFrame based on pattern groups.
        
        Args:
            df: Input DataFrame
            
        Returns:
            Tuple of (filtered DataFrame, mapping of row indices to matching pattern groups)
        """
        if df.empty or not self.pattern_groups:
            return df, {}
        
        # Start with no matches
        combined_mask = pd.Series([False] * len(df), index=df.index)
        row_matches = {}  # Maps row index to list of matching pattern group indices
        
        for i, pattern_group in enumerate(self.pattern_groups):
            group_mask = pd.Series([True] * len(df), index=df.index)
            # --- CUENTA ---
            cuenta_val = pattern_group.get('cuenta', None)
            if cuenta_val and 'Cuenta' in df.columns:
                if isinstance(cuenta_val, list):
                    cuenta_mask = pd.Series([False] * len(df), index=df.index)
                    for val in cuenta_val:
                        if val:
                            cuenta_mask |= df['Cuenta'].str.contains(str(val), case=False, na=False)
                    group_mask &= cuenta_mask
                else:
                    group_mask &= df['Cuenta'].str.contains(str(cuenta_val), case=False, na=False)
            # --- FORO ---
            foro_val = pattern_group.get('foro', None)
            if foro_val and 'Foro' in df.columns:
                if isinstance(foro_val, list):
                    foro_mask = pd.Series([False] * len(df), index=df.index)
                    for val in foro_val:
                        if val:
                            foro_mask |= df['Foro'].str.contains(str(val), case=False, na=False)
                    group_mask &= foro_mask
                else:
                    group_mask &= df['Foro'].str.contains(str(foro_val), case=False, na=False)
            # --- MENSAJE ---
            mensaje_val = pattern_group.get('mensaje', None)
            if mensaje_val and 'Mensaje' in df.columns:
                if isinstance(mensaje_val, list):
                    mensaje_mask = pd.Series([False] * len(df), index=df.index)
                    for pattern in mensaje_val:
                        if pattern:
                            mensaje_mask |= df['Mensaje'].str.contains(str(pattern), case=False, na=False)
                    group_mask &= mensaje_mask
                else:
                    group_mask &= df['Mensaje'].str.contains(str(mensaje_val), case=False, na=False)
            # Track which rows match this group
            matching_rows = df.index[group_mask]
            for row_idx in matching_rows:
                if row_idx not in row_matches:
                    row_matches[row_idx] = []
                row_matches[row_idx].append(i)
            # Add this group's matches to combined results
            combined_mask |= group_mask
        return df[combined_mask], row_matches
    
    def display_matches(self, df: pd.DataFrame, row_matches: Dict[int, list] = None, original_df: pd.DataFrame = None):
        """
        Display matching rows grouped by pattern.
        Args:
            df: DataFrame to display (should be filtered)
            row_matches: Mapping of row indices to matching pattern groups
            original_df: Original DataFrame for context
        """
        if df.empty or not row_matches:
            print("No rows match the specified patterns.")
            return

        print(f"\nFound {len(df)} matching row(s):")
        print("=" * 60)

        # For each pattern group, print the pattern and the rows that match it
        for i, group in enumerate(self.pattern_groups):
            # Find all rows that matched this group
            matching_indices = [idx for idx, groups in row_matches.items() if i in groups]
            if not matching_indices:
                continue
            print(f"Pattern {i+1}: {json.dumps(group, ensure_ascii=False)}")
            print("-" * 40)
            for idx in matching_indices:
                row = df.loc[idx]
                print(f"Cuenta: {row.get('Cuenta', '')}")
                print(f"Mensaje: {row.get('Mensaje', '')}")
                print(f"Foro: {row.get('Foro', '')}")
                print()
            print("=" * 40)
    
    def get_pattern_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current pattern configuration.
        
        Returns:
            Dictionary with pattern configuration
        """
        total_patterns = 0
        for group in self.pattern_groups:
            if 'cuenta' in group and group['cuenta']:
                total_patterns += 1
            if 'foro' in group and group['foro']:
                total_patterns += 1
            if 'mensaje' in group and group['mensaje']:
                total_patterns += len(group['mensaje'])
        
        return {
            'pattern_groups': self.pattern_groups,
            'total_groups': len(self.pattern_groups),
            'total_patterns': total_patterns
        }

    def save_matches_to_excel(self, df: pd.DataFrame, row_matches: Dict[int, list], output_filename: Optional[str] = None):
        """
        Save the matching results to an Excel file using the ExcelWriter class.
        
        Args:
            df: Filtered DataFrame
            row_matches: Mapping of row indices to matching pattern groups
            output_filename: Desired output file name (from .env)
        """
        if df.empty or not row_matches:
            print("No rows to save.")
            return
        
        writer = ExcelWriter(output_filename)
        writer.save_pattern_results(df, row_matches, self.pattern_groups)


def match_excel_patterns(df: pd.DataFrame, patterns_file: str = "patterns.json") -> tuple[pd.DataFrame, Dict[int, List[int]]]:
    """
    Convenience function to match patterns in Excel data.
    
    Args:
        df: Input DataFrame
        patterns_file: Path to JSON file containing pattern configurations
        
    Returns:
        Tuple of (filtered DataFrame, mapping of row indices to matching pattern groups)
    """
    matcher = PatternMatcher(patterns_file)
    return matcher.match_patterns(df) 