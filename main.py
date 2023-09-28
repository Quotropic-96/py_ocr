import pandas as pd
import os
import logging

# Checking variables
LETTERS_AND_SPACE = "abcdefghijklmnopqrstuvwxyzáéíóúñüABCDEFGHIJKLMNOPQRSTUVWXYZÁÉÍÓÚÑÜ "

# Initialize the logger
logging.basicConfig(level=logging.ERROR, format='%(message)s')
logger = logging.getLogger(__name__)





def clean_dataframe(df, filename):
    
    def parse_name(cell_value, idx):
      """
      Removes all characters from a cell that are not Spanish letters.
      """
      try:
        if isinstance(cell_value, str):  # Check if the value is a string
            return ''.join(c for c in cell_value if c in LETTERS_AND_SPACE).strip()
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
        
    def parse_object(cell_value,idx):
        """
        Parses the value in the third column: retains only letters and replaces 'Idem' with the value of the previous row.
        """
        try:
            if isinstance(cell_value, str):  # Check if the value is a string
                # Remove characters that aren't Spanish letters
                clean_value = ''.join(c for c in cell_value if c in LETTERS_AND_SPACE).strip()
                
                # If the value contains "Idem" or "ldem" and there is a previous row
                if ("Idem" in clean_value  or "ldem" in clean_value) and idx > 0:
                    return ''.join(c for c in df.iloc[idx - 1, 2] if c in LETTERS_AND_SPACE).strip()
                else:
                    return clean_value
        except Exception as e:
            line_number = idx + 2  # Adjusting for 0-based index and header
            logger.error(f"File: {filename} | Line: {line_number} | Error parsing object '{cell_value}': {e}")
        return cell_value  # Return the original value if not properly parsed

    # Cleaning the name column
    df[df.columns[0]] = df[df.columns[0]].apply(lambda x: parse_name(x, df.index[df[df.columns[0]] == x].tolist()[0]))

    # Cleaning the date column
    df[df.columns[1]] = df[df.columns[1]].apply(lambda x: parse_date(x, df.index[df[df.columns[1]] == x].tolist()[0]))

    # Parsing the object column
    df[df.columns[2]] = df[df.columns[2]].apply(lambda x: parse_object(x, df.index[df[df.columns[2]] == x].tolist()[0]))


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
