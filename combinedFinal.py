import streamlit as st
import pandas as pd
from io import BytesIO
import requests
import xml.etree.ElementTree as ET
import re
import pyisbn

APIKEY = "VwdNr2kjw0YPqIPDeY1tJU3cHMpQWQN5amDAwCijQlwE3W7Np9ETk3knq0cSag63GxlaBBBtjvFmPcEI"
toStrip = ",./© "

# Function to fetch data by ISBN from the WorldCat API
def getByISBN(isbn):
    url = f"https://worldcat.org/webservices/catalog/content/isbn/{isbn}?wskey={APIKEY}"
    response = requests.get(url)
    return response.content.decode()

# Function to fetch data by ISSN from the WorldCat API
def getByISSN(issn):
    url = f"https://worldcat.org/webservices/catalog/content/issn/{issn}?wskey={APIKEY}"
    response = requests.get(url)
    return response.content.decode()

# Extract title and publisher details from the API response
def parse_api_response(content):
    parsed = ET.fromstring(content)
    title, publisher, publicationYear = "", "", ""
    
    for child in parsed:
        tag = child.get("tag")
        ind1 = child.get("ind1")
        ind2 = child.get("ind2")

        # Extract the title (tag = 245)
        if tag == "245":
            titleA, titleB = "", ""
            for grandchild in child:
                code = grandchild.get("code")
                if code == "a": 
                    titleA = grandchild.text
                elif code == "b": 
                    titleB = grandchild.text
            title = (titleA + " " + titleB).strip(toStrip)
        
        # Extract the publisher (tag = 260 or 264)
        elif (tag == "260") or (tag == "264" and ind2 == "1"):
            for grandchild in child:
                code = grandchild.get("code")
                if code == "b":
                    publisher = grandchild.text.strip(toStrip)
                elif code == "c":
                    publicationYear = grandchild.text.strip(toStrip)
    
    return title, publisher, publicationYear

# Function to convert ISBN-10 to ISBN-13
def convert_isbn_using_pyisbn(isbn):
    isbn = isbn.replace('-', '').strip()
    if len(isbn) == 10:
        try:
            isbn10 = pyisbn.Isbn10(isbn)
            return isbn10.convert()
        except ValueError as e:
            st.write(f"Conversion failed for ISBN {isbn}: {e}")
            return isbn
    return isbn

# Check and format ISSN to 'XXXX-XXXX'
def format_issn(issn):
    issn = issn.strip().upper()
    pattern = re.compile(r'^(\d{4})-?(\d{3}[0-9X])$')
    match = pattern.match(issn)
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    return '0000-0000'

# Apply function based on string length (ISBN or ISSN)
def apply_function_based_on_length(s):
    if len(s) >= 10:
        return convert_isbn_using_pyisbn(s)
    return format_issn(s)

# Process the data and apply WorldCat API functions
def process_data(data):
    query_limit = 5
    query_count = 0
    
    if 'Title' not in data.columns:
        data['Title'] = ""
    if 'Publisher' not in data.columns:
        data['Publisher'] = ""
    if 'PublicationYear' not in data.columns:
        data['PublicationYear'] = ""
    
    if 'ISSN' in data.columns:
        data['ISSN'] = data['ISSN'].str.replace(' ', '').str.replace('-', '')
        data['ISSN'] = data['ISSN'].replace({'': '0000-0000', 'nan': '0000-0000', '?': '0000-0000'})
        data['ISSN'] = data['ISSN'].apply(lambda x: apply_function_based_on_length(str(x)))
        
        # Iterate through the ISSN and retrieve corresponding data from the API
        for i, issn in enumerate(data['ISSN']):
            if issn != '0000-0000' and query_count < query_limit:
                content = getByISSN(issn)
                title, publisher, publicationYear = parse_api_response(content)
                
                # Add the information to the DataFrame
                data.at[i, 'Title'] = title
                data.at[i, 'Publisher'] = publisher
                data.at[i, 'PublicationYear'] = publicationYear

                # Increment query count
                query_count += 1
    
    return data


# Set up Streamlit app structure
st.title('ILL Data Processing App')

# File upload functionality
uploaded_file = st.file_uploader("Upload your data file", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # Read the file into a dataframe
        if uploaded_file.name.endswith('.csv'):
            data = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            data = pd.read_excel(uploaded_file)
        
        # Process the data
        processed_data = process_data(data)
        
        # Display insights
        st.write("Data Processing Completed!")
        st.write(f"Number of rows: {processed_data.shape[0]}")
        st.write(f"Number of columns: {processed_data.shape[1]}")
        
        # Convert DataFrame to Excel for download
        def to_excel(df):
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='ProcessedData')
            return output.getvalue()

        # Download button for processed data
        excel_bytes = to_excel(processed_data)
        st.download_button(
            label="Download processed data as Excel",
            data=excel_bytes,
            file_name='processed_data.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        st.error(f"An error occurred: {e}")
