import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from pattern_reader import PatternReader
from data_reader import DataReader
from analyzer import Analyzer
from writter import Writter


def main():
    """Main function to run the analyzer application and apply patterns to data."""
    # Load patterns
    pattern_reader = PatternReader("data/patterns")
    patterns = pattern_reader.read_patterns()
    
    # Load data
    data_reader = DataReader("data/input")
    data = data_reader.read_all_files()
    
    # Analyze data with patterns
    analyzer = Analyzer("data/log")
    results = analyzer.apply_patterns(data, patterns)
    
    # Write results to XLSX file
    writter = Writter("data/log")
    output_file = writter.write_analysis_results(results, patterns, "data/output")
    
    print(f"Analysis completed successfully! Results saved to: {output_file}")


if __name__ == "__main__":
    main()
