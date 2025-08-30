#!/usr/bin/env python3
"""
Main entry point for the Womter application.

This script provides a command-line interface to read and display Excel file contents
with pattern matching capabilities.
"""

import sys
import os
import argparse

# Add src to Python path so we can import our package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from womter.reader import read_excel_file


def main():
    """Main function to run the Womter application."""
    parser = argparse.ArgumentParser(
        description="Read and filter Excel files based on patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Use patterns from .env file
  python main.py --no-patterns      # Show all data without filtering
  python main.py --help             # Show this help message
        """
    )
    
    parser.add_argument(
        '--no-patterns',
        action='store_true',
        help='Show all data without applying pattern matching'
    )
    
    args = parser.parse_args()
    
    try:
        use_patterns = not args.no_patterns
        read_excel_file(use_patterns=use_patterns)
    except ValueError as e:
        print(f"Configuration Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 