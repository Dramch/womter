

from reader import DataReader
from writter import DataWriter


def main():
    """Main function to run the merger application."""
    reader = DataReader("data/input")
    reader.process_all_data()
    
    language_data = reader.get_language_data()
    
    writer = DataWriter("data/output")
    output_file = writer.write_to_excel(language_data)
    
    print(f"Processed {len(language_data)} languages and created: {output_file}")


if __name__ == "__main__":
    main()
