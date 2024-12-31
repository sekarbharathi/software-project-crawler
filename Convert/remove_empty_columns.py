import pandas as pd

def remove_empty_columns(input_file, output_file):
    """
    Removes columns with no values from a CSV file and saves the cleaned data to a new file.
    
    Parameters:
        input_file (str): Path to the input CSV file.
        output_file (str): Path to save the cleaned CSV file.
    """
    try:
        # Read the CSV file
        data = pd.read_csv(input_file)
        
        # Remove columns with all NaN or missing values
        cleaned_data = data.dropna(axis=1, how='all')
        
        # Save the cleaned data to a new CSV file
        cleaned_data.to_csv(output_file, index=False)
        
        print(f"Columns with no values removed. Cleaned file saved as '{output_file}'.")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    input_file = 'new_converted_output_with_levels.csv'  # Input CSV file
    output_file = 'cleaned_output.csv'  # Output CSV file
    
    # Call the function to remove empty columns
    remove_empty_columns(input_file, output_file)

if __name__ == '__main__':
    main()
