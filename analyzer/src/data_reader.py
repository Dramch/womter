import os
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any
import unicodedata


class DataReader:
    """
    A class to read Excel data files from the data/input directory.
    Organizes data by language tabs and stores column information.
    """
    
    def __init__(self, input_dir: str = "data/input"):
        """
        Initialize the DataReader.
        
        Args:
            input_dir (str): Path to the input directory containing Excel files
        """
        self.input_dir = Path(input_dir)
        self.data: Dict[str, pd.DataFrame] = {}
        self.columns: List[str] = []
        self.languages: List[str] = []
        
    def _normalize_column_name(self, column_name: str) -> str:
        """
        Normalize column name by removing accents and converting to lowercase.
        
        Args:
            column_name (str): Original column name
            
        Returns:
            str: Normalized column name (tideless and lowercase)
        """
        # Remove accents and convert to lowercase
        normalized = unicodedata.normalize('NFD', str(column_name))
        normalized = ''.join(c for c in normalized if not unicodedata.combining(c))
        return normalized.lower()
    
    def _normalize_dataframe_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize all column names in a DataFrame while preserving row data.
        
        Args:
            df (pd.DataFrame): DataFrame with original column names
            
        Returns:
            pd.DataFrame: DataFrame with normalized column names (row data unchanged)
        """
        # Create a mapping of old column names to new normalized names
        column_mapping = {col: self._normalize_column_name(col) for col in df.columns}
        
        # Create a copy of the DataFrame and rename only the columns
        df_copy = df.copy()
        df_copy.columns = [self._normalize_column_name(col) for col in df.columns]
        return df_copy
    
    def read_all_files(self) -> Dict[str, pd.DataFrame]:
        """
        Read all Excel files from the input directory.
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary with language as key and DataFrame as value
        """
        # Create input directory if it doesn't exist
        if not self.input_dir.exists():
            self.input_dir.mkdir(parents=True, exist_ok=True)
            raise FileNotFoundError(f"Input directory {self.input_dir} does not exist")
            
        # Get all Excel files in the input directory
        excel_files = list(self.input_dir.glob("*.xlsx")) + list(self.input_dir.glob("*.xls"))
        
        if not excel_files:
            raise FileNotFoundError(f"No Excel files found in {self.input_dir}")
            
        # Read the first file to get column information
        first_file = excel_files[0]
        print(f"Reading file: {first_file.name}")
        
        # Read all sheets from the first file
        excel_file = pd.ExcelFile(first_file)
        sheet_names = excel_file.sheet_names
        
        # Filter out the "all" tab and get language tabs
        language_tabs = [sheet for sheet in sheet_names if sheet.lower() != "all"]
        self.languages = language_tabs
        
        # Read columns from the first language tab
        if language_tabs:
            first_tab = language_tabs[0]
            sample_df = pd.read_excel(first_file, sheet_name=first_tab)
            # Get normalized column names (without modifying the sample data)
            normalized_columns = [self._normalize_column_name(col) for col in sample_df.columns]
            self.columns = normalized_columns
            print(f"Columns found: {self.columns}")
            print(f"Language tabs: {self.languages}")
        
        # Read data from all files
        for file_path in excel_files:
            print(f"Processing file: {file_path.name}")
            self._read_file(file_path)
            
        return self.data
    
    def _read_file(self, file_path: Path) -> None:
        """
        Read a single Excel file and add its data to the main data dictionary.
        
        Args:
            file_path (Path): Path to the Excel file
        """
        try:
            excel_file = pd.ExcelFile(file_path)
            
            for language in self.languages:
                if language in excel_file.sheet_names:
                    # Read the language tab
                    df = pd.read_excel(file_path, sheet_name=language)
                    
                    # Normalize column names
                    df = self._normalize_dataframe_columns(df)
                    
                    # Ensure columns match (after normalization)
                    if list(df.columns) != self.columns:
                        print(f"Warning: Columns in {language} tab of {file_path.name} don't match expected columns after normalization")
                        continue
                    
                    # Add to data dictionary
                    if language in self.data:
                        # Append to existing data
                        self.data[language] = pd.concat([self.data[language], df], ignore_index=True)
                    else:
                        # Create new entry
                        self.data[language] = df
                        
                    print(f"  - Added {len(df)} rows from {language} tab")
                    
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
    
    def get_language_data(self, language: str) -> pd.DataFrame:
        """
        Get data for a specific language.
        
        Args:
            language (str): Language code (e.g., 'es', 'en')
            
        Returns:
            pd.DataFrame: Data for the specified language
        """
        return self.data.get(language, pd.DataFrame())
    
    def get_all_data(self) -> Dict[str, pd.DataFrame]:
        """
        Get all data organized by language.
        
        Returns:
            Dict[str, pd.DataFrame]: All data organized by language
        """
        return self.data
    
    def get_columns(self) -> List[str]:
        """
        Get the column names.
        
        Returns:
            List[str]: List of column names
        """
        return self.columns.copy()
    
    def get_languages(self) -> List[str]:
        """
        Get the list of available languages.
        
        Returns:
            List[str]: List of available language codes
        """
        return self.languages.copy()
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the loaded data.
        
        Returns:
            Dict[str, Any]: Summary information about the data
        """
        summary = {
            "total_files_processed": len(list(self.input_dir.glob("*.xlsx")) + list(self.input_dir.glob("*.xls"))),
            "languages": self.languages,
            "columns": self.columns,
            "total_rows_by_language": {},
            "total_rows": 0
        }
        
        for language, df in self.data.items():
            row_count = len(df)
            summary["total_rows_by_language"][language] = row_count
            summary["total_rows"] += row_count
            
        return summary
    
    def print_summary(self) -> None:
        """
        Print a summary of the loaded data to the console.
        """
        summary = self.get_summary()
        
        print("\n" + "="*50)
        print("DATA READER SUMMARY")
        print("="*50)
        print(f"Files processed: {summary['total_files_processed']}")
        print(f"Languages found: {', '.join(summary['languages'])}")
        print(f"Total columns: {len(summary['columns'])}")
        print(f"Total rows: {summary['total_rows']}")
        print("\nRows by language:")
        for language, count in summary['total_rows_by_language'].items():
            print(f"  {language}: {count:,} rows")
        print("="*50)


def main():
    """
    Example usage of the DataReader class.
    """
    try:
        # Initialize the reader
        reader = DataReader()
        
        # Read all files
        data = reader.read_all_files()
        
        # Print summary
        reader.print_summary()
        
        # Example: Access data for a specific language
        if 'es' in data:
            spanish_data = reader.get_language_data('es')
            print(f"\nSpanish data shape: {spanish_data.shape}")
            print(f"First few rows of Spanish data:")
            print(spanish_data.head())
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
