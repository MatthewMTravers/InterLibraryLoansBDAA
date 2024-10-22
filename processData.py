# pip install numpy pandas pyisbn openpyxl
import re
import pandas as pd
import pyisbn

INPUT_FILE = 'ILL.xlsx'
OUTPUT_FILE = 'CleanedData.xlsx'

# Convert ISBN-10 to ISBN-13 using pyisbn library.
def convert_isbn_using_pyisbn(isbn):
    isbn = isbn.replace('-', '').strip()  # Clean the ISBN
    if len(isbn) == 10:
        try:
            isbn10 = pyisbn.Isbn10(isbn)
            return isbn10.convert()
        except ValueError as e:
            # Return the original ISBN if conversion fails
            print(f"Conversion failed for ISBN {isbn}: {e}")
            return isbn
    else:
        return isbn

# Check and format ISSN to 'XXXX-XXXX' format.
def format_issn(issn):
    issn = issn.strip().upper()
    pattern = re.compile(r'^(\d{4})-?(\d{3}[0-9X])$')
    match = pattern.match(issn)
    if match:
        # Correct format, return in 'XXXX-XXXX' format
        return f"{match.group(1)}-{match.group(2)}"
    else:
        # If not matching, return a placeholder
        return '0000-0000'

# Define a function to apply different functions based on string length
def apply_function_based_on_length(s):
    if len(s) >= 10:
        return convert_isbn_using_pyisbn(s)
    else:
        return format_issn(s)

df = pd.read_excel(INPUT_FILE)

# Clean and transform 'ISSN' column
df['ISSN'] = df['ISSN'].str.replace(' ', '').str.replace('-', '')
df['ISSN'] = df['ISSN'].replace({'': '0000-0000', 'nan': '0000-0000', '?': '0000-0000'})
df['ISSN'] = df['ISSN'].apply(lambda x: apply_function_based_on_length(str(x)))

# Save cleaned data to Excel file
df.to_excel(OUTPUT_FILE, index=False)
print(f'Data saved to {OUTPUT_FILE}')