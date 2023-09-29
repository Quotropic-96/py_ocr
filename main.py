import pandas as pd
import os
import math
import logging

# Checking variables
LETTERS = "abcdefghijklmnopqrstuvwxyzáéíóúñüABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚÑÜ"
SPACE = " "
PARETHESES = "()"

ALLOWED_CHARS_NAME = LETTERS + SPACE
ALLOWED_CHARS_OBJECT = LETTERS + SPACE
ALLOWED_CHARS_PLACE = LETTERS + SPACE + PARETHESES
ALLOWED_CHARS_STATE = LETTERS

# Initialize the logger
logging.basicConfig(level=logging.ERROR, format='%(message)s')
logger = logging.getLogger(__name__)

def clean_dataframe(df, filename):
    cleaned_objects = []
    cleaned_places = []
    
    def parse_name(cell_value, idx):
      """
      Removes all characters from a cell that are not Spanish letters.
      """
      try:
        if isinstance(cell_value, str):  # Check if the value is a string
            return ''.join(c for c in cell_value if c in ALLOWED_CHARS_NAME).strip()
      except Exception as e:
          line_number = idx + 2  # Adjusting for 0-based index and header
          logger.error(f"File: {filename} | Line: {line_number} | Error parsing name '{cell_value}': {e}")
          return cell_value  # Return the original value if not a string
    
    def parse_date(cell_value, idx):
        """
        Checks if the cell value is an integer between 1700 and 1904. 
        """
        try:
            if 1700 <= int(cell_value) <= 1904:
                return int(cell_value)
            else:
              raise ValueError(f"Year out of range {cell_value}") 
        except Exception as e:
            line_number = idx + 2  # Adjusting for 0-based index and header
            logger.error(f"File: {filename} | Line: {line_number} | Error parsing date '{cell_value}': {e}")
            return 0
        
    def parse_object(cell_value, idx):
        """
        Parses the value in the third column: retains only letters and replaces 'Idem' with the value of the previous row.
        """
        try:
            if isinstance(cell_value, str):  # Check if the value is a string
                
                # If the value contains "Idem" or "ldem" and there is a previous row
                if ("Idem" in cell_value or "ldem" in cell_value) and idx > 0:
                    last_valid_value = cleaned_objects[-2] if cleaned_objects[-1] == 'Idem' else cleaned_objects[-1]
                    cleaned_objects.append(last_valid_value)
                    return last_valid_value
            
                else:
                    # Remove characters that aren't Spanish letters
                    clean_value = ''.join(c for c in cell_value if c in ALLOWED_CHARS_OBJECT).strip()
                    cleaned_objects.append(clean_value)
                    return clean_value
                
        except Exception as e:
            line_number = idx + 2  # Adjusting for 0-based index and header
            logger.error(f"File: {filename} | Line: {line_number} | Error parsing object '{cell_value}': {e}")
        return cell_value  # Return the original value if not properly parsed

    def parse_place(cell_value, idx):
        """
        Parses the value in the fourth column: 
        1. Retains only letters and replaces 'Idem' with the value of the previous row.
        2. Retains only letters.
        3. Capitalizes each word.
        """
        try:
            if isinstance(cell_value, str):  # Check if the value is a string
                    
                # If the value contains "Idem" or "ldem" and there is a previous row
                if ("Idem" in cell_value or "ldem" in cell_value) and idx > 0:
                    # If the last value in cleaned_places is an 'Idem', use the value before that, else use the last value
                    last_valid_value = cleaned_places[-2] if cleaned_places[-1] == 'Idem' else cleaned_places[-1]
                    cleaned_places.append(last_valid_value)
                    return last_valid_value
                
                else:
                    # Remove characters that aren't in ALLOWED_CHARS_PLACE
                    clean_value = ''.join(c for c in cell_value if c in ALLOWED_CHARS_PLACE).strip()
                    # Capitalize each word in the string
                    clean_value = ' '.join([word.capitalize() for word in clean_value.split()])
                    cleaned_places.append(clean_value)  # Store the cleaned value
                    return clean_value
                    
        except Exception as e:
            line_number = idx + 2  # Adjusting for 0-based index and header
            logger.error(f"File: {filename} | Line: {line_number} | Error parsing place '{cell_value}': {e}")
        
        cleaned_places.append(cell_value)  # If there's an error, store the original value
        return cell_value

    def parse_state(cell_value, idx):
        """
        Parses the next column:
        1. Check that the cell is not empty.
        2. Allow only uppercase letters.
        3. If the value contains lowercase letters, convert them to uppercase.
        """
        try:
            if isinstance(cell_value, str):  # Check if the value is a string
                if isinstance(cell_value, str):
                    # Check if the value only contains capital letters
                    if all(c.isupper() or c.isspace() for c in cell_value):
                        return cell_value
                    else:
                        logger.error(f"File: {filename} | Line: {line_number} | Error parsing state {cell_value}: Unexpected character. Expected only capital letters.")
                else:
                    logger.error(f"File: {filename} | Line: {line_number} | Error parsing state {cell_value}: Expected string but found {type(cell_value)}.")

            if cell_value is None or math.isnan(cell_value):
                line_number = idx + 2  # Adjusting for 0-based index and header
                logger.error(f"File: {filename} | Line: {line_number} | Error parsing state {cell_value}: Cell is empty")
                return cell_value
                    
        except Exception as e:
            line_number = idx + 2  # Adjusting for 0-based index and header
            logger.error(f"File: {filename} | Line: {line_number} | Error parsing state '{cell_value}': {e}")
        
        return cell_value
    

    # Cleaning the name column
    df[df.columns[0]] = [parse_name(value, idx) for idx, value in enumerate(df[df.columns[0]])]

    # Cleaning the date column
    df[df.columns[1]] = [parse_date(value, idx) for idx, value in enumerate(df[df.columns[1]])]

    # Parsing the object column
    df[df.columns[2]] = [parse_object(value, idx) for idx, value in enumerate(df[df.columns[2]])]

    # Parsing the place column
    df[df.columns[3]] = [parse_place(value, idx) for idx, value in enumerate(df[df.columns[3]])]

    # Parsing the state column
    df[df.columns[4]] = [parse_state(value, idx) for idx, value in enumerate(df[df.columns[4]])]


    return df


def merge_csv_files(input_dir):
    """
    Iterates over all CSV files in the specified directory, cleans them, and merges them.
    """
    list_of_dfs = []

    for filename in os.listdir(input_dir):
        if filename.endswith('.csv'):
            filepath = os.path.join(input_dir, filename)
            df = pd.read_csv(filepath, delimiter=';', dtype=str)
            cleaned_df = clean_dataframe(df, filename)
            list_of_dfs.append(cleaned_df)

    merged_df = pd.concat(list_of_dfs, ignore_index=True)
    return merged_df


def main():
    try:
      input_dir = 'input'
      output_dir = 'output'

      # Ensure the output directory exists
      if not os.path.exists(output_dir):
          os.makedirs(output_dir)

      # Merge all CSV files in the input directory
      merged_df = merge_csv_files(input_dir)

      # Now save the cleaned and merged data
      merged_df.to_csv(os.path.join(output_dir, "merged_output.csv"), index=False, sep=';')
      # Print the log messages
      if logger.handlers:
          for handler in logger.handlers:
              handler.flush()
              handler.close()
          logger.handlers.clear()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


if __name__ == '__main__':
    main()
